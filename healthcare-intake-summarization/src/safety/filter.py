import re
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger("safety")

# Medical Diagnosis Blacklist (common diagnostic names that the system must never output)
DIAGNOSIS_BLACKLIST = [
    "appendicitis", "bronchitis", "meningitis", "sepsis", "stroke", "migraine", 
    "myocardial infarction", "pneumonia", "asthma", "anaphylaxis",
    "covid", "influenza", "fracture", "diabetes", "hypertension", "angina",
    "cholecystitis", "embolism", "thrombosis", "hemorrhage", "heart attack",
    "ulcer", "gastritis", "gerd", "cancer", "tumor", "appendectomy",
    "tuberculosis", "copd", "arrhythmia", "ischemia", "hernia", "pancreatitis",
    "otitis", "sinusitis", "pharyngitis", "tonsillitis", "bronchospasm", "dementia",
    "depression", "anxiety", "schizophrenia", "arthritis", "gout", "osteoporosis"
]

# Syntactic patterns indicating diagnostic assertions
DIAGNOSTIC_PATTERNS = [
    re.compile(r"\bdiagnos(is|ed|tic|e)\b", re.IGNORECASE),
    re.compile(r"\bsuffer(ing|s)?\s+from\b", re.IGNORECASE),
    re.compile(r"\bconsistent\s+with\b", re.IGNORECASE),
    re.compile(r"\bindicates?\s+(a\s+)?(case\s+of|condition\s+of)\b", re.IGNORECASE),
    re.compile(r"\bpatient\s+has\s+(a\s+)?(case\s+of|bout\s+of|attack\s+of)\b", re.IGNORECASE),
    re.compile(r"\blikely\s+(to\s+be\s+)?(appendicitis|pneumonia|meningitis|stroke|sepsis)\b", re.IGNORECASE)
]

def verify_safety_rules(summary_text: str) -> Tuple[bool, Optional[str]]:
    """
    Enforces a strict programmatic guardrail over the LLM output text.
    Returns:
        (is_safe: bool, violation_reason: Optional[str])
    """
    text_lower = summary_text.lower()

    # 1. Lexical Blacklist Match (word-by-word matching with boundaries)
    matched_blacklist = []
    for term in DIAGNOSIS_BLACKLIST:
        pattern = re.compile(rf"\b{term}\b", re.IGNORECASE)
        if pattern.search(text_lower):
            matched_blacklist.append(term)
            
    if matched_blacklist:
        violation = f"Contains blacklisted diagnostic terms: {', '.join(matched_blacklist)}"
        logger.warning(f"Safety Violation: {violation}")
        return False, violation

    # 2. Syntactic Pattern Match (diagnosed with, suffering from, etc.)
    for idx, pattern in enumerate(DIAGNOSTIC_PATTERNS):
        match = pattern.search(summary_text)
        if match:
            violation = f"Triggered diagnostic syntactic pattern match: '{match.group(0)}'"
            logger.warning(f"Safety Violation: {violation}")
            return False, violation

    # 3. Groundedness validation checks
    # E.g. ensuring summary doesn't contain diagnostic-sounding claims like "disease" or "illness"
    if "patient is suffering from" in text_lower or "has the disease" in text_lower:
        return False, "Contains diagnostic groundedness violation."

    return True, None
