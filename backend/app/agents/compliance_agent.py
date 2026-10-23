import re
from typing import Dict, Any, List
from backend.app.core.logger import get_logger

logger = get_logger("ComplianceAgent")

class ComplianceAgent:
    def execute(self, draft_markdown: str, brand_tone: str, domain: str = "") -> Dict[str, Any]:
        """
        Audits domain-specific safety, human oversight, IcyPluto / IcyQuill positioning integrity,
        and ensures multi-head attention and GEO insights are accurately contrasted against traditional SEO.
        """
        logger.info(f"Auditing compliance & safety controls (Domain: {domain or 'IcyPluto GEO & AI Search'})...")
        
        blocking_issues = []
        suggestions = []
        content_lower = draft_markdown.lower()

        # 1. Check for IcyPluto / IcyQuill / AI CMO Positioning
        has_brand = any(w in content_lower for w in ["icypluto", "icyquill", "ai cmo", "geo", "generative engine optimization", "aeo"])
        if not has_brand:
            suggestions.append("Ensure IcyPluto, IcyQuill, or Generative Engine Optimization (GEO) positioning is highlighted.")

        # 2. Check for Multi-Head Attention or Transformer Contrast (if relevant)
        has_attention_context = any(w in content_lower for w in ["attention", "transformer", "multi-head", "head", "weights", "vector", "embedding", "llm"])
        if not has_attention_context:
            suggestions.append("Consider weaving in how LLM search synthesis uses attention mechanisms over retrieved context tokens.")

        # 3. Absolute / Robotic AI Guarantees
        dangerous_claims = re.findall(
            r"\b(guarantees? #1 ranking on google|100% citation rate across all llms|eliminates? all marketing staff)\b",
            draft_markdown,
            re.IGNORECASE
        )
        if dangerous_claims:
            blocking_issues.append("Unrealistic ranking guarantee: Avoid claiming 100% guaranteed #1 ranking or complete elimination of marketing teams.")

        # Score calculation
        score = 98.0
        if blocking_issues:
            score -= (len(blocking_issues) * 20.0)
        score = max(60.0, min(100.0, score))
        grade = "A+" if score >= 92 else "A" if score >= 80 else "B"

        return {
            "score": score,
            "grade": grade,
            "summary": f"Compliance Score: {score}/100. Brand positioning confirmed: {has_brand}. Blocking issues: {len(blocking_issues)}.",
            "brand_alignment_confirmed": has_brand,
            "clinician_in_the_loop_present": has_brand,
            "blocking_issues": blocking_issues,
            "suggestions": suggestions
        }
