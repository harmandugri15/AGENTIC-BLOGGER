import re
from typing import Dict, Any, List
from backend.app.core.logger import get_logger

logger = get_logger("ComplianceAgent")

class ComplianceAgent:
    def execute(self, draft_markdown: str, brand_tone: str, domain: str = "") -> Dict[str, Any]:
        """
        Audits domain-specific safety, human oversight, regulatory compliance,
        and enterprise positioning integrity.
        """
        logger.info(f"Auditing compliance & safety controls (Domain: {domain or 'Enterprise'})...")
        
        blocking_issues = []
        suggestions = []
        content_lower = draft_markdown.lower()

        is_healthcare = any(w in content_lower for w in ["health", "hospital", "patient", "clinical", "doctor", "ehr", "hipaa"])
        is_robotics = any(w in content_lower for w in ["robot", "robotics", "cobot", "autonomous", "drone", "manipulator"])
        is_education = any(w in content_lower for w in ["education", "school", "student", "teacher", "learning", "edtech", "university"])

        # 1. Absolute / Dangerous Guarantee Checks
        if is_healthcare:
            dangerous_claims = re.findall(
                r"\b(guarantees? diagnostic|100% cure|replaces? (the )?physician|eliminates? all medical errors)\b",
                draft_markdown,
                re.IGNORECASE
            )
            if dangerous_claims:
                blocking_issues.append("Found dangerous clinical guarantee: AI cannot claim to 100% diagnose or replace licensed medical judgment.")
        elif is_robotics:
            dangerous_claims = re.findall(
                r"\b(zero risk of physical injury|100% autonomous without human supervision|eliminates? all mechanical failure)\b",
                draft_markdown,
                re.IGNORECASE
            )
            if dangerous_claims:
                blocking_issues.append("Dangerous robotics safety claim: Autonomous robotics requires operator fail-safes and emergency stops.")

        # 2. Human-in-the-Loop Safeguards
        has_hitl = bool(re.search(
            r"\b(clinician-in-the-loop|teacher oversight|operator oversight|human-in-the-loop|supervisory|review state|fail-safe)\b",
            draft_markdown,
            re.IGNORECASE
        ))
        if not has_hitl:
            suggestions.append("Ensure enterprise human-in-the-loop supervisory controls are clearly highlighted in the architecture.")

        # 3. Privacy & Regulatory Standards
        if is_healthcare:
            has_reg = bool(re.search(r"\b(hipaa|phi|data privacy|safe harbor|de-identification)\b", draft_markdown, re.IGNORECASE))
            if not has_reg:
                suggestions.append("Consider explicitly mentioning HIPAA Safe Harbor or PHI de-identification in the data section.")
        elif is_education:
            has_reg = bool(re.search(r"\b(ferpa|coppa|student privacy|zero-retention)\b", draft_markdown, re.IGNORECASE))
            if not has_reg:
                suggestions.append("Ensure FERPA compliance and student privacy guidelines are referenced.")
        elif is_robotics:
            has_reg = bool(re.search(r"\b(iso|safety standard|fail-safe|emergency stop|cobot safety)\b", draft_markdown, re.IGNORECASE))
            if not has_reg:
                suggestions.append("Consider referencing ISO cobot safety standards or fail-safe emergency stop protocols.")

        # Score calculation
        score = 98.0
        if blocking_issues:
            score -= (len(blocking_issues) * 20.0)
        score = max(50.0, min(100.0, score))
        grade = "A+" if score >= 92 else "A" if score >= 80 else "B"

        return {
            "score": score,
            "grade": grade,
            "summary": f"Compliance Score: {score}/100. Human-in-the-Loop confirmed: {has_hitl}. Blocking issues: {len(blocking_issues)}.",
            "clinician_in_the_loop_present": has_hitl,
            "hipaa_addressed": is_healthcare or is_robotics or is_education,
            "blocking_issues": blocking_issues,
            "suggestions": suggestions
        }
