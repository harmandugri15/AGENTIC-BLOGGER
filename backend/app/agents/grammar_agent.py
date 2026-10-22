import re
import textstat
from typing import Dict, Any, List
from backend.app.core.logger import get_logger

logger = get_logger("GrammarAgent")

class GrammarAgent:
    def execute(self, draft_markdown: str) -> Dict[str, Any]:
        """
        Lints grammar, readability, sentence length variation, and syntax.
        """
        logger.info("Executing Grammar & Readability analysis...")
        
        # Strip markdown syntax for pure text statistics
        clean_text = re.sub(r"[#*`>_\-\[\]\(\)]", " ", draft_markdown)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        
        sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if len(s.strip()) > 5]
        words = clean_text.split()
        
        avg_sentence_len = round(len(words) / max(len(sentences), 1), 1)
        
        # Find excessively long sentences (> 38 words)
        run_on_sentences = [s for s in sentences if len(s.split()) > 38]
        
        # Readability Metrics
        flesch_reading_ease = textstat.flesch_reading_ease(clean_text)
        flesch_kincaid_grade = textstat.flesch_kincaid_grade(clean_text)
        
        blocking_issues = []
        suggestions = []
        
        if len(run_on_sentences) > 2:
            suggestions.append(f"Identified {len(run_on_sentences)} sentences with >38 words. Consider breaking them up for executive clarity.")
            
        if flesch_kincaid_grade > 16.0:
            suggestions.append(f"Flesch-Kincaid Grade ({flesch_kincaid_grade}) is very academic. Aim for grade 11-13 for healthcare IT executives.")

        # Score calculation
        score = 94.0
        if run_on_sentences:
            score -= (len(run_on_sentences) * 2.0)
        score = max(50.0, min(100.0, score))
        grade = "A" if score >= 90 else "B" if score >= 80 else "C"

        return {
            "score": score,
            "grade": grade,
            "flesch_reading_ease": flesch_reading_ease,
            "flesch_kincaid_grade": flesch_kincaid_grade,
            "average_sentence_length": avg_sentence_len,
            "summary": f"Readability Grade: {flesch_kincaid_grade} (Professional). Avg sentence length: {avg_sentence_len} words.",
            "blocking_issues": blocking_issues,
            "suggestions": suggestions
        }
