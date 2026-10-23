import pytest
from backend.app.services.yoast_seo_engine import YoastSEOEngine

def test_yoast_seo_engine_evaluation_and_optimization():
    engine = YoastSEOEngine()
    
    query = "Create a blog on the use rag in hr documentation"
    focus_kw = engine.extract_focus_keyword(query)
    assert focus_kw == "RAG in HR Documentation"
    
    sample_raw = """RAG in HR Documentation: Practical Guide for Enterprise Leaders

Enterprise HR departments spend too much time answering redundant policy questions. When evaluating RAG in HR Documentation, organizations can securely index employee handbooks and benefits documentation without risking data leakage [EVID-001].

1. ACCURATE EMBEDDINGS AND DOCUMENT CHUNKING
Accurate document chunking makes employee query search fast and reliable. For example, dividing policy documents by section prevents context truncation. In addition, semantic search enables natural questions. Specifically, employees can ask about maternity leave policies and get direct answers in seconds without reading a 50-page handbook.

2. PRIVACY-PRESERVING VECTOR RETRIEVAL
Role-based access control stops employees from seeing confidential executive compensation records. Consequently, vector filters ensure that query responses only retrieve data permitted for that employee's security tier. Furthermore, audit trails track every query for compliance.

THE BASE FOR THE SYSTEM: COMPLIANCE AND DATA GOVERNANCE
Enterprise HR needs strict security:
* SOC 2 Type II certified vector storage.
* Zero retention agreements with model providers.
* Human oversight for ambiguous policy queries.
"""

    eval_result = engine.evaluate_yoast_seo(
        content_markdown=sample_raw,
        focus_keyword=focus_kw,
        meta_title="RAG in HR Documentation: Practical Enterprise Guide",
        meta_description="Discover how to build RAG in HR documentation: accurate document chunking, privacy-preserving vector search, and strict enterprise compliance setups.",
        slug="rag-in-hr-documentation-guide"
    )

    assert eval_result["focus_keyword"] == "RAG in HR Documentation"
    assert eval_result["flesch_reading_ease"] >= 10.0
    assert eval_result["transition_words_pct"] >= 25.0
    
    # Test Auto-Optimizer on 350+ word text
    full_sample = sample_raw + "\n\n" + sample_raw
    opt_result = engine.optimize_content(
        content_markdown=full_sample,
        focus_keyword=focus_kw,
        meta_title="",
        meta_description="",
        slug=""
    )
    
    opt_eval = opt_result["yoast_assessment"]
    assert opt_eval["overall_score"] >= 80.0
    assert "RAG in HR Documentation" in opt_result["meta_title"]
    assert "rag in hr documentation" in opt_result["meta_description"].lower()
    assert "![" in opt_result["optimized_markdown"]  # Image injected with alt text
    assert "](/compliance" in opt_result["optimized_markdown"] or "](/solutions" in opt_result["optimized_markdown"]  # Internal links injected
    assert "https://" in opt_result["optimized_markdown"]  # Outbound link injected
