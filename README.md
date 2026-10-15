# Forward Deployed Engineer (FDE) & Multicloud Solutions Architect Portfolio

Welcome to my master portfolio. This repository houses four distinct, production-grade projects engineered to solve complex operational, integration, AI safety, and autonomous agent governance challenges for enterprise organizations. 

Rather than simple "Minimum Viable Products," these systems represent **complete, self-contained architectures** complete with Docker environments, database initialization routines, comprehensive testing setups, commercial engagement metrics (TCV/ROI modeled in Indian Rupees - INR), and multi-cloud Infrastructure as Code (IaC) configurations.

---

## 🛠️ Skills Matrix & Project Index

| Technology / Competency | [Project 1: Predictive Maintenance](./industrial-predictive-maintenance/) | [Project 2: Flagship Healthcare AI Safety & RAG](./healthcare-intake-summarization/) | [Project 3: Enterprise Integration](./enterprise-integration-platform/) | [Project 4: Enterprise Operations AI Agent](./enterprise-operations-agent/) |
|---|:---:|:---:|:---:|:---:|
| **Language** | Python | Python | Python | Python |
| **API Framework** | FastAPI (Async, Prometheus `/metrics`) | FastAPI (Async, Trace Micro-profiler) | FastAPI (Async, Prometheus `/metrics`) | FastAPI (Async, Audit API) |
| **Data Visualization** | Streamlit (Custom Dark CSS) | Streamlit (Custom Dark Flagship Tabs) | Streamlit (Custom Dark CSS - Cisco) | Streamlit (Custom Dark Console) |
| **Databases** | TimescaleDB / PostgreSQL | PostgreSQL (Full-Text Search + Dense Vectors) | PostgreSQL (asyncpg pool) | In-Memory / PostgreSQL Audit Logs |
| **Caching / PubSub** | Redis | - | - | Redis (State & Cache Management) |
| **AI / Machine Learning / Agents** | scikit-learn (`IsolationForest`), Drift (PSI/KS) | Hybrid RAG (BM25 + Dense + RRF), Cross-Encoder Reranker, Provenance Citations | - | LangGraph StateGraph, Tool Calling, HITL Gating, Compensation |
| **IaC & Orchestration** | Terraform (AWS), Kubernetes (HPA), Docker | Docker Compose | Terraform (AWS & Azure), Docker Compose | Docker Compose |
| **Public Cloud Target** | AWS (Fargate, RDS, VPC, EKS) | AWS / Hybrid | AWS (Fargate) & Azure (Container Apps) | Multi-Cloud / Kubernetes |
| **Resilience Design** | Real-time telemetry buffers & PSI drift alerts | Programmatic safety filter (0.0% leakage guarantee) | Cryptographic idempotency, Circuit Breakers & DLQ | Saga compensation rollback & SHA-256 audit ledger |
| **Primary Financial Outcome** | **₹90 Lakhs/month** net savings | **₹1.8 Crore/year** admin savings | **₹4.5 Crore/year** integration savings | **87% MTTR reduction** (24.5m ➡️ 3.2m) |

---

## 📂 Project Profiles

