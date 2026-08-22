import os
import base64
import streamlit as st
import pandas as pd
import requests

# Page configuration
st.set_page_config(
    page_title="Clinical Pre-Visit Summarizer Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Endpoint URL
API_URL = "http://127.0.0.1:8002"

def get_data(endpoint: str):
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=3.0)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def post_action(endpoint: str, json_data: dict = None):
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=json_data, timeout=5.0)
        if response.status_code in [200, 201]:
            return response.status_code, response.json()
    except Exception as e:
        return 500, {"detail": str(e)}
    return 500, {"detail": "Unknown API error"}

# Define zoom modal dialog
@st.dialog("📋 Pre-Visit Summary Report (Zoom View)", width="large")
def show_summary_modal(patient_name, summary_text, triage_level, safety_attempts, raw_symptoms, red_flags):
    st.markdown(f"### Patient: **{patient_name}**")
    st.markdown(f"**Triage Severity:** `{triage_level}` | **Generation Attempts:** `{safety_attempts}`")
    st.divider()
    
    col_modal_raw, col_modal_sum = st.columns(2)
    with col_modal_raw:
        st.markdown("#### 📝 Raw Symptom Transcript")
        st.info(raw_symptoms)
        st.markdown("#### 🚑 Clinical Red Flags Reference")
        st.error(red_flags)
    with col_modal_sum:
        st.markdown("#### 📄 Structured Pre-Visit Summary")
        st.write(summary_text)
        
    st.divider()
    if st.button("Close Zoom View", use_container_width=True):
        st.rerun()

