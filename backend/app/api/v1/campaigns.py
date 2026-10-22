from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
import json

from backend.app.models.base import get_db
from backend.app.models.models import Campaign, Source, EvidenceItem, Draft, AuditReport, AgentRunLog
from backend.app.schemas.schemas import CampaignCreate, CampaignDetailResponse, MultiFormatExportResponse
from backend.app.agents.supervisor import SupervisorOrchestrator
from backend.app.agents.format_agent import ContentFormatAgent

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.post("", response_model=Dict[str, Any])
async def create_campaign(payload: CampaignCreate, db: AsyncSession = Depends(get_db)):
    campaign = Campaign(
        name=payload.name,
        target_query=payload.target_query,
        target_audience=payload.target_audience,
        region=payload.region,
        brand_tone=payload.brand_tone,
        status="INITIATED",
        current_step="Pending Execution"
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return {"id": campaign.id, "name": campaign.name, "status": campaign.status}

@router.get("", response_model=List[Dict[str, Any]])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    stmt = select(Campaign).order_by(Campaign.created_at.desc())
    result = await db.execute(stmt)
    campaigns = result.scalars().all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "target_query": c.target_query,
            "status": c.status,
            "current_step": c.current_step,
            "created_at": c.created_at.isoformat()
        }
        for c in campaigns
    ]

@router.get("/{campaign_id}")
async def get_campaign_detail(campaign_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(
            selectinload(Campaign.sources),
            selectinload(Campaign.evidence_items),
            selectinload(Campaign.drafts),
            selectinload(Campaign.agent_logs)
        )
    )
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get latest audit
    latest_draft = campaign.drafts[-1] if campaign.drafts else None
    latest_audit = None
    if latest_draft:
        stmt_audit = (
            select(AuditReport)
            .where(AuditReport.draft_id == latest_draft.id)
            .order_by(AuditReport.created_at.desc())
        )
        res_audit = await db.execute(stmt_audit)
        audit = res_audit.scalar_one_or_none()
        if audit:
            latest_audit = {
                "id": audit.id,
                "overall_score": audit.overall_score,
                "seo_score": audit.seo_score,
                "factuality_score": audit.factuality_score,
                "grammar_score": audit.grammar_score,
                "editorial_score": audit.editorial_score,
                "compliance_score": audit.compliance_score,
                "blocking_issues": json.loads(audit.blocking_issues_json),
                "suggestions": json.loads(audit.suggestions_json),
                "details": json.loads(audit.full_report_json)
            }

    return {
        "id": campaign.id,
        "name": campaign.name,
        "target_query": campaign.target_query,
        "target_audience": campaign.target_audience,
        "region": campaign.region,
        "brand_tone": campaign.brand_tone,
        "status": campaign.status,
        "current_step": campaign.current_step,
        "created_at": campaign.created_at.isoformat(),
        "sources": [
            {
                "id": s.id,
                "url": s.url,
                "title": s.title,
                "publisher": s.publisher,
                "source_type": s.source_type
            }
            for s in campaign.sources
        ],
        "evidence_items": [
            {
                "id": e.id,
                "evidence_tag": e.evidence_tag,
                "claim_supported": e.claim_supported,
                "verbatim_quote": e.verbatim_quote,
                "source_title": e.source_title,
                "source_url": e.source_url,
                "source_tier": e.source_tier,
                "confidence_score": e.confidence_score
            }
            for e in campaign.evidence_items
        ],
        "drafts": [
            {
                "id": d.id,
                "revision_number": d.revision_number,
                "title": d.title,
                "slug": d.slug,
                "meta_title": d.meta_title,
                "meta_description": d.meta_description,
                "word_count": d.word_count,
                "reading_level": d.reading_level,
                "status": d.status,
                "content_markdown": d.content_markdown
            }
            for d in campaign.drafts
        ],
        "agent_logs": [
            {
                "agent_name": l.agent_name,
                "status": l.status,
                "summary": l.summary,
                "details": json.loads(l.details_json) if l.details_json else {},
                "latency_ms": l.latency_ms,
                "created_at": l.created_at.isoformat()
            }
            for l in campaign.agent_logs
        ],
        "latest_audit": latest_audit
    }

@router.post("/{campaign_id}/execute")
async def execute_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    orchestrator = SupervisorOrchestrator(db)
    result = await orchestrator.run_campaign_pipeline(campaign_id)
    return result

@router.post("/{campaign_id}/humanize")
async def humanize_campaign_draft(campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Runs an aggressive anti-AI looping pass to reduce AI detection probability (e.g. Quillbot)."""
    stmt = (
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(selectinload(Campaign.drafts))
    )
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()
    if not campaign or not campaign.drafts:
        raise HTTPException(status_code=404, detail="No draft found to humanize")

    latest_draft = campaign.drafts[-1]
    from backend.app.services.humanizer import HumanizerEngine
    humanizer = HumanizerEngine()
    
    loop_result = humanizer.run_humanization_loop(
        latest_draft.content_markdown,
        target_ai_threshold=18.0,
        max_iterations=4
    )

    latest_draft.content_markdown = loop_result["final_text"]
    latest_draft.word_count = len(loop_result["final_text"].split())
    await db.commit()

    return {
        "status": "HUMANIZED",
        "initial_ai_score": loop_result["initial_ai_score"],
        "final_ai_score": loop_result["final_ai_score"],
        "final_human_score": loop_result["final_human_score"],
        "iterations_count": loop_result["iterations_count"],
        "loop_history": loop_result["loop_history"],
        "humanized_markdown": loop_result["final_text"]
    }

@router.get("/{campaign_id}/export")
async def export_campaign_assets(campaign_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(selectinload(Campaign.drafts))
    )
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()
    if not campaign or not campaign.drafts:
        raise HTTPException(status_code=404, detail="No approved drafts available for export")

    latest_draft = campaign.drafts[-1]
    formatter = ContentFormatAgent()
    export_bundle = formatter.execute(
        latest_draft.content_markdown,
        {"recommended_meta_title": latest_draft.meta_title or latest_draft.title}
    )
    return export_bundle
