import os
import base64
import streamlit as st
import pandas as pd
import requests

# Page configuration
st.set_page_config(
    page_title="Enterprise Integration Dashboard",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Endpoint URL
API_URL = "http://127.0.0.1:8001"

def get_data(endpoint: str, params: dict = None):
    try:
        response = requests.get(f"{API_URL}{endpoint}", params=params, timeout=3.0)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def post_action(endpoint: str):
    try:
        response = requests.post(f"{API_URL}{endpoint}", timeout=5.0)
        return response.status_code, response.json()
    except Exception as e:
        return 500, {"detail": str(e)}

# --- Sidebar: Observability & Actions ---
# Logo resolution
import base64
logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "cisco.png")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.sidebar.markdown(
            f"""
            <div style="margin-top: 10px; margin-bottom: 10px; text-align: center;">
                <img src="data:image/png;base64,{encoded_string}" style="width: 180px; height: auto; object-fit: contain; border-radius: 8px;">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.image("https://img.shields.io/badge/FDE%20Portfolio-Active-blue", width=150)

st.sidebar.header("🕹️ Integration Controls")

# Webhook manual publisher
if st.sidebar.button("⚡ Fire Mock Webhook"):
    status_code, resp = post_action("/mock/trigger-webhook")
    if status_code == 200:
        st.sidebar.success(f"Webhook delivered! ID: {resp.get('sent_payload', {}).get('data', {}).get('id')}")
    else:
        st.sidebar.error(f"Failed: {resp.get('detail', 'Unknown error')}")

# CSV drop manual simulator
if st.sidebar.button("📂 Drop Mock CSV File"):
    status_code, resp = post_action("/mock/trigger-csv-drop")
    if status_code == 200:
        st.sidebar.success(f"CSV file dropped: {resp.get('file')}")
    else:
        st.sidebar.error(f"Failed: {resp.get('detail', 'Unknown error')}")

# Manual Poll triggers
st.sidebar.subheader("Manual Pull Syncs")
sources_info = get_data("/api/sources")
if sources_info:
    for src in sources_info:
        if src["type"] != "webhook":
            if st.sidebar.button(f"🔄 Sync {src['name']}"):
                status_code, resp = post_action(f"/api/sync/{src['id']}")
                if status_code == 200:
                    st.sidebar.info(f"Sync triggered for {src['id']}")
                else:
                    st.sidebar.error(f"Sync failed.")

# Custom Premium Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #f8fafc;
    }
    .metric-card-degraded {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #eab308;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #f8fafc;
    }
    .metric-card-down {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #ef4444;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #f8fafc;
    }
    .status-healthy {
        background-color: #065f46;
        color: #34d399;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
    }
    .status-degraded {
        background-color: #78350f;
        color: #fbbf24;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
    }
    .status-down {
        background-color: #7f1d1d;
        color: #f87171;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Title Area
st.title("🔌 Enterprise Integration Deployment Platform")
st.markdown("### Real-time legacy API schema discovery, translation, and resilience monitoring")

# Status reports
status_data = get_data("/api/observability/status")

if not status_data:
    st.warning("⚠️ Unable to connect to Ingestion API server. Please ensure the backend is running.")
else:
    # 1. Health Status Grid
    st.subheader("📡 Legacy Integration Feeds Status")
    cols = st.columns(len(status_data))
    
    for idx, src in enumerate(status_data):
        with cols[idx]:
            status = src["status"].lower()
            card_class = "metric-card"
            badge_class = "status-healthy"
            
            if status == "degraded":
                card_class = "metric-card-degraded"
                badge_class = "status-degraded"
            elif status == "down":
                card_class = "metric-card-down"
                badge_class = "status-down"
                
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: bold; font-size: 14px;">{src['name']}</span>
                    <span class="{badge_class}">{src['status'].upper()}</span>
                </div>
                <div style="font-size: 12px; color: #94a3b8;">
                    <p>Type: <strong style="color:#ffffff;">{src['type'].upper()}</strong></p>
                    <p>Latency: <strong style="color:#ffffff;">{src['latency_ms']} ms</strong></p>
                    <p>Sync Pings (OK/Err): <strong style="color:#34d399;">{src['success_pings']}</strong> / <strong style="color:#f87171;">{src['failed_pings']}</strong></p>
                    <p>DLQ Errors: <strong style="color:#ef4444;">{src['dlq_errors_count']}</strong></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    # 2. Main tabs
    tab_records, tab_circuit, tab_dlq, tab_failover, tab_cost = st.tabs([
        "📊 Integrated Records", 
        "⚡ Circuit Breakers", 
        "🚨 Dead Letter Queue & Replay", 
        "🌐 Multi-Cloud Failover", 
        "💰 Cloud Cost Comparison"
    ])
    
    with tab_records:
        st.subheader("Unified Customer Directory")
        records = get_data("/api/records")
        if records:
            df = pd.DataFrame(records)
            st.dataframe(
                df[["external_id", "source_name", "name", "email", "balance", "status", "synced_at"]],
                column_config={
                    "external_id": "External ID",
                    "source_name": "Ingestion Source",
                    "name": "Full Name",
                    "email": "Email",
                    "balance": st.column_config.NumberColumn("Account Balance", format="₹%.2f"),
                    "status": "System Status",
                    "synced_at": "Last Sync Timestamp"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No unified customer records synced yet.")

    with tab_circuit:
        st.subheader("⚡ Integration Adapters Circuit Breaker Status")
        st.markdown("Automatic fault isolation protecting upstream systems. Trips from `CLOSED` to `OPEN` under failure thresholds, then probes via `HALF_OPEN` canary.")
        
        breakers_data = get_data("/api/circuit-breakers")
        if breakers_data:
            df_cb = pd.DataFrame(list(breakers_data.values()))
            st.dataframe(
                df_cb[["name", "state", "failure_count", "state_uptime_seconds"]],
                column_config={
                    "name": "Integration Adapter",
                    "state": "Circuit State",
                    "failure_count": "Consecutive Failures",
                    "state_uptime_seconds": "State Uptime (s)"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("All circuit breakers operating in CLOSED (healthy) state.")
            
    with tab_dlq:
        st.subheader("🚨 Dead Letter Queue & Programmatic Message Replay")
        st.markdown("Quarantined payloads with schema violations or timeouts. Click **Replay** to safely re-ingest resolved records.")
        
        dlq_data = get_data("/api/dlq")
        if dlq_data:
            for item in dlq_data:
                d_col1, d_col2 = st.columns([4, 1])
                with d_col1:
                    st.error(f"**DLQ #{item['id']} ({item['source_name']}):** {item['error_message']}")
                    st.code(item['raw_payload'], language="json")
                with d_col2:
                    if st.button(f"🔄 Replay #{item['id']}", key=f"dlq_rep_{item['id']}"):
                        code, r = post_action(f"/api/dlq/{item['id']}/replay")
                        if code == 200:
                            st.success(f"DLQ #{item['id']} replayed successfully!")
                            st.rerun()
                        else:
                            st.error(f"Replay failed: {r.get('message')}")
        else:
            st.success("Dead Letter Queue is empty. No ingestion failures recorded!")

    with tab_failover:
        st.subheader("🌐 Active-Passive Multi-Cloud Disaster Recovery Control")
        st.markdown("Automated failover between **Primary (AWS ECS Fargate)** and **Secondary (Azure Container Apps)**.")
        
        failover_info = get_data("/api/failover")
        if failover_info:
            active_c = failover_info["active_cloud"]
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                st.markdown(f"### Currently Active Route: **`{active_c}`**")
                st.markdown(f"- **Primary Target**: {failover_info['primary_target']}")
                st.markdown(f"- **Secondary Target**: {failover_info['secondary_target']}")
                st.markdown(f"- **Consecutive Primary Failures**: `{failover_info['primary_consecutive_failures']}` / 3")
            with f_col2:
                st.markdown("### 🛠️ Manual Disaster Recovery Drill")
                target_switch = "AZURE" if active_c == "AWS" else "AWS"
                if st.button(f"🚨 Switch Active Traffic to {target_switch}", use_container_width=True):
                    try:
                        res = requests.post(f"{API_URL}/api/failover/switch", json={"target_cloud": target_switch}, timeout=5.0)
                        if res.status_code == 200:
                            st.success(f"Switched active cloud to {target_switch}!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failover trigger failed: {e}")

    with tab_cost:
        st.subheader("💰 Multi-Cloud Total Cost of Ownership (TCV) Comparison")
        st.markdown("Comparative financial analysis showing why **Azure Container Apps is ~30% cheaper** than AWS ECS Fargate for this architecture.")
        
        cost_data = get_data("/api/costs/compare")
        if cost_data:
            summary = cost_data["summary"]
            c_col1, c_col2, c_col3 = st.columns(3)
            with c_col1:
                st.metric("AWS Monthly Cost", f"${cost_data['aws']['monthly_total_usd']}", f"₹{cost_data['aws']['monthly_total_inr']:,.0f} INR")
            with c_col2:
                st.metric("Azure Monthly Cost", f"${cost_data['azure']['monthly_total_usd']}", f"₹{cost_data['azure']['monthly_total_inr']:,.0f} INR", delta=f"-{summary['azure_monthly_savings_pct']}% Savings")
            with c_col3:
                st.metric("Annual Savings (Azure vs AWS)", f"₹{summary['annual_savings_inr']:,.0f} INR", delta="~30% Net Reduction")
                
            st.write("---")
            st.markdown("#### Itemized Architectural Cost Breakdown (USD / Month)")
            comparison_rows = [
                {"Resource": "Managed Containers", "AWS (ECS Fargate)": f"${cost_data['aws']['compute_usd']}", "Azure (Container Apps)": f"${cost_data['azure']['compute_usd']}", "GCP (Cloud Run)": f"${cost_data['gcp']['compute_usd']}"},
                {"Resource": "PostgreSQL Database", "AWS (ECS Fargate)": f"${cost_data['aws']['database_usd']}", "Azure (Container Apps)": f"${cost_data['azure']['database_usd']}", "GCP (Cloud Run)": f"${cost_data['gcp']['database_usd']}"},
                {"Resource": "Ingress / Load Balancer", "AWS (ECS Fargate)": f"${cost_data['aws']['load_balancer_usd']} (ALB)", "Azure (Container Apps)": "$0.00 (Built-in Free)", "GCP (Cloud Run)": f"${cost_data['gcp']['load_balancer_usd']}"},
                {"Resource": "NAT Gateway / Egress", "AWS (ECS Fargate)": f"${cost_data['aws']['nat_gateway_usd']}", "Azure (Container Apps)": "$0.00 (VNet Routes)", "GCP (Cloud Run)": f"${cost_data['gcp']['nat_gateway_usd']}"},
                {"Resource": "Total Monthly Cost", "AWS (ECS Fargate)": f"${cost_data['aws']['monthly_total_usd']}", "Azure (Container Apps)": f"${cost_data['azure']['monthly_total_usd']}", "GCP (Cloud Run)": f"${cost_data['gcp']['monthly_total_usd']}"}
            ]
            st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)
            st.info("💡 **Cost Driver Analysis**: In AWS, deploying containers in private VPC subnets requires an Application Load Balancer ($26.50/mo) and an AWS NAT Gateway ($48.20/mo minimum base charge). Azure Container Apps provides built-in ingress routing at the environment tier and eliminates NAT gateway charges via integrated route tables, generating ~30% net operational savings.")

