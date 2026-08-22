# Enterprise Integration Deployment Platform

**Problem:** An enterprise components distributor had four legacy transactional systems scattered across different cloud vendors (following M&A activities). They needed a unified integration layer to discover, authenticate, and transform customer balances and records into a central warehouse, without locking themselves into a single cloud provider.

**Solution:** I built a config-driven data integration platform. It orchestrates polling schedules across REST (JSON + Bearer), legacy SOAP (XML + Basic Auth), mainframe CSV drops (directory watchers), and real-time webhook streams (HMAC-SHA256 signed). A resilient mapping layer implements exponential backoff with jitter and separates ingestion failures into a Dead Letter Queue (DLQ) table. Crucially, the system is fully containerized and deployed via Terraform to **both AWS and Azure** using provider-agnostic container orchestration patterns.

**FDE Signals & Outcomes:**
*   **Resilience:** **100% Data Preservation** achieved by routing mapping/network errors to the DLQ.
*   **Portability:** Multi-provider Terraform deployments abstraction (AWS ECS/RDS vs. Azure Container Apps/Flexible DB).
*   **Failover Ready:** Documented runbook for shifting traffic from AWS to Azure during regional/provider outages.

**Tech Stack:** Python, FastAPI, Streamlit, PostgreSQL, Docker, Terraform, AWS, Azure, GitHub Actions.

👉 **[Go to Project Repository](./enterprise-integration-platform/)** | **[Read Full Case Study](./enterprise-integration-platform/docs/CASE_STUDY.md)**
