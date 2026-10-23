import re
import numpy as np
import requests
from typing import Dict, Any, List
from backend.app.core.logger import get_logger

logger = get_logger("AIDetectionEngine")

class AIDetectionEngine:
    """
    Production-grade AI Detection Engine mirroring ZeroGPT, GPTZero, and Turnitin:
    1. Analyzes sentence burstiness (Coefficient of Variation of sentence length).
    2. Analyzes perplexity indicators, repetitive n-gram uniformity, and formulaic sentence structures.
    3. Detects heavy AI marker vocabulary and robotic transition words.
    4. Evaluates short punchy sentence fragment ratios and natural contractions.
    5. Optionally queries public Hugging Face AI text classification endpoints with fallback.
    """

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

    PUBLIC_HF_DETECTOR_URL = "https://api-inference.huggingface.co/models/answerdotai/ModernBERT-base-ai-detector"

    def query_public_ai_api(self, text: str) -> Dict[str, Any]:
        """Tries public AI detector model if network is available, with strict 3s timeout."""
        try:
            # Query with first 500 chars to check likelihood
            sample = " ".join(text.split()[:120])
            res = requests.post(
                self.PUBLIC_HF_DETECTOR_URL,
                json={"inputs": sample},
                timeout=3.0
            )
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    first = data[0]
                    if isinstance(first, list):
                        first = first[0]
                    label = first.get("label", "").lower()
                    score = float(first.get("score", 0.5))
                    ai_prob = score * 100.0 if "ai" in label or "fake" in label or "generated" in label else (1.0 - score) * 100.0
                    return {
                        "api_success": True,
                        "ai_prob": round(ai_prob, 1),
                        "source": "ModernBERT AI Detector (HuggingFace Public API)"
                    }
        except Exception as e:
            logger.debug(f"Public AI detector endpoint unavailable ({e}); proceeding with local ZeroGPT calibrator.")
        
        return {"api_success": False, "ai_prob": None, "source": "Local ZeroGPT Calibrator"}

    def evaluate_ai_detection(self, text: str) -> Dict[str, Any]:
        """
        Deep ZeroGPT-calibrated evaluation returning AI probability, burstiness, and risk factors.
        Target: AI score < 35.0% (target 10% - 25% human).
        """
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 3]
        if not sentences:
            return {
                "ai_probability": 15.0,
                "human_probability": 85.0,
                "burstiness_cv": 0.70,
                "short_fragment_ratio": 0.30,
                "ai_markers_count": 0,
                "verdict": "Human-Written (< 35% AI)"
            }

        word_counts = [len(s.split()) for s in sentences]
        total_words = sum(word_counts)
        mean_len = float(np.mean(word_counts))
        std_len = float(np.std(word_counts))
        # Coefficient of Variation: Human text has CV > 0.55 (extreme variation); AI has CV < 0.35 (rigid uniformity)
        cv = std_len / max(mean_len, 1.0)

        # 1. Short human sentence fragments (<= 7 words: e.g. "It takes time.", "Mistakes get expensive.")
        short_sentences = sum(1 for c in word_counts if c <= 7)
        short_ratio = short_sentences / max(len(word_counts), 1)

        # 2. Contractions (don't, can't, it's, doesn't, we're)
        contractions = len(re.findall(r"\b(don't|can't|it's|doesn't|won't|isn't|aren't|didn't|we're|they're|there's|that's)\b", text, re.IGNORECASE))
        contraction_ratio = contractions / max(len(sentences), 1)

        # 3. AI Marker Vocabulary matches
        ai_markers_found = []
        for pat in self.AI_MARKER_PATTERNS:
            m = re.findall(pat, text, re.IGNORECASE)
            if m:
                ai_markers_found.append(pat.replace(r"\b", "").replace(r"\s+", " "))

        # 4. Markdown Hashes check (Instant AI trigger for ZeroGPT)
        has_hashes = "#" in text

        # 5. Calculate ZeroGPT Score Baseline
        # High predictability base: 65% for raw AI output
        base_ai = 45.0

        if has_hashes:
            base_ai += 35.0  # ZeroGPT immediately flags raw markdown hashes as AI generated

        # Penalty for AI markers
        base_ai += (len(ai_markers_found) * 8.0)

        # Bonus for burstiness (varied sentence lengths)
        if cv >= 0.65:
            base_ai -= 22.0
        elif cv >= 0.50:
            base_ai -= 14.0
        elif cv < 0.35:
            base_ai += 18.0  # Rigid uniform sentence lengths

        # Bonus for punchy short fragments
        if short_ratio >= 0.25:
            base_ai -= 18.0
        elif short_ratio >= 0.15:
            base_ai -= 10.0
        elif short_ratio < 0.08:
            base_ai += 12.0  # All long sentences

        # Bonus for human contractions
        if contraction_ratio >= 0.30:
            base_ai -= 12.0
        elif contraction_ratio >= 0.15:
            base_ai -= 6.0
        elif contractions == 0:
            base_ai += 10.0

        # Check external public model if helpful
        ext_check = self.query_public_ai_api(text)
        if ext_check["api_success"] and ext_check["ai_prob"] is not None:
            # Blend 50% public model + 50% ZeroGPT calibrator
            final_ai = round((base_ai * 0.5) + (ext_check["ai_prob"] * 0.5), 1)
        else:
            final_ai = round(base_ai, 1)

        final_ai = max(4.0, min(96.0, final_ai))
        human_prob = round(100.0 - final_ai, 1)

        verdict = (
            "Human-Written (Safe < 35% AI)" if final_ai < 35.0
            else "Moderate AI Detection Risk (35-65% AI)" if final_ai < 65.0
            else "High AI Detection Risk (> 65% AI)"
        )

        return {
            "ai_probability": final_ai,
            "human_probability": human_prob,
            "is_safe": final_ai < 35.0,
            "verdict": verdict,
            "burstiness_cv": round(cv, 2),
            "short_fragment_ratio": round(short_ratio, 2),
            "sentence_std_dev": round(std_len, 1),
            "contractions_count": contractions,
            "has_markdown_hashes": has_hashes,
            "ai_markers_count": len(ai_markers_found),
            "ai_markers_found": ai_markers_found,
            "detector_source": ext_check["source"]
        }
