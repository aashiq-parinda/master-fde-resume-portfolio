# Ashraf Khan
**Forward Deployed Engineer (FDE) · Multi-Cloud Solutions Architect · Senior Full-Stack Systems Engineer**  
📍 Mumbai, Maharashtra, India | 📧 [ashrafksalim1@gmail.com](mailto:ashrafksalim1@gmail.com) | 📞 +91-8779559898  
🌐 **GitHub**: [github.com/aashiq-parinda](https://github.com/aashiq-parinda) | 💼 **LinkedIn**: [linkedin.com/in/ashrafksalim](https://linkedin.com/in/ashrafksalim) | 📱 **10+ Published Apps** (App Store & Play Store)  

---

## 🎯 Professional Executive Summary
Accomplished **Forward Deployed Engineer (FDE) & Multi-Cloud Solutions Architect** with **5+ years of production software engineering experience**, **10+ published commercial applications**, and **4 enterprise FDE system deployments**. Specializes in bridging enterprise operational challenges with resilient multi-cloud architectures (AWS Fargate, Azure Container Apps, Kubernetes HPA, Terraform IaC, TimescaleDB, PostgreSQL), zero-trust security governance (HIPAA, PCI-DSS, Level 2 VAPT, SEBI/RBI standards), agentic AI workflows (LangGraph, Tool Calling, Human-in-the-Loop Governance, Compensating Transactions), and high-throughput microservices (FastAPI, Flask, Node.js, gRPC). Proven track record of delivering direct enterprise financial impact, including **₹4.5 Crore/yr integration savings**, **₹1.8 Crore/yr administrative savings**, **₹25.20 Crore/yr line-halt prevention**, and **87% incident MTTR reduction**.

---

## 🏗️ Forward Deployed Engineering (FDE) & Multi-Cloud Portfolio Projects

### 1. **Industrial Predictive Maintenance Telemetry Platform** | [`industrial-predictive-maintenance`](https://github.com/aashiq-parinda/master-fde-resume-portfolio/tree/main/industrial-predictive-maintenance)
* **Enterprise Problem:** Provisioned real-time predictive telemetry pipeline for a Tier-1 automotive manufacturer losing **₹25.20 Crore/year** to stamping line halting.
* **Technical Core:** Edge vibration, temperature, and RPM telemetry stream processed using statistical Z-scores, Redis pub/sub buffers, and an `IsolationForest` ML model for failure prediction. Built real-time sensor drift detection (Population Stability Index [PSI] & Kolmogorov-Smirnov test), automated evaluation benchmark suite (ROC-AUC/PR-AUC), Prometheus `/metrics`, Kubernetes manifests (`Deployment`, `Service`, `HPA`), and Terraform IaC for AWS.
* **Impact & Metrics:** **12.4ms telemetry ingestion-to-detection latency**, **₹90 Lakhs/month net savings**, **421% Year 1 ROI**, **2.3-month payback period**, and **100% test pass rate across 19 unit tests**.

### 2. **Healthcare Patient Intake & AI Safety Flagship Platform** | [`healthcare-intake-summarization`](https://github.com/aashiq-parinda/master-fde-resume-portfolio/tree/main/healthcare-intake-summarization)
* **Enterprise Problem:** Engineered patient charting, triage, and RAG summarization system for a clinic network processing **15,000+ monthly patient intakes**, where medical liability rules strictly prohibit LLM-generated diagnoses.
* **Technical Core:** **Hybrid RAG** combining sparse BM25 and dense clinical semantic vector embeddings via Reciprocal Rank Fusion (`k=60`), paired with a 6-cluster Contextual Cross-Encoder Reranker. Generated summaries include exact inline provenance citation markers (`[^1]`) linked to authoritative clinical guidelines with groundedness scoring. Programmatic multi-layer safety filter enforces a 100+ term medical blacklist, syntactic assertions, and PHI regex scrubbers with distributed span micro-tracing.
* **Impact & Metrics:** **0.0% Diagnostic Leakage Rate** (guaranteed), **100% Adversarial Injection Defense**, **90% Triage Concordance**, **87.5% Groundedness**, **p50 retrieval latency under 5ms**, physician reading time cut by **85%** (under 45s), and **₹1.8 Crore/year administrative savings**.

### 3. **Enterprise Multi-Cloud Integration & Failover Platform** | [`enterprise-integration-platform`](https://github.com/aashiq-parinda/master-fde-resume-portfolio/tree/main/enterprise-integration-platform)
* **Enterprise Problem:** Consolidated four legacy transactional feeds (REST API, legacy SOAP/XML, mainframe CSV files, and signed webhooks) into a unified relational schema for an acquired distributor.
* **Technical Core:** Cryptographic SHA-256 idempotency locking (`PENDING`, `COMPLETED`, `FAILED` state machine), circuit breakers (`CLOSED`, `OPEN`, `HALF_OPEN`) with exponential backoff and jitter, Dead Letter Queue (DLQ) replay engine, and active-passive automated multi-cloud failover/failback between AWS and Azure. Complete multi-cloud infrastructure abstraction built with Terraform.
* **Impact & Metrics:** **100% Data Preservation** via DLQ routing and idempotency, **₹4.5 Crore/year integration savings**, and a documented multi-cloud financial model proving Azure Container Apps is **30% cheaper** than AWS ECS Fargate due to built-in ingress and route tables eliminating ALB and NAT Gateway minimum fees.

### 4. **Enterprise Operations AI Agent (Autonomous Remediation with HITL Governance)** | [`enterprise-operations-agent`](https://github.com/aashiq-parinda/master-fde-resume-portfolio/tree/main/enterprise-operations-agent)
* **Enterprise Problem:** Built autonomous cloud infrastructure remediation agent resolving operational incidents (pod memory leaks, DB connection pool exhaustion, cache staleness, service latency spikes) while enforcing strict human oversight and zero-tampering compliance.
* **Technical Core:** LangGraph-compatible 8-node state graph orchestrator (`INGEST` ➡️ `DIAGNOSE` ➡️ `PLAN` ➡️ `APPROVAL_GATE` ➡️ `EXECUTE` ➡️ `VERIFY` ➡️ `FINALIZE` / `ROLLBACK`). Integrates a tool-calling registry (`scale_service`, `restart_pod`, `optimize_db_pool`, `flush_redis_cache`), a Saga-pattern compensating transaction engine for automated rollback, an immutable append-only cryptographic audit ledger (SHA-256 chained hashing), and human-in-the-loop approval gating for high-risk interventions.
* **Impact & Metrics:** **87% MTTR Reduction** (from 24.5 min to 3.2 min), **100% HITL Approval Gate Enforcement**, **100% Tool Selection Accuracy**, and zero-tampering audit compliance.

### 5. **Contract Clause Risk Review & PEFT Agent** | [Hugging Face Live Demo](https://huggingface.co/spaces/ashrafksalim/contract-clause-risk-review) · [`contract-risk-review`](https://github.com/aashiq-parinda/LLM-Fine-Tuning-Agentic-Reasoning-for-Contract-Risk-Review)
* **Enterprise Problem:** Enterprise legal teams spend hours manually parsing high-risk clauses (indemnification, governing law, termination) across commercial agreements.
* **Technical Core:** Parameter-efficient fine-tuning (LoRA) on `microsoft/deberta-v3-small` over the SEC LEDGAR dataset for clause classification; wrapped in a LangGraph state machine with Chroma RAG for precedent retrieval, LLM plain-English risk summarization, and confidence-threshold human escalation guardrails.
* **Impact & Metrics:** Deployed interactive **Hugging Face Space** evaluating classifier accuracy, macro-F1, per-category fairness metrics, and confidence-routed human-in-the-loop fallback queues.

---

## 🌐 Published Commercial Mobile Applications & Enterprise Portals

### 📱 Published Commercial Mobile Applications (App Store & Play Store)
* **Lead Yatra (Reliance / IndusInd Bank)**: [App Store Link](https://apps.apple.com/in/app/lead-yatra/id6758609992) | [Google Play Link](https://play.google.com/store/apps/details?id=com.rnlic.leadyatra) — Enterprise field sales lead capture & banking venue booking system powering IndusInd Bank operations.
* **MAXX AI Voice Assistant**: [App Store Link](https://apps.apple.com/us/app/maxx/id6747980186) — Enterprise voice AI assistant with custom wake-word activation & multi-advisor conversational flows via Millis.ai.
* **Kokomo 24/7**: [App Store Link](https://apps.apple.com/us/app/kokomo24-7/id1504839321) — Scalable enterprise 24/7 operational service management platform.
* **FitWell | All-in-One**: [App Store Link](https://apps.apple.com/in/app/fitwell-all-in-one/id1641657795) — HIPAA-compliant health platform with biometric auth, CDC/CMS reporting, and private Jitsi video consultations.
* **InstaQuote 2.0 by HDFC Life**: [App Store Link](https://apps.apple.com/in/app/instaquote-2-0-by-hdfc-life/id6639613496) | [Google Play Link](https://play.google.com/store/apps/details?id=com.hdfclife.instaquotev2) — Instant insurance quoting & financial premium calculation engine.

### 💻 Enterprise Web Portals
* **Monitor Health AI (Primary Landing)**: [`monitorhealth.ai`](https://monitorhealth.ai/) — Commercial AI healthcare landing page & sales engine.
* **Remote Survey Portal**: [`survey.monitorhealth.ai`](https://survey.monitorhealth.ai) — HIPAA-compliant remote health survey platform.
* **Institutional School Platform**: [`main.di10toj4buhn9.amplifyapp.com`](https://main.di10toj4buhn9.amplifyapp.com/) — Multi-tenant health tracking platform for educational institutions.

---

## 💼 Professional Experience

### **Senior Software & Systems Engineer** | Logicloop *(Mumbai, India | Jan 2026 – Present)*
* **Lead Yatra (Reliance IndusInd)**: Architected cross-platform Flutter application optimizing field sales lead capture and venue booking at enterprise scale, securing banking data for IndusInd Bank operations.
* **MAXX AI Voice Assistant**: Developed end-to-end AI voice assistant featuring custom wake-word activation and multi-advisor conversational flows powered by Millis.ai.
* **Team Leadership & DevOps**: Led 3 developers, established GitHub Actions CI/CD pipelines (40% deployment overhead reduction), and enforced Level 2 VAPT security standards across financial flows.

### **Full-Stack Developer & Data Custodian** | Fitwell Technologies Inc. *(Remote – VA, USA | Jun 2025 – Present)*
* **Monitor Health AI Ecosystem**: Built commercial landing page (`monitorhealth.ai`), remote survey portal (`survey.monitorhealth.ai`), and multi-tenant institutional school platform (`amplifyapp.com`).
* **Private Cloud & Telehealth Video**: Deployed Flask microservices on AWS (EC2, S3, ELB), private Supabase cloud backend on EC2 for PHI data isolation, hosted private Jitsi Meet server for HIPAA-compliant consultations, and integrated Amazon Connect workflows.
* **Data Custodianship & Compliance**: Owned PHI data governance as data custodian, maintaining zero data breach posture and Level 2 VAPT security.

### **Lead Software Engineer** | QuantGen Private Limited *(India | Nov 2024 – Jun 2025)*
* **Fitwell AI - All-in-One**: Led full-stack React Native development for HIPAA-compliant wellness platform with biometric auth, goal tracking, and CDC/CMS health reporting.
* **Kokomo 24/7**: Architected enterprise mobile solution for 24/7 service operations; built admin panel on AWS App Runner with AWS ECS orchestration and private Jitsi video servers.

### **Software Engineer** | Logicloop *(Mumbai, India | May 2024 – Oct 2024)*
* **HDFC Life InstaQuote**: Built Flutter frontend for instant insurance quoting, financial premium calculations, and lead generation workflows.

### **Software Engineer** | SoftProdigy *(Remote – USA | Nov 2023 – Apr 2024)*
* Developed loan lending application workflows in Flutter and implemented gRPC Client API libraries.

### **Senior Software Development Engineer** | AKcess Labs Pvt. Ltd. *(Remote – London, UK | Jan 2023 – Nov 2023)*
* Built Flutter cross-platform applications with Flask backends; created the *CityShop* hyperlocal commerce application.

### **Software Developer** | We3.Tech *(Maharashtra, India | Aug 2021 – Jan 2023)*
* **Mangal Keshav eKYC App**: Integrated eKYC and Digio eSign SDKs for digital onboarding.
* **Motilal Oswal MO Investor**: Delivered Add Funds module with banking API integrations and cryptographic security compliant with SEBI and RBI guidelines.

### **Unity Game Developer (Intern)** | IDZ Digital Pvt. Ltd. *(Mumbai, India)*
* Prototyped 12+ interactive mobile games for KidloLand in Unity 3D.

---

## 💻 Technical Skills & Core Competencies

* **Agentic AI & Orchestration**: LangGraph, StateGraph State Machines, LangSmith (Tracing, Evals, Debugging & Monitoring), Tool Calling Registries, Human-In-The-Loop (HITL) Gating, Saga Compensating Transactions, Cryptographic Audit Ledgers.
* **Retrieval-Augmented Generation (RAG) & Safety**: Hybrid Retrieval (BM25 Sparse + Dense Clinical Semantic Vectors), Reciprocal Rank Fusion (RRF), Contextual Cross-Encoder Rerankers, Provenance Citations, Programmatic Safety Filters (0.0% Diagnostic Leakage), Distributed Span Micro-Tracing.
* **Multi-Cloud & Infrastructure**: Terraform (IaC), AWS (Fargate, ECS, EKS, EC2, S3, ELB, App Runner, RDS, VPC), Azure (Container Apps), GCP, Kubernetes (Deployments, Services, HPA), Docker, GitHub Actions CI/CD.
* **Data & Streaming Engineering**: TimescaleDB, PostgreSQL (asyncpg, Full-Text Search, pgvector), Redis Pub/Sub, Cryptographic Idempotency Locking, Circuit Breakers (Half-Open), Dead Letter Queues (DLQ), Exponential Backoff Jitter.
* **Software & Systems Engineering**: Python (FastAPI Async, Pydantic V2, Flask), Node.js, Flutter (Lead), React Native, Android (Java/Kotlin), iOS (Swift), REST, gRPC, Protobuf, WebSockets.
* **ML & Predictive Analytics**: scikit-learn (`IsolationForest` Telemetry), Population Stability Index (PSI), Kolmogorov-Smirnov (KS) Drift Detection, ROC-AUC / PR-AUC Benchmark Evaluation, OpenCV.
* **Compliance & Security**: HIPAA, PCI-DSS, SEBI / RBI Guidelines, CDC/CMS Health Reporting, Data Custodianship & Governance, Level 2 VAPT, Biometric Auth, eKYC, Digio eSign.

---

## 🎓 Education & Certifications

### **Education**
* **B.Sc. in Computer Science** | Rizvi College, Mumbai University *(2017 – 2020)* — **CGPA:** 9.33 / 10.00
* **Vocational Computer Science / HSC (12th)** | M.H. Saboo Siddik Polytechnic, Mumbai *(2015 – 2017)* — **Percentage:** 75.80%

### **AI & Professional Certifications**
* **LangChain**: [Project: Deep Research with LangGraph](https://academy.langchain.com/certificates/yn40p3bviz) *(Issued Oct 2026 · Credential ID: `yn40p3bviz`)* — Multi-agent research architecture, recursive search planning, iterative synthesis, and LangSmith evaluation.
* **LangChain**: [Quickstart: LangGraph Essentials - Python](https://academy.langchain.com/certificates/1hhanf8ox7) *(Issued Oct 2026 · Credential ID: `1hhanf8ox7`)* — StateGraph orchestration, State schemas, Nodes, Edges, and Checkpointer memory.
* **LangChain**: [Quickstart: LangSmith Essentials](https://academy.langchain.com/certificates/rlwlwmnqzc) *(Issued Oct 2026 · Credential ID: `rlwlwmnqzc`)* — Developing, debugging, tracing, monitoring, and evaluating LLM and agentic workflows.
* **Google Cloud**: [Introduction to Generative AI Badge](https://www.skills.google/public_profiles/c0e9e44f-59b6-4e05-b972-7da8fd405a4a/badges/9066294) *(Issued May 2024)*.
* **Claude Academy**: AI Fluency: Framework & Foundations | Human-Agent Teams | Claude Platform 101.
* **Reliance Foundation & Skill India (NSDC)**: Foundation Course in Bioinformatics *(90-Hour Intensive Program | Certified Dec 2025)* — Computational biology, genomics data structures, and molecular informatics.
* **Healthcare & FinTech Compliance**: Healthcare API Compliance & HIPAA PHI Data Governance | FinTech Regulatory Standards & PCI-DSS Payment Processing.
