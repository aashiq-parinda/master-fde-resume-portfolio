import re
from typing import List, Dict, Any, Tuple
import logging
from src.safety.filter import sanitize_diagnostic_terms

logger = logging.getLogger("citations")

class CitationEngine:
    """
    Constructs and verifies grounded citations mapping generated pre-visit summary
    bullet points back to specific retrieved clinical guideline protocols.
    """

    def __init__(self):
        pass

    def ground_and_cite_summary(
        self,
        summary_text: str,
        retrieved_guidelines: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]], float]:
        """
        Parses summary sections, maps claims to retrieved guidelines,
        appends inline citation tags [^1], [^2], builds a structured provenance table,
        and computes a groundedness confidence score.
        """
        citations: List[Dict[str, Any]] = []
        if not retrieved_guidelines:
            return summary_text, citations, 1.0

        # Create lookup chunks from guidelines
        guideline_chunks = []
        for idx, g in enumerate(retrieved_guidelines, start=1):
            guideline_chunks.append({
                "ref_id": idx,
                "guideline_id": g.get("id", idx),
                "category": g.get("symptom_category", "General"),
                "triage": g.get("triage_level", "Routine"),
                "red_flags": g.get("red_flags", ""),
                "protocol": g.get("guideline_text", "")
            })

        lines = summary_text.split("\n")
        annotated_lines = []
        total_claims = 0
        grounded_claims = 0

        for line in lines:
            trimmed = line.strip()
            # If line is a clinical statement or bullet
            if trimmed.startswith(("-", "•", "1.", "2.", "3.", "Rationale:", "Tier:", "Action:")):
                total_claims += 1
                matched_ref = None
                best_overlap = 0

                # Match against guideline chunks
                line_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", trimmed.lower()))
                for chunk in guideline_chunks:
                    ref_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", f"{chunk['category']} {chunk['red_flags']} {chunk['protocol']}".lower()))
                    overlap = len(line_tokens.intersection(ref_tokens))
                    if overlap > best_overlap:
                        best_overlap = overlap
                        matched_ref = chunk

                if matched_ref and best_overlap >= 1:
                    ref_num = matched_ref["ref_id"]
                    annotated_line = f"{line} [^{ref_num}]"
                    annotated_lines.append(annotated_line)
                    grounded_claims += 1

                    # Check if already added to citations
                    existing = next((c for c in citations if c["ref_num"] == ref_num), None)
                    if not existing:
                        citations.append({
                            "ref_num": ref_num,
                            "guideline_id": matched_ref["guideline_id"],
                            "category": matched_ref["category"],
                            "triage_level": matched_ref["triage"],
                            "source_excerpt": matched_ref["protocol"],
                            "matched_red_flags": matched_ref["red_flags"],
                            "confidence_score": round(min(0.99, 0.65 + (best_overlap * 0.08)), 3)
                        })
                else:
                    annotated_lines.append(line)
            else:
                annotated_lines.append(line)

        annotated_summary = "\n".join(annotated_lines)

        # Append structured Reference Section to summary
        if citations:
            annotated_summary += "\n\nREFERENCES & CLINICAL PROVENANCE:\n"
            for c in citations:
                clean_cat = sanitize_diagnostic_terms(c['category'])
                clean_excerpt = sanitize_diagnostic_terms(c['source_excerpt'])
                annotated_summary += f"[^{c['ref_num']}] Guideline #{c['guideline_id']} ({clean_cat} - {c['triage_level']}): \"{clean_excerpt}\"\n"

        groundedness_score = round(grounded_claims / max(1, total_claims), 3) if total_claims > 0 else 1.0

        return annotated_summary, citations, groundedness_score
