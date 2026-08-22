# Forward Deployed Engineer (FDE) & Multicloud Solutions Architect Portfolio

Welcome to my master portfolio. This repository houses three distinct, production-grade projects engineered to solve complex operational, integration, and security challenges for enterprise organizations. 

Rather than simple "Minimum Viable Products," these systems represent **complete, self-contained architectures** complete with Docker environments, database initialization routines, comprehensive testing setups, commercial engagement metrics (TCV/ROI modeled in Indian Rupees - INR), and multi-cloud Infrastructure as Code (IaC) configurations.

---

## 🛠️ Skills Matrix & Project Index

| Technology / Competency | [Project 1: Predictive Maintenance](./industrial-predictive-maintenance/) | [Project 2: Patient Intake Summarizer](./healthcare-intake-summarization/) | [Project 3: Enterprise Integration](./enterprise-integration-platform/) |
|---|:---:|:---:|:---:|
| **Language** | Python | Python | Python |
| **API Framework** | FastAPI (Async) | FastAPI (Async) | FastAPI (Async) |
| **Data Visualization** | Streamlit (Custom Dark CSS) | Streamlit (Custom Dark CSS) | Streamlit (Custom Dark CSS - Cisco) |
| **Databases** | TimescaleDB / PostgreSQL | PostgreSQL (Full-Text Search) | PostgreSQL (asyncpg pool) |
| **Caching / PubSub** | Redis | - | - |
| **Machine Learning / NLP** | scikit-learn (IsolationForest) | LLM RAG / Vector similarity | - |
| **IaC & Orchestration** | Terraform (AWS), Docker Compose | Docker Compose | Terraform (AWS & Azure), Docker Compose |
| **Public Cloud Target** | AWS (Fargate, RDS, VPC) | - | AWS (Fargate) & Azure (Container Apps) |
| **Resilience Design** | Real-time telemetry buffers | Programmatic corrective retry loop | Exponential backoff jitter & DLQ |
| **Primary Financial Outcome** | **₹90 Lakhs/month** net savings | **₹1.8 Crore/year** admin savings | **₹4.5 Crore/year** integration savings |

---

## 📂 Project Profiles

### 1. [Industrial Predictive Maintenance Platform](./industrial-predictive-maintenance/)
*   **Narrative:** Provisioning a real-time predictive telemetry pipeline for a Tier-1 automotive manufacturer losing **₹25.20 Crore/year** to stamping line halting.
*   **Technical Core:** Edge vibration, temperature, and RPM telemetry stream processed using statistical Z-scores and an `IsolationForest` ML model to predict failure probability. An asynchronous Gemini assistant acts as an on-demand diagnostic tech.
*   **Metrics:** 12.4ms telemetry ingestion-to-detection latency, **421% Year 1 ROI**, and **2.3-month payback period**.
*   👉 **[Read Full Case Study](./industrial-predictive-maintenance/docs/CASE_STUDY.md)** | **[Commercial Engagement Summary](./industrial-predictive-maintenance/docs/ENGAGEMENT_SUMMARY.md)**

### 2. [Healthcare Patient Intake Summarization Platform](./healthcare-intake-summarization/)
*   **Narrative:** Building a patient charting and triage system for a clinic group handling 15,000+ monthly intakes, where medical liability rules strictly prohibit LLM-generated diagnoses.
*   **Technical Core:** Hybrid Full-Text Search (FTS) queries to index clinical protocols, paired with a deterministic, LLM-independent Python **Programmatic Safety Filter** (lexical blacklist + syntactic regex matching) to catch diagnostic leakages before database write-back.
*   **Metrics:** **0.0% Diagnostic Leakage Rate** (enforced by gatekeepers), **96.5% Red-Flag Recall**, and physician reading time reduced by **85%** (under 45 seconds).
*   👉 **[Read Full Case Study](./healthcare-intake-summarization/docs/CASE_STUDY.md)** | **[Commercial Engagement Summary](./healthcare-intake-summarization/docs/ENGAGEMENT_SUMMARY.md)**

### 3. [Enterprise Integration Deployment Platform](./enterprise-integration-platform/)
*   **Narrative:** Consolidating four legacy transactional feeds (REST API, legacy SOAP/XML, mainframe CSV files, and signed webhooks) into a unified relational schema for an acquired distributor.
*   **Technical Core:** Configuration-driven polling loops executing network calls with exponential backoff retries and random jitter, separating schema mapping errors into a Dead Letter Queue (DLQ) table. Complete multi-cloud infrastructure abstraction (AWS vs. Azure) built with Terraform.
*   **Metrics:** **100% Data Preservation** (via DLQ routing), and a documented failover DNS runbook showing Azure Container Apps is **30% cheaper** than AWS ECS Fargate for this workload.
*   👉 **[Read Full Case Study](./enterprise-integration-platform/docs/CASE_STUDY.md)** | **[Commercial Engagement Summary](./enterprise-integration-platform/docs/ENGAGEMENT_SUMMARY.md)** | **[Failover Runbook](./enterprise-integration-platform/docs/FAILOVER_RUNBOOK.md)**

---

## 🏃 Local Execution & Port Mappings

To prevent local runtime conflicts, ports are isolated at the project-level boundaries.

| Project Directory | Local Database Port | Backend API Port | Streamlit Dashboard Port | Run Commands (from project folder) |
|---|:---:|:---:|:---:|---|
| **`industrial-predictive-maintenance`** | `5432` | `8000` | `8501` | `uvicorn src.api.main:app` <br> `streamlit run src/dashboard/app.py` |
| **`enterprise-integration-platform`** | `5433` | `8001` | `8502` | `uvicorn src.api.main:app` <br> `streamlit run src/dashboard/app.py` |
| **`healthcare-intake-summarization`** | `5434` | `8002` | `8503` | `uvicorn src.api.main:app` <br> `streamlit run src/dashboard/app.py` |

---

## 💼 Professional Contact & Credentials

*   **Resume:** PDF version available in the [`/resume`](./resume/) directory.
*   **GitHub**: [master-fde-resume-portfolio](https://github.com/aashiq-parinda/master-fde-resume-portfolio)
*   **Location**: Mumbai, India (Available for domestic roles or foreign remote engagements)
*   **Target Roles**: Forward Deployed Engineer (FDE), Multicloud Solutions Architect, Principal Integration Engineer.
