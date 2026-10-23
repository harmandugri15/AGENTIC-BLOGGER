import urllib.request
import json

def test_live_gemini():
    query = "Create a blog on the best use cases of AI in Education"
    print(f"Submitting query to Live Gemini Agent System: '{query}'...")

    data = json.dumps({
        "name": "Live Gemini - AI in Education",
        "target_query": query,
        "target_audience": "Academic Deans, EdTech CTOs, and Higher Education Leaders",
        "brand_tone": "Authoritative, Rigorous, Pedagogically Nuanced"
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/campaigns",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    cid = res["id"]
    print("Campaign created, ID:", cid)

    # Execute
    print("Executing Multi-Agent Pipeline with Live Gemini 3.8 Flash...")
    req2 = urllib.request.Request(
        f"http://127.0.0.1:8000/api/v1/campaigns/{cid}/execute",
        data=b"{}",
        headers={"Content-Type": "application/json"}
    )
    res2 = json.loads(urllib.request.urlopen(req2).read().decode("utf-8"))
    print("\n================== LIVE GEMINI RESULT ==================")
    print("Draft Title:", res2["draft"]["title"])
    print("Draft Slug:", res2["draft"]["slug"])
    print("Word Count:", res2["draft"]["word_count"])
    print("Overall Score:", res2["overall_score"], "/ 100")
    print("SEO Score:", res2["audit_report"]["seo_score"])
    print("Factuality Score:", res2["audit_report"]["factuality_score"])
    print("Human Editorial Score:", res2["audit_report"]["editorial_score"])
    print("\nSample Generated Markdown Paragraphs:")
    print("\n".join(res2["draft"]["content_markdown"].split("\n\n")[:4]))

if __name__ == "__main__":
    test_live_gemini()
