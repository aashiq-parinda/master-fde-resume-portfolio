import streamlit as st
import httpx
import pandas as pd
import time
from datetime import datetime

# Configure page metadata
st.set_page_config(
    page_title="Industrial Predictive Maintenance Platform",
    page_icon="⚙️",
    layout="wide"
)

# Custom Premium Styling (Safe, strictly static CSS with no user-input interpolation)
st.markdown("""
<style>
    .badge-healthy {
        background-color: #065f46;
        color: #34d399;
        border: 1px solid #047857;
    }
    .badge-anomaly {
        background-color: #7f1d1d;
        color: #f87171;
        border: 1px solid #b91c1c;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# API Endpoint Configuration
API_BASE_URL = "http://127.0.0.1:8000"

st.title("⚙️ Industrial Predictive Maintenance Platform")
st.subheader("Real-Time Ingestion, ML Anomaly Detection & AI Diagnostics")

# Helper to query the backend API
def get_data(endpoint: str, params: dict = None):
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{API_BASE_URL}{endpoint}", params=params)
            if response.status_code == 200:
                return response.json()
            return []
    except Exception:
        return []

def post_data(endpoint: str, payload: dict):
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(f"{API_BASE_URL}{endpoint}", json=payload)
            return response.status_code, response.json()
    except Exception as e:
        return 500, {"detail": str(e)}

# --- Sidebar: Pipeline Observability Metrics ---
import os
import base64
logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "images.png")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.sidebar.markdown(
            f"""
            <div style="margin-top: 5px; margin-bottom: 5px; text-align: center;">
                <img src="data:image/png;base64,{encoded_string}" style="width: 100%; max-width: 250px; height: 50px; object-fit: cover; object-position: center; border-radius: 8px;">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.image("https://img.shields.io/badge/FDE%20Portfolio-Active-blue", width=150)
st.sidebar.header("📊 Pipeline Ingestion Telemetry")


obs_data = get_data("/api/observability/metrics")
if obs_data:
    st.sidebar.metric(label="Throughput", value=f"{obs_data.get('throughput_events_per_sec', 0.0)} eps")
    st.sidebar.metric(label="Total Processed", value=f"{obs_data.get('events_processed', 0)} events")
    st.sidebar.metric(label="Avg Latency", value=f"{obs_data.get('avg_latency_ms', 0.0)} ms")
    st.sidebar.metric(label="Pipeline Errors", value=f"{obs_data.get('errors_count', 0)}")
    st.sidebar.text(f"Uptime: {obs_data.get('uptime_seconds', 0)}s")
else:
    st.sidebar.warning("Unable to fetch telemetry. Ingestion engine offline.")

# Refresh page button
if st.sidebar.button("🔄 Refresh Telemetry"):
    st.rerun()

# --- Main Grid: Machine Overview ---
st.header("🏭 Factory Floor Status")
machines = get_data("/api/machines")

if not machines:
    st.info("Waiting for telemetry generator connection. Please ensure the backend is running.")
else:
    cols = st.columns(len(machines))
    for idx, m in enumerate(machines):
        with cols[idx]:
            is_anomaly = m["status"] == "anomalous"
            status_text = "ANOMALY" if is_anomaly else "HEALTHY"
            status_class = "badge-anomaly" if is_anomaly else "badge-healthy"
            border_color = "#ef4444" if is_anomaly else "#3b82f6"
            prob_pct = int(m["failure_probability"] * 100)
            
            st.markdown(f"""
            <div style="background-color: #1e293b; border-radius: 12px; padding: 18px; border-top: 5px solid {border_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.15); color: #f8fafc; font-family: 'Source Sans Pro', sans-serif; height: 270px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 15px; font-weight: 600; color: #ffffff; line-height: 1.2;">{m['name']}</span>
                        <span style="font-size: 10px; color: #94a3b8; font-weight: bold; background-color: #334155; padding: 2px 6px; border-radius: 4px;">{m['machine_id']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span class="{status_class}" style="font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 9999px; text-transform: uppercase;">{status_text}</span>
                        <span style="font-size: 11px; color: #cbd5e1;">Fail Prob: <strong style="color: {border_color}; font-size: 13px;">{prob_pct}%</strong></span>
                    </div>
                </div>
                <div style="border-top: 1px solid #334155; padding-top: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div style="background-color: #0f172a; padding: 8px; border-radius: 6px; text-align: center;">
                        <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase; margin-bottom: 2px;">Vibration</div>
                        <div style="font-size: 13px; font-weight: bold; color: #f8fafc;">{m['vibration']} mm/s</div>
                    </div>
                    <div style="background-color: #0f172a; padding: 8px; border-radius: 6px; text-align: center;">
                        <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase; margin-bottom: 2px;">Temp</div>
                        <div style="font-size: 13px; font-weight: bold; color: #f8fafc;">{m['temperature']} °C</div>
                    </div>
                    <div style="background-color: #0f172a; padding: 8px; border-radius: 6px; text-align: center;">
                        <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase; margin-bottom: 2px;">Pressure</div>
                        <div style="font-size: 13px; font-weight: bold; color: #f8fafc;">{m['pressure']} PSI</div>
                    </div>
                    <div style="background-color: #0f172a; padding: 8px; border-radius: 6px; text-align: center;">
                        <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase; margin-bottom: 2px;">RPM</div>
                        <div style="font-size: 13px; font-weight: bold; color: #f8fafc;">{int(m['rpm'])}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# --- Tabs for detailed insights ---
tab_plots, tab_alerts, tab_remedies, tab_assistant = st.tabs([
    "📈 Live Telemetry Streaming", 
    "🚨 Anomaly Log & AI Diagnostics",
    "🔧 Maintenance Intervention",
    "🤖 Ask AI Reliability Agent"
])

# 1. Telemetry Plots Tab
with tab_plots:
    st.subheader("Historical Telemetry Trends")
    if machines:
        selected_m = st.selectbox(
            "Select Machine to Plot", 
            options=[f"{m['machine_id']} - {m['name']}" for m in machines]
        )
        selected_id = selected_m.split(" - ")[0]
        
        hist_data = get_data(f"/api/machines/{selected_id}/telemetry", params={"limit": 50})
        
        if hist_data:
            df = pd.DataFrame(hist_data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)
            
            col_left, col_right = st.columns(2)
            with col_left:
                st.write("**Vibration Profile (mm/s)**")
                st.line_chart(df["vibration"])
                st.write("**Temperature Profile (°C)**")
                st.line_chart(df["temperature"])
            with col_right:
                st.write("**Pressure Profile (PSI)**")
                st.line_chart(df["pressure"])
                st.write("**Rotation Speed (RPM)**")
                st.line_chart(df["rpm"])
        else:
            st.info("No historical readings recorded for this machine.")
    else:
        st.info("No machines available.")

# 2. Anomaly Log Tab
with tab_alerts:
    st.subheader("Detected Failures & AI Explanations")
    anomalies = get_data("/api/anomalies")
    
    if not anomalies:
        st.success("No anomalies currently logged. All machines nominal.")
    else:
        for a in anomalies:
            time_str = datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
            expander_title = f"⚠️ [{time_str}] {a['machine_name']} ({a['machine_id']}) - Failure Probability: {int(a['failure_probability']*100)}%"
            with st.expander(expander_title, expanded=True):
                st.markdown(f"**Anomaly Severity & Vector:**")
                st.write(
                    f"Vibration: `{a['vibration_status']}` | Temperature: `{a['temperature_status']}` | "
                    f"RPM: `{a['rpm_status']}` | Pressure: `{a['pressure_status']}`"
                )
                if a["estimated_window_hours"]:
                    st.warning(f"⏳ Recommended Maintenance Window: **{a['estimated_window_hours']} hours**")
                
                st.markdown("**AI Diagnostic Report:**")
                st.markdown(a["ai_explanation"] or "*AI is generating diagnostic explanation...*")

# 3. Maintenance Tab
with tab_remedies:
    st.subheader("Record Maintenance Event")
    st.write("Submit this form to record a corrective maintenance action. This will reset the simulator for the machine.")
    
    if machines:
        with st.form("maintenance_form"):
            selected_m = st.selectbox(
                "Target Machine", 
                options=[f"{m['machine_id']} - {m['name']}" for m in machines]
            )
            target_id = selected_m.split(" - ")[0]
            action = st.text_input("Intervention Action Performed", placeholder="e.g. Swapped seals, calibrated bearings")
            notes = st.text_area("Detailed notes (optional)")
            
            submitted = st.form_submit_submit_button = st.form_submit_button("Submit Intervention Log")
            if submitted:
                if not action:
                    st.error("Please specify the intervention action.")
                else:
                    payload = {"machine_id": target_id, "action": action, "notes": notes}
                    code, res = post_data("/api/maintenance", payload)
                    if code == 201:
                        st.success(f"Successfully recorded maintenance! {target_id} has been reset to Healthy.")
                        st.balloons()
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error(f"Failed to submit maintenance log: {res.get('detail', 'Unknown error')}")
    else:
        st.info("No machines registered.")

# 4. AI Assistant Tab
with tab_assistant:
    st.subheader("💬 AI Reliability Diagnostic Assistant")
    st.write("Query the LLM agent about machine health, baseline drifts, or repair recommendations.")
    
    user_query = st.text_input("Ask the Assistant:", placeholder="e.g. what is wrong with M-102 right now?")
    
    if st.button("Send Query"):
        if not user_query:
            st.error("Please enter a question.")
        else:
            with st.spinner("AI Agent analyzing machine status..."):
                code, res = post_data("/api/assistant/query", {"query": user_query})
                if code == 200:
                    st.markdown("**Assistant Response:**")
                    st.markdown(res.get("response"))
                else:
                    st.error(f"Error querying AI Assistant: {res.get('detail', 'Backend offline')}")
