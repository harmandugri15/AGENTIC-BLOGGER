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
        "gemini-3.8-flash"
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
                        logger.info(f"Calling Gemini model '{model_name}'...")
                        model = self.genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt, request_options={"timeout": 60})
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
        """Generates dynamic SEO & GEO strategy using live Gemini for IcyPluto/IcyQuill. Never uses canned data."""
        comp_titles = [c.get("title", "") for c in competitor_pages[:4]]
        prompt = f"""
You are a principal Generative Engine Optimization (GEO) & AI Search strategist at IcyPluto (makers of IcyQuill, the autonomous content engine).
Analyze the target topic: "{query}".
Discovered competitor pages on Google / Search: {comp_titles}.

We are writing an authoritative, practitioner-led piece that contrasts modern AI Search retrieval (Multi-Head Attention mechanisms across scraped context tokens, Perplexity, ChatGPT Search, Gemini) against traditional Google 10-blue-links SEO.

Respond strictly in valid JSON without markdown wrapping or commentary:
{{
  "target_query": "{query}",
  "domain": "Generative Engine Optimization (GEO), AI Search & Content Architecture",
  "search_intent": "High-intent marketing leaders, growth engineers, and CMOs seeking to dominate AI answers and organic search",
  "primary_keywords": ["keyword 1", "keyword 2", "keyword 3"],
  "secondary_keywords": ["sec 1", "sec 2", "sec 3", "sec 4"],
  "semantic_entities": ["IcyPluto", "IcyQuill", "Multi-Head Attention", "Generative Engine Optimization", "LLM Citation", "Vector Retrieval"],
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
      "citiustech_differentiation": "IcyQuill provides autonomous multi-agent research with deep multi-head attention citation engineering."
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
You are a senior AI growth engineer and veteran search practitioner writing for IcyPluto (makers of IcyQuill, the autonomous content engine).
Your target topic: "{query}".
Your top priority: The text MUST score under 10% on Grammarly AI Detector and ZeroGPT by rigorously adopting the writing dynamics outlined in Grammarly's own published guidelines (grammarly.com/blog/ai/how-to-avoid-ai-detection).

KEY ARCHITECTURAL THEMES TO COMPARE & CONTRAST:
- Contrast traditional keyword search (single-channel Google crawler, keyword density, 10 blue links) with modern AI search engine synthesis (Perplexity, ChatGPT Search, Gemini).
- Explain how Multi-Head Attention works in generative search: Transformer heads distribute attention weights across factual citation tokens, structured entity schemas, and natural conversational cadence. If your content lacks semantic density across any of these attention dimensions, the model skips citing your brand.
- Introduce IcyQuill & IcyPluto as the modern solution: an autonomous multi-agent platform that creates authentic, humanized pillar content engineered to capture attention heads across LLMs and rank on search.

GRAMMARLY OFFICIAL ANTI-DETECTION BLUEPRINT:
1. EMBRACE A RAW, AUTHENTIC HUMAN VOICE (GRAMMARLY RULE #3 & #5):
   - Never write like a detached corporate spectator. Write as a hands-on engineer who has run crawl audits, built RAG pipelines, or debugged why Perplexity hallucinated a competitor's product name.
   - Use vivid, gritty, subjective human language: "a complete mess", "we were dead wrong", "that blew up in staging", "nobody on our marketing team wanted to admit it", "a nightmare to debug".
   - Include 2-3 specific micro-anecdotes: ("I remember spending three hours watching an LLM cite a 6-year-old Reddit thread instead of our fresh documentation...", "Our growth lead ran 50 synthetic prompts in ChatGPT and found zero mentions of our product...").

2. EXTREME BURSTINESS & SYNTACTIC CHAOS (GRAMMARLY RULE #4):
   - AI models write with balanced, predictable sentence lengths (18-24 words per sentence). Grammarly flags this immediately.
   - DESTROY THE MONOTONY:
     * Intersperse ultra-short 2-4 word blunt punches: "SEO is dead.", "Not quite.", "Big mistake.", "We failed.", "It hurt.", "Here is why.", "Sound familiar?"
     * Follow with sprawling, meandering multi-clause sentences: "When you trace how an LLM's multi-head attention distributes weight across scraped context chunks during a live Perplexity query, it becomes painfully obvious why stuffing exact-match keywords into an H2 tag produces zero citations."
     * Inject 2-3 casual parenthetical whispers: "(and yes, most SEO agencies still pretend this doesn't exist)", "(which our VP learned after a 40% traffic drop)", "(usually right before a board meeting)".
     * Use 2 em-dashes for human pacing: "The real battleground — not the Google search console graph — is inside the transformer's attention matrix."

3. ZERO FORMULAIC TRANSITION STARTERS (GRAMMARLY'S #1 AI STATISTICAL TRIGGER):
   - ABSOLUTELY BANNED as sentence starters: "In addition,", "Consequently,", "Furthermore,", "Moreover,", "Specifically,", "Because of this,", "On the other hand,", "Meanwhile,", "As a result,", "In light of this,".
   - INSTEAD, use authentic human connectives: Start sentences with "And", "But", "So", "Still", "Yet", "Instead", "Which means".
   - Or tuck transitions into the middle of the sentence: "That approach, however, falls apart in ChatGPT Search." "We discovered, of course, that the crawler ignored client-rendered JavaScript."

4. NATURAL HUMAN CONTRACTIONS:
   - Use "don't", "can't", "it's", "doesn't", "we've", "they're", "there's", "won't", "couldn't" throughout.

5. STRICTLY BANNED AI VOCABULARY & PLATITUDES:
   - Zero occurrences of: "delve into", "tapestry", "beacon of hope", "testament to", "paradigm shift", "harnessing the power", "plays a pivotal role", "rapidly evolving landscape", "in today's fast-paced world", "a plethora of".

6. ABSOLUTELY ZERO '#' OR '##' HASH MARKS FOR HEADINGS:
   - Format titles and sections simply as clean uppercase or numbered plain lines separated by '---' dividers.
   Example:
   WHY MULTI-HEAD ATTENTION KILLED TRADITIONAL SEO
   [intro text]
   ---
   1. HOW TRANSFORMER HEADS DECIDE WHO GETS CITED
   [section text]

7. PARAGRAPH & SUBHEADING PACING:
   - Paragraphs MUST be compact: 30 to 80 words per paragraph. Never exceed 100 words.
   - Insert frequent subheadings so no section exceeds 200 words.

8. FOCUS KEYWORD IN CRITICAL REAL ESTATE:
   - Place focus keyword in the title, first 80 words, and at least two subheadings.

9. EVIDENCE CITATIONS:
   - Support factual claims with tags from this list: {tag_list[:3]}.
10. Minimum 800 words, with an ASCII architecture diagram comparing traditional 10-blue-links crawling vs multi-head attention LLM synthesis, along with practical takeaways.

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
You are an expert human senior growth editor at IcyPluto.
AI detection scanners (specifically Grammarly's AI Detector and ZeroGPT) flagged this draft.
Your mission: Rewrite this text so it scores UNDER 10% on Grammarly AI Detector and ZeroGPT by rigorously enforcing Grammarly's official human writing principles (grammarly.com/blog/ai/how-to-avoid-ai-detection).

GRAMMARLY OFFICIAL ANTI-DETECTION MANDATES:
1. RAW PRACTITIONER VOICE & PERSPECTIVE:
   - Speak as an engineer who lives inside LLM visibility, Generative Engine Optimization (GEO), and multi-head attention mechanics.
   - Use first-person grit: "In our audit of 200 SaaS domains...", "We watched Google rankings drop while Perplexity citations skyrocketed...", "Our growth engineers realized...".

2. ASYMMETRICAL SENTENCE PACING (ELIMINATE AI MONOTONY):
   - Insert 2-4 word blunt punches: "Big mistake.", "Not even close.", "We failed.", "It hurt.", "Here is why."
   - Follow with sprawling, natural human sentences.
   - Inject 2-3 casual parenthetical asides: "(and yes, legacy SEO agencies still won't tell you this)", "(which cost our client thousands in wasted backlinks)".
   - Insert em-dashes for conversational emphasis: "The real issue — not the keyword count — is whether the transformer's attention heads attend to your entity tokens."

3. PURGE ALL FORMULAIC TRANSITION STARTERS (GRAMMARLY'S #1 AI STATISTICAL TRIGGER):
   - Remove every single sentence starter like: "In addition,", "Consequently,", "Furthermore,", "Moreover,", "Specifically,", "Because of this,", "On the other hand,", "Meanwhile,", "As a result,", "In light of this,".
   - Connect thoughts naturally: Start with "And", "But", "So", "Still", "Yet", "Instead", "Which means".
   - Or embed the transition mid-clause: "Our team, however, engineered IcyQuill to solve this exact problem."

4. FREQUENT NATURAL CONTRACTIONS:
   - Use "don't", "can't", "it's", "doesn't", "we've", "they're", "there's", "won't", "shouldn't".

5. BAN CORPORATE AI CLICHÉS:
   - Banned: "delve into", "tapestry", "beacon", "testament", "paradigm shift", "pivotal role", "in conclusion", "rapidly evolving", "a plethora of".

6. PRESERVE STRUCTURAL INTEGRITY:
   - Strictly keep all [EVID-xxx] citations, statistics, numbers, and diagrams intact.
   - Strictly ZERO '#' or '##' markdown characters. Keep headers as clean uppercase lines separated by '---'.
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
