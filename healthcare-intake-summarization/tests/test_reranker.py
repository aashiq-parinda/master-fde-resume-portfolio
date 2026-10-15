import pytest
from src.retrieval.reranker import ClinicalCrossEncoderReranker
from src.summarizer.engine import get_guidelines_corpus

def test_reranker_scores_and_promotes_relevant():
    reranker = ClinicalCrossEncoderReranker()
    candidates = get_guidelines_corpus()[:3]
    
    query = "Rebound tenderness in the lower right stomach with severe nausea"
    reranked = reranker.rerank(query, candidates, top_n=2)
    
    assert len(reranked) == 2
    # Abdominal Pain should be ranked #1
    assert reranked[0]["symptom_category"] == "Abdominal Pain"
    assert "rerank_score" in reranked[0]
    assert reranked[0]["rerank_score"] > 0.4
    assert "rerank_factors" in reranked[0]
