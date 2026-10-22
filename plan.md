# CitiusTech AI Content Intelligence & SEO Agent Platform: Master Engineering Plan

## 1. Executive Summary & Problem Statement

### 1.1 The Business Problem
In enterprise healthcare technology and consulting, standing out in organic search requires deep authority, factual precision, clinical nuance, and authoritative differentiation. When users search for queries such as:
> *"Create a blog on the best use cases of AI in healthcare"*

General tech publications, consulting giants (TCS, Wipro, Accenture), healthtech platforms (Innovaccer, Kore.ai), and medical journals dominate search engine result pages (SERPs). A standard generic LLM-generated article fails because:
1. **Shallow Analysis & Generic Fluff**: Typical LLMs produce clichés ("In today's fast-paced world...") without concrete technical architectures, workflow integration details, or domain-specific nuances.
2. **Hallucination & Clinical/Regulatory Liability**: Medical claims, regulatory assertions (FDA, HIPAA, EU AI Act, ONC HTI-1), or clinical metrics without traceable citations create serious enterprise and legal risk.
3. **Lack of Distinct CitiusTech Perspective**: The article fails to represent CitiusTech's genuine strengths in healthcare data interoperability (HL7 FHIR, SMART on FHIR), payer/provider workflows, and enterprise compliance.
4. **Poor SEO & Search Intent Alignment**: Articles often fail to match the user's explicit and implicit search intent, missing semantic entities, competitor content gaps, FAQs, structured data, and authoritative internal/external linking.

### 1.2 Product Objectives
The CitiusTech AI Content Intelligence & SEO Agent Platform is an enterprise-grade multi-agent platform designed to research, analyze, synthesize, write, verify, and format high-impact healthcare technology content. 

Core goals:
- **Evidence-Grounded**: Every factual, clinical, financial, or performance claim is mapped to an authoritative source (PubMed, WHO, FDA, HHS, peer-reviewed research, or official competitor/industry disclosures).
- **Competitor Gap & Intent Driven**: Systematically analyzes top-ranking competitor pages, extracts core themes, detects missing angles or outdated information, and identifies differentiation opportunities for CitiusTech.
- **Autonomous Multi-Agent Orchestration with Human-in-the-Loop**: A supervisor orchestrates specialized agents (Research, SEO, Writing, Factuality, Compliance, Grammar, Editorial Review), running parallel audits and bounded revision cycles.
- **Auditable Quality Gates**: Prevents unverified drafts from passing without explicit human review and approval.
- **Deterministic & Modular Architecture**: Clean separation between storage, retrieval, orchestration, model providers, and user interfaces.

---

## 2. User Personas & Workflows

### 2.1 Personas
1. **Healthcare Content Strategist / Marketing Lead**: Sets campaign goals, target audience (e.g., Hospital CIOs, Payer Chief Medical Officers, Healthtech Founders), keywords, tone of voice, and review checkpoints.
2. **Technical Healthcare Content Writer / Editor**: Reviews research dossiers, edits outlines, inspects factual claims and citations, refines drafts, and exports multi-format assets.
3. **Medical & Regulatory Compliance Reviewer**: Inspects claims for HIPAA compliance, FDA AI/ML guidance, clinical evidence validity, and brand integrity.
4. **SEO Specialist**: Audits search intent, entity coverage, keyword placement, meta tags, schema markup, and internal linking structures.

