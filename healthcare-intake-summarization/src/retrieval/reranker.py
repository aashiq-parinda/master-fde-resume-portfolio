import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("reranker")

# Anatomical and clinical affinity clusters for deep contextual alignment
ANATOMICAL_CLUSTERS = {
    "cardiac": ["chest", "heart", "arm", "jaw", "sweat", "angina", "pulse", "palpitation"],
    "respiratory": ["breath", "breathing", "lung", "cough", "stridor", "wheeze", "cyanosis", "oxygen", "choke"],
    "gastrointestinal": ["abdomen", "abdominal", "stomach", "belly", "appendix", "quadrant", "nausea", "vomit", "bowel"],
    "neurological": ["headache", "head", "skull", "slurred", "speech", "weakness", "numb", "vision", "thunderclap", "confused"],
    "systemic_infection": ["fever", "chills", "temp", "temperature", "lethargy", "stiff", "neck", "rash", "septic"],
    "musculoskeletal": ["knee", "joint", "back", "shoulder", "muscle", "bone", "sprain", "strain", "swelling", "bend", "ache", "tennis", "soreness"]
}

class ClinicalCrossEncoderReranker:
    """
    Contextual Cross-Encoder Reranker that scores retrieved guidelines against raw patient symptoms.
    Evaluates:
    - Anatomical cluster concordance
    - Direct red-flag co-occurrence
    - Severity and acuity indicators
    - Triage risk calibration
    """

    def __init__(self):
        pass

    def _extract_tokens(self, text: str) -> set:
        return set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))

    def score_candidate(self, query: str, candidate: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Computes a calibrated cross-encoder score in [0.0, 1.0] along with explainability factors.
        """
        q_tokens = self._extract_tokens(query)
        cat_tokens = self._extract_tokens(candidate.get("symptom_category", ""))
        flags_tokens = self._extract_tokens(candidate.get("red_flags", ""))
        protocol_tokens = self._extract_tokens(candidate.get("guideline_text", ""))

        # 1. Red Flag Match (highest clinical weight)
        matched_flags = q_tokens.intersection(flags_tokens)
        flag_score = min(1.0, len(matched_flags) * 0.35)

        # 2. Category Match
        matched_cat = q_tokens.intersection(cat_tokens)
        cat_score = 1.0 if matched_cat else 0.0

        # 3. Protocol Match
        matched_proto = q_tokens.intersection(protocol_tokens)
        proto_score = min(1.0, len(matched_proto) * 0.15)

        # 4. Anatomical Cluster Alignment
        cluster_affinity = 0.0
        active_clusters = []
        for cluster, keywords in ANATOMICAL_CLUSTERS.items():
            if any(k in q_tokens for k in keywords):
                active_clusters.append(cluster)
                # Check if candidate category or red flags also touch this cluster
                if any(k in cat_tokens or k in flags_tokens for k in keywords):
                    cluster_affinity += 0.4

        cluster_affinity = min(1.0, cluster_affinity)

        # 5. Triage severity weighting
        triage = candidate.get("triage_level", "Routine")
        triage_weight = 1.15 if triage == "Emergency" and flag_score > 0 else 1.0

        # Composite Cross-Encoder Relevance Score
        raw_score = (
            (0.40 * flag_score) +
            (0.25 * cat_score) +
            (0.20 * cluster_affinity) +
            (0.15 * proto_score)
        ) * triage_weight

        # Base prior from initial hybrid score (0.2 prior)
        initial_hybrid = candidate.get("hybrid_score", 0.5)
        final_score = round(min(0.99, max(0.01, 0.70 * raw_score + 0.30 * initial_hybrid)), 4)

        factors = {
            "matched_red_flags": list(matched_flags),
            "flag_score": round(flag_score, 3),
            "category_match": bool(matched_cat),
            "cluster_affinity": round(cluster_affinity, 3),
            "active_clusters": active_clusters,
            "triage_multiplier": triage_weight
        }

        return final_score, factors

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_n: int = 2) -> List[Dict[str, Any]]:
        """
        Reranks candidates and assigns cross-encoder scores and rank deltas.
        """
        reranked = []
        for initial_rank, cand in enumerate(candidates, start=1):
            c = dict(cand)
            score, factors = self.score_candidate(query, c)
            c["rerank_score"] = score
            c["rerank_factors"] = factors
            c["initial_rank"] = initial_rank
            reranked.append(c)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Calculate rank movement
        for final_rank, c in enumerate(reranked, start=1):
            c["final_rank"] = final_rank
            c["rank_delta"] = c["initial_rank"] - final_rank  # positive = promoted

        return reranked[:top_n]
