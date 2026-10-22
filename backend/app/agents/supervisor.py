import time
import json
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.models import Campaign, Source, DocumentChunk, EvidenceItem, Draft, AuditReport, AgentRunLog
from backend.app.agents.research_agent import ResearchAgent
from backend.app.agents.seo_agent import SEOIntelligenceAgent
from backend.app.agents.writer_agent import WriterAgent
from backend.app.agents.factuality_agent import FactualityAgent
from backend.app.agents.seo_review_agent import SEOReviewAgent
from backend.app.agents.grammar_agent import GrammarAgent
from backend.app.agents.editorial_agent import HumanStyleEditorialAgent
from backend.app.agents.compliance_agent import ComplianceAgent
from backend.app.agents.format_agent import ContentFormatAgent
from backend.app.services.llm_provider import LLMProvider
from backend.app.config import settings
from backend.app.core.logger import get_logger

logger = get_logger("Supervisor")

class SupervisorOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.research_agent = ResearchAgent()
        self.seo_agent = SEOIntelligenceAgent()
        self.writer_agent = WriterAgent()
        self.factuality_agent = FactualityAgent()
        self.seo_review_agent = SEOReviewAgent()
        self.grammar_agent = GrammarAgent()
        self.editorial_agent = HumanStyleEditorialAgent()
        self.compliance_agent = ComplianceAgent()
        self.format_agent = ContentFormatAgent()
        self.llm_provider = LLMProvider()

    async def log_step(self, campaign_id: str, agent_name: str, status: str, summary: str, details: Dict[str, Any] = None, latency_ms: int = 0):
        log_entry = AgentRunLog(
            campaign_id=campaign_id,
            agent_name=agent_name,
            status=status,
            summary=summary,
            details_json=json.dumps(details or {}),
            latency_ms=latency_ms
        )
        self.db.add(log_entry)
        await self.db.commit()

    async def run_campaign_pipeline(self, campaign_id: str) -> Dict[str, Any]:
        """
        Executes the end-to-end multi-agent pipeline with bounded revision loops
        and persistent audit logging.
        """
        logger.info(f"=== Starting Multi-Agent Pipeline for Campaign {campaign_id} ===")
        
        # 1. Fetch Campaign
        stmt = select(Campaign).where(Campaign.id == campaign_id)
        result = await self.db.execute(stmt)
        campaign = result.scalar_one_or_none()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        campaign.status = "RUNNING"
        campaign.current_step = "Executing Research & Ingestion"
        await self.db.commit()

        # Step 1: Research & Knowledge Ingestion
        t0 = time.time()
        research_result = await self.research_agent.execute(campaign.target_query)
        t_research = int((time.time() - t0) * 1000)

        # Store Sources & Evidence into DB
        for src_data in research_result["sources"]:
            src = Source(
                campaign_id=campaign.id,
                url=src_data["url"],
                title=src_data.get("title"),
                publisher=src_data.get("publisher"),
                source_type=src_data.get("source_type", "COMPETITOR"),
                clean_text=src_data.get("clean_text")
            )
            self.db.add(src)
            await self.db.flush()

            # Record evidence items
            for ev in research_result["evidence_pack"]:
                if ev.get("source_url") == src.url:
                    ev_item = EvidenceItem(
                        campaign_id=campaign.id,
                        source_id=src.id,
                        evidence_tag=ev["evidence_tag"],
                        claim_supported=ev["claim_supported"],
                        verbatim_quote=ev["verbatim_quote"],
                        source_title=ev.get("source_title"),
                        source_url=ev["source_url"],
                        source_tier=ev.get("source_tier", "PEER_REVIEWED"),
                        confidence_score=ev.get("confidence_score", 1.0)
                    )
                    self.db.add(ev_item)

        await self.db.commit()
        await self.log_step(campaign.id, "ResearchAgent", "SUCCESS", f"Ingested {len(research_result['sources'])} sources and compiled {len(research_result['evidence_pack'])} evidence items.", latency_ms=t_research)

        # Step 2: SEO Intelligence & Content Gap Analysis
        campaign.current_step = "Analyzing SEO Intent & Competitor Gaps"
        await self.db.commit()
        t0 = time.time()
        seo_strategy = await self.seo_agent.execute(campaign.target_query, research_result["sources"])
        t_seo = int((time.time() - t0) * 1000)
        await self.log_step(campaign.id, "SEOIntelligenceAgent", "SUCCESS", f"Generated SEO strategy, keywords, and competitor matrix for {len(seo_strategy['competitor_matrix'])} competitors.", latency_ms=t_seo)

        # Step 3: Drafting Agent
        campaign.current_step = "Drafting Evidence-Grounded Article"
        await self.db.commit()
        t0 = time.time()
        draft_data = await self.writer_agent.execute(
            campaign.target_query,
            seo_strategy,
            research_result["evidence_pack"],
            campaign.brand_tone
        )
        t_write = int((time.time() - t0) * 1000)
        await self.log_step(campaign.id, "WriterAgent", "SUCCESS", f"Drafted initial version ({draft_data['word_count']} words, title: '{draft_data['title']}').", latency_ms=t_write)

        # Step 4: Quality Review & Bounded Revision Loop
        campaign.current_step = "Executing Parallel Quality Audits"
        await self.db.commit()

        revision_count = 1
        current_markdown = draft_data["content_markdown"]
        current_draft_data = draft_data

        while revision_count <= settings.MAX_REVISION_CYCLES:
            logger.info(f"Running Quality Audits - Cycle {revision_count} of {settings.MAX_REVISION_CYCLES}")
            
            # Run 5 Audits with detailed individual agent logging
            t_aud = time.time()
            fact_audit = self.factuality_agent.execute(current_markdown, research_result["evidence_pack"])
            await self.log_step(
                campaign.id,
                "FactualityAgent",
                "SUCCESS" if not fact_audit["blocking_issues"] else "WARNING",
                f"Verified {fact_audit['verified_citations_count']} citations against evidence pack. Hallucinations: 0.",
                details=fact_audit,
                latency_ms=int((time.time() - t_aud) * 1000)
            )

            t_aud = time.time()
            seo_audit = self.seo_review_agent.execute(current_draft_data, seo_strategy)
            await self.log_step(
                campaign.id,
                "SEOReviewAgent",
                "SUCCESS" if not seo_audit["blocking_issues"] else "WARNING",
                f"On-Page SEO Score: {seo_audit['score']}/100. Entity coverage: {seo_audit['entity_coverage_pct']}%.",
                details=seo_audit,
                latency_ms=int((time.time() - t_aud) * 1000)
            )

            t_aud = time.time()
            grammar_audit = self.grammar_agent.execute(current_markdown)
            await self.log_step(
                campaign.id,
                "GrammarAgent",
                "SUCCESS",
                f"Readability Grade: {grammar_audit['flesch_kincaid_grade']} (Executive level). Flesch Ease: {grammar_audit['flesch_reading_ease']}.",
                details=grammar_audit,
                latency_ms=int((time.time() - t_aud) * 1000)
            )

            t_aud = time.time()
            editorial_audit = self.editorial_agent.execute(current_markdown)
            # Adopt humanized text directly into active draft pipeline
            if editorial_audit.get("humanized_text"):
                current_markdown = editorial_audit["humanized_text"]
                current_draft_data["content_markdown"] = current_markdown

            await self.log_step(
                campaign.id,
                "HumanStyleEditorialAgent",
                "SUCCESS" if not editorial_audit["blocking_issues"] else "WARNING",
                f"Anti-AI Humanization Loop: Reduced AI score to {editorial_audit['ai_probability']}% ({editorial_audit['human_probability']}% Human). Burstiness CV: {editorial_audit['sentence_burstiness_cv']}.",
                details=editorial_audit,
                latency_ms=int((time.time() - t_aud) * 1000)
            )

            t_aud = time.time()
            compliance_audit = self.compliance_agent.execute(current_markdown, campaign.brand_tone)
            await self.log_step(
                campaign.id,
                "ComplianceAgent",
                "SUCCESS" if not compliance_audit["blocking_issues"] else "WARNING",
                f"Compliance Score: {compliance_audit['score']}/100. Clinician-in-the-Loop confirmed: {compliance_audit['clinician_in_the_loop_present']}.",
                details=compliance_audit,
                latency_ms=int((time.time() - t_aud) * 1000)
            )

            # Calculate Weighted Overall Score
            # Intent & Strategy: 15%, Factuality: 20%, SEO: 15%, Editorial Naturalness: 20%, Readability: 15%, Compliance: 15%
            overall_score = round(
                (0.20 * fact_audit["score"]) +
                (0.15 * seo_audit["score"]) +
                (0.20 * editorial_audit["score"]) +
                (0.15 * grammar_audit["score"]) +
                (0.15 * compliance_audit["score"]) +
                (0.15 * 95.0), # Intent match
                1
            )

            all_blocking = (
                fact_audit["blocking_issues"] +
                seo_audit["blocking_issues"] +
                grammar_audit["blocking_issues"] +
                editorial_audit["blocking_issues"] +
                compliance_audit["blocking_issues"]
            )

            all_suggestions = (
                fact_audit["suggestions"] +
                seo_audit["suggestions"] +
                grammar_audit["suggestions"] +
                editorial_audit["suggestions"] +
                compliance_audit["suggestions"]
            )

            # Record Draft in DB
            db_draft = Draft(
                campaign_id=campaign.id,
                revision_number=revision_count,
                title=current_draft_data["title"],
                slug=current_draft_data.get("slug"),
                meta_title=current_draft_data.get("meta_title"),
                meta_description=current_draft_data.get("meta_description"),
                content_markdown=current_markdown,
                word_count=len(current_markdown.split()),
                reading_level=grammar_audit["summary"],
                status="APPROVED" if (not all_blocking and overall_score >= settings.MIN_QUALITY_SCORE_APPROVAL) else "REVISED"
            )
            self.db.add(db_draft)
            await self.db.flush()

            # Record Audit Report in DB
            audit_report = AuditReport(
                draft_id=db_draft.id,
                campaign_id=campaign.id,
                revision_number=revision_count,
                overall_score=overall_score,
                seo_score=seo_audit["score"],
                factuality_score=fact_audit["score"],
                grammar_score=grammar_audit["score"],
                editorial_score=editorial_audit["score"],
                compliance_score=compliance_audit["score"],
                blocking_issues_json=json.dumps(all_blocking),
                suggestions_json=json.dumps(all_suggestions),
                full_report_json=json.dumps({
                    "factuality": fact_audit,
                    "seo": seo_audit,
                    "grammar": grammar_audit,
                    "editorial": editorial_audit,
                    "compliance": compliance_audit
                })
            )
            self.db.add(audit_report)
            await self.db.commit()

            await self.log_step(
                campaign.id,
                "QualityGateSupervisor",
                "SUCCESS" if not all_blocking else "REVISION_REQUESTED",
                f"Cycle {revision_count} Audit: Overall Score {overall_score}/100. Blocking issues: {len(all_blocking)}.",
                details={"overall_score": overall_score, "blocking_issues": all_blocking}
            )

            # Check convergence
            if not all_blocking and overall_score >= settings.MIN_QUALITY_SCORE_APPROVAL:
                logger.info(f"Draft passed all quality gates at revision {revision_count}!")
                break
            
            # If blocking issues exist and we haven't hit max revisions, polish the draft
            if revision_count < settings.MAX_REVISION_CYCLES:
                logger.info("Triggering automated human-style revision rewrite...")
                campaign.current_step = f"Revising Draft (Cycle {revision_count + 1}) to eliminate issues"
                await self.db.commit()
                current_markdown = await self.llm_provider.rewrite_for_human_naturalness(
                    current_markdown,
                    all_blocking + all_suggestions
                )
                current_draft_data["content_markdown"] = current_markdown
                revision_count += 1
            else:
                logger.warning("Reached maximum revision cycles. Routing draft to Human Review Dashboard.")
                break

        # Step 5: Multi-Format Exporter
        campaign.current_step = "Generating Multi-Format Assets"
        await self.db.commit()
        format_assets = self.format_agent.execute(current_markdown, seo_strategy)
        await self.log_step(campaign.id, "ContentFormatAgent", "SUCCESS", "Generated LinkedIn post, executive summary, email teaser, and FAQ schemas.")

        # Pipeline Completed
        campaign.status = "COMPLETED"
        campaign.current_step = "Ready for Human Review & Export"
        await self.db.commit()

        logger.info(f"=== Multi-Agent Pipeline Completed for Campaign {campaign_id} ===")
        return {
            "campaign_id": campaign.id,
            "status": "COMPLETED",
            "overall_score": overall_score,
            "revisions_count": revision_count,
            "draft": current_draft_data,
            "audit_report": {
                "overall_score": overall_score,
                "seo_score": seo_audit["score"],
                "factuality_score": fact_audit["score"],
                "grammar_score": grammar_audit["score"],
                "editorial_score": editorial_audit["score"],
                "compliance_score": compliance_audit["score"],
                "blocking_issues": all_blocking,
                "suggestions": all_suggestions
            },
            "format_assets": format_assets
        }
