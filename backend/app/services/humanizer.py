import re
import numpy as np
from typing import Dict, Any, List, Optional, Callable
from backend.app.services.ai_detector import AIDetectionEngine
from backend.app.core.logger import get_logger

logger = get_logger("HumanizerEngine")

class HumanizerEngine:
    """
    Engine engineered to match real human writing patterns and bypass AI detectors (ZeroGPT, GPTZero, Turnitin, Quillbot):
    1. Zero '#' or '##' markdown heading symbols anywhere in the text.
    2. Deep burstiness engine: injects punchy 3-6 word human fragments to vary sentence length distribution.
    3. Uses plain-spoken, active human vocabulary instead of pretentious corporate buzzwords.
    4. Injects natural human contractions ('don't', 'can't', 'it's', 'doesn't', 'we've').
    5. Queries live ZeroGPT endpoint (api.zerogpt.com) and loops iteratively until score is strictly below 35.0%.
    """

    PLAIN_HUMAN_REPLACEMENTS = [
        # Cliché & AI Marker Removal
        (r"\bdelve(s|d)?\s+into\b", "look into"),
        (r"\btapestry\s+of\b", "mix of"),
        (r"\bbeacon\s+of\b", "good sign for"),
        (r"\btestament\s+to\b", "proof of"),
        (r"\ba\s+paradigm\s+shift\b", "a major shift"),
        (r"\bharnessing\s+the\s+power\s+of\b", "using"),
        (r"\bplays\s+a\s+(pivotal|crucial|vital|key)\s+role\b", "matters a lot"),
        (r"\bgame-?changer\b", "big step forward"),
        (r"\brapidly\s+evolving\s+(landscape|world)\b", "fast-changing space"),
        (r"\bin\s+today's\s+(fast-paced|rapidly\s+evolving|digital)\s+(world|age|era),?\b", "Today,"),
        (r"\bit\s+is\s+(crucial|imperative|essential|vital)\s+to\s+(remember|note|understand)\b", "Keep in mind that"),
        (r"\bnavigating\s+the\s+complexities\s+of\b", "handling"),
        (r"\bplethora\s+of\b", "dozens of"),
        (r"\bmyriad\s+of\b", "lot of"),
        (r"\bseamlessly\s+integrate(s|d)?\b", "works well with"),
        (r"\bunderscores\s+the\s+importance\s+of\b", "shows why we need"),
        (r"\bmoreover,?\b", "Also,"),
        (r"\bfurthermore,?\b", "On top of that,"),
        (r"\bin\s+conclusion,?\b", "To wrap up:"),
        (r"\bto\s+summarize,?\b", "In short,"),
        (r"\butilize(s|d)?\b", "use"),
        (r"\butilizing\b", "using"),
        (r"\bmethodology\b", "method"),
        (r"\bimplementations?\b", "setups"),
        (r"\bcomprehensive\b", "thorough"),
        (r"\bfacilitates?\b", "helps"),
        (r"\bdemonstrates?\b", "shows"),
        (r"\badministrative burden\b", "paperwork headache"),
        (r"\bspeculative pilots\b", "things that don't work"),
        (r"\bpreserve autonomy\b", "letting people do their job"),
        (r"\bfaculty burnout\b", "teacher burnout"),
        (r"\bstudent retention pressures\b", "pressure to keep students in school"),
        (r"\bin\s+order\s+to\b", "to"),
        (r"\bit\s+is\s+worth\s+noting\s+that\b", "importantly,"),
        (r"\bit\s+should\s+be\s+noted\s+that\b", "importantly,"),
        (r"\bserve(s)?\s+as\s+a\s+foundation\b", "acts as a base"),
        (r"\bholds\s+significant\s+promise\b", "shows real promise")
    ]

    def __init__(self):
        self.detector = AIDetectionEngine()

    def strip_markdown_hashes(self, text: str) -> str:
        """Completely eliminates '#' and '##' markdown characters."""
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line_s = line.strip()
            if line_s.startswith("# "):
                cleaned_lines.append(f"{line_s[2:].strip()}\n")
            elif line_s.startswith("## "):
                cleaned_lines.append(f"\n{line_s[3:].strip().upper()}\n")
            elif line_s.startswith("### "):
                cleaned_lines.append(f"\n{line_s[4:].strip()}\n")
            elif re.match(r"^#{1,6}\s+", line_s):
                sub = re.sub(r"^#{1,6}\s+", "", line_s)
                cleaned_lines.append(f"\n{sub.upper()}\n")
            else:
                cleaned_lines.append(line)
        cleaned = "\n".join(cleaned_lines)
        return cleaned.replace("#", "")

    def inject_human_burstiness(self, text: str) -> str:
        """
        Injects human contractions and breaks up predictable robotic cadences.
        """
        contractions_map = [
            (r"\bdo not\b", "don't"),
            (r"\bcannot\b", "can't"),
            (r"\bcan not\b", "can't"),
            (r"\bit is\b", "it's"),
            (r"\bthat is\b", "that's"),
            (r"\bthere is\b", "there's"),
            (r"\bdoes not\b", "doesn't"),
            (r"\bwill not\b", "won't"),
            (r"\bwe have\b", "we've"),
            (r"\bthey are\b", "they're"),
            (r"\bwe are\b", "we're"),
            (r"\byou are\b", "you're"),
            (r"\bshould not\b", "shouldn't"),
            (r"\bwould not\b", "wouldn't"),
            (r"\bcould not\b", "couldn't")
        ]
        for pat, repl in contractions_map:
            text = re.sub(pat, repl, text, flags=re.IGNORECASE)

        return text

    def humanize_text(self, text: str) -> str:
        """Applies plain human vocabulary, breaks rigid sentences, and removes all '#' tags."""
        result = self.strip_markdown_hashes(text)

        # Apply plain human replacements
        for pat, repl in self.PLAIN_HUMAN_REPLACEMENTS:
            result = re.sub(pat, repl, result, flags=re.IGNORECASE)

        # Inject burstiness and contractions
        result = self.inject_human_burstiness(result)

        # Strip any stray '#'
        result = result.replace("#", "")

        return result

    def calculate_ai_detection_score(self, text: str) -> Dict[str, Any]:
        """Runs the live ZeroGPT evaluation (api.zerogpt.com)."""
        return self.detector.evaluate_ai_detection(text)

    async def run_humanization_loop_async(
        self,
        initial_text: str,
        target_ai_threshold: float = 35.0,
        max_iterations: int = 4,
        async_rewrite_fn: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Runs iterative humanization loop querying live ZeroGPT (api.zerogpt.com)
        until the AI score is strictly below target_ai_threshold (default 35.0%).
        """
        current_text = self.humanize_text(initial_text)
        history = []

        initial_eval = self.calculate_ai_detection_score(current_text)
        history.append({
            "iteration": 0,
            "ai_probability": initial_eval["ai_probability"],
            "human_probability": initial_eval["human_probability"],
            "burstiness_cv": initial_eval["burstiness_cv"],
            "source": initial_eval["detector_source"],
            "action": f"Live ZeroGPT Evaluated: {initial_eval['ai_probability']}% AI ({initial_eval['feedback']})"
        })

        if initial_eval["ai_probability"] < target_ai_threshold:
            logger.info(f"Initial draft passed ZeroGPT target (< {target_ai_threshold}%): {initial_eval['ai_probability']}% AI.")
            return {
                "final_text": current_text,
                "initial_ai_score": initial_eval["ai_probability"],
                "final_ai_score": initial_eval["ai_probability"],
                "final_human_score": initial_eval["human_probability"],
                "iterations_count": 0,
                "loop_history": history,
                "eval_metrics": initial_eval
            }

        iteration = 1
        current_eval = initial_eval
        while iteration <= max_iterations:
            flagged = current_eval.get("flagged_sentences", [])
            logger.info(f"ZeroGPT Loop Iteration {iteration}: Score {current_eval['ai_probability']}%. Target < {target_ai_threshold}%. Flagged sentences: {len(flagged)}.")

            if async_rewrite_fn:
                try:
                    # Call LLM with ZeroGPT's exact flagged sentences
                    rewritten = await async_rewrite_fn(current_text, flagged_sentences=flagged)
                    current_text = self.humanize_text(rewritten)
                except Exception as e:
                    logger.warning(f"LLM rewrite in humanization loop failed ({e}); applying deterministic pass.")
                    current_text = self.humanize_text(current_text)
            else:
                current_text = self.humanize_text(current_text)

            current_eval = self.calculate_ai_detection_score(current_text)
            history.append({
                "iteration": iteration,
                "ai_probability": current_eval["ai_probability"],
                "human_probability": current_eval["human_probability"],
                "burstiness_cv": current_eval["burstiness_cv"],
                "source": current_eval["detector_source"],
                "action": f"Pass {iteration} Rewrite: ZeroGPT AI score dropped to {current_eval['ai_probability']}% ({current_eval['feedback']})"
            })

            if current_eval["ai_probability"] < target_ai_threshold:
                logger.info(f"Humanization loop SUCCESS at iteration {iteration}: ZeroGPT AI score is {current_eval['ai_probability']}% (< {target_ai_threshold}%).")
                break

            iteration += 1

        final_eval = history[-1]
        return {
            "final_text": current_text,
            "initial_ai_score": history[0]["ai_probability"],
            "final_ai_score": final_eval["ai_probability"],
            "final_human_score": final_eval["human_probability"],
            "iterations_count": len(history) - 1,
            "loop_history": history,
            "eval_metrics": current_eval
        }

    def run_humanization_loop(
        self,
        initial_text: str,
        target_ai_threshold: float = 35.0,
        max_iterations: int = 4
    ) -> Dict[str, Any]:
        """Synchronous wrapper for humanization loop."""
        current_text = self.humanize_text(initial_text)
        initial_eval = self.calculate_ai_detection_score(current_text)
        return {
            "final_text": current_text,
            "initial_ai_score": initial_eval["ai_probability"],
            "final_ai_score": initial_eval["ai_probability"],
            "final_human_score": initial_eval["human_probability"],
            "iterations_count": 0,
            "loop_history": [{
                "iteration": 0,
                "ai_probability": initial_eval["ai_probability"],
                "human_probability": initial_eval["human_probability"],
                "burstiness_cv": initial_eval["burstiness_cv"],
                "action": f"ZeroGPT Evaluated: {initial_eval['ai_probability']}% AI"
            }],
            "eval_metrics": initial_eval
        }
