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
    tab_records, tab_dlq = st.tabs(["📊 Integrated Records", "🚨 Dead Letter Queue (DLQ) Logs"])
    
    with tab_records:
        st.subheader("Unified Customer Directory")
        records = get_data("/api/records")
        if records:
            df = pd.DataFrame(records)
            # Display cleanly
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
            
    with tab_dlq:
        st.subheader("Failed Ingestion & Mapping Audits")
        dlq_data = get_data("/api/dlq")
        if dlq_data:
            df_dlq = pd.DataFrame(dlq_data)
            st.dataframe(
                df_dlq[["source_name", "error_message", "raw_payload", "failed_at"]],
                column_config={
                    "source_name": "Ingestion Source",
                    "error_message": "Ingestion/Mapping Error Details",
                    "raw_payload": "Raw Captured Payload",
                    "failed_at": "Failure Timestamp"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("Dead Letter Queue is empty. No ingestion failures recorded!")
