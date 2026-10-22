from typing import Dict, Any, List
from backend.app.services.llm_provider import LLMProvider
from backend.app.core.logger import get_logger

logger = get_logger("WriterAgent")

class WriterAgent:
    def __init__(self):
        self.llm_provider = LLMProvider()

    async def execute(self, query: str, seo_brief: Dict[str, Any], evidence_pack: List[Dict[str, Any]], brand_tone: str) -> Dict[str, Any]:
        """
        Drafts a high-impact, clinically grounded, human-like article adhering strictly to the evidence pack.
        """
        logger.info(f"WriterAgent drafting article for '{query}' with {len(evidence_pack)} evidence items.")
        draft = await self.llm_provider.generate_draft(query, seo_brief, evidence_pack, brand_tone)
        return draft