### 2.2 End-to-End Workflow
```
[User Input: Topic, Keyword, Audience, Brief, Competitor URLs]
                               │
                               ▼
            ┌──────────────────────────────────────┐
            │   Supervisor / Orchestration Engine  │
            └──────────────────────────────────────┘
                               │
       ┌───────────────────────┴───────────────────────┐
       ▼                                               ▼
┌──────────────────────────────┐        ┌──────────────────────────────┐
│  Research & Knowledge Agent  │        │     SEO Intelligence Agent   │
│  - Web Crawling & Scraping   │        │  - Search Intent & Keywords  │
│  - PubMed / Medical APIs     │        │  - Competitor Gap Analysis   │
│  - Hybrid RAG (BM25 + Dense) │        │  - Entity & Topic Clustering │
└──────────────────────────────┘        └──────────────────────────────┘
       │                                               │
       └───────────────────────┬───────────────────────┘
                               ▼
            ┌──────────────────────────────────────┐
            │ Content Strategist & Writer Agent    │
            │ - Evidence-Backed Content Brief      │
            │ - Structured Outline & Section Drafts│
            └──────────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────────┐
            │       Parallel Quality Review        │
            ├──────────────────────────────────────┤
            │ 1. Factuality & Citation Agent       │
            │ 2. SEO Audit Agent                   │
            │ 3. Brand & Compliance Agent          │
            │ 4. Grammar & Readability Agent       │
            │ 5. Human-Style Editorial Agent       │
            └──────────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────────┐
            │  Supervisor Re-evaluation & Revision │
            │  (Bounded loop, max N revisions)     │
            └──────────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────────┐
            │     Human Review & Approval Gate     │
            │  - Inline Claim Verifier             │
            │  - Audit Reports & Score Breakdown   │
            │  - Editable Markdown / Rich Text     │
            └──────────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────────┐
            │         Multi-Format Exporter        │
            │  (Blog, LinkedIn, Exec Summary, etc.)│
            └──────────────────────────────────────┘
```

---

## 3. System Architecture & Multi-Agent Design

### 3.1 Logical Agents & Responsibilities

| Agent Name | Primary Responsibility | Input Artifacts | Output Artifacts |
|---|---|---|---|
| **1. Supervisor / Orchestrator** | Task graph generation, dependency management, budget/token tracking, retry handling, quality evaluation, convergence checks | Campaign brief, user parameters | Orchestration state, execution logs, final synthesis |
| **2. Research & Knowledge Agent** | SERP analysis, permitted crawling, text extraction, PubMed/E-utilities retrieval, CitiusTech brand library RAG | Target keywords, competitor URLs, search query | Evidence pack, source metadata, raw parsed documents, vector index |
| **3. SEO Intelligence Agent** | Search intent classification, keyword clustering, competitor matrix, content gap extraction, schema & slug recommendation | Evidence pack, competitor content | SEO strategy brief, competitor comparison matrix, target entity list |
| **4. Content Strategist & Writer** | Section-by-section evidence-grounded drafting, CitiusTech differentiation synthesis, natural enterprise tone | SEO brief, evidence pack, brand guidelines | Structured content outline, full article draft with citation markers |
| **5. Factuality & Citation Agent** | Material claim extraction, source verification, citation mapping, hallucination detection, confidence tagging | Article draft, evidence pack | Factuality report, claim-to-source mapping, unverified claim flags |
| **6. SEO Audit Agent** | On-page SEO evaluation, heading hierarchy, keyword density, semantic entity coverage, meta tags, scannability | Article draft, SEO brief | SEO audit score, non-blocking suggestions, blocking issues |
| **7. Grammar & Readability Agent** | Syntactic linting, readability scoring (Flesch-Kincaid, Gunning Fog), passive voice reduction, clarity enhancements | Article draft | Grammar & readability score, concrete line-item edits |
| **8. Human-Style Editorial Agent** | Detection of AI tropes ("rapidly evolving world"), rhythm analysis, concrete example injection, flow refinement | Article draft | Editorial naturalness report, refined passages |
| **9. Brand & Compliance Agent** | CitiusTech messaging alignment, HIPAA/PHI risks, FDA/regulatory claim validation, client confidentiality rules | Article draft, brand knowledge base | Compliance scorecard, legal flags, disclaimer recommendations |
| **10. Content Format Agent** | Repurposing approved draft into derivative assets (LinkedIn posts, executive summaries, FAQs, newsletter copy) | Approved final draft | Multi-format asset bundle |

### 3.2 Agent State & Memory Architecture
The supervisor maintains an immutable state log using a structured Pydantic model (`CampaignWorkflowState`).
```json
{
  "campaign_id": "uuid",
  "status": "RESEARCHING | DRAFTING | REVIEWING | REVISING | COMPLETED | FAILED",
  "current_revision": 1,
  "max_revisions": 3,
  "brief": { ... },
  "evidence_pack": [ ... ],
  "seo_intelligence": { ... },
  "outline": { ... },
  "draft": { ... },
  "audit_results": {
    "seo": { "score": 88, "blocking": [] },
    "factuality": { "score": 92, "unverified_claims": [] },
    "grammar": { "score": 95, "issues": [] },
    "editorial": { "score": 85, "suggestions": [] },
    "compliance": { "score": 100, "flags": [] }
  },
  "overall_score": 90.8,
  "execution_logs": [ ... ]
}
```

