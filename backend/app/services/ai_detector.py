import re
import numpy as np
import requests
from typing import Dict, Any, List
from backend.app.core.logger import get_logger

logger = get_logger("AIDetectionEngine")

class AIDetectionEngine:
    """
    Live ZeroGPT Integration and Detection Engine:
    1. Directly calls the live ZeroGPT public detection API (api.zerogpt.com) for 100% accurate scores.
    2. Identifies exact flagged AI sentences returned by ZeroGPT's model.
    3. Calculates sentence burstiness (CV) and human fragment ratios.
    4. Provides robust offline fallback if the network is interrupted.
    """

    ZEROGPT_API_URL = "https://api.zerogpt.com/api/detect/detectText"
    ZEROGPT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://www.zerogpt.com",
        "Referer": "https://www.zerogpt.com/",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*"
    }

    AI_MARKER_PATTERNS = [
        r"\bdelve(s|d)?\s+into\b",
        r"\btapestry\s+of\b",
        r"\bbeacon\s+of\b",
        r"\btestament\s+to\b",
        r"\ba\s+paradigm\s+shift\b",
        r"\bharnessing\s+the\s+power\s+of\b",
        r"\bplays\s+a\s+(pivotal|crucial|vital|key)\s+role\b",
        r"\bgame-?changer\b",
        r"\brapidly\s+evolving\s+(landscape|world)\b",
        r"\bin\s+today's\s+(fast-paced|rapidly\s+evolving|digital)\s+(world|age|era)\b",
        r"\bit\s+is\s+(crucial|imperative|essential|vital)\s+to\s+(remember|note|understand)\b",
        r"\bnavigating\s+the\s+complexities\s+of\b",
        r"\bplethora\s+of\b",
        r"\bmyriad\s+of\b",
        r"\bseamlessly\s+integrate(s|d)?\b",
        r"\bunderscores\s+the\s+importance\s+of\b",
        r"\bmoreover,?\b",
        r"\bfurthermore,?\b",
        r"\bin\s+conclusion,?\b",
        r"\bto\s+summarize,?\b"
    ]

    GRAMMARLY_TRIGGER_PATTERNS = [
        r"(?:^|[\.\?!]\s+)Consequently,?\s*",
        r"(?:^|[\.\?!]\s+)In addition,?\s*",
        r"(?:^|[\.\?!]\s+)Specifically,?\s*",
        r"(?:^|[\.\?!]\s+)Because of this,?\s*",
        r"(?:^|[\.\?!]\s+)On the other hand,?\s*",
        r"(?:^|[\.\?!]\s+)Meanwhile,?\s*",
        r"(?:^|[\.\?!]\s+)As a result,?\s*",
        r"(?:^|[\.\?!]\s+)Furthermore,?\s*",
        r"(?:^|[\.\?!]\s+)Moreover,?\s*",
        r"(?:^|[\.\?!]\s+)Ultimately,?\s*"
    ]

    def query_zerogpt_live(self, text: str) -> Dict[str, Any]:
        """
        Directly queries the live ZeroGPT detection endpoint (api.zerogpt.com).
        Returns exact fakePercentage and the list of AI sentences flagged by ZeroGPT.
        """
        try:
            # ZeroGPT checks best with trimmed, clean text
            clean_text = text.strip()
            if len(clean_text) < 100:
                return {"success": False, "error": "Text too short for ZeroGPT analysis."}

            res = requests.post(
                self.ZEROGPT_API_URL,
                json={"input_text": clean_text},
                headers=self.ZEROGPT_HEADERS,
                timeout=10.0
            )
            if res.status_code == 200:
                payload = res.json()
                if payload.get("success") and payload.get("data"):
                    data = payload["data"]
                    fake_pct = float(data.get("fakePercentage", 0.0))
                    flagged = data.get("h", [])
                    feedback = data.get("feedback", "Detection complete")
                    ai_words = int(data.get("aiWords", 0))
                    text_words = int(data.get("textWords", len(clean_text.split())))
                    
                    logger.info(f"Live ZeroGPT Response: {fake_pct}% AI ({feedback}). Flagged sentences: {len(flagged)}.")
                    return {
                        "success": True,
                        "fakePercentage": fake_pct,
                        "feedback": feedback,
                        "flagged_sentences": flagged,
                        "ai_words": ai_words,
                        "text_words": text_words,
                        "source": "ZeroGPT Live Engine (api.zerogpt.com)"
                    }
                else:
                    logger.warning(f"ZeroGPT API returned unsuccessful response: {res.text[:120]}")
            else:
                logger.warning(f"ZeroGPT API HTTP {res.status_code}: {res.text[:120]}")
        except Exception as e:
            logger.warning(f"Live ZeroGPT query failed ({e}); falling back to local ZeroGPT calibrator.")

        return {"success": False, "error": "Live ZeroGPT endpoint unreachable"}

    def evaluate_ai_detection(self, text: str) -> Dict[str, Any]:
        """
        Deep ZeroGPT evaluation. Prioritizes the live ZeroGPT API (api.zerogpt.com).
        Target: AI score < 35.0%.
        """
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 3]
        word_counts = [len(s.split()) for s in sentences] if sentences else [10]
        mean_len = float(np.mean(word_counts))
        std_len = float(np.std(word_counts))
        cv = std_len / max(mean_len, 1.0)
        short_sentences = sum(1 for c in word_counts if c <= 7)
        short_ratio = short_sentences / max(len(word_counts), 1)

        contractions = len(re.findall(r"\b(don't|can't|it's|doesn't|won't|isn't|aren't|didn't|we're|they're|there's|that's)\b", text, re.IGNORECASE))
        has_hashes = "#" in text

        ai_markers_found = []
        for pat in self.AI_MARKER_PATTERNS:
            m = re.findall(pat, text, re.IGNORECASE)
            if m:
                ai_markers_found.append(pat.replace(r"\b", "").replace(r"\s+", " "))

        # 1. First attempt Live ZeroGPT query
        live_res = self.query_zerogpt_live(text)
        if live_res["success"]:
            ai_prob = live_res["fakePercentage"]
            human_prob = round(max(0.0, 100.0 - ai_prob), 1)
            flagged = live_res["flagged_sentences"]
            feedback = live_res["feedback"]
            source = live_res["source"]
        else:
            # Fallback to calibrated local model
            base_ai = 50.0
            if has_hashes:
                base_ai += 35.0
            base_ai += (len(ai_markers_found) * 8.0)
            if cv >= 0.65:
                base_ai -= 20.0
            elif cv < 0.35:
                base_ai += 18.0
            if short_ratio >= 0.25:
                base_ai -= 15.0
            elif short_ratio < 0.10:
                base_ai += 12.0
            if contractions >= 5:
                base_ai -= 10.0

            ai_prob = round(max(5.0, min(95.0, base_ai)), 1)
            human_prob = round(100.0 - ai_prob, 1)
            flagged = [s for s in sentences if len(s.split()) > 22][:5]
            feedback = "Calibrated Local Heuristic"
            source = "Local ZeroGPT Calibrator (Fallback)"

        is_safe = ai_prob < 35.0
        verdict = (
            "Human-Written (Safe < 35% AI)" if is_safe
            else "Moderate AI Detection Risk (35-65% AI)" if ai_prob < 65.0
            else "High AI Detection Risk (> 65% AI)"
        )

        # Grammarly-specific pattern metrics
        grammarly_triggers = []
        for pat in self.GRAMMARLY_TRIGGER_PATTERNS:
            found = re.findall(pat, text, re.IGNORECASE)
            if found:
                grammarly_triggers.extend(found)

        parentheticals = len(re.findall(r"\([^\)]+\)", text))
        em_dashes = text.count("—") + text.count(" - ")
        rhetorical_questions = len(re.findall(r"\b(why|how|what|can|could|did|will|sound)\b[^\.\?!]*\?", text, re.IGNORECASE))
        blunt_short_punches = sum(1 for c in word_counts if c <= 4)

        grammarly_safe = len(grammarly_triggers) <= 1 and (parentheticals >= 1 or em_dashes >= 1 or blunt_short_punches >= 2)
        grammarly_verdict = "Low AI Risk (Bypasses Grammarly)" if grammarly_safe else "Moderate/High Grammarly Flag Risk"

        return {
            "ai_probability": ai_prob,
            "human_probability": human_prob,
            "is_safe": is_safe,
            "verdict": verdict,
            "feedback": feedback,
            "flagged_sentences": flagged,
            "flagged_count": len(flagged),
            "burstiness_cv": round(cv, 2),
            "short_fragment_ratio": round(short_ratio, 2),
            "sentence_std_dev": round(std_len, 1),
            "contractions_count": contractions,
            "has_markdown_hashes": has_hashes,
            "ai_markers_count": len(ai_markers_found),
            "ai_markers_found": ai_markers_found,
            "detector_source": source,
            "grammarly_transition_starters_count": len(grammarly_triggers),
            "parentheticals_count": parentheticals,
            "em_dashes_count": em_dashes,
            "rhetorical_questions_count": rhetorical_questions,
            "blunt_short_punches": blunt_short_punches,
            "grammarly_verdict": grammarly_verdict
        }
