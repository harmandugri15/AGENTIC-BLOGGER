from typing import Dict, Any, List
from backend.app.services.llm_provider import LLMProvider
from backend.app.services.yoast_seo_engine import YoastSEOEngine
from backend.app.core.logger import get_logger

logger = get_logger("SEOIntelligenceAgent")

class SEOIntelligenceAgent:
    def __init__(self):
        self.llm_provider = LLMProvider()
        self.yoast_engine = YoastSEOEngine()

    async def execute(self, query: str, competitor_sources: List[Dict[str, Any]], lsi_terms: List[str] = None) -> Dict[str, Any]:
        """
        Evaluates search intent, extracts focus keyword, maps competitor gaps, and establishes Yoast SEO guidelines.
        Enriches strategy with real corpus LSI terms fetched from Datamuse Public API.
        """
        logger.info(f"Generating SEO strategy & competitor gap matrix for '{query}'")
        seo_strategy = await self.llm_provider.generate_seo_strategy(query, competitor_sources)
        
        # Extract deterministic focus keyword
        focus_kw = self.yoast_engine.extract_focus_keyword(query, seo_strategy.get("primary_keywords", []))
        seo_strategy["focus_keyword"] = focus_kw

        # Ensure focus keyword is in primary keywords
        if "primary_keywords" not in seo_strategy:
            seo_strategy["primary_keywords"] = []
        if focus_kw not in seo_strategy["primary_keywords"]:
            seo_strategy["primary_keywords"].insert(0, focus_kw)

        # Merge real LSI entities from Datamuse Public API
        if lsi_terms:
            existing = set(e.lower() for e in seo_strategy.get("semantic_entities", []))
            for term in lsi_terms[:8]:
                if term.lower() not in existing:
                    seo_strategy.setdefault("semantic_entities", []).append(term.title())
            seo_strategy["public_apis_used"] = ["Datamuse Semantic Engine (public-apis)"]

        return seo_strategy
