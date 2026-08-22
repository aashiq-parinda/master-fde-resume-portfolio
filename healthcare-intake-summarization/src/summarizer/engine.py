import logging
import httpx
import google.generativeai as genai
from typing import Dict, Any, List
from src.config import settings
from src.database import db_manager
from src.safety.filter import verify_safety_rules

logger = logging.getLogger("engine")

# Initialize Gemini if API key is provided
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

async def retrieve_guidelines(symptom_text: str) -> List[Dict[str, Any]]:
    """Performs native PostgreSQL Full-Text Search to match guidelines against symptoms."""
    try:
        # Use full-text search vector query matching symptom category and red flags
        rows = await db_manager.fetch("""
            SELECT symptom_category, red_flags, triage_level, guideline_text,
                   ts_rank(to_tsvector('english', symptom_category || ' ' || red_flags || ' ' || guideline_text), plainto_tsquery('english', $1)) as rank
            FROM clinical_guidelines
            WHERE to_tsvector('english', symptom_category || ' ' || red_flags || ' ' || guideline_text) @@ plainto_tsquery('english', $1)
            ORDER BY rank DESC
            LIMIT 2
        """, symptom_text)
        
        if not rows:
            # Fallback to fetch default musculoskeletal/routine guidelines
            rows = await db_manager.fetch("""
                SELECT symptom_category, red_flags, triage_level, guideline_text
                FROM clinical_guidelines
                WHERE symptom_category = 'Musculoskeletal Pain'
            """)
            
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"PostgreSQL FTS guidelines retrieval failed: {e}")
        # Return hardcoded default if DB fails
        return [{
            "symptom_category": "General Outpatient",
            "red_flags": "none",
            "triage_level": "Routine",
            "guideline_text": "Schedule regular outpatient consult."
        }]

def generate_mock_llm_response(raw_symptoms: str, guidelines: List[Dict[str, Any]], attempt: int) -> str:
    """
    Simulates LLM generation for offline testing.
    On the first attempt, if the input symptoms mention "appendix" or "appendicitis",
    it intentionally leaks the diagnosis "appendicitis" to test the safety filter retry loop.
    On subsequent attempts, it returns a safe, descriptive clinical summary.
    """
    symptoms_lower = raw_symptoms.lower()
    triage = guidelines[0]["triage_level"]
    guideline_info = guidelines[0]["guideline_text"]
    
    # 1. Simulate diagnostic leakage on attempt 1
    if attempt == 1:
        if "appendicitis" in symptoms_lower or "appendix" in symptoms_lower:
            return (
                "SUMMARY:\n"
                "The patient presents with symptoms consistent with acute appendicitis. "
                "They report severe pain in the right lower quadrant of the abdomen for 12 hours. "
                "Triage Level: Urgent. Action: Refer to surgeon immediately."
            )
        elif "migraine" in symptoms_lower:
            return (
                "SUMMARY:\n"
                "Patient exhibits symptoms of a classic migraine headache. "
                "Triage Level: Emergency. Action: Monitor closely."
            )
            
    # 2. Return a safe, purely descriptive summary
    red_flag_mentions = []
    for g in guidelines:
        if g["red_flags"] != "none":
            red_flag_mentions.append(g["red_flags"])
            
    red_flags_str = ", ".join(red_flag_mentions) if red_flag_mentions else "None identified"
    
    return (
        f"SYMPTOM SUMMARY:\n"
        f"- Location/Description: Patient reports severe distress/symptoms in matching region.\n"
        f"- Identified Guidelines Category: {guidelines[0]['symptom_category']}\n"
        f"- Guideline Reference: {guideline_info}\n\n"
        f"RED FLAGS DETECTED:\n"
        f"- Matching reference items: {red_flags_str}\n\n"
        f"TRIAGE RECOMMENDATION:\n"
        f"- Tier: {triage}\n"
        f"- Rationale: Descriptive symptom profile matches clinical guidelines threshold."
    )

async def call_gemini_api(prompt: str) -> str:
    """Calls Gemini API for intake summarization."""
    # Use gemini-1.5-flash as it is fast and accurate for summarization
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

