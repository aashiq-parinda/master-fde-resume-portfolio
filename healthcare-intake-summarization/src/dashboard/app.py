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
tab_queue, tab_rag, tab_safety, tab_traces, tab_evals, tab_info = st.tabs([
    "📋 Physician Triage & Citations", 
    "🔍 Hybrid RAG & Reranker", 
    "🛡️ Safety Guardrails", 
    "⏱️ Observability & Tracing", 
    "📊 Benchmark Evaluations", 
    "⚙️ System Architecture"
])

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
                        st.markdown("### 📊 Structured Pre-Visit Summary (with Citations)")
                        st.write(summary["summary_text"])
                        
                        if st.button("🔄 Reprocess and Re-run Pipeline", key=f"rep_{current_intake['id']}", use_container_width=True):
                            status_code, resp = post_action(f"/api/intakes/{current_intake['id']}/reprocess")
                            if status_code == 200:
                                st.success("Intake reprocessed successfully!")
                                st.rerun()

with tab_rag:
    st.subheader("🔍 Hybrid Retrieval & Cross-Encoder Reranker Explorer")
    st.markdown("Explore how the system executes **Dense Vector Cosine Similarity**, **Sparse BM25 Keyword Search**, and **Reciprocal Rank Fusion (RRF)**, followed by deep **Cross-Encoder Contextual Reranking**.")
    
    rag_query = st.text_input(
        "Enter Patient Symptoms Query for RAG Inspection:",
        value="Crushing central chest pain radiating to left jaw with cold sweats and shortness of breath"
    )
    
    if st.button("🔬 Execute Hybrid Search & Reranking", use_container_width=True):
        with st.spinner("Executing dense embeddings, BM25 sparse matching, and cross-encoder scoring..."):
            status_code, rag_data = post_action("/api/retrieval/inspect", {"query": rag_query})
            if status_code == 200 and "telemetry" in rag_data:
                telemetry = rag_data["telemetry"]
                
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    st.markdown("#### 1️⃣ Hybrid Retrieval Candidates (Dense + Sparse + RRF)")
                    df_hybrid = pd.DataFrame(telemetry["hybrid_candidates"])
                    st.dataframe(
                        df_hybrid[["category", "dense_score", "sparse_score", "rrf_score", "hybrid_score"]],
                        column_config={
                            "category": "Protocol Category",
                            "dense_score": st.column_config.ProgressColumn("Dense Score (Cosine)", min_value=0, max_value=1),
                            "sparse_score": "Sparse BM25",
                            "rrf_score": "RRF Score",
                            "hybrid_score": st.column_config.ProgressColumn("Fused Score", min_value=0, max_value=1)
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                with r_col2:
                    st.markdown("#### 2️⃣ Cross-Encoder Contextual Reranking")
                    reranked_top = telemetry["reranked_top"]
                    for idx, cand in enumerate(reranked_top, start=1):
                        delta = cand.get("rank_delta", 0)
                        delta_badge = f"⬆️ +{delta}" if delta > 0 else f"⬇️ {delta}" if delta < 0 else "⏺️ 0"
                        st.markdown(f"**Rank #{idx}: {cand['category']}** ({delta_badge}) | Score: `{cand.get('rerank_score')}`")
                        factors = cand.get("factors", {})
                        st.json(factors)
            else:
                st.error("Failed to fetch retrieval inspection data.")

with tab_safety:
    st.subheader("🛡️ Multi-Tier Safety Guardrails & Infraction Audit Trail")
    st.markdown("Multi-tiered defense ensuring a strict **0.0% Diagnostic Leakage Rate** through lexical boundary matching, syntactic regex assertion interception, PHI/PII masking, and deterministic template fallback.")
    
    if not safety_logs:
        st.success("✅ Clean Audit Record: 0 diagnostic leakage violations in active database session.")
    else:
        df_logs = pd.DataFrame(safety_logs)
        st.dataframe(
            df_logs[["patient_name", "violation_reason", "blocked_output", "timestamp"]],
            column_config={
                "patient_name": "Patient Context",
                "violation_reason": "Interception Rule",
                "blocked_output": "Blocked Response",
                "timestamp": "Timestamp"
            },
            use_container_width=True,
            hide_index=True
        )

with tab_traces:
    st.subheader("⏱️ Observability & Distributed Execution Tracing")
    st.markdown("Micro-profiling every stage of the clinical RAG pipeline: Ingestion, Sparse BM25, Dense Vector, Fusion, Cross-Encoder, LLM Synthesis, Guardrails, and DB write-back.")
    
    traces_data = get_data("/api/traces")
    if not traces_data:
        st.info("No execution traces currently in buffer. Submit an intake in the sidebar or run benchmarks.")
    else:
        tr_col1, tr_col2 = st.columns([1, 2])
        with tr_col1:
            st.markdown("#### Recent Pipeline Traces")
            for t in traces_data[:10]:
                t_label = f"{t.get('patient_name', 'Patient')} ({t['total_duration_ms']}ms - {t['status']})"
                if st.button(t_label, key=f"tr_{t['trace_id']}", use_container_width=True):
                    st.session_state["selected_trace_id"] = t["trace_id"]
        with tr_col2:
            sel_tr_id = st.session_state.get("selected_trace_id", traces_data[0]["trace_id"])
            curr_trace = next((t for t in traces_data if t["trace_id"] == sel_tr_id), traces_data[0])
            st.markdown(f"#### Trace Details: `{curr_trace['trace_id']}`")
            st.markdown(f"**Total Duration:** `{curr_trace['total_duration_ms']} ms` | **Status:** `{curr_trace['status']}`")
            
            spans = curr_trace.get("spans", [])
            if spans:
                df_spans = pd.DataFrame(spans)
                st.dataframe(
                    df_spans[["name", "duration_ms", "status", "metadata"]],
                    column_config={
                        "name": "Pipeline Stage / Span",
                        "duration_ms": "Duration (ms)",
                        "status": "Outcome",
                        "metadata": "Telemetry Metadata"
                    },
                    use_container_width=True,
                    hide_index=True
                )

with tab_evals:
    st.subheader("📊 Automated Clinical AI Safety & RAG Benchmark Suite")
    st.markdown("Automated evaluation harness testing standard clinical intakes, subtle presentations, and adversarial diagnostic jailbreak attacks against gold-standard ground truth.")
    
    if st.button("🚀 Run Full Automated Benchmark Suite (10 Gold Cases)", use_container_width=True):
        with st.spinner("Executing gold dataset test cases against multi-tier guardrails and RAG pipeline..."):
            status_code, eval_summary = post_action("/api/evals/run")
            if status_code == 200 and "metrics" in eval_summary:
                st.session_state["latest_eval_results"] = eval_summary
                st.success("Benchmark completed successfully!")
            else:
                st.error("Evaluation run failed.")
                
    latest_eval = st.session_state.get("latest_eval_results")
    if not latest_eval and os.path.exists(os.path.join(os.path.dirname(__file__), "..", "..", "evals", "results.json")):
        try:
            import json
            with open(os.path.join(os.path.dirname(__file__), "..", "..", "evals", "results.json"), "r") as f:
                latest_eval = json.load(f)
        except Exception:
            pass

    if latest_eval:
        m = latest_eval["metrics"]
        st.markdown("### 🏆 Gold Standard Performance Scorecard")
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        with sc1:
            st.metric("Diagnostic Leakage Rate", f"{m['diagnostic_leakage_rate_pct']}%", delta="0.0% Target", delta_color="inverse")
        with sc2:
            st.metric("Adversarial Defense Rate", f"{m['adversarial_defense_rate_pct']}%", delta="100% Intercepted")
        with sc3:
            st.metric("Triage Concordance", f"{m['triage_accuracy_pct']}%", delta="High Accuracy")
        with sc4:
            st.metric("Claim Groundedness", f"{m['mean_groundedness_pct']}%", delta="Protocol Provenance")
        with sc5:
            st.metric("Latency (p50 / p95)", f"{m['latency_p50_ms']}ms / {m['latency_p95_ms']}ms")
            
        st.markdown("#### Test Case Breakdown")
        df_cases = pd.DataFrame(latest_eval["case_details"])
        st.dataframe(
            df_cases[["case_id", "category", "is_adversarial", "triage_expected", "triage_assigned", "is_safe", "citations_count", "latency_ms"]],
            column_config={
                "case_id": "Case ID",
                "category": "Clinical Category",
                "is_adversarial": "Adversarial Trap?",
                "triage_expected": "Expected Triage",
                "triage_assigned": "Assigned Triage",
                "is_safe": "Safety Compliant",
                "citations_count": "Citations",
                "latency_ms": "Latency (ms)"
            },
            use_container_width=True,
            hide_index=True
        )

with tab_info:
    st.subheader("⚙️ System Architecture & Programmatic Guardrails")
    st.markdown("""
    This project demonstrates a **Zero-Diagnosis Clinical Intake Pipeline** engineered to resolve medical liability risk in automated pre-visit charting.
    
    ### 🔬 Architectural Core
    1. **Hybrid Retrieval**: Combines Dense Vector Cosine Similarity (semantic context) and Sparse BM25 Keyword Search (lexical red-flags) via Reciprocal Rank Fusion (RRF).
    2. **Contextual Cross-Encoder Reranker**: Evaluates clinical affinity clusters, symptom acuity, and emergency triage weights.
    3. **Generative Synthesis with Grounded Citations**: Summarizes patient presentations with inline citation tags linked directly to source protocol excerpts.
    4. **Multi-Tier Safety Guardrails**: Programmatically intercepts diagnostic terms, assertions, and PHI prior to database write-back.
    5. **Self-Correction & Failsafe Containment**: Automatic feedback retry loop with guaranteed 0.0% leakage template fallback.
    6. **Distributed Tracing & Benchmarking**: End-to-end span micro-profiling and automated gold test evaluation.
    """)

