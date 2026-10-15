import pytest
from src.retrieval.hybrid import HybridRetriever, compute_sparse_bm25_score, reciprocal_rank_fusion
from src.retrieval.embeddings import generate_dense_embedding, cosine_similarity
from src.summarizer.engine import get_guidelines_corpus

def test_dense_embeddings_shape_and_normalization():
    vec = generate_dense_embedding("Patient reports crushing chest pain and shortness of breath", dim=64)
    assert len(vec) == 64
    norm = sum(x**2 for x in vec)**0.5
    assert abs(norm - 1.0) < 1e-4

def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert abs(cosine_similarity(v1, v2) - 1.0) < 1e-5
    assert abs(cosine_similarity(v1, v3) - 0.0) < 1e-5

def test_sparse_bm25_score():
    score = compute_sparse_bm25_score("chest pain arm numbness", "Chest Pain - radiating chest pressure left arm jaw pain")
    assert score > 0.0

def test_hybrid_retriever_ranking():
    corpus = get_guidelines_corpus()
    retriever = HybridRetriever(corpus)
    
    # Query matching cardiac
    results = retriever.retrieve("Severe pressure on my chest and numbness down left arm", top_k=2)
    assert len(results) == 2
    assert results[0]["symptom_category"] == "Chest Pain"
    assert "dense_score" in results[0]
    assert "sparse_score" in results[0]
    assert "rrf_score" in results[0]