---

## 4. RAG Architecture & Ingestion Pipeline

### 4.1 Hybrid Retrieval Engine
Healthcare knowledge requires both keyword precision (e.g., exact drug names, regulatory codes like "21 CFR Part 11", medical terms like "SNOMED-CT", "FHIR US Core") and semantic understanding (e.g., understanding that "reducing physician cognitive load" relates to "ambient clinical documentation").

1. **Lexical Retrieval**: BM25 / SQLite FTS5 / PostgreSQL Full-Text Search with healthcare stemmers.
2. **Dense Semantic Retrieval**: Vector embeddings (`all-MiniLM-L6-v2` / `text-embedding-3-small` / fast local embeddings) with cosine similarity.
3. **Reciprocal Rank Fusion (RRF)**:
   $$\text{RRF\_Score}(d) = \sum_{m \in \{\text{dense}, \text{lexical}\}} \frac{1}{k + \text{rank}_m(d)} \quad (k=60)$$
4. **Contextual Reranking**: Cross-encoder reranking or LLM relevance filtering to filter false positives before evidence pack creation.

### 4.2 Document Chunking Strategy
- **Document-Aware Chunking**: Markdown headings (`#`, `##`, `###`), HTML section tags, and paragraph breaks are preserved as semantic boundaries.
- **Chunk Parameters**: 400-600 tokens with 80-token overlap.
- **Metadata Inheritance**: Every chunk stores `{source_url, document_title, publisher, published_date, section_heading, doc_type, hash}`.

### 4.3 Evidence Pack Generation
Claims are verified against an explicitly assembled `EvidencePack` containing:
- Unique Evidence ID (`EVID-001`, `EVID-002`)
- Direct quotation snippet
- Source URL & Publisher
- Authoritativeness level (`PEER_REVIEWED`, `GOVERNMENT_OFFICIAL`, `INDUSTRY_LEADER`, `GENERAL_WEB`)
- Publication / Access timestamp

---

## 5. Technology Stack & Directory Structure

### 5.1 Chosen Technology Stack

| Layer | Component | Choice | Justification |
|---|---|---|---|
| **Backend Framework** | FastAPI (Python 3.12) | Asynchronous, auto-generating OpenAPI schemas, high performance |
| **Data Validation** | Pydantic v2 | Strict schema enforcement across agent interfaces |
| **Database & ORM** | SQLAlchemy 2.0 (Async) + SQLite / PostgreSQL | Zero-friction local development with production PostgreSQL + pgvector readiness |
| **Search & Lexical RAG** | SQLite FTS5 / BM25 + Vector DB Abstraction | Embedded, high-speed lexical and vector retrieval without requiring Docker |
| **Crawler & Extraction** | `httpx` + `BeautifulSoup4` + Trafilatura | Fast, respectful HTTP extraction respecting `robots.txt` and rate limits |
| **LLM Provider Abstraction** | Pluggable Provider (`OpenAI`, `Gemini`, `Anthropic`, `Groq`, `Local/Mock`) | Flexible configuration via environment variables with full fallback mock runner for testing |
| **Frontend UI** | React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons | Responsive, modern enterprise dashboard with rich interactive state |
| **Testing** | `pytest`, `pytest-asyncio`, `httpx` test client | Comprehensive test coverage for agents, RAG, and APIs |

