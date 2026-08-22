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

# --- Sidebar: Logo and Simulator ---
logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "hospital.jpg")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.sidebar.markdown(
            f"""
            <div style="margin-top: 5px; margin-bottom: 5px; text-align: center;">
                <img src="data:image/jpeg;base64,{encoded_string}" style="width: 100%; max-width: 250px; height: 50px; object-fit: contain; object-position: center; border-radius: 8px;">
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
                st.success(f"Intake Created! Triage Recommendation: {resp['triage_recommendation'].upper()}")
                if resp["safety_attempts_triggered"] > 1:
                    st.warning(f"Safety Trigger: LLM diagnostic output blocked and regenerated {resp['safety_attempts_triggered'] - 1} times.")
            else:
                st.error("Ingestion failed.")

# Custom Premium Styling
st.markdown("""
<style>
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
        background-color: #111827;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #10b981;
    }
    .card-safety-retry {
        background-color: #111827;
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

# Tabs
tab_queue, tab_safety = st.tabs(["📋 Physician Triage Queue", "🚨 Diagnostic Safety Audits"])

with tab_queue:
    if not intakes:
        st.info("No patient intakes submitted in the system. Use the Intake Simulator in the sidebar to add patients.")
    else:
        # Create layouts
        col_list, col_detail = st.columns([1, 2])
        
        with col_list:
            st.subheader("Patient Intake Queue")
            
            # Search / Filter
            search = st.text_input("🔍 Search Patient Name", "")
            
            for patient in intakes:
                if search and search.lower() not in patient["patient_name"].lower():
                    continue
                    
                status = patient["status"].lower()
                status_color = "🟢 Cleared" if status == "cleared" else "🟡 Flagged" if status == "flagged" else "⚪ Pending"
                
                # Checkbox selection simulated by button click
                btn_label = f"{patient['patient_name']} (DOB: {patient['date_of_birth']}) \n {status_color}"
                if st.button(btn_label, key=f"btn_{patient['id']}", use_container_width=True):
                    st.session_state["selected_intake_id"] = patient["id"]
                    
        with col_detail:
            selected_id = st.session_state.get("selected_intake_id")
            
            # Find matching intake
            current_intake = None
            if selected_id:
                current_intake = next((i for i in intakes if i["id"] == selected_id), None)
            if not current_intake and intakes:
                current_intake = intakes[0]
                
            if current_intake:
                st.subheader(f"Patient Pre-Visit Record: {current_intake['patient_name']}")
                st.markdown(f"**Date of Birth:** {current_intake['date_of_birth']}")
                st.markdown(f"**Intake ID:** `{current_intake['id']}`")
                
                # Find matching summary
                summary = None
                if summaries:
                    summary = next((s for s in summaries if s["intake_id"] == current_intake["id"]), None)
                    
                if not summary:
                    st.info("🔄 Pre-visit summary generation is running in the background. Please wait.")
                else:
                    # Triage Display
                    triage_class = "triage-routine"
                    triage_text = summary["triage_recommendation"].upper()
                    
                    if triage_text == "EMERGENCY":
                        triage_class = "triage-emergency"
                    elif triage_text == "URGENT":
                        triage_class = "triage-urgent"
                        
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
                        <strong>Triage Severity Recommendation:</strong>
                        <span class="{triage_class}">{triage_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Safety Checklist Card
                    attempts = summary["safety_attempts"]
                    safety_card_class = "card-safety-ok" if attempts == 1 else "card-safety-retry"
                    safety_status_text = "PASSED on first attempt (0% diagnostic leakage)" if attempts == 1 else f"WARNING: Programmatic filter blocked {attempts - 1} diagnostic attempts. Safe version successfully generated."
                    
                    st.markdown(f"""
                    <div class="{safety_card_class}">
                        <h4 style="margin-top:0; color:#ffffff;">🔒 Programmatic Safety Gate Status</h4>
                        <p style="margin: 5px 0 0 0; font-size:13px; color:#e2e8f0;">
                            <strong>Safety Audit:</strong> {safety_status_text}<br>
                            <strong>Medical Liability Rule:</strong> Enforces 100% diagnostic terminology containment prior to write-back.
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
                        
                        # Add a reprocess button
                        if st.button("🔄 Reprocess and Re-run Pipeline", key=f"rep_{current_intake['id']}"):
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
