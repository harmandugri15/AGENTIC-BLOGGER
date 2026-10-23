import re
import json
import os
import asyncio
from typing import Dict, Any, List, Optional
from backend.app.config import settings
from backend.app.core.logger import get_logger
from backend.app.services.humanizer import HumanizerEngine

logger = get_logger("LLMProvider")

class LLMProvider:
    """
    Enterprise LLM Provider that interfaces directly with Google Gemini models.
    Strictly adheres to user directive:
    - Never substitutes canned or hardcoded paragraphs.
    - If live AI models fail or quota is exhausted, raises explicit errors so the frontend can notify the user.
    """

    CANDIDATE_MODELS = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3-flash-preview"
    ]
    CANDIDATE_GEMINI_MODELS = CANDIDATE_MODELS
    CANDIDATE_GROQ_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]

    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.groq_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
        self.humanizer = HumanizerEngine()
        self.genai = None

        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.genai = genai
                logger.info("Configured Google Gemini API client.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini client: {e}")
                self.genai = None
        else:
            self.genai = None

    def _call_groq_fallback(self, prompt: str, groq_key: str) -> str:
        """Calls Groq Llama 3.3 / 3.1 models as live fallback."""
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            errors = []
            for model_name in self.CANDIDATE_GROQ_MODELS:
                try:
                    logger.info(f"Attempting live generation using Groq model '{model_name}'...")
                    completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=model_name,
                        temperature=0.7,
                        max_tokens=4096
                    )
                    if completion.choices and completion.choices[0].message.content:
                        text = completion.choices[0].message.content.strip()
                        logger.info(f"Successfully generated live content using Groq model '{model_name}'.")
                        return text
                except Exception as e:
                    err_msg = str(e)
                    logger.warning(f"Groq model '{model_name}' failed: {err_msg[:120]}")
                    errors.append(f"{model_name}: {err_msg[:120]}")
            raise RuntimeError(f"ALL_GROQ_MODELS_FAILED: {'; '.join(errors)}")
        except ImportError:
            raise RuntimeError("GROQ_LIB_MISSING: python 'groq' package is not installed.")

    def _call_llm_with_fallback(self, prompt: str) -> str:
        """
        Executes live generation across candidate providers:
        1. Google Gemini candidate models
        2. Groq (Llama 3.3 70B / Llama 3.1 8B) fallback if Gemini fails or quota exceeded
        Never uses canned or hardcoded content.
        """
        current_gemini_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY or self.gemini_key
        current_groq_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY or self.groq_key

        errors = []

        # 1. Try Google Gemini if key available
        if current_gemini_key:
            if not self.genai or current_gemini_key != self.gemini_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=current_gemini_key)
                    self.genai = genai
                    self.gemini_key = current_gemini_key
                    logger.info("Updated Google Gemini client with active key.")
                except Exception as e:
                    logger.error(f"Failed to configure Gemini client: {e}")

            if self.genai:
                for model_name in self.CANDIDATE_GEMINI_MODELS:
                    try:
                        model = self.genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        if response and response.text:
                            logger.info(f"Successfully generated content using Gemini '{model_name}'.")
                            return response.text.strip()
                    except Exception as e:
                        err_msg = str(e)
                        logger.warning(f"Gemini model '{model_name}' failed: {err_msg[:120]}")
                        errors.append(f"Gemini {model_name}: {err_msg[:120]}")

        # 2. Try Groq Fallback if Gemini failed or key missing
        if current_groq_key:
            logger.info("Engaging Groq live LLM fallback...")
            try:
                return self._call_groq_fallback(prompt, current_groq_key)
            except Exception as e:
                errors.append(f"Groq Fallback: {str(e)[:120]}")

        # If neither or all failed:
        if not current_gemini_key and not current_groq_key:
            raise RuntimeError("API_KEY_MISSING: Neither Gemini API key nor Groq API key is configured. Please provide one in the UI.")

        raise RuntimeError(f"ALL_MODELS_FAILED: Live LLM calls failed across Google Gemini and Groq. Details: {'; '.join(errors)}")

    def _call_gemini_with_fallback(self, prompt: str) -> str:
        """Alias for backward compatibility."""
        return self._call_llm_with_fallback(prompt)

    async def generate_seo_strategy(self, query: str, competitor_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates dynamic SEO strategy using live Gemini. Never uses canned data."""
        comp_titles = [c.get("title", "") for c in competitor_pages[:3]]
        prompt = f"""
You are a principal SEO strategist. Analyze the user query: "{query}".
Discovered competitor references: {comp_titles}.

Respond strictly in valid JSON without markdown wrapping or commentary:
{{
  "target_query": "{query}",
  "domain": "Specific Domain (e.g. Robotics, Education, Healthcare, Supply Chain)",
  "search_intent": "Clear commercial and practitioner search intent description",
  "primary_keywords": ["keyword 1", "keyword 2", "keyword 3"],
  "secondary_keywords": ["sec 1", "sec 2", "sec 3", "sec 4"],
  "semantic_entities": ["Entity 1", "Entity 2", "Entity 3", "Entity 4", "Entity 5", "Entity 6"],
  "target_slug": "seo-friendly-url-slug",
  "recommended_meta_title": "Meta title under 60 chars",
  "recommended_meta_description": "Meta description under 155 chars",
  "recommended_h2_sections": ["H2 1", "H2 2", "H2 3", "H2 4", "H2 5"],
  "competitor_matrix": [
    {{
      "competitor": "Competitor Name",
      "url": "https://example.com",
      "strengths": ["strength 1"],
      "content_gaps": ["gap 1"],
      "citiustech_differentiation": "differentiation angle"
    }}
  ]
}}
"""
        txt = await asyncio.to_thread(self._call_gemini_with_fallback, prompt)
        
        # Clean any json code block fences if present
        cleaned = txt
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()

        try:
            data = json.loads(cleaned)
        except Exception:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                raise RuntimeError(f"INVALID_JSON_RESPONSE: Gemini returned non-JSON response for SEO strategy: {txt[:200]}")

        data["target_query"] = query
        return data

    async def generate_draft(self, query: str, seo_brief: Dict[str, Any], evidence_pack: List[Dict[str, Any]], brand_tone: str) -> Dict[str, Any]:
        """Generates live, authentic article using Google Gemini without '#' marks or canned text."""
        tag_list = [e["evidence_tag"] for e in evidence_pack] if evidence_pack else ["[EVID-001]", "[EVID-002]"]
        evidence_prompt = "\n".join([f"- {ev['evidence_tag']}: {ev['verbatim_quote']} (Source: {ev['source_title']}, {ev['source_url']})" for ev in evidence_pack[:4]])
        
        prompt = f"""
You are a candid, battle-tested enterprise engineering director and veteran practitioner writing for fellow professionals.
Your top priority: The text MUST score under 15% on Grammarly AI Detector and ZeroGPT by reading 100% authentically human.

CORE GRAMMARLY & ZEROGPT ANTI-DETECTION BLUEPRINT:
1. NEVER USE FORMULAIC TRANSITION STARTERS (GRAMMARLY'S #1 AI TRIGGER):
   - ABSOLUTELY DO NOT start sentences with: "In addition,", "Consequently,", "Furthermore,", "Moreover,", "Specifically,", "Because of this,", "On the other hand,", "Meanwhile,", "As a result,".
   - INSTEAD, use natural conversational transitions: Start sentences with "And", "But", "So", "Still", "Yet", "Instead", "Which means".
   - Or embed transitions inside the sentence: "Our team, however, took a different approach." "That works, of course, until traffic spikes."

2. BREAK SYNTACTIC SYMMETRY (DESTROY MONOTONOUS AI RHYTHM):
   - Drop in 2-4 word blunt punches: "We were wrong.", "Big mistake.", "Not even close.", "It fails right there.", "That hurts.", "Here is the catch."
   - Include 2-3 candid parenthetical asides: "(and yes, we learned that the hard way)", "(which our VP hated)", "(usually around 2 AM on a Friday)".
   - Use em-dashes for natural human pauses: "The real bottleneck — not the shiny vendor slide deck — is messy source data."
   - Ask 2-3 rhetorical questions and answer them immediately: "Why does this happen? Because legacy portals are built like mazes." "Sound familiar?"

3. CONCRETE, GROUNDED REAL-WORLD FRICTION:
   - Talk about messy reality: corrupted PDFs, angry employees, broken search queries, late-night Slack messages, compliance reviews.
   - Speak in first-person plural and singular ("In our production rollout...", "I watched our team spend four days debugging...", "We learned the hard way...").

4. NATURAL HUMAN CONTRACTIONS:
   - Use "don't", "can't", "it's", "doesn't", "we've", "they're", "there's", "won't" throughout.

5. ABSOLUTELY ZERO '#' OR '##' HASH MARKS FOR HEADINGS:
   - Never use '#' anywhere. Format titles and major sections simply as clean uppercase or numbered plain lines separated by '---' dividers.
   Example:
   BEST USE CASES OF AI IN HR DOCUMENTATION
   [intro text]
   ---
   1. AMBIENT WORKFLOWS AND DATA PIPELINES
   [section text]

6. PARAGRAPH & SUBHEADING LENGTH (STRICT YOAST LIMITS):
   - Keep paragraphs SHORT: 30 to 80 words per paragraph. NEVER write a paragraph longer than 110 words.
   - Insert frequent subheadings so no section exceeds 220 words.

7. ZERO CORPORATE AI BUZZWORDS:
   - Never use: "delve into", "tapestry", "beacon of hope", "testament to", "paradigm shift", "harnessing the power", "plays a pivotal role", "rapidly evolving landscape", "in today's fast-paced world".

8. FOCUS KEYWORD IN CRITICAL REAL ESTATE:
   - Include the focus keyword naturally in the title, the very first paragraph (first 80 words), and at least two subheadings.

9. EVIDENCE CITATIONS:
   - Cite factual claims with explicit tags from this list: {tag_list[:3]}.
10. Minimum 800 words, including an ASCII architecture diagram and practical bullet points.

EVIDENCE PACK AVAILABLE FOR CITATION:
{evidence_prompt}
"""
        raw_md = await asyncio.to_thread(self._call_gemini_with_fallback, prompt)
        
        # Ensure zero '#' hashes and human touches
        md = self.humanizer.humanize_text(raw_md)

        first_line = [l.strip() for l in md.split("\n") if l.strip() and not l.strip().startswith("---")][0]
        title = first_line[:80]
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
        
        meta_title = f"{title[:55]}"
        meta_desc = f"Enterprise implementation guide on {query}: production architectures, ROI metrics, and practical setups."
        if len(meta_desc) > 155:
            meta_desc = meta_desc[:152] + "..."

        return {
            "title": title,
            "slug": slug,
            "meta_title": meta_title,
            "meta_description": meta_desc,
            "word_count": len(md.split()),
            "reading_level": "Grade 11-12 (Executive & Professional)",
            "content_markdown": md
        }

    async def rewrite_for_human_naturalness(
        self,
        draft_markdown: str,
        editorial_feedback: Optional[List[str]] = None,
        flagged_sentences: Optional[List[str]] = None
    ) -> str:
        """
        Rewrites the article using live LLM with an aggressive Anti-ZeroGPT prompt,
        specifically targeting flagged AI sentences to beat ZeroGPT with a score under 35%.
        """
        flagged_context = ""
        if flagged_sentences:
            flagged_context = f"""
EXACT SENTENCES FLAGGED AS AI BY ZEROGPT (REWRITE THESE AGGRESSIVELY INTO SHORT, CASUAL HUMAN PHRASES):
{json.dumps(flagged_sentences[:20], indent=2)}
"""

        prompt = f"""
You are an expert human editor and veteran engineering director.
AI detection scanners (Grammarly AI Detector and ZeroGPT) flagged this draft as AI-generated.
Your mission: Rewrite this text so it scores UNDER 15% on Grammarly AI Detector and ZeroGPT.

TACTICS TO DEFEAT GRAMMARLY & ZEROGPT:
1. ELIMINATE FORMULAIC TRANSITION STARTERS (GRAMMARLY'S #1 AI TRIGGER):
   - Replace any sentence beginning with "Consequently,", "In addition,", "Furthermore,", "Moreover,", "Specifically,", "Because of this,", "On the other hand,", "Meanwhile,", "As a result,".
   - Start with natural human words: "And", "But", "So", "Still", "Yet", "Instead", "Which means".
   - Or place transitions inside the sentence: "Our team, however, took a different approach."

2. BREAK SENTENCE SYMMETRY & INJECT ASYMMETRY:
   - Drop in 2-4 word blunt punches: "It works.", "Not quite.", "Big mistake.", "Here is why.", "Nobody warned us."
   - Insert 2 candid parenthetical asides: "(and yes, we learned that the hard way)", "(which our VP hated)".
   - Use em-dashes for human pacing: "The real bottleneck — not the shiny vendor slide deck — is messy source data."
   - Ask 1-2 rhetorical questions and answer them immediately: "Why does this happen? Because legacy portals are built like mazes."

3. FIRST-PERSON PRACTITIONER CONTEXT:
   - Say 'In our deployments...', 'We spent weeks troubleshooting...', 'Engineers often realize...', 'If you look at our logs...'

4. NATURAL HUMAN CONTRACTIONS:
   - Use 'don't', 'can't', 'it's', 'doesn't', 'we've', 'they're', 'there's' everywhere.

5. ZERO ROBOTIC CORPORATE FILLER:
   - Never use 'delve into', 'tapestry', 'beacon', 'testament', 'paradigm shift', 'pivotal', 'moreover', 'furthermore', 'in conclusion', 'rapidly evolving'.

6. PRESERVE ESSENTIAL CONTENT:
   - Strictly keep all [EVID-xxx] citation tags, numbers, statistics, and code blocks.
   - Strictly ZERO '#' or '##' markdown characters. Keep headers as plain uppercase lines.
{flagged_context}

TEXT TO REWRITE:
{draft_markdown}
"""
        try:
            raw_rewritten = await asyncio.to_thread(self._call_gemini_with_fallback, prompt)
            return self.humanizer.humanize_text(raw_rewritten)
        except Exception as e:
            logger.warning(f"LLM humanization rewrite failed ({e}); falling back to deterministic humanizer pass.")
            return self.humanizer.humanize_text(draft_markdown)
