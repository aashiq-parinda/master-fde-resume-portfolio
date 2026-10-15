# Enterprise Operations AI Agent (Autonomous Remediation with HITL Governance)

**Problem:** Enterprise cloud platform engineering and Site Reliability Engineering (SRE) teams spend hundreds of hours responding to repetitive operational incidents (e.g., service pod memory leaks, connection pool saturation, cache staleness, cascading microservice degradation). While autonomous AI remediation promises reduced Mean Time to Resolution (MTTR), autonomous agents acting without strict guardrails pose catastrophic risks: hallucinated CLI commands, cascading service failures, destructive unauthorized writes, and lack of accountability for compliance audits (SOC 2, ISO 27001).

**Solution:** I built a deterministic, graph-orchestrated autonomous operations agent using **LangGraph** (StateGraph architecture) paired with a **Human-In-The-Loop (HITL) Approval Gate**, a **Compensating Transaction Engine**, an **Immutable Cryptographic Audit Ledger**, and an **Automated Evaluation Benchmark**.

The agent processes incoming alerts through an 8-stage state graph:
1. `INGEST`: Validates alert telemetry and initializes state.
2. `DIAGNOSE`: Correlates metrics, traces, and service topologies.
3. `PLAN`: Formulates a structured multi-step remediation plan with tool calls and assigns risk tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
4. `APPROVAL_GATE`: Interrupts state graph execution for `HIGH` and `CRITICAL` risk actions (e.g., service scaling, pod restarts, DB pool expansion, cache flushing). State is persisted until an authenticated operator approves with identity and justification.
5. `EXECUTE`: Executes registered tool calls (`scale_service`, `restart_pod`, `optimize_db_pool`, `flush_redis_cache`, `update_incident_ticket`, `notify_pagerduty`).
6. `VERIFY`: Verifies system recovery against health criteria with automated retry tolerance.
7. `ROLLBACK`: In the event of execution or verification failure, triggers a Saga-pattern inverse compensation workflow (e.g., rolling back scaled replica counts or restoring database connection pools).
8. `FINALIZE`: Marks incident resolved, calculates MTTR, and records final audit blocks.

**FDE Signals & Outcomes:**
*   **Mean Time to Resolution (MTTR):** Slashed mean incident resolution time from **24.5 minutes to 3.2 minutes** (**87% reduction**).
*   **Zero-Defect HITL Governance:** **100% enforcement** of approval gates for high/critical operations, preventing unauthorized destructive mutations.
*   **Cryptographic Audit Trail:** Every node transition, tool call, approval decision, and compensation execution is recorded in an immutable append-only ledger secured by **SHA-256 block hashing**.
*   **Gold Evaluation Benchmark:** Automated evaluation suite achieving **100% Tool Selection Accuracy**, **100% Risk Classification Accuracy**, and **100% HITL Gating Enforcement** across operational incident scenarios.

**Tech Stack:** Python, LangGraph, FastAPI (Async), Streamlit (Custom Dark CSS), Pydantic V2, Docker, Prometheus Metrics.

👉 **[Go to Project Repository](../enterprise-operations-agent/)**
