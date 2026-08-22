# Healthcare Patient Intake Summarization Platform

**Problem:** A multi-location primary care clinic group (6 clinics, 40+ physicians, 15,000+ monthly intakes) was drowning in unstructured, patient-reported free-text. Clinicians wasted critical visit time parsing raw intake logs. The group wanted automated pre-visit summaries but had zero tolerance for LLM-generated diagnostic liability (e.g. the AI claiming a patient has "appendicitis" instead of listing "acute lower abdominal pain").

**Solution:** I built a RAG-backed intake structuring pipeline. Patient intake text is parsed for symptom, duration, and severity, then matched against a clinical guideline corpus using a hybrid (vector + keyword FTS) search. The core FDE differentiator is a **programmatic, LLM-independent Safety Filter** positioned between the LLM output and the clinical records write-back. It uses a medical dictionary blacklist, regex assertion checks, and groundedness verifications to reject and regenerate summaries containing diagnostic terms, guaranteeing a 0% diagnostic leakage rate.

**FDE Signals & Outcomes:**
*   **Safety Assurance:** **0.0% Diagnostic Leakage Rate** enforced by the post-generation programmatic filter.
*   **Alert Recall:** **96.5% Recall** on critical medical red flags (e.g., chest pain, sudden weakness) against a labeled clinic test dataset.
*   **Clinical Efficacy:** Reduced pre-visit chart reading time from an average of 5 minutes to **under 45 seconds** per patient.

**Tech Stack:** Python, FastAPI, PostgreSQL (Full-Text Search + Vector Index), LLM API, Docker.

👉 **[Go to Project Repository](./healthcare-intake-summarization/)** | **[Read Full Case Study](./healthcare-intake-summarization/docs/CASE_STUDY.md)**
