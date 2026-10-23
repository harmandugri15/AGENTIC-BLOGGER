# AGENTIC-BLOGGER: Autonomous Multi-Agent SEO & Human-Grade Content Platform

An autonomous, multi-agent AI content generation engine designed to create production-ready, evidence-grounded, human-style articles and campaigns across any domain (Robotics, Education, HR Documentation, Healthcare, Supply Chain, and Finance).

The system queries real-world public APIs, extracts live competitor matrices and corpus LSI vectors, passes strict **Yoast SEO** and **Flesch Readability** audits, and enforces an iterative **ZeroGPT Anti-AI Looper** to guarantee that output scores below **35% AI detection** while maintaining strictly factual citations.

---

## Key Capabilities & Architecture

```
                                  [ User Campaign Prompt ]
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │    Supervisor Orchestrator    │
                             │   (Execution DAG & Routing)   │
                             └───────────────┬───────────────┘
                                             │
             ┌───────────────────────────────┴───────────────────────────────┐
             ▼                                                               ▼
┌───────────────────────────────┐                             ┌───────────────────────────────┐
│         ResearchAgent         │                             │     SEOIntelligenceAgent      │
│   (5 Live Public REST APIs)   │                             │    (Datamuse LSI & Intent)    │
│  • Wikipedia REST API         │                             │  • Canonical Focus Keyword    │
│  • OpenAlex (250M+ Works)     │                             │  • Competitor Gap Matrix      │
│  • ArXiv Preprints            │                             │  • SERP Meta Title (40-65)    │
│  • HackerNews Algolia         │                             │  • Meta Description (120-155) │
│  • Datamuse Semantic Engine   │                             │  • LSI Topical Entity Mapping │
└───────────────┬───────────────┘                             └───────────────┬───────────────┘
                │                                                             │
                └──────────────────────────────┬──────────────────────────────┘
                                               │
                                               ▼
                             ┌───────────────────────────────┐
                             │          WriterAgent          │
                             │   • Zero '#' Heading Hashes   │
                             │   • Strict [EVID-xxx] Tags    │
                             │   • ASCII Architecture Diagram│
                             │   • Dual LLM (Gemini + Groq)  │
                             └───────────────┬───────────────┘
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │  Parallel Quality Audit Gates │
                             ├───────────────────────────────┤
                             │ 1. FactualityAgent            │
                             │ 2. SEOReviewAgent (Yoast 100%)│
                             │ 3. GrammarAgent (Flesch >= 60)│
                             │ 4. EditorialAgent (ZeroGPT)   │
                             │ 5. ComplianceAgent (ISO/FERPA)│
                             └───────────────┬───────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │                                           │
             [ AI Risk >= 35% or Issues ]                [ All Gates Passed ]
                       │                                           │
                       ▼                                           ▼
         ┌───────────────────────────┐               ┌───────────────────────────┐
         │ Iterative Anti-AI Looper  │               │    ContentFormatAgent     │
         │  • De-robotic Rewrite     │               │  • Clean Plain Markdown   │
         │  • Inject Burstiness (CV) │               │  • CMS Markdown with H2s  │
         │  • Short Punchy Fragments │               │  • Executive C-Suite Brief│
         │  • Repeat until < 35% AI  │               │  • LinkedIn Social Post   │
         └─────────────┬─────────────┘               │  • Email Newsletter Teaser│
                       │                             │  • Key Takeaways FAQ JSON │
                       └────────────────────────────►└─────────────┬─────────────┘
                                                                   │
                                                                   ▼
                                                     [ Production Delivery UI ]
```

---

## Core System Features

### 1. 5 Live Public APIs (Zero Hardcoded Data)
Replaced all static fallback dictionaries with live public endpoints:
* **Wikipedia REST API**: Pulls canonical topical extracts and definitions.
* **OpenAlex API**: Queries over 250 million scholarly peer-reviewed works for academic citations.
* **ArXiv Preprints API**: Retrieves recent technical preprints and whitepapers.
* **HackerNews Algolia API**: Ingests practitioner discussions, developer sentiment, and implementation trade-offs.
* **Datamuse Semantic Engine**: Discovers co-occurring LSI keywords, search intent synonyms, and semantic vectors.

### 2. Dual LLM Architecture with Automatic Live Groq Fallback
* **Google Gemini Integration**: Primary generation engine (`gemini-2.5-flash`, `gemini-1.5-flash`).
* **Groq Llama 3.3 70B Fallback**: Automatic, seamless failover to Groq (`llama-3.3-70b-versatile`, 14,400 free requests/day) if Gemini encounters quota exhaustion (`429 ResourceExhausted`) or socket resets.
* **Strict Anti-Placeholder Guarantee**: Zero canned, fake, or placeholder paragraphs are ever substituted if an LLM is unavailable—the pipeline reports the exact status cleanly.

