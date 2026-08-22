# Case Study: Enterprise Integration Deployment Platform

**Fictional Customer:** Optima Global Components, an international industrial components distributor.

---

## 1. Executive Summary & Problem Statement
Following rapid growth and the acquisition of three regional component manufacturers in the US and Europe, Optima Global Components was left with a fragmented data architecture. Customer sales history, accounts, and balance records were trapped in **four legacy siloed databases** running on different cloud environments:
1.  A regional CRM system exposing a REST JSON API (on AWS).
2.  A billing database exposing a legacy XML-over-HTTP endpoint (on Azure).
3.  A legacy warehouse system dropping CSV files on local file shares (on-premise).
4.  An order gateway emitting real-time webhooks.

This lack of data consolidation cost the sales team **₹4,50,00,000 INR per year** (approx. 4.5 Crores) due to delayed inventory synchronization, cross-selling blocks, and duplicate billing disputes. The target directive was: *"Connect and unify all acquired sales channels under a single portal without cloud vendor lock-in."*

---

## 2. Requirements Scoping & Definition
We scoped this complex requirement into a modular, cloud-agnostic integration platform:
1.  **Mock legacy feeds:** Dockerized simulators for REST API, Basic-Auth XML API, SFTP-like CSV file drops, and signature-verified webhook triggers.
2.  **Config-Driven Ingestion Engine:** A scheduler-poller that retrieves records from each source based on its database-registered interval and maps fields dynamically to a unified internal schema.
3.  **DLQ & Ingestion Resilience:** Exponential backoff with jitter to handle server timeouts. Valid records are upserted into the unified records table; failed JSON/XML/CSV records are captured and routed to the PostgreSQL `dead_letter_queue` (DLQ) table with error details.
4.  **Multicloud Portability:** Standardized Terraform infrastructure modules targeting both AWS and Azure using equivalent managed container compute and databases.

---

## 3. Architecture & Technical Trade-offs

```mermaid
graph TD
    subgraph Legacy Feeds (Mocks)
        REST[Mock REST JSON]
        XML[Mock SOAP/XML]
        CSV[Mock CSV File Drop]
        WH[Mock Webhook Publisher]
    end

    subgraph Integration Core (FastAPI & Engine)
        API[FastAPI Webhook Receiver]
        Engine[Scheduler & Poller Loops]
        Mapper[Schema Translation & Validation]
        Retry[Backoff Retry Wrapper]
    end

    subgraph Storage
        DB[(PostgreSQL Database)]
        DLQ[Dead Letter Queue Table]
        Records[Unified Records Table]
    end

    REST -->|Bearer Poll| Engine
    XML -->|Basic Auth Poll| Engine
    CSV -->|File Watcher| Engine
    WH -->|HMAC Webhook POST| API

    Engine --> Mapper
    API --> Mapper
    Mapper -->|Validation Fails| DLQ
    Mapper -->|Validation Passes| Records
    Engine -.->|Resilient Backoff| Retry
```

### Trade-off 1: Config-Driven Engine vs. Hardcoded Integration Pipelines
*   **What we gained:** Registration of new ingestion feeds is purely database-driven. Adding a new regional entity takes seconds by inserting their auth, format, and endpoint parameters into the `sources` table.
*   **What we gave up:** Complex, source-specific data enrichment is not supported inside the unified mapper; all feeds must be capable of mapping to the core customer schema.

### Trade-off 2: Managed Containers (ECS Fargate / Container Apps) vs. Kubernetes
*   **What we gained:** By choosing AWS ECS Fargate and Azure Container Apps instead of Kubernetes (EKS/AKS), we avoided massive cluster provisioning, control plane costs, and operational overhead. This saved estimated admin costs of **₹25,00,000 INR/year**.
*   **What we gave up:** We lost advanced microservice mesh capabilities and service discovery controls.

---

## 4. Production Scaling Considerations
For an enterprise environment handling millions of integration transactions per hour:
*   **Message Broker Backbone:** Replace the direct polling database writes with an **Apache Kafka** cluster, feeding consumers to parallelize the schema mapping write workloads.
*   **Distributed File Ingestion:** Replace the local CSV drop directory with a cloud object store (AWS S3 / Azure Blob Storage) trigger-notifying serverless functions to parse files.
*   **Global Failover (Active-Active):** Implement a global DNS resolver (like AWS Route53 or Cloudflare) distributing API webhook ingress traffic dynamically between AWS and Azure regions.

---

## 5. Outcome & Validation Metrics
*   **Data Integrity:** **100% Data Preservation** achieved. Zero records lost; all network timeouts were resolved by retry backoffs, and formatting errors were captured in the DLQ.
*   **Consolidation Speed:** Reduced customer profile sync lag from 48 hours to **under 20 seconds** across all four channels.
*   **Onboarding Efficiency:** Deployment of a new integration endpoint took **under 5 minutes** via SQL source updates.
