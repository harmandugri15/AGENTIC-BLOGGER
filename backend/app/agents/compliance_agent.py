import re
from typing import Dict, Any, List
from backend.app.core.logger import get_logger

logger = get_logger("ComplianceAgent")

class ComplianceAgent:
    def execute(self, draft_markdown: str, brand_tone: str) -> Dict[str, Any]:
        """
        Audits healthcare regulatory disclaimers, HIPAA protection, clinical liability,
        and CitiusTech positioning integrity.
        """
        logger.info("Auditing healthcare compliance, clinical safety, and brand alignment...")
        
        blocking_issues = []
        suggestions = []
        
        # 1. Check for clinical liability / absolute diagnostic promises
        dangerous_claims = re.findall(
            r"\b(guarantees? diagnostic|100% cure|replaces? (the )?physician|eliminates? all medical errors)\b",
            draft_markdown,
            re.IGNORECASE
        )
        if dangerous_claims:
            blocking_issues.append("Found dangerous clinical guarantee: AI cannot claim to 100% diagnose or replace licensed medical judgment.")

        # 2. Check for Clinician-in-the-Loop safeguard mention
        has_citl = bool(re.search(r"\b(clinician-in-the-loop|physician oversight|human-in-the-loop|review state)\b", draft_markdown, re.IGNORECASE))
        if not has_citl:
            blocking_issues.append("Missing essential clinical safeguard: Enterprise healthcare AI must emphasize clinician-in-the-loop validation.")

        # 3. Check for privacy / HIPAA / PHI security awareness
        has_hipaa = bool(re.search(r"\b(hipaa|phi|data privacy|safe harbor|de-identification)\b", draft_markdown, re.IGNORECASE))
        if not has_hipaa:
            suggestions.append("Consider explicitly mentioning HIPAA Safe Harbor or PHI de-identification protocols in the interoperability section.")

        # 4. Brand Positioning
        has_brand = bool(re.search(r"\bcitiustech\b", draft_markdown, re.IGNORECASE))
        if not has_brand:
            suggestions.append("Draft should naturally weave in CitiusTech's authoritative positioning in healthcare interoperability and engineering.")

        # Score calculation
        score = 98.0
        if blocking_issues:
            score -= (len(blocking_issues) * 25.0)
        score = max(0.0, min(100.0, score))
        grade = "A+" if score >= 95 else "B" if score >= 80 else "F"

        return {
            "score": score,
            "grade": grade,
            "summary": f"Compliance Score: {score}/100. Clinician-in-the-Loop confirmed: {has_citl}. HIPAA/PHI addressed: {has_hipaa}.",
            "clinician_in_the_loop_present": has_citl,
            "hipaa_addressed": has_hipaa,
            "blocking_issues": blocking_issues,
            "suggestions": suggestions
        }
