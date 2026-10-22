from typing import Dict, Any, List
from backend.app.services.llm_provider import LLMProvider
from backend.app.core.logger import get_logger

logger = get_logger("SEOIntelligenceAgent")

class SEOIntelligenceAgent:
    def __init__(self):
        self.llm_provider = LLMProvider()

    async def execute(self, query: str, competitor_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates search intent, extracts keywords, maps competitor gaps, and establishes SEO guidelines.
        """
        logger.info(f"Generating SEO strategy & competitor gap matrix for '{query}'")
        seo_strategy = await self.llm_provider.generate_seo_strategy(query, competitor_sources)
        return seo_strategy