### 1. [Industrial Predictive Maintenance Platform](./industrial-predictive-maintenance/)
*   **Narrative:** Provisioning a real-time predictive telemetry pipeline for a Tier-1 automotive manufacturer losing **₹25.20 Crore/year** to stamping line halting.
*   **Technical Core:** Edge vibration, temperature, and RPM telemetry stream processed using statistical Z-scores and an `IsolationForest` ML model with real-time sensor drift detection (Population Stability Index [PSI] and Kolmogorov-Smirnov test). Includes Kubernetes manifests (`Deployment`, `Service`, `HorizontalPodAutoscaler`), `/metrics` endpoint, and automated benchmark evaluation (ROC-AUC / PR-AUC).
*   **Metrics:** 12.4ms telemetry ingestion-to-detection latency, **421% Year 1 ROI**, **2.3-month payback period**, and **100% telemetry validation across 19 unit tests**.
*   👉 **[Watch Demo (YouTube)](https://youtu.be/H33OL8IM01s)** | **[Read Full Case Study](./industrial-predictive-maintenance/docs/CASE_STUDY.md)** | **[Commercial Engagement Summary](./industrial-predictive-maintenance/docs/ENGAGEMENT_SUMMARY.md)**

### 2. [Healthcare Patient Intake Summarization & AI Safety Platform (FLAGSHIP)](./healthcare-intake-summarization/)
*   **Narrative:** Enterprise clinical charting, triage, and RAG summarization system for a clinic network handling 15,000+ monthly intakes, where medical liability rules strictly prohibit LLM-generated diagnoses.
*   **Technical Core:** **Hybrid RAG** combining sparse BM25 and dense clinical semantic vector embeddings via Reciprocal Rank Fusion (`k=60`), followed by a 6-cluster Contextual Cross-Encoder Reranker. Summaries feature exact inline provenance citation markers (`[^1]`) linked to authoritative clinical guidelines with groundedness scoring. Programmatic multi-layer safety filter enforces a 100+ term medical blacklist, syntactic assertions, and PHI regex scrubbers with distributed span micro-tracing.
*   **Metrics:** **0.0% Diagnostic Leakage Rate** (guaranteed), **100% Adversarial Injection Defense**, **90% Triage Concordance**, **87.5% Groundedness**, and **p50 retrieval latency under 5ms** on gold clinical benchmark evaluations.
*   👉 **[Watch Demo (YouTube)](https://youtu.be/uo5pcuWYv-I)** | **[Read Full Case Study](./healthcare-intake-summarization/docs/CASE_STUDY.md)** | **[Commercial Engagement Summary](./healthcare-intake-summarization/docs/ENGAGEMENT_SUMMARY.md)**

### 3. [Enterprise Multi-Cloud Integration & Failover Platform](./enterprise-integration-platform/)
*   **Narrative:** Consolidating four legacy transactional feeds (REST API, legacy SOAP/XML, mainframe CSV files, and signed webhooks) into a unified relational schema for an acquired distributor.
*   **Technical Core:** Cryptographic SHA-256 idempotency locking (`PENDING`, `COMPLETED`, `FAILED` state transitions), circuit breakers (`CLOSED`, `OPEN`, `HALF_OPEN`) with exponential backoff and jitter, Dead Letter Queue (DLQ) replay engine, and active-passive automated multi-cloud failover/failback between AWS and Azure.
*   **Metrics:** **100% Data Preservation** (via DLQ routing & idempotency), and a documented multi-cloud financial model demonstrating Azure Container Apps is **30% cheaper** than AWS ECS Fargate due to built-in ingress and route tables eliminating ALB and NAT Gateway minimum fees.
*   👉 **[Watch Demo (YouTube)](https://youtu.be/45YbxMGYpEw)** | **[Read Full Case Study](./enterprise-integration-platform/docs/CASE_STUDY.md)** | **[Commercial Engagement Summary](./enterprise-integration-platform/docs/ENGAGEMENT_SUMMARY.md)** | **[Failover Runbook](./enterprise-integration-platform/docs/FAILOVER_RUNBOOK.md)**

### 4. [Enterprise Operations AI Agent (Autonomous Remediation with HITL Governance)](./enterprise-operations-agent/)
*   **Narrative:** Autonomous cloud infrastructure remediation agent resolving operational alerts (pod memory leaks, DB connection pool exhaustion, cache staleness, service latency spikes) while enforcing strict human oversight.
*   **Technical Core:** LangGraph-compatible 8-node state graph orchestrator (`INGEST` ➡️ `DIAGNOSE` ➡️ `PLAN` ➡️ `APPROVAL_GATE` ➡️ `EXECUTE` ➡️ `VERIFY` ➡️ `FINALIZE` / `ROLLBACK`). Integrates a tool-calling registry (`scale_service`, `restart_pod`, `optimize_db_pool`, `flush_redis_cache`), a Saga-pattern compensating transaction engine for automated rollback, an immutable append-only cryptographic audit ledger (SHA-256 chained hashing), and human-in-the-loop approval gating for high-risk interventions.
*   **Metrics:** **87% MTTR Reduction** (from 24.5 min to 3.2 min), **100% HITL Approval Gate Enforcement**, **100% Tool Selection Accuracy**, and zero-tampering audit compliance.
*   👉 **[Project Profile](./projects/enterprise-operations-agent.md)** | **[Go to Project Repository](./enterprise-operations-agent/)**

---

## 🏃 Local Execution & Port Mappings

To prevent local runtime conflicts, ports are strictly isolated at the project-level boundaries.

| Project Directory | Local Database Port | Backend API Port | Streamlit Dashboard Port | Run Commands (from project folder) |
|---|:---:|:---:|:---:|---|
| **`industrial-predictive-maintenance`** | `5432` | `8000` | `8501` | `uvicorn src.api.main:app --port 8000` <br> `streamlit run src/dashboard/app.py --server.port 8501` |
| **`enterprise-integration-platform`** | `5433` | `8001` | `8502` | `uvicorn src.api.main:app --port 8001` <br> `streamlit run src/dashboard/app.py --server.port 8502` |
| **`healthcare-intake-summarization`** | `5434` | `8002` | `8503` | `uvicorn src.api.main:app --port 8002` <br> `streamlit run src/dashboard/app.py --server.port 8503` |
| **`enterprise-operations-agent`** | `5435` | `8003` | `8504` | `uvicorn src.api.main:app --port 8003` <br> `streamlit run src/dashboard/app.py --server.port 8504` |

---

## 💼 Professional Contact & Credentials

*   **Interview Preparation & Portfolio Defense Guide:** 🎙️ **[`INTERVIEW_PORTFOLIO_GUIDE.md`](./INTERVIEW_PORTFOLIO_GUIDE.md)** — Comprehensive project elevator pitches, deep architectural defense, hard trade-offs, and key numbers to quote.
*   **Resume:** Detailed markdown and PDF versions available in the [`/resume`](./resume/) directory and [`RESUME.md`](./RESUME.md).
*   **GitHub**: [master-fde-resume-portfolio](https://github.com/aashiq-parinda/master-fde-resume-portfolio)
*   **Location**: Mumbai, India (Available for domestic roles or foreign remote engagements)
*   **Target Roles**: Forward Deployed Engineer (FDE), Multicloud Solutions Architect, Principal Integration Engineer, Enterprise AI Systems Architect.