# --- Sidebar: Logo and Simulator ---
logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "hospital.png")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.sidebar.markdown(
            f"""
            <div style="margin-top: 5px; margin-bottom: 5px; text-align: center;">
                <img src="data:image/png;base64,{encoded_string}" style="width: 100%; max-width: 250px; height: 110px; object-fit: contain; object-position: center; border-radius: 8px;">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.image("https://img.shields.io/badge/FDE%20Portfolio-Active-blue", width=150)

st.sidebar.header("📝 Intake Simulator")
st.sidebar.markdown("Submit a synthetic patient symptom report to test RAG guidelines and the diagnostic safety filter.")

# Prepopulated Template Selection
templates = {
    "Select Template...": {},
    "Abdominal Pain (Urgent - Appendicitis Mock)": {
        "name": "Arjun Sharma",
        "dob": "1994-08-12",
        "symptoms": "Severe stabbing pain starting near my belly button and moving to the lower right side of my stomach. It hurts when I press down. I have a slight fever of 100.2F and feel nauseous."
    },
    "Chest Pain (Emergency - Cardiac Mock)": {
        "name": "Maria Fernandez",
        "dob": "1965-03-24",
        "symptoms": "I have an intense heavy pressure in the middle of my chest. It feels like someone is squeezing my heart. The pain goes down my left arm and up to my jaw. I am breaking out in a cold sweat."
    },
    "Headache (Emergency - Stroke Mock)": {
        "name": "Devendra Patil",
        "dob": "1972-11-05",
        "symptoms": "I was suddenly hit with the worst headache of my life. It felt like a thunderclap in my skull. I am feeling slightly weak on my right side and my speech feels slurred."
    },
    "Knee Pain (Routine - Musculoskeletal)": {
        "name": "Karan Johar",
        "dob": "1989-06-18",
        "symptoms": "My left knee has been aching after running yesterday. It's a dull throbbing pain. There is no major swelling, but it is stiff when I bend it."
    }
}

template_choice = st.sidebar.selectbox("Load Symptom Template", list(templates.keys()))

with st.sidebar.form("intake_form"):
    patient_name = st.text_input("Patient Name", value=templates[template_choice].get("name", ""))
    dob = st.date_input("Date of Birth", value=pd.to_datetime(templates[template_choice].get("dob", "1990-01-01")).date())
    raw_symptoms = st.text_area("Patient Reported Symptoms", value=templates[template_choice].get("symptoms", ""), height=150)
    
    submit_btn = st.form_submit_button("Submit Patient Intake")
    
    if submit_btn:
        if not patient_name or not raw_symptoms:
            st.error("Please provide both Patient Name and Symptoms.")
        else:
            payload = {
                "patient_name": patient_name,
                "date_of_birth": dob.isoformat(),
                "raw_symptoms": raw_symptoms
            }
            status_code, resp = post_action("/api/intakes", payload)
            if status_code == 201:
                st.sidebar.success(f"Intake Created! Triage: {resp['triage_recommendation'].upper()}")
                if resp["safety_attempts_triggered"] > 1:
                    st.sidebar.warning(f"Safety Trigger: Blocked and regenerated {resp['safety_attempts_triggered'] - 1} times.")
            else:
                st.sidebar.error("Ingestion failed.")

# Custom Premium Styling
st.markdown("""
<style>
    .top-card {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-top: 4px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        text-align: center;
        color: #f8fafc;
    }
    .top-card-emergency {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-top: 4px solid #ef4444;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        text-align: center;
        color: #f8fafc;
    }
    .top-card-urgent {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-top: 4px solid #eab308;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        text-align: center;
        color: #f8fafc;
    }
    .top-card-safety {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-top: 4px solid #10b981;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        text-align: center;
        color: #f8fafc;
    }
    .triage-emergency {
        background-color: #7f1d1d;
        color: #f87171;
        font-weight: bold;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 13px;
        border-left: 5px solid #ef4444;
    }
    .triage-urgent {
        background-color: #78350f;
        color: #fbbf24;
        font-weight: bold;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 13px;
        border-left: 5px solid #eab308;
    }
    .triage-routine {
        background-color: #065f46;
        color: #34d399;
        font-weight: bold;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 13px;
        border-left: 5px solid #10b981;
    }
    .card-safety-ok {
        background-color: #0f172a;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #10b981;
    }
    .card-safety-retry {
        background-color: #0f172a;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #eab308;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Title Area
st.title("🏥 Clinical Patient Intake Summarization Platform")
st.markdown("### Pre-visit structured charting, guideline routing, and diagnostic safety gating")

# Fetch data from API
intakes = get_data("/api/intakes")
summaries = get_data("/api/summaries")
safety_logs = get_data("/api/safety-logs")

# Calculate counts for top-level stats
total_intakes = len(intakes) if intakes else 0
emergency_count = 0
urgent_count = 0
if summaries:
    emergency_count = len([s for s in summaries if s["triage_recommendation"].lower() == "emergency"])
    urgent_count = len([s for s in summaries if s["triage_recommendation"].lower() == "urgent"])
safety_blocks = len(safety_logs) if safety_logs else 0

# Tabs
tab_queue, tab_safety = st.tabs(["📋 Physician Triage Queue", "🚨 Diagnostic Safety Audits"])

with tab_queue:
    if not intakes:
        st.info("No patient intakes submitted in the system. Use the Intake Simulator in the sidebar to add patients.")
    else:
        # 1. Metric Cards Grid
        st.markdown("### 📊 Live Operations Summary")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.markdown(f"""
            <div class="top-card">
                <p style="margin:0; font-size:14px; color:#94a3b8;">Total Patients Ingested</p>
                <h2 style="margin:5px 0 0 0; font-size:28px; color:#ffffff;">{total_intakes}</h2>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="top-card-emergency">
                <p style="margin:0; font-size:14px; color:#94a3b8;">Emergency Triage Cases</p>
                <h2 style="margin:5px 0 0 0; font-size:28px; color:#f87171;">{emergency_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""
            <div class="top-card-urgent">
                <p style="margin:0; font-size:14px; color:#94a3b8;">Urgent Triage Cases</p>
                <h2 style="margin:5px 0 0 0; font-size:28px; color:#fbbf24;">{urgent_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        with m_col4:
            st.markdown(f"""
            <div class="top-card-safety">
                <p style="margin:0; font-size:14px; color:#94a3b8;">Safety Gating Blocks</p>
                <h2 style="margin:5px 0 0 0; font-size:28px; color:#34d399;">{safety_blocks}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("---")
        
        # 2. Main content split layout
        col_list, col_detail = st.columns([1, 2])
        
        with col_list:
            st.subheader("Patient Queue")
            search = st.text_input("🔍 Filter Patient by Name", "")
            
            for patient in intakes:
                if search and search.lower() not in patient["patient_name"].lower():
                    continue
                    
                status = patient["status"].lower()
                status_color = "🟢 Cleared" if status == "cleared" else "🟡 Flagged" if status == "flagged" else "⚪ Pending"
                
                btn_label = f"{patient['patient_name']} (DOB: {patient['date_of_birth']}) \n {status_color}"
                if st.button(btn_label, key=f"btn_{patient['id']}", use_container_width=True):
                    st.session_state["selected_intake_id"] = patient["id"]
                    
        with col_detail:
            selected_id = st.session_state.get("selected_intake_id")
            
            current_intake = None
            if selected_id:
                current_intake = next((i for i in intakes if i["id"] == selected_id), None)
            if not current_intake and intakes:
                current_intake = intakes[0]
                
            if current_intake:
                st.subheader(f"Patient Pre-Visit Record: {current_intake['patient_name']}")
                st.markdown(f"**Date of Birth:** {current_intake['date_of_birth']} | **Intake ID:** `{current_intake['id']}`")
                
                summary = None
                if summaries:
                    summary = next((s for s in summaries if s["intake_id"] == current_intake["id"]), None)
                    
                if not summary:
                    st.info("🔄 Pre-visit summary generation is running in the background. Please wait.")
                else:
                    triage_class = "triage-routine"
                    triage_text = summary["triage_recommendation"].upper()
                    
                    if triage_text == "EMERGENCY":
                        triage_class = "triage-emergency"
                    elif triage_text == "URGENT":
                        triage_class = "triage-urgent"
                        
                    # Action row with zoom & triage badge
                    act_col1, act_col2 = st.columns([2, 1])
                    with act_col1:
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 15px; margin-top: 5px;">
                            <strong>Triage Level:</strong>
                            <span class="{triage_class}">{triage_text}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with act_col2:
                        if st.button("🔍 Open Zoom View (Modal)", use_container_width=True):
                            show_summary_modal(
                                current_intake["patient_name"],
                                summary["summary_text"],
                                triage_text,
                                summary["safety_attempts"],
                                current_intake["raw_symptoms"],
                                summary["red_flags_extracted"]
                            )
                            
                    st.write("")
                    
                    # Safety Checklist Card
                    attempts = summary["safety_attempts"]
                    safety_card_class = "card-safety-ok" if attempts == 1 else "card-safety-retry"
                    safety_status_text = "PASSED on first attempt (0% diagnostic leakage)" if attempts == 1 else f"WARNING: Programmatic filter blocked {attempts - 1} diagnostic attempts. Safe version successfully generated."
                    
                    st.markdown(f"""
                    <div class="{safety_card_class}">
                        <h4 style="margin-top:0; color:#ffffff;">🔒 Programmatic Safety Gate Status</h4>
                        <p style="margin: 5px 0 0 0; font-size:13px; color:#e2e8f0;">
                            <strong>Safety Audit:</strong> {safety_status_text}<br>
                            <strong>Medical Liability Rule:</strong> Enforces 100% diagnostic terminology containment prior to database write-back.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Columns for symptoms vs summary
                    col_raw, col_summary = st.columns(2)
                    
                    with col_raw:
                        st.markdown("### 📝 Patient Raw Intake Transcript")
                        st.info(current_intake["raw_symptoms"])
                        
                        st.markdown("### 🚑 Matched Clinical Red Flags Checklist")
                        st.error(summary["red_flags_extracted"])
                        
                    with col_summary:
                        st.markdown("### 📊 Structured Pre-Visit Summary")
                        st.write(summary["summary_text"])
                        
                        if st.button("🔄 Reprocess and Re-run Pipeline", key=f"rep_{current_intake['id']}", use_container_width=True):
                            status_code, resp = post_action(f"/api/intakes/{current_intake['id']}/reprocess")
                            if status_code == 200:
                                st.success("Intake reprocessed successfully!")
                                st.rerun()

with tab_safety:
    st.subheader("Programmatic Safety Filter Infraction Logs")
    st.markdown("This audit trail logs all attempts where the LLM violated the medical liability safety gate (i.e. attempted to output a clinical diagnosis instead of descriptive symptoms). It documents the raw blocked response, the matched terms, and the timestamp.")
    
    if not safety_logs:
        st.success("✅ Clean Audit Record: The safety filter has recorded 0 diagnostic leakage violations in this session!")
    else:
        df_logs = pd.DataFrame(safety_logs)
        st.dataframe(
            df_logs[["patient_name", "violation_reason", "blocked_output", "timestamp"]],
            column_config={
                "patient_name": "Patient Context",
                "violation_reason": "Matching Rule Violation",
                "blocked_output": "Blocked LLM Output Content",
                "timestamp": "Trigger Timestamp"
            },
            use_container_width=True,
            hide_index=True
        )
