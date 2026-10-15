import os
import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Enterprise Operations AI Agent Console",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8003"

def get_data(endpoint: str):
    try:
        res = requests.get(f"{API_URL}{endpoint}", timeout=3.0)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def post_action(endpoint: str, payload: dict = None):
    try:
        res = requests.post(f"{API_URL}{endpoint}", json=payload or {}, timeout=5.0)
        return res.status_code, res.json()
    except Exception as e:
        return 500, {"detail": str(e)}

# Custom CSS for Enterprise Operations
st.markdown("""
<style>
    .top-metric {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-top: 4px solid #3b82f6;
        text-align: center;
        color: #f8fafc;
    }
    .top-metric-critical {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-top: 4px solid #ef4444;
        text-align: center;
        color: #f8fafc;
    }
    .top-metric-approval {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-top: 4px solid #eab308;
        text-align: center;
        color: #f8fafc;
    }
    .top-metric-success {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-top: 4px solid #10b981;
        text-align: center;
        color: #f8fafc;
    }
    .risk-critical {
        background-color: #7f1d1d;
        color: #f87171;
        font-weight: bold;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
    }
    .risk-high {
        background-color: #78350f;
        color: #fbbf24;
        font-weight: bold;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
    }
    .risk-medium {
        background-color: #1e3a8a;
        color: #60a5fa;
        font-weight: bold;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
    }
    .risk-low {
        background-color: #065f46;
        color: #34d399;
        font-weight: bold;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🚀 Operations Agent")
st.sidebar.markdown("### Autonomous Site Reliability & Remediation")

PRESETS = {
    "Select Incident Template...": {},
    "SEV1: Checkout Memory Leak (High Risk - Requires Approval)": {
        "service_name": "checkout-api",
        "severity": "SEV1",
        "alert": "Pod memory reached 94% (1850MB / 2048MB). JVM heap saturation. Frequent GC pauses causing 504 timeouts.",
        "metrics": {"memory_mb": 1850, "cpu_pct": 45.0, "error_rate_pct": 14.5}
    },
    "SEV1: DB Connection Pool Exhausted (Critical Risk - Requires Approval)": {
        "service_name": "inventory-db",
        "severity": "SEV1",
        "alert": "Active connection pool reached ceiling (25/25). Queries queued for > 8000ms. Saturated unclosed cursors.",
        "metrics": {"active_connections": 25, "max_connections": 25, "queued_queries": 42}
    },
    "SEV2: Order Traffic Burst (Medium Risk - Auto-Scale)": {
        "service_name": "order-processor",
        "severity": "SEV2",
        "alert": "CPU utilization surged to 88% following marketing campaign broadcast. Request queue depth escalating.",
        "metrics": {"cpu_pct": 88.0, "replicas": 2, "throughput_rps": 4500}
    },
    "SEV2: Redis Cache Poisoning (High Risk - Requires Approval)": {
        "service_name": "billing-gateway",
        "severity": "SEV2",
        "alert": "Corrupted deserialization key poisoning session cache cluster. 120 poisoned keys causing auth filter exceptions.",
        "metrics": {"poisoned_keys": 120, "cache_hit_ratio": 0.54}
    }
}

preset_choice = st.sidebar.selectbox("Load Incident Preset", list(PRESETS.keys()))

with st.sidebar.form("incident_dispatch_form"):
    svc = st.text_input("Target Service", value=PRESETS[preset_choice].get("service_name", "checkout-api"))
    sev = st.selectbox("Severity", ["SEV1", "SEV2", "SEV3"], index=0 if PRESETS[preset_choice].get("severity") == "SEV1" else 1)
    alert = st.text_area("Alert Description", value=PRESETS[preset_choice].get("alert", ""), height=100)
    
    if st.form_submit_button("⚡ Ingest Incident to Agent"):
        if alert:
            payload = {
                "service_name": svc,
                "severity": sev,
                "alert_description": alert,
                "telemetry_metrics": PRESETS[preset_choice].get("metrics", {})
            }
            code, res = post_action("/api/incidents", payload)
            if code == 201:
                st.sidebar.success(f"Incident {res['incident_id']} Ingested! Node: {res['current_node']}")
                st.session_state["selected_inc_id"] = res["incident_id"]
                st.rerun()
            else:
                st.sidebar.error("Ingestion failed.")

st.title("🤖 Enterprise Operations AI Agent Console")
st.markdown("### Autonomous Site Reliability Engineering, Tool Calling & Human-In-The-Loop Governance")

st.markdown("""
<div style="background: linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%); border: 1px solid #6366f1; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
    <div>
        <span style="font-weight: 700; color: #a5b4fc; font-size: 14px;">🔗 LANGSMITH TRACING ACTIVE:</span>
        <span style="color: #e2e8f0; font-size: 13px; margin-left: 8px;">Project <code>enterprise-operations-agent</code> &bull; Live state transitions, HITL gates & tool execution traces streaming to LangSmith</span>
    </div>
    <a href="https://smith.langchain.com" target="_blank" style="background-color: #4f46e5; color: white; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 600;">Open LangSmith Console ↗</a>
</div>
""", unsafe_allow_html=True)

incidents = get_data("/api/incidents") or []

# Calculate counts
total_inc = len(incidents)
awaiting_approval = sum(1 for i in incidents if i.get("approval_status") == "PENDING" and i.get("requires_human_approval"))
resolved_count = sum(1 for i in incidents if i.get("is_closed") and i.get("verification_passed"))
rollbacks_count = sum(1 for i in incidents if i.get("rollback_executed"))

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="top-metric">
        <p style="margin:0; font-size:13px; color:#94a3b8;">Total Incidents Handled</p>
        <h2 style="margin:5px 0 0 0; color:#ffffff;">{total_inc}</h2>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="top-metric-approval">
        <p style="margin:0; font-size:13px; color:#94a3b8;">Awaiting Human Approval</p>
        <h2 style="margin:5px 0 0 0; color:#fbbf24;">{awaiting_approval}</h2>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="top-metric-success">
        <p style="margin:0; font-size:13px; color:#94a3b8;">Autonomous Resolutions</p>
        <h2 style="margin:5px 0 0 0; color:#34d399;">{resolved_count}</h2>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="top-metric-critical">
        <p style="margin:0; font-size:13px; color:#94a3b8;">Compensatory Rollbacks</p>
        <h2 style="margin:5px 0 0 0; color:#f87171;">{rollbacks_count}</h2>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

tab_ops, tab_graph, tab_audit, tab_evals = st.tabs([
    "🚨 Active Incidents & HITL Gate", 
    "🔄 State Graph Workflow", 
    "📜 Immutable Audit Ledger", 
    "📊 Benchmark Evaluations"
])

with tab_ops:
    if not incidents:
        st.info("No active incidents. Use the sidebar to trigger an incident preset.")
    else:
        col_list, col_view = st.columns([1, 2])
        with col_list:
            st.subheader("Incident Queue")
            for inc in incidents:
                status_icon = "🟡 AWAITING APPROVAL" if inc.get("approval_status") == "PENDING" and inc.get("requires_human_approval") else "🟢 RESOLVED" if inc.get("is_closed") else "🔵 PROCESSING"
                btn_txt = f"{inc['incident_id']} - {inc['service_name']} ({inc['severity']})\n{status_icon}"
                if st.button(btn_txt, key=f"sel_{inc['incident_id']}", use_container_width=True):
                    st.session_state["selected_inc_id"] = inc["incident_id"]

        with col_view:
            sel_id = st.session_state.get("selected_inc_id", incidents[0]["incident_id"])
            curr_inc = next((i for i in incidents if i["incident_id"] == sel_id), incidents[0])

            st.subheader(f"Incident: {curr_inc['incident_id']} ({curr_inc['service_name']})")
            
            risk = curr_inc.get("risk_tier", "LOW")
            risk_class = f"risk-{risk.lower()}"
            st.markdown(f"""
            <div style="display:flex; gap:15px; align-items:center; margin-bottom:15px;">
                <strong>Severity:</strong> <code>{curr_inc['severity']}</code> |
                <strong>Current Graph Node:</strong> <code>{curr_inc['current_node']}</code> |
                <strong>Risk Assessment:</strong> <span class="{risk_class}">{risk} RISK</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🔍 Root-Cause Diagnosis")
            st.info(curr_inc.get("diagnosis", "Analyzing..."))

            st.markdown("#### 🛠️ Proposed Operational Remediations")
            actions = curr_inc.get("proposed_actions", [])
            if actions:
                for a in actions:
                    st.markdown(f"- **Tool:** `{a['tool_name']}` | **Risk:** `{a['risk_level']}` | **Rationale:** {a['rationale']}")
                    st.json(a['arguments'])
            else:
                st.write("No actions proposed.")

            # Human In The Loop Approval Form
            if curr_inc.get("requires_human_approval") and curr_inc.get("approval_status") == "PENDING":
                st.warning("⚠️ **HUMAN APPROVAL GATE INTERRUPT**: This remediation modifies production infrastructure. Operator authorization is required to proceed.")
                
                with st.form(f"approval_form_{curr_inc['incident_id']}"):
                    appr_id = st.text_input("Approver Email / Operator ID", value="devops.lead@enterprise.com")
                    appr_notes = st.text_area("Approval Justification", value="Approved rolling restart with connection draining.")
                    
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        approve_btn = st.form_submit_button("✅ Authorize & Execute Remediation", use_container_width=True)
                    with b_col2:
                        reject_btn = st.form_submit_button("❌ Reject & Abort Remediation", use_container_width=True)

                    if approve_btn:
                        code, r = post_action(f"/api/incidents/{curr_inc['incident_id']}/approve", {"approver_id": appr_id, "approval_notes": appr_notes})
                        if code == 200:
                            st.success("Remediation authorized and executed!")
                            st.rerun()
                        else:
                            st.error(f"Execution error: {r.get('detail')}")

                    if reject_btn:
                        code, r = post_action(f"/api/incidents/{curr_inc['incident_id']}/reject", {"approver_id": appr_id, "rejection_reason": appr_notes})
                        if code == 200:
                            st.info("Remediation rejected and aborted.")
                            st.rerun()

            elif curr_inc.get("is_closed"):
                st.markdown("#### 📋 Resolution Summary")
                st.success(curr_inc.get("resolution_summary", "Incident Closed."))

with tab_graph:
    st.subheader("🔄 State Graph Execution Workflow")
    st.markdown("Visual representation of state graph nodes and conditional edge transitions:")
    
    st.markdown("""
    ```
    [ Alert Ingest ]
           │
           ▼
    [ Root-Cause Diagnose ]
           │
           ▼
    [ Plan Remediation & Risk Assessment ]
           │
           ├─► (Risk: HIGH/CRITICAL) ──► [ Human Approval Gate (HITL) ] ──► (Rejected: Abort)
           │                                      │
           │                                      ▼ (Approved)
           └───────────────────────────────► [ Execute Remediation Tools ]
                                                  │
                                                  ▼
                                       [ Verify Telemetry Recovery ]
                                                  │
                                                  ├─► (Success) ──► [ Finalize & Resolve ]
                                                  │
                                                  └─► (Failure) ──► [ Compensation Rollback ]
    ```
    """)

    sel_id = st.session_state.get("selected_inc_id")
    if sel_id:
        detail_data = get_data(f"/api/incidents/{sel_id}")
        if detail_data and "incident" in detail_data:
            inc = detail_data["incident"]
            st.markdown(f"#### Execution History for `{inc['incident_id']}`")
            st.write("Visited Nodes: " + " ➡️ ".join([f"`{n}`" for n in inc.get("node_history", [])]))
            
            tool_execs = inc.get("tool_executions", [])
            if tool_execs:
                st.markdown("#### Tool Call Results")
                for t in tool_execs:
                    st.markdown(f"**{t['tool_name']}** - Status: `{t['status']}`")
                    st.json(t["result"])

with tab_audit:
    st.subheader("📜 Immutable Cryptographic Audit Ledger")
    st.markdown("Tamper-evident audit trail linking every graph transition, tool execution, and human approval in a **SHA-256 cryptographic hash chain**.")
    
    audit_data = get_data("/api/audit-logs")
    if audit_data:
        is_intact = audit_data["chain_integrity_valid"]
        if is_intact:
            st.success(f"🟢 **CRYPTOGRAPHIC CHAIN INTACT**: {audit_data['verification_message']} ({audit_data['records_count']} Total Blocks)")
        else:
            st.error(f"🔴 **CHAIN TAMPERING DETECTED**: {audit_data['verification_message']}")
            
        records = audit_data.get("records", [])
        if records:
            df_audit = pd.DataFrame(records)
            st.dataframe(
                df_audit[["sequence", "event_type", "node", "actor", "hash", "prev_hash", "timestamp"]],
                column_config={
                    "sequence": "Block #",
                    "event_type": "Event Type",
                    "node": "Graph Node",
                    "actor": "Actor / Identity",
                    "hash": "Cryptographic Hash (SHA-256)",
                    "prev_hash": "Previous Pointer Hash",
                    "timestamp": "Timestamp"
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No audit ledger events recorded yet.")

with tab_evals:
    st.subheader("📊 Automated Evaluation Benchmark Suite")
    st.markdown("Automated benchmark testing agent autonomy, tool selection precision, HITL compliance, and compensation rollbacks.")
    
    if st.button("🚀 Run Automated Operations Benchmark (5 Gold Incidents)", use_container_width=True):
        with st.spinner("Executing incident state graphs and measuring compliance..."):
            code, eval_res = post_action("/api/evals/run")
            if code == 200:
                st.session_state["ops_eval_res"] = eval_res
                st.success("Benchmark completed successfully!")
            else:
                st.error("Evaluation run failed.")
                
    eval_res = st.session_state.get("ops_eval_res")
    if eval_res:
        m = eval_res["metrics"]
        st.markdown("### 🏆 Benchmark Evaluation Scorecard")
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        with sc1:
            st.metric("Task Completion Rate", f"{m['task_completion_rate_pct']}%", delta="High Autonomy")
        with sc2:
            st.metric("HITL Compliance", f"{m['hitl_gate_compliance_pct']}%", delta="100% Target")
        with sc3:
            st.metric("Tool Selection Precision", f"{m['tool_selection_accuracy_pct']}%", delta="Optimal Tools")
        with sc4:
            st.metric("Audit Ledger Integrity", "VALID" if m["audit_integrity_verified"] else "INVALID", delta="SHA-256 Chained")
        with sc5:
            st.metric("Latency (p50 / p95)", f"{m['latency_p50_ms']}ms / {m['latency_p95_ms']}ms")
            
        st.markdown("#### Scenario Breakdown")
        st.dataframe(pd.DataFrame(eval_res["cases"]), use_container_width=True, hide_index=True)
