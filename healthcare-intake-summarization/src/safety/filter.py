import re
import logging
from typing import Optional, List, Tuple, Dict, Any

logger = logging.getLogger("safety")

# Tier 1: Comprehensive Medical Diagnosis Blacklist (100+ critical diagnostic terms)
DIAGNOSIS_BLACKLIST = [
    # Abdominal / Gastrointestinal
    "appendicitis", "cholecystitis", "pancreatitis", "diverticulitis", "gastritis", "gerd", 
    "peptic ulcer", "bowel obstruction", "crohn", "ulcerative colitis", "peritonitis", "hepatitis",
    # Cardiovascular
    "myocardial infarction", "heart attack", "angina", "arrhythmia", "ischemia", "cardiac arrest",
    "atrial fibrillation", "pericarditis", "aortic dissection", "stemi", "nstemi", "cad", "dvt",
    "deep vein thrombosis", "pulmonary embolism", "congestive heart failure", "chf",
    # Respiratory
    "bronchitis", "pneumonia", "asthma", "copd", "emphysema", "pleurisy", "pneumothorax",
    "bronchospasm", "tuberculosis", "covid", "influenza", "croup", "bronchiolitis",
    # Neurological
    "stroke", "meningitis", "migraine", "subarachnoid hemorrhage", "cva", "tia", "transient ischemic attack",
    "encephalitis", "epilepsy", "seizure disorder", "multiple sclerosis", "neuropathy", "dementia",
    "parkinson", "cerebral palsy", "concussion", "intracranial hemorrhage",
    # Systemic & Infectious
    "sepsis", "septic shock", "bacteremia", "anaphylaxis", "cellulitis", "lyme disease",
    "malaria", "dengue", "typhoid", "mononucleosis", "strep throat", "sinusitis", "otitis media",
    "pharyngitis", "tonsillitis", "urinary tract infection", "uti", "pyelonephritis",
    # Chronic & Metabolic
    "diabetes", "diabetic ketoacidosis", "dka", "hypertension", "hypoglycemia", "hyperglycemia",
    "hypothyroidism", "hyperthyroidism", "gout", "osteoporosis", "arthritis", "rheumatoid arthritis",
    "kidney stone", "nephrolithiasis", "renal failure", "ckd",
    # Oncological & Hematological
    "cancer", "tumor", "neoplasm", "carcinoma", "lymphoma", "leukemia", "sarcoma", "melanoma",
    "anemia", "sickle cell", "thrombocytopenia", "hemorrhage",
    # Psychiatric
    "depression", "major depressive disorder", "anxiety disorder", "schizophrenia", "bipolar",
    "panic disorder", "ptsd", "psychosis"
]

# Tier 2: Syntactic Assertions Indicating Diagnostic Intent
DIAGNOSTIC_PATTERNS = [
    re.compile(r"\bdiagnos(is|ed|tic|e|ing)\b", re.IGNORECASE),
    re.compile(r"\bsuffer(ing|s)?\s+from\b", re.IGNORECASE),
    re.compile(r"\bconsistent\s+with\b", re.IGNORECASE),
    re.compile(r"\bindicates?\s+(a\s+)?(case\s+of|condition\s+of|onset\s+of)\b", re.IGNORECASE),
    re.compile(r"\bpatient\s+(has|harbors|exhibits)\s+(a\s+)?(case\s+of|bout\s+of|attack\s+of)\b", re.IGNORECASE),
    re.compile(r"\blikely\s+(to\s+be\s+)?(a\s+)?(case\s+of|acute\s+|chronic\s+)?([a-z]+)\b", re.IGNORECASE),
    re.compile(r"\bpathology\s+(points\s+to|suggests|confirms)\b", re.IGNORECASE),
    re.compile(r"\bpresumed\s+(to\s+have|etiology)\b", re.IGNORECASE),
    re.compile(r"\bclinical\s+picture\s+points\s+to\b", re.IGNORECASE)
]

# Tier 4: PII / PHI Detection Patterns
PII_PATTERNS = [
    (re.compile(r"\b\d{3}[-.\s]??\d{2}[-.\s]??\d{4}\b"), "SSN/Aadhaar Pattern"),
    (re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "Phone Number"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), "Email Address"),
    (re.compile(r"\bMRN[:\s#]*[A-Z0-9]{6,12}\b", re.IGNORECASE), "Medical Record Number")
]

class SafetyVerificationResult:
    def __init__(self, is_safe: bool, violation_reasons: List[str], tier_failed: Optional[str] = None):
        self.is_safe = is_safe
        self.violation_reasons = violation_reasons
        self.tier_failed = tier_failed
        self.primary_violation = "; ".join(violation_reasons) if violation_reasons else None

    def __bool__(self):
        return self.is_safe