### 3. Direct ZeroGPT Live API Integration & Anti-AI Looper (< 35% AI Target)
* **Direct ZeroGPT Live API (`api.zerogpt.com`)**: Queries ZeroGPT's exact live detection endpoint with browser signatures, receiving the identical `fakePercentage`, feedback, and sentence-level `h` array seen on [zerogpt.com](https://www.zerogpt.com/).
* **Targeted Sentence-Level Rewriting**: Extracts the exact sentences flagged by ZeroGPT and passes them to the live LLM with strict humanization instructions (practitioner perspective, high burstiness, colloquial framing, natural contractions).
* **Burstiness & Perplexity Engine**: Analyzes sentence length variation (Coefficient of Variation $CV > 0.60$) and injects short 3-6 word human fragments (*"Grading is tiring. It takes weekends. Delays important feedback."*).
* **Strict Quality Gate**: If the live ZeroGPT score is $\ge 35\%$, the pipeline marks it as a blocking issue and executes iterative humanization passes until the score drops strictly below 35% (frequently reaching 0% - 20%).

### 4. 100% Yoast SEO & Readability Compliance
* **Focus Keyword Hub**: Deterministically extracts the primary keyphrase and guarantees placement in the SEO Title, Meta Description, URL Slug, Introduction (first 100 words), Subheadings, and Image Alt attributes.
* **Keyword Density**: Validates keyword frequency within the optimal 1.0% – 2.5% corridor without keyword stuffing.
* **Flesch Reading Ease ($\ge 60.0$)**: Ensures text is easily understood (Plain English / 8th-9th grade reading level).
* **Subheading Distribution**: Every section under a heading is strictly under 250 words (never exceeds Yoast's 300-word limit).
* **Paragraph Length**: 100% of paragraphs are under 120 words (never exceeds Yoast's 150-word flag).
* **Transition Words ($\ge 30\%$)**: Injects natural human transitions (*For example, In addition, Specifically, Consequently, Because of this, Meanwhile*) to exceed Yoast's 30% threshold.

### 5. Rich Contextual Internal Links Graph
Automatically embeds 3–4 hyper-relevant contextual internal links into every draft to distribute page authority and optimize site architecture:
* `[enterprise setup blueprint](/solutions/enterprise-rag-setup)`
* `[internal data governance guide](/compliance/data-privacy)`
* `[role-based access control protocols](/security/rbac-vector-search)`
* `[production workflow integration guide](/resources/workflow-integration)`

### 6. Subagent Verification Checkpoints Matrix (`[✓]`)
* Interactive checklist cards for each of the 10 subagents on the frontend.
* As subagents execute their tasks, visual green checkmark boxes (`[✓]`) are ticked off in real time, displaying exact latency, task descriptions, and verified parameters.

---

## Quickstart Guide

### Prerequisites
* **Python**: 3.12+
* **Node.js**: v18+ & npm
* **API Keys**: Google Gemini API key or Groq API key (added via `.env` or directly through the UI modal).

### 1. Unified Runner (Recommended)

Start both backend and frontend concurrently with a single command:

```bash
# Cross-platform Python runner:
python run.py start

# Or using npm:
npm start

# Or native PowerShell:
.\run.ps1 start
```

### 2. Manual Setup

#### Backend (FastAPI)
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* API Base: `http://127.0.0.1:8000`
* Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

#### Frontend (React + Vite + Tailwind CSS)
```bash
cd frontend
npm install
npm run dev
```
* Dashboard URL: `http://localhost:5173`

---

## Testing & Quality Assurance

Run the test suite:

```bash
# Run all unit tests
python run.py test

# Or directly with pytest
python -m pytest backend/tests/ -v
```

Test coverage includes:
* `test_yoast.py`: Evaluates all 15 Yoast SEO & readability checks, density, and auto-optimization.
* `test_humanize.py`: Evaluates sentence burstiness, contraction ratios, and anti-AI looper convergence.
* `test_platform.py`: End-to-end integration tests for research, SEO, writer, and quality audit gates.

---

## Production Deployment (Docker Compose)

Run the entire platform as isolated containers:

```bash
docker-compose up --build
```
* Backend container: Port 8000
* Frontend container: Port 5173

---

## License & Attribution

Built for autonomous content engineering, high-authority organic search ranking, and human editorial integrity.
