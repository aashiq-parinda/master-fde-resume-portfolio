import math
import re
import logging
from typing import List, Dict, Any, Tuple
from src.retrieval.embeddings import generate_dense_embedding, cosine_similarity

logger = logging.getLogger("hybrid_retrieval")

def compute_sparse_bm25_score(query: str, document_text: str, k1: float = 1.5, b: float = 0.75, avg_doc_len: float = 40.0) -> float:
    """
    Computes BM25-style lexical relevance between query and guideline text.
    """
    query_tokens = re.findall(r"\b[a-zA-Z]{3,}\b", query.lower())
    doc_tokens = re.findall(r"\b[a-zA-Z]{3,}\b", document_text.lower())
    
    if not query_tokens or not doc_tokens:
        return 0.0

    doc_len = len(doc_tokens)
    doc_freqs: Dict[str, int] = {}
    for t in doc_tokens:
        doc_freqs[t] = doc_freqs.get(t, 0) + 1

    score = 0.0
    for q in query_tokens:
        if q in doc_freqs:
            tf = doc_freqs[q]
            # Term weight factor
            num = tf * (k1 + 1.0)
            den = tf + k1 * (1.0 - b + b * (doc_len / avg_doc_len))
            # IDF proxy weight
            score += (num / den) * 1.5
            
    return score

def reciprocal_rank_fusion(dense_ranked: List[Dict[str, Any]], sparse_ranked: List[Dict[str, Any]], k: int = 60) -> List[Dict[str, Any]]:
    """
    Combines dense and sparse ranked lists using Reciprocal Rank Fusion (RRF).
    Formula: RRF_Score(d) = sum(1 / (k + rank_i))
    """
    scores: Dict[int, float] = {}
    guideline_map: Dict[int, Dict[str, Any]] = {}
    dense_ranks: Dict[int, int] = {}
    sparse_ranks: Dict[int, int] = {}

    dense_scores: Dict[int, float] = {item["id"]: item.get("dense_score", 0.0) for item in dense_ranked}
    sparse_scores: Dict[int, float] = {item["id"]: item.get("sparse_score", 0.0) for item in sparse_ranked}

    for rank, item in enumerate(dense_ranked, start=1):
        gid = item["id"]
        guideline_map[gid] = item
        dense_ranks[gid] = rank
        scores[gid] = scores.get(gid, 0.0) + (1.0 / (k + rank))

    for rank, item in enumerate(sparse_ranked, start=1):
        gid = item["id"]
        guideline_map[gid] = item
        sparse_ranks[gid] = rank
        scores[gid] = scores.get(gid, 0.0) + (1.0 / (k + rank))

    fused = []
    for gid, rrf_score in scores.items():
        doc = dict(guideline_map[gid])
        doc["rrf_score"] = round(rrf_score, 5)
        doc["dense_rank"] = dense_ranks.get(gid, 999)
        doc["sparse_rank"] = sparse_ranks.get(gid, 999)
        doc["dense_score"] = dense_scores.get(gid, 0.0)
        doc["sparse_score"] = sparse_scores.get(gid, 0.0)
        fused.append(doc)

    fused.sort(key=lambda x: x["rrf_score"], reverse=True)
    return fused

class HybridRetriever:
    """
    State-of-the-art Hybrid Retriever uniting:
    1. Sparse Lexical Search (BM25 token frequency & clinical red-flag matching)
    2. Dense Semantic Search (Clinical vector embeddings & cosine similarity)
    3. Reciprocal Rank Fusion (RRF) for optimal calibration.
    """

    def __init__(self, guidelines_corpus: List[Dict[str, Any]]):
        self.corpus = guidelines_corpus
        self._precompute_embeddings()

    def _precompute_embeddings(self):
        for g in self.corpus:
            doc_text = f"{g['symptom_category']} - Red Flags: {g['red_flags']} - Protocol: {g['guideline_text']}"
            g["_doc_text"] = doc_text
            g["_embedding"] = generate_dense_embedding(doc_text)

    def retrieve(self, query: str, top_k: int = 3, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """
        Executes hybrid search across the clinical guidelines corpus.
        Returns candidates scored by dense, sparse, and fused metrics.
        """
        query_embedding = generate_dense_embedding(query)

        # 1. Dense retrieval
        dense_candidates = []
        for g in self.corpus:
            sim = cosine_similarity(query_embedding, g["_embedding"])
            candidate = dict(g)
            candidate["dense_score"] = round(float(sim), 4)
            dense_candidates.append(candidate)
        dense_candidates.sort(key=lambda x: x["dense_score"], reverse=True)

        # 2. Sparse retrieval
        sparse_candidates = []
        for g in self.corpus:
            score = compute_sparse_bm25_score(query, g["_doc_text"])
            candidate = dict(g)
            candidate["sparse_score"] = round(float(score), 4)
            sparse_candidates.append(candidate)
        sparse_candidates.sort(key=lambda x: x["sparse_score"], reverse=True)

        # 3. Reciprocal Rank Fusion
        fused = reciprocal_rank_fusion(dense_candidates, sparse_candidates, k=60)
        
        # Add composite hybrid score for explainability
        for item in fused:
            dense_s = item.get("dense_score", 0.0)
            sparse_s = item.get("sparse_score", 0.0)
            # Normalize sparse roughly into [0, 1] for composite display
            norm_sparse = min(1.0, sparse_s / 5.0) if sparse_s > 0 else 0.0
            item["hybrid_score"] = round(alpha * dense_s + (1.0 - alpha) * norm_sparse, 4)

        return fused[:top_k]