### 5.2 Directory Structure
```
d:\AGENTIC SYSTEM\
├── plan.md                               # Master engineering plan & tracking
├── README.md                             # Quickstart & documentation
├── .env.example                          # Sample environment configuration
├── backend\
│   ├── app\
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI application entrypoint
│   │   ├── config.py                     # App settings & environment validation
│   │   ├── core\                         # Core utilities, logging, security
│   │   │   ├── logger.py
│   │   │   ├── exceptions.py
│   │   │   └── security.py
│   │   ├── models\                       # SQLAlchemy ORM models
│   │   │   ├── base.py
│   │   │   ├── campaign.py
│   │   │   ├── source.py
│   │   │   ├── document.py
│   │   │   ├── evidence.py
│   │   │   └── audit.py
│   │   ├── schemas\                      # Pydantic schemas (Agent IO & APIs)
│   │   │   ├── campaign.py
│   │   │   ├── research.py
│   │   │   ├── seo.py
│   │   │   ├── draft.py
│   │   │   └── audit.py
│   │   ├── services\                     # Business logic & integrations
│   │   │   ├── crawler.py                # Ethical web crawler
│   │   │   ├── search.py                 # DuckDuckGo / PubMed / Custom search
│   │   │   ├── rag_engine.py             # Chunking, indexing, hybrid retrieval
│   │   │   └── llm_provider.py           # Multi-provider LLM abstraction
│   │   ├── agents\                       # Autonomous agent implementations
│   │   │   ├── supervisor.py             # Orchestration state machine
│   │   │   ├── research_agent.py         # Knowledge acquisition & SERP
│   │   │   ├── seo_agent.py              # Keyword & content gap analysis
│   │   │   ├── writer_agent.py           # Evidence-backed draft generation
│   │   │   ├── factuality_agent.py       # Claim verification & citation checking
│   │   │   ├── seo_review_agent.py       # On-page SEO auditing
│   │   │   ├── grammar_agent.py          # Readability & syntactic linting
│   │   │   ├── editorial_agent.py        # Human-style editorial polish
│   │   │   ├── compliance_agent.py       # Healthcare regulatory & brand audit
│   │   │   └── format_agent.py           # Multi-format conversion (LinkedIn, etc.)
│   │   └── api\                          # REST API routes
│   │       ├── v1\
│   │       │   ├── campaigns.py
│   │       │   ├── research.py
│   │       │   ├── documents.py
│   │       │   ├── drafts.py
│   │       │   ├── audits.py
│   │       │   └── export.py
│   ├── tests\                            # Pytest test suite
│   │   ├── test_crawler.py
│   │   ├── test_rag.py
│   │   ├── test_agents.py
│   │   ├── test_api.py
│   │   └── benchmark_topics.json
│   └── requirements.txt                  # Python dependencies
└── frontend\
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.js
    └── src\
        ├── main.tsx
        ├── App.tsx
        ├── components\                   # UI components
        │   ├── Navbar.tsx
        │   ├── ScoreCard.tsx
        │   ├── EvidenceViewer.tsx
        │   ├── ClaimInspector.tsx
        │   └── MarkdownEditor.tsx
        ├── pages\                        # Dashboard pages
        │   ├── CampaignCreate.tsx
        │   ├── ResearchWorkspace.tsx
        │   ├── ContentEditor.tsx
        │   ├── QualityDashboard.tsx
        │   ├── KnowledgeBase.tsx
        │   └── CampaignHistory.tsx
        ├── services\                     # API client layer
        │   └── api.ts
        └── types\                        # TypeScript type definitions
            └── index.ts
```

---

## 6. Detailed Database Schema

