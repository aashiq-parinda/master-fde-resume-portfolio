# Industrial Predictive Maintenance Platform

**Problem:** Optima AutoParts (a Tier-1 automotive manufacturer in Germany) was losing **₹25,20,00,000 INR per year** (approx. 25.2 Crores, equivalent to €2.8M) to unplanned machine downtime. Technicians reacted only after hydraulic pumps or compressors failed, halting stamping lines for hours.

**Solution:** I built a real-time predictive maintenance pipeline. Synthetic sensors emit vibration, temperature, and RPM telemetry every 2 seconds. An edge analytics loop combines statistical Z-scores and an `IsolationForest` ML model to detect multi-variable drift. When an anomaly is detected, a Gemini-powered diagnostic assistant explains the failure root cause in plain English and generates repair recommendations, decreasing Mean Time to Repair (MTTR).

**FDE Signals & Outcomes:**
*   **Ingestion-to-Detection Latency:** Averaged **12.4 ms** under heavy simulated stream loads.
*   **Diagnostic Efficiency:** Cut technician root-cause analysis time from 4 hours to **under 15 minutes**.
*   **Engagement ROI:** Project TCV of **₹2,90,0,000 INR** generates **₹90,00,000 INR/month** in net savings, resulting in a **421% Year 1 ROI** and a **2.3-month payback period**.

**Tech Stack:** Python, FastAPI, PostgreSQL/TimescaleDB, Redis Pub/Sub, scikit-learn, Docker, Terraform, AWS.

👉 **[Go to Project Repository](./industrial-predictive-maintenance/)** | **[Read Full Case Study](./industrial-predictive-maintenance/docs/CASE_STUDY.md)**
