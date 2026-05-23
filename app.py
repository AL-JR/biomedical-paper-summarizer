import base64
import streamlit as st
import anthropic
import fitz  # PyMuPDF

st.set_page_config(
    page_title="Biomedical Paper Summarizer",
    page_icon="🧬",
    layout="wide",
)

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


def extract_pdf(pdf_bytes):
    """Extract full text and render each page as a PNG image."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []
    pages_images = []

    for page in doc:
        pages_text.append(page.get_text())
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        pages_images.append(base64.b64encode(pix.tobytes("png")).decode())

    return "\n\n".join(pages_text), pages_images


PROMPT = """You are a biomedical research assistant. Analyze the full research paper below — including any figures, graphs, and tables provided as page images — and return a comprehensive structured summary using exactly these six sections. Use markdown bold headers for each section.

1. **Research Objective** — What question or problem does this study address?
2. **Methods Used** — What experimental, computational, or statistical approaches were used?
3. **Key Findings** — What were the main results? Include specific data points or statistics where relevant. Reference figures or graphs where applicable.
4. **Drug Targets or Biological Entities Mentioned** — List genes, proteins, pathways, drugs, disease models, or organisms.
5. **Clinical or Research Implications** — Why do these findings matter? What do they enable or suggest?
6. **Limitations** — What limitations are stated or implied by the authors?"""

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
        has_text = paper_text.strip() != ""

        if not has_pdf and not has_text:
            st.warning("Please upload a PDF or paste paper text.")
        else:
            with st.spinner("Analyzing paper..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)

                    if has_pdf:
                        full_text, page_images = extract_pdf(uploaded_file.read())

                        if len(page_images) > 20:
                            st.info(f"Paper has {len(page_images)} pages — analyzing the first 20.")
                            page_images = page_images[:20]

                        content = [
                            {
                                "type": "text",
                                "text": f"{PROMPT}\n\nPaper text:\n{full_text}\n\nThe following are page images from the paper (figures, graphs, and tables are included):",
                            }
                        ]
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
                        content = [
                            {
                                "type": "text",
                                "text": f"{PROMPT}\n\nPaper text:\n{paper_text}",
                            }
                        ]

                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=2048,
                        messages=[{"role": "user", "content": content}],
                    )

                    st.divider()
                    st.subheader("Structured Summary")
                    st.markdown(message.content[0].text)

                except anthropic.AuthenticationError:
                    st.error("Invalid API key. Please check your Anthropic API key and try again.")
                except anthropic.RateLimitError:
                    st.error("Rate limit reached. Please wait a moment and try again.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
