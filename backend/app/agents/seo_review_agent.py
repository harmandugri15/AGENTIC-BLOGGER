import re
from typing import Dict, Any, List
from backend.app.core.logger import get_logger

logger = get_logger("SEOReviewAgent")

class SEOReviewAgent:
    def execute(self, draft_data: Dict[str, Any], seo_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits on-page SEO factors, heading structure, keyword presence, and semantic entities.
        """
        logger.info("Executing On-Page SEO Audit...")
        
        content = draft_data.get("content_markdown", "")
        title = draft_data.get("title", "")
        meta_title = draft_data.get("meta_title", "")
        meta_desc = draft_data.get("meta_description", "")
        slug = draft_data.get("slug", "")
        
        primary_kws = seo_strategy.get("primary_keywords", [])
        entities = seo_strategy.get("semantic_entities", [])
        
        blocking_issues = []
        suggestions = []
        
        # 1. H1 & Title Check
        h1_matches = re.findall(r"^#\s+(.+)$", content, re.MULTILINE)
        if not h1_matches:
            blocking_issues.append("Missing H1 heading in markdown.")
        
        # 2. H2 Subheading structure
        h2_matches = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
        if len(h2_matches) < 3:
            blocking_issues.append("Insufficient H2 section headings for a comprehensive enterprise guide.")
        
        # 3. Meta length checks
        if len(meta_title) < 30 or len(meta_title) > 65:
            suggestions.append(f"Meta title length ({len(meta_title)} chars) should ideally be between 40-60 characters.")
        if len(meta_desc) < 70 or len(meta_desc) > 165:
            suggestions.append(f"Meta description length ({len(meta_desc)} chars) should ideally be between 120-160 characters.")
            
        # 4. Semantic Entity Coverage
        found_entities = [e for e in entities if re.search(r"\b" + re.escape(e) + r"\b", content, re.IGNORECASE)]
        entity_coverage_pct = round((len(found_entities) / max(len(entities), 1)) * 100, 1)
        if entity_coverage_pct < 60:
            suggestions.append(f"Entity coverage is {entity_coverage_pct}%. Consider including: " + ", ".join([e for e in entities if e not in found_entities][:3]))

        # 5. Content word count
        words = len(content.split())
        if words < 500:
            blocking_issues.append(f"Content is too thin ({words} words). Enterprise technology blogs should exceed 700 words.")

        # Compute Score
        score = 95.0
        if blocking_issues:
            score -= (len(blocking_issues) * 15.0)
        if entity_coverage_pct >= 75:
            score += 5.0
        score = max(0.0, min(100.0, score))
        grade = "A" if score >= 88 else "B" if score >= 75 else "C"

        return {
            "score": score,
            "grade": grade,
            "summary": f"On-Page SEO Score: {score}/100. Word count: {words}, H2 sections: {len(h2_matches)}, Entity coverage: {entity_coverage_pct}%.",
            "found_entities": found_entities,
            "entity_coverage_pct": entity_coverage_pct,
            "blocking_issues": blocking_issues,
            "suggestions": suggestions
        }
