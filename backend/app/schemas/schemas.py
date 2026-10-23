from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CampaignCreate(BaseModel):
    name: str = Field(..., example="AI in Healthcare Enterprise Leadership Blog")
    target_query: str = Field(..., example="Create a blog on the best use cases of AI in healthcare")
    target_audience: Optional[str] = "Healthcare CIOs, Clinical Informaticists, Healthtech Leaders"
    region: Optional[str] = "US"
    brand_tone: Optional[str] = "Authoritative, Nuanced, Clinically Rigorous, Forward-Looking"
    custom_competitor_urls: Optional[List[str]] = []

class SourceResponse(BaseModel):
    id: str
    url: str
    domain: Optional[str]
    title: Optional[str]
    publisher: Optional[str]
    source_type: str
    status: str
    publication_date: Optional[str]
    summary: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class EvidenceItemResponse(BaseModel):
    id: str
    evidence_tag: str
    claim_supported: str
    verbatim_quote: str
    source_title: Optional[str]
    source_url: str
    source_tier: str
    confidence_score: float

    model_config = ConfigDict(from_attributes=True)

class CompetitorMatrixItem(BaseModel):
    competitor: str
    url: str
    strengths: List[str]
    content_gaps: List[str]
    citiustech_differentiation: str

class SEOStrategyResponse(BaseModel):
    target_query: str
    search_intent: str
    primary_keywords: List[str]
    secondary_keywords: List[str]
    semantic_entities: List[str]
    target_slug: str
    recommended_meta_title: str
    recommended_meta_description: str
    recommended_h2_sections: List[str]
    competitor_matrix: List[CompetitorMatrixItem]

class AuditCategoryDetail(BaseModel):
    score: float
    grade: str
    summary: str
    blocking_issues: List[str]
    suggestions: List[str]

class AuditReportResponse(BaseModel):
    id: str
    draft_id: str
    revision_number: int
    overall_score: float
    seo_score: float
    factuality_score: float
    grammar_score: float
    editorial_score: float
    compliance_score: float
    blocking_issues: List[str]
    suggestions: List[str]
    details: Dict[str, Any]

class DraftResponse(BaseModel):
    id: str
    campaign_id: str
    revision_number: int
    title: str
    slug: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    focus_keyword: Optional[str] = None
    word_count: int
    reading_level: str
    status: str
    created_at: datetime
    content_markdown: str
    yoast_assessment: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class AgentLogResponse(BaseModel):
    agent_name: str
    status: str
    summary: str
    latency_ms: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CampaignDetailResponse(BaseModel):
    id: str
    name: str
    target_query: str
    target_audience: str
    region: str
    brand_tone: str
    status: str
    current_step: str
    created_at: datetime
    sources: List[SourceResponse] = []
    evidence_items: List[EvidenceItemResponse] = []
    drafts: List[DraftResponse] = []
    agent_logs: List[AgentLogResponse] = []
    latest_audit: Optional[AuditReportResponse] = None

class MultiFormatExportResponse(BaseModel):
    title: str
    focus_keyword: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    slug: Optional[str] = None
    blog_markdown: str
    cms_markdown: Optional[str] = None
    blog_html: str
    executive_summary: str
    linkedin_thought_leadership: str
    email_newsletter_teaser: str
    key_takeaways_faq: List[Dict[str, str]]
    yoast_assessment: Optional[Dict[str, Any]] = None
