import pytest
from src.safety.filter import verify_safety_rules

def test_safety_filter_safe_input():
    # purely descriptive inputs should pass
    text = (
        "SYMPTOM SUMMARY:\n"
        "- Patient reports localized right lower abdominal pain.\n"
        "- Pain is sharp and has been present for 12 hours.\n"
        "- Patient reports mild nausea but no vomiting.\n"
        "Triage Level: Urgent."
    )
    is_safe, reason = verify_safety_rules(text)
    assert is_safe is True
    assert reason is None

def test_safety_filter_blacklist_violation():
    # Contains a blacklisted term: "appendicitis"
    text = (
        "SUMMARY:\n"
        "The patient presents with severe right lower quadrant abdominal pain, "
        "strongly suggesting acute appendicitis."
    )
    is_safe, reason = verify_safety_rules(text)
    assert is_safe is False
    assert "appendicitis" in reason.lower()

def test_safety_filter_syntactic_pattern_violation():
    # Contains a syntactic assertion: "diagnosed with"
    text = (
        "SUMMARY:\n"
        "Patient complains of throbbing headache. They were diagnosed with migraines "
        "last year and reports similar symptoms today."
    )
    is_safe, reason = verify_safety_rules(text)
    # Note: "migraines" matches migraine in blacklist, and "diagnosed with" matches syntactic rules
    assert is_safe is False
    assert "diagnostic" in reason.lower() or "blacklist" in reason.lower()

def test_safety_filter_case_insensitivity():
    # Blacklisted word in uppercase: "SEPSIS"
    text = "The patient presents with symptoms indicating SEPSIS."
    is_safe, reason = verify_safety_rules(text)
    assert is_safe is False
    assert "sepsis" in reason.lower()
