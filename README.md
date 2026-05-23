# 🧬 Biomedical Paper Summarizer

A Streamlit web app that extracts structured insights from biomedical research abstracts using the Anthropic Claude API.

Paste any biomedical abstract and get an instant, structured breakdown — ideal for researchers, students, and anyone navigating dense scientific literature.

---

## Features

- Structured extraction across 6 key dimensions:
  - Research Objective
  - Methods Used
  - Key Findings
  - Drug Targets / Biological Entities
  - Clinical or Research Implications
  - Limitations
- Clean, professional UI with sidebar configuration
- Secure API key input (never stored)
- Error handling for auth failures and rate limits

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI / LLM | Anthropic Claude (`claude-sonnet-4-20250514`) |
| Language | Python 3.11 |
| Deployment | Hugging Face Spaces (planned) |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/biomedical-paper-summarizer.git
cd biomedical-paper-summarizer
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

### 5. Enter your API key

Get a free API key at [console.anthropic.com](https://console.anthropic.com) and paste it into the sidebar when the app loads.

---

## Project Structure

```
biomedical-paper-summarizer/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── images/             # Logo and assets
└── README.md
```

---

## About

Built by a Bioinformatics undergrad / Data Science MS student as a portfolio project demonstrating:
- LLM API integration (Anthropic Claude)
- Streamlit application development
- Biomedical NLP use cases

---

## License

MIT