```sql
-- Campaigns
CREATE TABLE campaigns (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    target_query VARCHAR(500) NOT NULL,
    target_audience VARCHAR(255),
    region VARCHAR(50) DEFAULT 'US',
    brand_tone VARCHAR(100) DEFAULT 'Authoritative, Clinical, Innovative',
    status VARCHAR(50) DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sources & Crawled Web Pages
CREATE TABLE sources (
    id VARCHAR(36) PRIMARY KEY,
    campaign_id VARCHAR(36) REFERENCES campaigns(id),
    url TEXT NOT NULL,
    domain VARCHAR(255),
    title TEXT,
    publisher VARCHAR(255),
    source_type VARCHAR(50), -- COMPETITOR, PUBMED, FDA, INTERNAL_BRAND, GOV
    status VARCHAR(50) DEFAULT 'INDEXED',
    crawled_at TIMESTAMP,
    published_date VARCHAR(50),
    raw_content TEXT,
    clean_text TEXT
);

-- Document Chunks & Vector Metadata
CREATE TABLE document_chunks (
    id VARCHAR(36) PRIMARY KEY,
    source_id VARCHAR(36) REFERENCES sources(id),
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    token_count INT,
    embedding_json TEXT, -- Serialized vector representation
    metadata_json TEXT   -- Heading hierarchy, section context
);

-- Evidence Items
CREATE TABLE evidence_items (
    id VARCHAR(36) PRIMARY KEY,
    campaign_id VARCHAR(36) REFERENCES campaigns(id),
    source_id VARCHAR(36) REFERENCES sources(id),
    claim_supported TEXT NOT NULL,
    verbatim_quote TEXT NOT NULL,
    confidence_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Drafts & Outlines
CREATE TABLE drafts (
    id VARCHAR(36) PRIMARY KEY,
    campaign_id VARCHAR(36) REFERENCES campaigns(id),
    revision_number INT NOT NULL,
    title VARCHAR(500),
    slug VARCHAR(255),
    meta_description TEXT,
    outline_json TEXT,
    content_markdown TEXT NOT NULL,
    word_count INT,
    status VARCHAR(50) DEFAULT 'IN_REVIEW', -- IN_REVIEW, APPROVED, REVISED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Reports & Evaluations
CREATE TABLE audit_reports (
    id VARCHAR(36) PRIMARY KEY,
    draft_id VARCHAR(36) REFERENCES drafts(id),
    overall_score FLOAT NOT NULL,
    seo_score FLOAT NOT NULL,
    factuality_score FLOAT NOT NULL,
    grammar_score FLOAT NOT NULL,
    editorial_score FLOAT NOT NULL,
    compliance_score FLOAT NOT NULL,
    report_json TEXT NOT NULL, -- Detailed issues and non-blocking advice
    blocking_issues_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. External Integrations, Costs & Fallbacks

| Integration | Purpose | Mode / Cost | Fallback Mechanism |
|---|---|---|---|
| **DuckDuckGo Search / SERP** | Discovery of real competitor and ranking pages | Free / No API Key required | Built-in zero-key search client via HTML/JSON endpoint |
| **PubMed / E-Utilities** | Authoritative peer-reviewed biomedical research | Free / Public NCBI API | Built-in NCBI E-utilities client (esearch + efetch) |
| **OpenAI / Gemini / Anthropic** | Advanced reasoning, drafting, and agent auditing | Paid / API key configured | Pluggable local mock provider with complete realistic outputs for zero-cost dev/test |
| **CitiusTech Website & Content** | Official CitiusTech positioning, solutions, case studies | Permitted HTTP fetching | Seed knowledge files included in repository (`data/citiustech_seed/`) |
| **Readability & Grammar** | Syntactic linting and readability metrics | Free / Local Python libs | Textstat, custom regex rules, and LLM contextual review |

---

## 8. Content Quality & Scoring Rubric

The overall quality score is calculated using the weighted formula:
$$\text{Overall Score} = (0.20 \times \text{Intent}) + (0.20 \times \text{Factuality}) + (0.15 \times \text{Topical Coverage}) + (0.15 \times \text{Differentiation}) + (0.10 \times \text{On-Page SEO}) + (0.10 \times \text{Readability}) + (0.10 \times \text{Compliance})$$

### Strict Blocking Rules
A draft **CANNOT be approved** (Hard Failure Gate) if any of the following exist:
1. **Unverified Clinical/Safety Claims**: Unbacked claims regarding patient diagnostic accuracy or drug interactions.
2. **Fabricated Citations**: Any citation marker `[Citation: ...]` referencing a non-existent URL or source.
3. **Severe Brand Violations**: Unapproved client disclosure or breach of PHI/confidentiality rules.
4. **Keyword Stuffing / AI Cliché Index**: Exceeding acceptable thresholds for formulaic transitions or robotic repetition.

---

## 9. Implementation Milestones & Verification Checklist

### Milestone 1: Planning & Architecture (Completed)
- [x] Inspect local repository and runtimes (Python 3.12.8, Node v22.21.0, npm 10.9.4 available).
- [x] Create comprehensive `plan.md` with system design, agent boundaries, schemas, and risks.

### Milestone 2: Foundation & Core Backend Setup (Completed)
- [x] Initialize Python backend with FastAPI and async SQLAlchemy.
- [x] Configure environment management (`.env`, `.env.example`).
- [x] Implement database models, migrations/schema bootstrap, and health endpoints.
- [x] Create mock LLM and real LLM provider abstraction.
- [x] Verify backend startup and API tests.

### Milestone 3: Research & Web Ingestion Engine (Completed)
- [x] Implement ethical crawler with `httpx` and `BeautifulSoup4` (robots.txt checking, rate limiting, clean text extraction).
- [x] Implement zero-key search connector (DuckDuckGo / SERP) and NCBI PubMed connector.
- [x] Implement CitiusTech knowledge base seed loader.
- [x] Write integration test verifying real web retrieval and document extraction.

### Milestone 4: Hybrid RAG & Evidence Management (Completed)
- [x] Implement document-aware chunking with metadata preservation.
- [x] Implement hybrid retrieval (BM25 lexical search + dense vector similarity with reciprocal rank fusion).
- [x] Build automated `EvidencePack` compiler with source citation mappings.
- [x] Write RAG retrieval test suite on healthcare benchmark queries.

### Milestone 5: Supervisor & Multi-Agent Orchestration (Completed)
- [x] Build Supervisor state machine tracking campaign progression.
- [x] Implement SEO Intelligence Agent (Search intent, competitor matrix, gap identification).
- [x] Implement Content Strategist & Writer Agent (Evidence-backed drafting with citation tags).
- [x] Add structured state persistence and failure recovery.

### Milestone 6: Quality Gate & Parallel Review Agents (Completed)
- [x] Implement Factuality & Citation Agent (Claim extraction and evidence verification).
- [x] Implement SEO Audit Agent (On-page checklist, heading structure, density).
- [x] Implement Grammar & Readability Agent (Flesch-Kincaid, syntax checks).
- [x] Implement Human-Style Editorial Agent (AI clichés, rhythm, concrete examples).
- [x] Implement Brand & Compliance Agent (Healthcare liability, CitiusTech positioning).
- [x] Implement bounded revision loop in Supervisor.

### Milestone 7: Content Formatting & Derivative Assets (Completed)
- [x] Implement Content Format Agent (Transform approved blog into LinkedIn post, executive summary, email newsletter, FAQs).
- [x] Implement Markdown, HTML, and JSON export endpoints.

### Milestone 8: Frontend Dashboard (React + TypeScript + Tailwind) (Completed)
- [x] Scaffold Vite + React + Tailwind frontend.
- [x] Implement Campaign Creation & Launcher panel.
- [x] Implement Multi-Agent Assembly status visualization.
- [x] Implement Interactive Content Editor with citation tooltips and inline claim inspector.
- [x] Implement Quality & Audit Dashboard with score dials and blocking issue resolutions.
- [x] Implement Multi-format export tabs (Blog, LinkedIn, Exec Summary, Newsletter, FAQ).

### Milestone 9: Evaluation Benchmark & Quality Verification (Completed)
- [x] Run test suite on core healthcare topics (AI Use Cases, Ambient Voice, Interoperability, Prior Authorization).
- [x] Verify citation accuracy, competitor gap coverage, and editorial readability.
- [x] Confirm all tests pass (`pytest backend/tests/test_platform.py` -> 4/4 passed).

### Milestone 10: Production Readiness & Packaging (Completed)
- [x] Create reproducible startup scripts (`run_backend.bat`, `run_frontend.bat`).
- [x] End-to-end live API verification script (`backend/tests/test_api_flow.py`).
- [x] Comprehensive documentation in `README.md`.

---

## 10. Technical Risks & Mitigations

| Risk | Impact | Mitigation Strategy |
|---|---|---|
| **External Search API Rate Limits / Paywalls** | Medium | Provide built-in zero-key search fallback (DuckDuckGo + PubMed E-Utilities) plus support for SerpApi/Tavily. Gracefully handle blocked pages without breaking the pipeline. |
| **Hallucination of Healthcare Metrics** | Critical | Factuality Agent isolates all numeric claims and checks against the compiled `EvidencePack`. If a metric is not supported, the agent flags it as a blocking issue or removes it. |
| **Supervisor Infinite Revision Loop** | Medium | Hard boundary on revision attempts (`MAX_REVISIONS = 3`). If issues persist, draft is routed to the human reviewer with explicit unresolved warning tags. |
| **Competitor Content Scraping Copyright Risks** | High | The platform extracts topics, concepts, entities, and headings for comparative gap analysis only. It never duplicates sentences or reproduces competitor prose. |
| **High Token Cost / Latency** | Medium | Use small, specialized prompts for review agents; run evaluation agents in parallel using async I/O; cache retrieval chunks and SERP responses. |