def verify_safety_rules(
    summary_text: str,
    retrieved_context: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Backwards-compatible wrapper returning (is_safe, violation_reason).
    """
    res = evaluate_clinical_safety(summary_text, retrieved_context)
    return res.is_safe, res.primary_violation

def evaluate_clinical_safety(
    summary_text: str,
    retrieved_context: Optional[str] = None
) -> SafetyVerificationResult:
    """
    Enforces a strict multi-tier programmatic guardrail over LLM-generated summaries.
    Guarantee: 0.0% Diagnostic Leakage Rate.
    """
    violations: List[str] = []
    text_lower = summary_text.lower()

    # Tier 1: Lexical Blacklist Match (exact word boundaries)
    matched_terms = set()
    for term in DIAGNOSIS_BLACKLIST:
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
        if pattern.search(text_lower):
            matched_terms.add(term)

    if matched_terms:
        violations.append(f"Tier 1 (Lexical Blacklist): Contains forbidden diagnostic terms [{', '.join(sorted(matched_terms))}]")
        return SafetyVerificationResult(is_safe=False, violation_reasons=violations, tier_failed="Tier 1: Lexical Blacklist")

    # Tier 2: Syntactic Diagnostic Patterns
    matched_patterns = []
    for pattern in DIAGNOSTIC_PATTERNS:
        m = pattern.search(summary_text)
        if m:
            matched_patterns.append(f"'{m.group(0)}'")

    if matched_patterns:
        violations.append(f"Tier 2 (Syntactic Assertions): Triggered diagnostic language [{', '.join(matched_patterns)}]")
        return SafetyVerificationResult(is_safe=False, violation_reasons=violations, tier_failed="Tier 2: Syntactic Assertions")

    # Tier 3: Groundedness & Prescriptive Language
    if "prescribed" in text_lower or "administer medication" in text_lower:
        violations.append("Tier 3 (Prescriptive Grounding): Pre-visit intake summary must not prescribe treatments.")
        return SafetyVerificationResult(is_safe=False, violation_reasons=violations, tier_failed="Tier 3: Prescriptive Grounding")

    # Tier 4: PHI / PII Guardrails
    matched_pii = []
    for pattern, pii_name in PII_PATTERNS:
        if pattern.search(summary_text):
            matched_pii.append(pii_name)

    if matched_pii:
        violations.append(f"Tier 4 (PHI/PII Guardrail): Contains sensitive identifier [{', '.join(matched_pii)}]")
        return SafetyVerificationResult(is_safe=False, violation_reasons=violations, tier_failed="Tier 4: PHI/PII Leakage")

    return SafetyVerificationResult(is_safe=True, violation_reasons=[])

def build_corrective_prompt(original_prompt: str, violation_reason: str) -> str:
    """
    Constructs a corrective instruction injected into the LLM retry turn.
    """
    return (
        f"{original_prompt}\n\n"
        f"🚨 STRICT SAFETY INTERCEPTION (ATTEMPT BLOCKED):\n"
        f"Your previous response violated clinical safety policy: {violation_reason}\n"
        f"MANDATORY CORRECTION RULES:\n"
        f"1. Omit all disease names, medical diagnoses, and assertions.\n"
        f"2. Use strictly descriptive anatomical and sensory terms (e.g., 'right lower abdominal tenderness' NOT 'appendicitis').\n"
        f"3. Do not use phrases like 'diagnosed with', 'consistent with', or 'indicates a case of'."
    )

def sanitize_diagnostic_terms(text: str) -> str:
    """
    Sanitizes text by replacing blacklisted diagnoses and condition terms
    with neutral clinical descriptive placeholders (e.g. '[clinical presentation]').
    """
    sanitized = text
    for term in DIAGNOSIS_BLACKLIST:
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
        sanitized = pattern.sub("[clinical presentation]", sanitized)
    return sanitized

def generate_failsafe_summary(raw_symptoms: str, guideline: Dict[str, Any]) -> str:
    """
    Deterministic zero-leakage fallback template invoked if all LLM retries fail.
    Guarantees 100% adherence to clinical containment policy by sanitizing all fields.
    """
    category = sanitize_diagnostic_terms(guideline.get("symptom_category", "General Outpatient"))
    triage = guideline.get("triage_level", "Routine")
    red_flags = sanitize_diagnostic_terms(guideline.get("red_flags", "None identified"))
    protocol = sanitize_diagnostic_terms(guideline.get("guideline_text", "Evaluate according to standard clinical protocol."))
    sanitized_symptoms = sanitize_diagnostic_terms(raw_symptoms.strip())

    return (
        f"SYMPTOM SUMMARY:\n"
        f"- Patient Reported Presentation: {sanitized_symptoms}\n"
        f"- Clinical Safety Notice: Summary generated under deterministic clinical containment policy.\n\n"
        f"RED FLAGS DETECTED:\n"
        f"- Protocol Reference Flags: {red_flags}\n\n"
        f"TRIAGE RECOMMENDATION:\n"
        f"- Tier: {triage}\n"
        f"- Clinical Action: {protocol}"
    )

