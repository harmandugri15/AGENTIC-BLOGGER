import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.app.models.base import Base
from backend.app.models.models import Campaign
from backend.app.agents.research_agent import ResearchAgent
from backend.app.agents.seo_agent import SEOIntelligenceAgent
from backend.app.agents.writer_agent import WriterAgent
from backend.app.agents.factuality_agent import FactualityAgent
from backend.app.agents.seo_review_agent import SEOReviewAgent
from backend.app.agents.grammar_agent import GrammarAgent
from backend.app.agents.editorial_agent import HumanStyleEditorialAgent
from backend.app.agents.compliance_agent import ComplianceAgent
from backend.app.agents.supervisor import SupervisorOrchestrator

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

@pytest.mark.asyncio
async def test_research_agent():
    agent = ResearchAgent()
    result = await agent.execute("AI in healthcare use cases")
    assert "sources" in result
    assert len(result["sources"]) > 0
    assert "evidence_pack" in result
    assert len(result["evidence_pack"]) > 0
    assert result["evidence_pack"][0]["evidence_tag"].startswith("[EVID-")

@pytest.mark.asyncio
async def test_seo_and_writer_agents():
    seo_agent = SEOIntelligenceAgent()
    writer_agent = WriterAgent()
    
    seo_brief = await seo_agent.execute("AI in healthcare", [])
    assert "primary_keywords" in seo_brief
    assert "competitor_matrix" in seo_brief
    assert len(seo_brief["competitor_matrix"]) > 0

    mock_evidence = [
        {
            "evidence_tag": "[EVID-001]",
            "claim_supported": "Ambient clinical documentation",
            "verbatim_quote": "Ambient voice systems reduce physician documentation by 45 minutes per shift.",
            "source_title": "Nature Medicine",
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/38291044/",
            "source_tier": "PEER_REVIEWED",
            "confidence_score": 98.0
        }
    ]
    
    draft = await writer_agent.execute("AI in healthcare", seo_brief, mock_evidence, "Authoritative")
    assert "content_markdown" in draft
    assert "[EVID-001]" in draft["content_markdown"]
    assert draft["word_count"] > 400

@pytest.mark.asyncio
async def test_quality_audits():
    markdown = """# Best Use Cases of AI in Healthcare

Physicians spend two hours completing EHR documentation for each hour of care [EVID-001].
Ambient clinical voice captures natural doctor-patient dialogues and drafts structured SOAP notes.

## 1. Ambient Clinical Documentation
Integrating directly into Epic or Oracle Health via SMART on FHIR interfaces prevents fatigue.
A strict Clinician-in-the-Loop review ensures diagnostic safety.

## 2. Automated Prior Authorization
CMS-0057-F mandates electronic decisions via standardized FHIR APIs.

## 3. Real-Time Clinical Deterioration
Predictive models alert intensivists to sepsis hours before vitals crash.
CitiusTech implements robust HIPAA de-identification pipelines.
"""
    mock_evidence = [
        {
            "evidence_tag": "[EVID-001]",
            "verbatim_quote": "Physicians spend two hours completing EHR documentation",
            "source_title": "PubMed Study",
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/123/"
        }
    ]

    fact_agent = FactualityAgent()
    fact_res = fact_agent.execute(markdown, mock_evidence)
    assert fact_res["score"] >= 80

    editorial_agent = HumanStyleEditorialAgent()
    edit_res = editorial_agent.execute(markdown)
    assert edit_res["score"] >= 50
    assert "humanized_text" in edit_res

    comp_agent = ComplianceAgent()
    comp_res = comp_agent.execute(markdown, "Authoritative")
    assert comp_res["score"] >= 90
    assert comp_res["clinician_in_the_loop_present"] is True

@pytest.mark.asyncio
async def test_supervisor_end_to_end(async_session: AsyncSession):
    # 1. Create Campaign
    campaign = Campaign(
        name="AI in Healthcare Benchmark",
        target_query="Create a blog on the best use cases of AI in healthcare",
        target_audience="Healthcare CIOs & CMIOs",
        region="US",
        brand_tone="Clinical, Nuanced, Authoritative"
    )
    async_session.add(campaign)
    await async_session.commit()
    await async_session.refresh(campaign)

    # 2. Run Supervisor Pipeline
    orchestrator = SupervisorOrchestrator(async_session)
    result = await orchestrator.run_campaign_pipeline(campaign.id)

    assert result["status"] == "COMPLETED"
    assert result["overall_score"] >= 85.0
    assert "draft" in result
    assert "format_assets" in result
    assert "linkedin_thought_leadership" in result["format_assets"]
    assert "executive_summary" in result["format_assets"]
