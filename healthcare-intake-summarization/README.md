# Healthcare Patient Intake Summarization Platform

A RAG-backed pre-visit summarization platform that parses raw, unstructured patient-reported symptoms, checks them against standard clinical guidelines, and generates structured pre-visit physician charts. The platform programmatically guarantees a **0.0% diagnostic leakage rate** via an independent Python safety filter that intercepts clinical diagnoses (e.g. "appendicitis") before saving to the database.

---

## 🚀 Local Quick Start

### 1. Prerequisites
Ensure you have Docker and Python 3.11+ installed on your host system.

### 2. Start PostgreSQL Database
Spin up the database container (mapped to host port `5434` to prevent conflict with other projects):
```bash
docker compose up -d
```

### 3. Setup Python Virtual Environment
Install all required libraries inside a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Launch Ingestion API & Summarizer Engine
Start the FastAPI server (runs the API, connects to Postgres, and starts the summarizer listener on port `8002`):
```bash
PYTHONPATH=. .venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8002
```

### 5. Launch Streamlit Clinical Portal
In a separate terminal tab, run the Streamlit physician portal on port `8503`:
```bash
PYTHONPATH=. .venv/bin/streamlit run src/dashboard/app.py --server.port 8503
```
Now, open your browser and navigate to **`http://127.0.0.1:8503`**.

---

## 📁 Repository Directory Structure

```
healthcare-intake-summarization/
├── assets/                  # Frontend assets (hospital.jpg logo)
├── docs/                    # Technical architecture & financials
│   ├── CASE_STUDY.md        # Medical liability, scoping, & FTS RAG
│   └── ENGAGEMENT_SUMMARY.md# Project commercials (TCV, Milestones, TDS/GST)
├── notebooks/
│   └── rag_safety_eval.py   # Commented training, SentenceTransformer & local LLM code
├── src/
│   ├── api/
│   │   └── main.py          # FastAPI endpoints (intakes, safety audits, reprocess)
│   ├── dashboard/
│   │   └── app.py           # Streamlit clinical portal (Cisco/hospital branding)
│   ├── safety/
│   │   └── filter.py        # Programmatic lexical & syntactic safety gate
│   ├── summarizer/
│   │   └── engine.py        # RAG retrieval (FTS search) & Gemini/Mock LLM loops
│   ├── config.py            # Pydantic Settings env loader
│   └── database.py          # asyncpg connection pools and seed data
├── tests/
│   └── test_safety.py       # Unit tests verifying safety filter compliance
├── docker-compose.yml       # Local PostgreSQL database definition
└── requirements.txt         # Python package dependencies list
```

---

## 🧪 Running Unit Tests
Verify safety filter rules, syntactic checks, and blacklist matches:
```bash
PYTHONPATH=. .venv/bin/pytest tests/
```
