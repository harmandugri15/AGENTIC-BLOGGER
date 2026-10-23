import re
from typing import Dict, Any, List
from backend.app.services.humanizer import HumanizerEngine
from backend.app.core.logger import get_logger

logger = get_logger("EditorialAgent")

class HumanStyleEditorialAgent:
    """
    Specifically targets and eliminates robotic AI patterns, cliché transitions,
    and uniform cadence using an iterative Humanization Loop to ensure the output
    reads authentically human and passes detectors like Quillbot.
    """

    def __init__(self):
        self.humanizer = HumanizerEngine()

    def execute(self, draft_markdown: str) -> Dict[str, Any]:
        logger.info("Executing Human-Style Editorial & Anti-Robotic Audit with Humanization Loop (Target: < 35% AI)...")
        
        # Run iterative anti-AI looping technique with target < 35% AI
        loop_result = self.humanizer.run_humanization_loop(
            draft_markdown,
            target_ai_threshold=35.0,
            max_iterations=4
        )

        final_text = loop_result["final_text"]
        eval_metrics = self.humanizer.calculate_ai_detection_score(final_text)

        blocking_issues = []
        suggestions = []

        if eval_metrics["ai_probability"] >= 35.0:
            blocking_issues.append(f"ZeroGPT AI Detection risk is {eval_metrics['ai_probability']}%. Target is < 35%. Requires automated de-robotic rewrite cycle.")
        else:
            suggestions.append(f"ZeroGPT Threshold Met: {eval_metrics['ai_probability']}% AI ({eval_metrics['human_probability']}% Human). Safe from AI detectors.")

        suggestions.append(f"Sentence burstiness score: {eval_metrics['burstiness_cv']} CV. Pacing reflects organic human editorial structure.")

        score = max(50.0, min(100.0, eval_metrics["human_probability"]))
        grade = "A+" if score >= 90 else "A" if score >= 80 else "B"

        return {
            "score": score,
            "grade": grade,
            "ai_probability": eval_metrics["ai_probability"],
            "human_probability": eval_metrics["human_probability"],
            "is_safe_under_35": eval_metrics["ai_probability"] < 35.0,
            "summary": f"ZeroGPT Human-Likeness Score: {score}/100. AI detection probability reduced to {eval_metrics['ai_probability']}% across {loop_result['iterations_count']} humanization loops.",
            "sentence_burstiness_cv": eval_metrics["burstiness_cv"],
            "sentence_burstiness_std": eval_metrics["sentence_std_dev"],
            "humanized_text": final_text,
            "loop_history": loop_result["loop_history"],
            "detector_source": eval_metrics.get("detector_source", "ZeroGPT Calibrator"),
            "blocking_issues": blocking_issues,
            "suggestions": suggestions
        }
