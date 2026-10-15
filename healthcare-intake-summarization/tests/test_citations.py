import pytest
from src.summarizer.citations import CitationEngine
from src.summarizer.engine import get_guidelines_corpus

def test_citations_grounding_and_provenance():
    engine = CitationEngine()
    guidelines = get_guidelines_corpus()[:2]
    
    summary = (
        "SYMPTOM SUMMARY:\n"
        "- Patient reports radiating chest pressure and left arm discomfort.\n"
        "- Shortness of breath noted upon mild exertion.\n"
        "TRIAGE RECOMMENDATION:\n"
        "- Tier: Emergency\n"
        "- Action: Refer to nearest cardiac emergency facility."
    )
    
    annotated, citations, groundedness = engine.ground_and_cite_summary(summary, guidelines)
    assert len(citations) > 0
    assert "[^1]" in annotated
    assert "REFERENCES & CLINICAL PROVENANCE" in annotated
    assert groundedness > 0.5
