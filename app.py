import streamlit as st
import anthropic

st.set_page_config(
    page_title="Biomedical Paper Summarizer",
    page_icon="🧬",
    layout="wide",
)

# --- Header ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("images/logo.png", width=80)
    except Exception:
        st.markdown("🧬")
with col_title:
    st.title("Biomedical Paper Summarizer")
st.divider()

# --- API Key: use secret if available, otherwise ask the user ---
hosted_key = st.secrets.get("ANTHROPIC_API_KEY", "")

# --- Sidebar ---
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
        "This tool uses Claude to extract structured insights from biomedical papers — "
        "including objectives, methods, findings, drug targets, and clinical implications."
    )
    st.markdown("---")

# --- Main input ---
st.subheader("Paste your paper")
st.caption("Paste the full text of a biomedical research paper — abstract, methods, results, and discussion.")
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
    elif not paper_text.strip():
        st.warning("Please paste a paper before analyzing.")
    else:
        with st.spinner("Analyzing paper..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2048,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""You are a biomedical research assistant. Read the full research paper below and provide a comprehensive structured summary using exactly these six sections. Use markdown bold headers for each section.

1. **Research Objective** — What question or problem does this study address?
2. **Methods Used** — What experimental, computational, or statistical approaches were used?
3. **Key Findings** — What were the main results? Include specific data points or statistics where relevant.
4. **Drug Targets or Biological Entities Mentioned** — List genes, proteins, pathways, drugs, disease models, or organisms.
5. **Clinical or Research Implications** — Why do these findings matter? What do they enable or suggest?
6. **Limitations** — What limitations are stated or implied by the authors?

Paper:
{paper_text}""",
                        }
                    ],
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
