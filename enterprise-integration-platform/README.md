# Enterprise Integration Deployment Platform

A config-driven integration engine that consolidates customer records from four legacy customer systems (REST JSON, SOAP/XML, CSV watcher, and HMAC-signed webhooks) into a unified PostgreSQL database. It features exponential backoff retries, Dead Letter Queue (DLQ) routing for mapping failures, and multicloud Terraform IaC configurations.

---

## 🚀 Local Quick Start

### 1. Prerequisites
Ensure you have Docker and Python 3.11+ installed on your host system.

### 2. Start PostgreSQL Database
Spin up the PostgreSQL database container (mapped to host port `5433` to prevent conflicts with other projects):
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

### 4. Launch Ingestion API & Mock Feeds
Start the FastAPI server (runs the API, mounts mock legacy services, and launches scheduler threads on port `8001`):
```bash
PYTHONPATH=. .venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8001
```

### 5. Launch Streamlit Observability Dashboard
In a separate terminal tab, run the Streamlit dashboard on port `8502`:
```bash
PYTHONPATH=. .venv/bin/streamlit run src/dashboard/app.py --server.port 8502
```
Now, open your browser and navigate to **`http://127.0.0.1:8502`**.

---

## 📁 Repository Directory Structure

```
enterprise-integration-platform/
├── assets/                  # Frontend assets (cisco.png logo)
├── docs/                    # Technical architecture & financials
│   ├── CASE_STUDY.md        # M&A business context & trade-offs
│   ├── ENGAGEMENT_SUMMARY.md# Project commercials (TCV, Milestones, Taxes)
│   └── FAILOVER_RUNBOOK.md  # Multi-cloud failover guide & costs (INR)
├── src/
│   ├── api/
│   │   └── main.py          # FastAPI application & webhook receiver
│   ├── dashboard/
│   │   └── app.py           # Streamlit metrics dashboard (Cisco branding)
│   ├── engine/
│   │   ├── mapping.py       # Legacy schema XML/JSON/CSV translation
│   │   ├── retry.py         # Backoff retry and health logging metrics
│   │   └── scheduler.py     # Background loop ingestion coordinators
│   ├── mocks/
│   │   └── services.py      # Simulators for legacy REST, SOAP, and webhooks
│   ├── config.py            # Pydantic Settings env configuration
│   └── database.py          # asyncpg connection pools and table schemas
├── terraform/               # Multi-cloud Infrastructure as Code (IaC)
│   ├── aws/                 # VPC, ECS Fargate, RDS PostgreSQL, Secrets
│   └── azure/               # VNet, Container Apps, Flex Database, Vault
├── tests/
│   └── test_integration.py  # Mapping and parsing validation tests
├── docker-compose.yml       # Local PostgreSQL database definition
└── requirements.txt         # Python package dependencies list
```

---

## 🧪 Running Unit Tests
Verify data mapping and parser transformations:
```bash
PYTHONPATH=. .venv/bin/pytest tests/
```

---

## 🌐 Cloud Infrastructure Deployment (IaC)
This project is built to deploy seamlessly to AWS or Azure. Review the full deployment strategies and failover instructions:
*   👉 **[AWS ECS Fargate Module](./terraform/aws/main.tf)**
*   👉 **[Azure Container Apps Module](./terraform/azure/main.tf)**
*   👉 **[Failover Runbook & Cost Analysis](./docs/FAILOVER_RUNBOOK.md)**
*   👉 **[Commercial Engagement Summary](./docs/ENGAGEMENT_SUMMARY.md)**
