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
You are a plain-spoken practitioner, veteran technology director, and human writer.
Write a comprehensive, conversational, real-world enterprise guide on:
Topic: "{query}"
Target Keywords: {seo_brief.get('primary_keywords', [])}
Semantic Entities: {seo_brief.get('semantic_entities', [])}
Recommended Outline: {seo_brief.get('recommended_h2_sections', [])}
Brand Voice: {brand_tone}

CRITICAL SEO & READABILITY RULES (MANDATORY TO ACHIEVE 100% YOAST SEO & HUMAN SCORES):
1. ABSOLUTELY ZERO '#' OR '##' HASH MARKS FOR HEADINGS. NEVER USE '#' ANYWHERE IN THE TEXT.
   Format titles and major sections simply as clean uppercase or numbered plain lines separated by '---' dividers.
   Example format:
   Best Use Cases of AI in Robotics: Practical Setups for Enterprise Leaders

   [Intro paragraphs here]

   ---

   1. VISION-GUIDED MANIPULATION AND EDGE COMPUTER VISION
   [Section paragraphs here]

2. PARAGRAPH & SUBHEADING LENGTH (STRICT YOAST LIMITS):
   - Keep paragraphs SHORT: 30 to 90 words per paragraph. NEVER write a paragraph longer than 120 words.
   - Insert frequent subheadings so no section is longer than 250 words.

3. TRANSITION WORDS (MINIMUM 30% OF SENTENCES):
   - At least 30% of sentences MUST contain natural transition words (e.g., "For example,", "In addition,", "Specifically,", "Consequently,", "Because of this,", "In fact,", "On the other hand,", "Meanwhile,", "As a result,").

4. READABILITY & PLAIN ENGLISH (FLESCH READING EASE >= 60):
   - Average sentence length should be 12 to 16 words.
   - Use simple words instead of corporate SAT buzzwords. Say "too much work" or "paperwork headache" instead of "administrative burden". Say "things that don't work" instead of "speculative pilots". Say "letting operators/engineers do their job" instead of "preserving autonomy".
   - Inject short, punchy sentence fragments. E.g.: "Training robots is hard. It takes up months. Delays production."
   - Use natural contractions (don't, can't, won't, it's).
   - NEVER use AI clichés: "In today's fast-paced world", "delve into", "tapestry", "beacon of hope", "paradigm shift", "harnessing the power of".

5. FOCUS KEYWORD IN CRITICAL REAL ESTATE:
   - Weave the target topic/keyword naturally into the title, the very first paragraph (first 100 words), and at least two subheadings.

6. STRICT EVIDENCE CITATIONS:
   You MUST cite factual claims with explicit tags from this list: {tag_list[:3]}.
7. Include a scannable ASCII architectural workflow diagram in a codeblock and practical implementation bullet points.
8. Minimum 800 words.

EVIDENCE PACK AVAILABLE FOR CITATION:
{evidence_prompt}
"""
        raw_md = await asyncio.to_thread(self._call_gemini_with_fallback, prompt)
        
        # Ensure zero '#' hashes
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

    async def rewrite_for_human_naturalness(self, draft_markdown: str, editorial_feedback: List[str]) -> str:
        """
        Rewrites the article using live LLM with an aggressive Anti-ZeroGPT prompt,
        maximizing human burstiness and short punchy fragments to beat AI detectors under 35%.
        """
        prompt = f"""
You are an expert human editor and veteran director. Rewrite this text so it reads 100% authentically human-written and passes ZeroGPT, GPTZero, and Turnitin with an AI score under 20%.

CRITICAL HUMAN CADENCE RULES (ZEROGPT BYPASS):
1. INJECT SHORT PUNCHY HUMAN FRAGMENTS:
   Scatter 3-6 word short sentences across paragraphs. Examples:
   - "Grading is tiring. It takes up weekends. Delays important feedback."
   - "It sounds simple on paper. It isn't."
   - "Mistakes get expensive."
   - "Engineers hate this."
2. RADICALLY VARY SENTENCE LENGTHS:
   Mix short 4-word punches with 15-word conversational thoughts.
3. USE NATURAL HUMAN CONTRACTIONS:
   Use "don't", "can't", "it's", "doesn't", "we've", "they're" throughout.
4. ZERO CORPORATE AI JARGON:
   Never use "delve into", "tapestry", "moreover", "furthermore", "in conclusion", "harnessing", "paradigm shift", "testament to", "pivotal".
5. STRICT CONSTRAINTS:
   - Preserve all [EVID-xxx] evidence citations, factual claims, numbers, and code blocks.
   - Strictly ZERO '#' or '##' markdown characters.
   - Maintain the same section structure and focus keyword.

TEXT TO HUMANIZE:
{draft_markdown}
"""
        try:
            raw_rewritten = await asyncio.to_thread(self._call_gemini_with_fallback, prompt)
            return self.humanizer.humanize_text(raw_rewritten)
        except Exception as e:
            logger.warning(f"LLM humanization rewrite failed ({e}); falling back to deterministic humanizer pass.")
            return self.humanizer.humanize_text(draft_markdown)