async def generate_pre_visit_summary(intake_id: int, patient_name: str, raw_symptoms: str) -> Dict[str, Any]:
    """
    Retrieves matching clinical guidelines, generates summary, runs it through the safety filter,
    logs violations, and retries generation up to 3 times to ensure 100% diagnostic safety.
    """
    guidelines = await retrieve_guidelines(raw_symptoms)
    triage = guidelines[0]["triage_level"]
    
    # Format guidelines for prompt context
    guidelines_context = ""
    for idx, g in enumerate(guidelines):
        guidelines_context += (
            f"Guideline Category {idx+1}: {g['symptom_category']}\n"
            f"- Triage Level: {g['triage_level']}\n"
            f"- Critical Red Flags: {g['red_flags']}\n"
            f"- Clinical Protocol: {g['guideline_text']}\n\n"
        )

    attempts = 0
    max_attempts = 3
    summary_text = ""
    violation_reason = None
    
    while attempts < max_attempts:
        attempts += 1
        logger.info(f"Summary generation attempt {attempts} for intake ID {intake_id}...")
        
        if settings.GEMINI_API_KEY:
            # Build Gemini system instructions prompt
            prompt = (
                "You are a medical intake summarizer working in a clinical portal.\n"
                "Your task is to summarize the patient's unstructured symptoms into a pre-visit review.\n\n"
                "CRITICAL CLINICAL SAFETY RULES:\n"
                "1. NEVER make a diagnosis or guess the disease name (e.g. do NOT output 'appendicitis', 'migraine', 'covid', or 'flu').\n"
                "2. Describe symptoms purely using descriptive language (e.g. instead of 'bronchitis', write 'persistent productive cough and chest congestion').\n"
                "3. Do NOT use phrases like 'patient is diagnosed with' or 'indicates a case of'.\n\n"
                f"PATIENT REPORTED SYMPTOMS:\n{raw_symptoms}\n\n"
                f"REFERENCE CLINICAL GUIDELINES:\n{guidelines_context}\n"
                "OUTPUT FORMAT:\n"
                "SYMPTOM SUMMARY:\n"
                "[List symptoms, location, duration, and severity in descriptive terms]\n\n"
                "RED FLAGS DETECTED:\n"
                "[List any specific red flags that match the reference guidelines]\n\n"
                f"TRIAGE RECOMMENDATION:\n"
                f"- Tier: {triage}\n"
                "- Rationale: [Describe why based strictly on the guidelines]"
            )
            
            # If it's a retry, add corrective warning
            if violation_reason:
                prompt += (
                    f"\n\n⚠️ SAFETY VIOLATION WARNING FROM PREVIOUS ATTEMPT:\n"
                    f"Your last output was BLOCKED because: {violation_reason}\n"
                    f"Please rewrite the summary. Ensure you strictly omit any disease terms and write-up diagnostic-free descriptions."
                )
                
            try:
                summary_text = await call_gemini_api(prompt)
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Falling back to mock generator.")
                summary_text = generate_mock_llm_response(raw_symptoms, guidelines, attempt=attempts)
        else:
            # Mock mode
            summary_text = generate_mock_llm_response(raw_symptoms, guidelines, attempt=attempts)
            
        # Run programmatic safety verification
        is_safe, violation_reason = verify_safety_rules(summary_text)
        
        if is_safe:
            logger.info(f"Ingestion summary verified safe on attempt {attempts}.")
            break
        else:
            # Log violation to database for auditing
            await db_manager.execute("""
                INSERT INTO safety_logs (intake_id, blocked_output, violation_reason)
                VALUES ($1, $2, $3)
            """, intake_id, summary_text, violation_reason)
            
    # If it failed 3 times, construct a fallback template-driven safe summary
    if not is_safe:
        logger.error(f"Intake {intake_id} summary failed safety checks after {max_attempts} attempts. Triggering template fallback.")
        summary_text = (
            f"SYMPTOM SUMMARY:\n"
            f"- Patient reported symptoms: {raw_symptoms.strip()}\n"
            f"- Note: Automated clinical summary was regenerated due to diagnostic containment rules.\n\n"
            f"RED FLAGS DETECTED:\n"
            f"- Reference checklist matching: {guidelines[0]['red_flags']}\n\n"
            f"TRIAGE RECOMMENDATION:\n"
            f"- Tier: {triage}\n"
            f"- Rationale: Symptoms routed for outpatient evaluation matching {guidelines[0]['symptom_category']} protocols."
        )
        
    # Extracted red flags list (or default)
    red_flags_extracted = guidelines[0]["red_flags"] if triage in ["Emergency", "Urgent"] else "None identified"
    
    # Save the safe summary to visit_summaries
    await db_manager.execute("""
        INSERT INTO visit_summaries (intake_id, summary_text, red_flags_extracted, triage_recommendation, safety_attempts)
        VALUES ($1, $2, $3, $4, $5)
    """, intake_id, summary_text, red_flags_extracted, triage, attempts)
    
    # Update intake status based on triage
    status = "Flagged" if triage in ["Emergency", "Urgent"] else "Cleared"
    await db_manager.execute("""
        UPDATE patient_intakes 
        SET status = $1 
        WHERE id = $2
    """, status, intake_id)
    
    return {
        "intake_id": intake_id,
        "summary_text": summary_text,
        "red_flags_extracted": red_flags_extracted,
        "triage_recommendation": triage,
        "safety_attempts": attempts,
        "status": status
    }
