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
        "This tool uses Claude to extract structured insights from biomedical abstracts — "
        "including objectives, methods, findings, drug targets, and clinical implications."
    )
    st.markdown("---")

# --- Main input ---
st.subheader("Paste your abstract")
abstract = st.text_area(
    label="Abstract text",
    placeholder="Paste a biomedical research abstract here...",
    height=250,
    label_visibility="collapsed",
)

analyze = st.button("Analyze Paper", type="primary", use_container_width=False)

# --- Analysis ---
if analyze:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    elif not abstract.strip():
        st.warning("Please paste an abstract before analyzing.")
    else:
        with st.spinner("Analyzing abstract..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""You are a biomedical research assistant. Analyze the abstract below and return a structured summary using exactly these six sections. Use markdown bold headers for each section.

1. **Research Objective** — What question or problem does this study address?
2. **Methods Used** — What experimental, computational, or statistical approaches were used?
3. **Key Findings** — What were the main results?
4. **Drug Targets or Biological Entities Mentioned** — List genes, proteins, pathways, drugs, or organisms.
5. **Clinical or Research Implications** — Why do these findings matter?
6. **Limitations** — What limitations are stated or implied?

Abstract:
{abstract}""",
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
