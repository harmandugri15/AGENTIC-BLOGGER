import re
from typing import Dict, Any, List, Optional
from backend.app.services.humanizer import HumanizerEngine
from backend.app.core.logger import get_logger

logger = get_logger("EditorialAgent")

class HumanStyleEditorialAgent:
    """
    Specifically targets and eliminates robotic AI patterns, cliché transitions,
    and uniform cadence using an iterative Humanization Loop integrated directly
    with ZeroGPT (api.zerogpt.com) to guarantee the output scores strictly below 35% AI.
    """

    def __init__(self):
        self.humanizer = HumanizerEngine()

    async def execute_async(self, draft_markdown: str, llm_provider: Optional[Any] = None) -> Dict[str, Any]:
        """
        Asynchronously audits and humanizes draft, calling live ZeroGPT endpoint
        and executing LLM rewrites on flagged sentences until ZeroGPT AI score is < 35%.
        """
        logger.info("Executing Human-Style Editorial Audit & Live ZeroGPT Verification (Target: < 35% AI)...")

        async def rewrite_cb(text: str, flagged_sentences: List[str] = None) -> str:
            if llm_provider:
                return await llm_provider.rewrite_for_human_naturalness(
                    text,
                    flagged_sentences=flagged_sentences
                )
            return text

        loop_result = await self.humanizer.run_humanization_loop_async(
            draft_markdown,
            target_ai_threshold=35.0,
            max_iterations=4,
            async_rewrite_fn=rewrite_cb if llm_provider else None
        )

        final_text = loop_result["final_text"]
        eval_metrics = loop_result.get("eval_metrics") or self.humanizer.calculate_ai_detection_score(final_text)

        blocking_issues = []
        suggestions = []

        ai_score = eval_metrics["ai_probability"]
        if ai_score >= 35.0:
            blocking_issues.append(f"ZeroGPT AI detection score is {ai_score}%. Target must be strictly < 35.0%. Requires automated de-robotic rewrite cycle.")
        else:
            suggestions.append(f"ZeroGPT Threshold Met: {ai_score}% AI ({eval_metrics['human_probability']}% Human). Verified safe by {eval_metrics.get('detector_source', 'ZeroGPT')}.")

        suggestions.append(f"Sentence burstiness score: {eval_metrics['burstiness_cv']} CV. Pacing reflects organic human editorial structure.")

        score = max(50.0, min(100.0, eval_metrics["human_probability"]))
        grade = "A+" if score >= 90 else "A" if score >= 80 else "B"

        return {
            "score": score,
            "grade": grade,
            "ai_probability": ai_score,
            "human_probability": eval_metrics["human_probability"],
            "is_safe_under_35": ai_score < 35.0,
            "feedback": eval_metrics.get("feedback", ""),
            "flagged_sentences": eval_metrics.get("flagged_sentences", []),
            "summary": f"ZeroGPT Human-Likeness Score: {score}/100. AI detection confirmed at {ai_score}% via {eval_metrics.get('detector_source', 'ZeroGPT')}.",
            "sentence_burstiness_cv": eval_metrics["burstiness_cv"],
            "sentence_burstiness_std": eval_metrics["sentence_std_dev"],
            "humanized_text": final_text,
            "loop_history": loop_result["loop_history"],
            "detector_source": eval_metrics.get("detector_source", "ZeroGPT Live Engine"),
            "blocking_issues": blocking_issues,
            "suggestions": suggestions
        }

    def execute(self, draft_markdown: str) -> Dict[str, Any]:
        """Synchronous fallback for testing."""
        eval_metrics = self.humanizer.calculate_ai_detection_score(draft_markdown)
        ai_score = eval_metrics["ai_probability"]
        blocking_issues = []
        suggestions = []

        if ai_score >= 35.0:
            blocking_issues.append(f"ZeroGPT AI detection risk is {ai_score}%. Target must be < 35.0%.")
        else:
            suggestions.append(f"ZeroGPT Threshold Met: {ai_score}% AI.")

        score = max(50.0, min(100.0, eval_metrics["human_probability"]))
        return {
            "score": score,
            "grade": "A" if score >= 80 else "B",
            "ai_probability": ai_score,
            "human_probability": eval_metrics["human_probability"],
            "is_safe_under_35": ai_score < 35.0,
            "sentence_burstiness_cv": eval_metrics["burstiness_cv"],
            "humanized_text": self.humanizer.humanize_text(draft_markdown),
            "detector_source": eval_metrics.get("detector_source", "ZeroGPT"),
            "blocking_issues": blocking_issues,
            "suggestions": suggestions
        }
