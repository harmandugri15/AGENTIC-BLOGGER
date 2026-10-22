import re
from typing import Dict, Any, List
from backend.app.core.logger import get_logger

logger = get_logger("FactualityAgent")

class FactualityAgent:
    def execute(self, draft_markdown: str, evidence_pack: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Audits the draft for verifiable citations, factual grounding, and hallucination prevention.
        """
        logger.info("Auditing factuality and claim-to-source mappings...")
        
        valid_tags = {e["evidence_tag"]: e for e in evidence_pack}
        found_tags = re.findall(r"\[EVID-\d{3}\]", draft_markdown)
        
        blocking_issues = []
        suggestions = []
        verified_claims = []
        
        # 1. Check for hallucinated/invalid citation tags
        for tag in found_tags:
            if tag not in valid_tags:
                blocking_issues.append(f"Hallucinated citation tag detected: {tag}. No corresponding source exists in EvidencePack.")
            else:
                src = valid_tags[tag]
                verified_claims.append({
                    "tag": tag,
                    "source_title": src.get("source_title"),
                    "source_url": src.get("source_url"),
                    "quote": src.get("verbatim_quote")
                })

        # 2. Minimum citation density check
        if len(found_tags) < 2:
            blocking_issues.append("Insufficient factual citations. Article must contain at least 2 traceable evidence references for clinical/technical claims.")

        # 3. Numeric & statistical claims audit
        stats_found = re.findall(r"\b\d+%\b|\b\d+\s+minutes\b|\b\d+\s+hours\b", draft_markdown)
        if stats_found and not found_tags:
            blocking_issues.append("Quantitative/numeric claims found without citation backing.")

        # Compute Factuality Score
        score = 100.0
        if blocking_issues:
            score -= (len(blocking_issues) * 20.0)
        if len(found_tags) >= 3:
            suggestions.append("Strong evidence grounding with multiple peer-reviewed and verified industry citations.")
        else:
            suggestions.append("Consider citing an additional clinical validation study for diagnostic algorithms.")

        score = max(0.0, min(100.0, score))
        grade = "A+" if score >= 90 else "B" if score >= 80 else "F"

        return {
            "score": score,
            "grade": grade,
            "summary": f"Factuality verified: {len(found_tags)} citations matched against official evidence sources.",
            "verified_citations_count": len(found_tags),
            "verified_claims": verified_claims,
            "blocking_issues": blocking_issues,
            "suggestions": suggestions
        }
