import base64
import streamlit as st
import anthropic
import fitz  # PyMuPDF

st.set_page_config(
    page_title="Biomedical Paper Summarizer",
    page_icon="🧬",
    layout="wide",
)

# --- Custom CSS ---
st.markdown("""
<style>
.section-card {
    background-color: #f8fafc;
    border-left: 4px solid #2563eb;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1e40af;
    margin-bottom: 0.4rem;
    letter-spacing: 0.03em;
}
.section-body {
    font-size: 0.95rem;
    color: #1e293b;
    line-height: 1.6;
}
.figure-caption {
    font-size: 0.75rem;
    color: #64748b;
    text-align: center;
    margin-top: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("images/caduceus.png", width=300)
    except Exception:
        st.markdown("🧬")
with col_title:
    st.title("Biomedical Paper Summarizer")
st.divider()

# --- API Key ---
hosted_key = st.secrets.get("ANTHROPIC_API_KEY", "")

with st.sidebar:
    st.header("Configuration")
    if hosted_key:
        api_key = hosted_key
        st.success("API key loaded from secrets.")
    else:
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="Get your key at console.anthropic.com",
        )
    st.markdown("---")
    st.markdown("**About**")
    st.markdown(
        "This tool uses Claude to extract structured insights from full biomedical research papers — "
        "including objectives, methods, findings, drug targets, and clinical implications. "
        "Upload a PDF to include graphs and figures in the analysis."
    )
    st.markdown("---")


SECTION_ICONS = {
    "Research Objective": "🎯",
    "Methods Used": "🔬",
    "Key Findings": "📊",
    "Drug Targets or Biological Entities Mentioned": "💊",
    "Clinical or Research Implications": "🏥",
    "Limitations": "⚠️",
}


def render_summary(text):
    """Parse Claude's ## sections and render each as a styled card."""
    import re
    parts = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("## "):
            lines = part.split("\n", 1)
            title = lines[0].replace("## ", "").strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            icon = SECTION_ICONS.get(title, "📌")
            body_html = body.replace("\n", "<br>")
            # render bold markdown **text** as <strong>
            import re as _re
            body_html = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body_html)
            st.markdown(f"""
            <div class="section-card">
                <div class="section-title">{icon} {title}</div>
                <div class="section-body">{body_html}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(part)


def extract_pdf(pdf_bytes):
    """Extract full text, page images (for Claude), and embedded figures (for display)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []
    pages_images = []
    figures = []

    for page_num, page in enumerate(doc):
        pages_text.append(page.get_text())
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        pages_images.append(base64.b64encode(pix.tobytes("png")).decode())

        for img in page.get_images(full=True):
            xref = img[0]
            base_img = doc.extract_image(xref)
            w, h = base_img["width"], base_img["height"]
            # skip tiny images (icons, bullets, etc.)
            if w >= 150 and h >= 150:
                figures.append({
                    "page": page_num + 1,
                    "bytes": base_img["image"],
                    "ext": base_img["ext"],
                })

    return "\n\n".join(pages_text), pages_images, figures


PROMPT = """You are a biomedical research assistant. Analyze the full research paper below — including any figures, graphs, and tables provided as page images — and return a comprehensive structured summary.

Use exactly these six sections, each starting with ## followed by the section name on its own line:

## Research Objective
What question or problem does this study address?

## Methods Used
What experimental, computational, or statistical approaches were used?

## Key Findings
What were the main results? Include specific data points or statistics where relevant. Reference figures or graphs where applicable.

## Drug Targets or Biological Entities Mentioned
List genes, proteins, pathways, drugs, disease models, or organisms.

## Clinical or Research Implications
Why do these findings matter? What do they enable or suggest?

## Limitations
What limitations are stated or implied by the authors?"""


# --- Input tabs ---
st.subheader("Input")
tab_pdf, tab_text = st.tabs(["Upload PDF", "Paste Text"])

with tab_pdf:
    uploaded_file = st.file_uploader(
        "Upload a biomedical research paper (PDF)",
        type="pdf",
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.caption(f"Uploaded: {uploaded_file.name}")

with tab_text:
    paper_text = st.text_area(
        label="Paper text",
        placeholder="Paste the full paper text here...",
        height=400,
        label_visibility="collapsed",
    )

analyze = st.button("Analyze Paper", type="primary")

# --- Analysis ---
if analyze:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    else:
        has_pdf = uploaded_file is not None
        has_text = "paper_text" in dir() and paper_text.strip() != ""

        if not has_pdf and not has_text:
            st.warning("Please upload a PDF or paste paper text.")
        else:
            with st.spinner("Analyzing paper..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    figures = []

                    if has_pdf:
                        full_text, page_images, figures = extract_pdf(uploaded_file.read())

                        if len(page_images) > 20:
                            st.info(f"Paper has {len(page_images)} pages — analyzing the first 20.")
                            page_images = page_images[:20]

                        content = [{
                            "type": "text",
                            "text": f"{PROMPT}\n\nPaper text:\n{full_text}\n\nPage images follow:",
                        }]
                        for img_b64 in page_images:
                            content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": img_b64,
                                },
                            })
                    else:
                        content = [{
                            "type": "text",
                            "text": f"{PROMPT}\n\nPaper text:\n{paper_text}",
                        }]

                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=2048,
                        messages=[{"role": "user", "content": content}],
                    )

                    st.divider()

                    # --- Layout: summary + figures side by side ---
                    if figures:
                        col_summary, col_figures = st.columns([3, 2])
                    else:
                        col_summary = st.container()
                        col_figures = None

                    with col_summary:
                        st.subheader("Structured Summary")
                        render_summary(message.content[0].text)

                    if col_figures and figures:
                        with col_figures:
                            st.subheader(f"Figures ({len(figures)} extracted)")
                            for i, fig in enumerate(figures):
                                st.image(
                                    fig["bytes"],
                                    caption=f"Figure {i + 1} — Page {fig['page']}",
                                    use_container_width=True,
                                )

                except anthropic.AuthenticationError:
                    st.error("Invalid API key. Please check your Anthropic API key and try again.")
                except anthropic.RateLimitError:
                    st.error("Rate limit reached. Please wait a moment and try again.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
