import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_query: Mapped[str] = mapped_column(String(500), nullable=False)
    target_audience: Mapped[str] = mapped_column(String(255), default="Healthcare IT Executives, CIOs, Chief Medical Officers")
    region: Mapped[str] = mapped_column(String(50), default="US")
    brand_tone: Mapped[str] = mapped_column(String(100), default="Authoritative, Clinical, Innovative")
    status: Mapped[str] = mapped_column(String(50), default="INITIATED")
    current_step: Mapped[str] = mapped_column(String(100), default="Pending Research")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sources: Mapped[list["Source"]] = relationship("Source", back_populates="campaign", cascade="all, delete-orphan")
    drafts: Mapped[list["Draft"]] = relationship("Draft", back_populates="campaign", cascade="all, delete-orphan")
    evidence_items: Mapped[list["EvidenceItem"]] = relationship("EvidenceItem", back_populates="campaign", cascade="all, delete-orphan")
    agent_logs: Mapped[list["AgentRunLog"]] = relationship("AgentRunLog", back_populates="campaign", cascade="all, delete-orphan")

class Source(Base):
    __tablename__ = "sources"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    publisher: Mapped[str] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="COMPETITOR") # COMPETITOR, PUBMED, FDA, BRAND_INTERNAL
    status: Mapped[str] = mapped_column(String(50), default="INDEXED")
    publication_date: Mapped[str] = mapped_column(String(50), nullable=True)
    clean_text: Mapped[str] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="sources")
    chunks: Mapped[list["DocumentChunk"]] = relationship("DocumentChunk", back_populates="source", cascade="all, delete-orphan")
    evidence: Mapped[list["EvidenceItem"]] = relationship("EvidenceItem", back_populates="source", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id"), nullable=False)
    campaign_id: Mapped[str] = mapped_column(String(36), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    heading_path: Mapped[str] = mapped_column(Text, nullable=True)
    embedding_json: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    source: Mapped["Source"] = relationship("Source", back_populates="chunks")

class EvidenceItem(Base):
    __tablename__ = "evidence_items"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id"), nullable=False)
    evidence_tag: Mapped[str] = mapped_column(String(20), nullable=False) # e.g. [EVID-001]
    claim_supported: Mapped[str] = mapped_column(Text, nullable=False)
    verbatim_quote: Mapped[str] = mapped_column(Text, nullable=False)
    source_title: Mapped[str] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_tier: Mapped[str] = mapped_column(String(50), default="PEER_REVIEWED")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="evidence_items")
    source: Mapped["Source"] = relationship("Source", back_populates="evidence")

class Draft(Base):
    __tablename__ = "drafts"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=True)
    meta_title: Mapped[str] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str] = mapped_column(Text, nullable=True)
    outline_json: Mapped[str] = mapped_column(Text, nullable=True)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    reading_level: Mapped[str] = mapped_column(String(50), default="Grade 11-12 (Professional)")
    status: Mapped[str] = mapped_column(String(50), default="IN_REVIEW") # IN_REVIEW, APPROVED, REVISED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="drafts")
    audit_reports: Mapped[list["AuditReport"]] = relationship("AuditReport", back_populates="draft", cascade="all, delete-orphan")

class AuditReport(Base):
    __tablename__ = "audit_reports"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    draft_id: Mapped[str] = mapped_column(String(36), ForeignKey("drafts.id"), nullable=False)
    campaign_id: Mapped[str] = mapped_column(String(36), nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, default=1)
    
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    seo_score: Mapped[float] = mapped_column(Float, default=0.0)
    factuality_score: Mapped[float] = mapped_column(Float, default=0.0)
    grammar_score: Mapped[float] = mapped_column(Float, default=0.0)
    editorial_score: Mapped[float] = mapped_column(Float, default=0.0)
    compliance_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    blocking_issues_json: Mapped[str] = mapped_column(Text, default="[]")
    suggestions_json: Mapped[str] = mapped_column(Text, default="[]")
    full_report_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    draft: Mapped["Draft"] = relationship("Draft", back_populates="audit_reports")

class AgentRunLog(Base):
    __tablename__ = "agent_run_logs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    details_json: Mapped[str] = mapped_column(Text, default="{}")
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="agent_logs")
