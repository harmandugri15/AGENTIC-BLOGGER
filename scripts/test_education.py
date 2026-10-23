import urllib.request
import json

def test_education():
    # 1. Create education campaign
    data = json.dumps({
        "name": "AI in Education Guide",
        "target_query": "Create a blog on the best use cases of AI in Education",
        "target_audience": "University Deans, Provosts, and EdTech Leaders",
        "brand_tone": "Forward-Looking, Pedagogically Rigorous"
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/campaigns",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    cid = res["id"]
    print("Created Education campaign:", cid)

    # 2. Execute
    req2 = urllib.request.Request(
        f"http://127.0.0.1:8000/api/v1/campaigns/{cid}/execute",
        data=b"{}",
        headers={"Content-Type": "application/json"}
    )
    res2 = json.loads(urllib.request.urlopen(req2).read().decode("utf-8"))
    print("\n--- RESULTS FOR AI IN EDUCATION ---")
    print("Draft Title:", res2["draft"]["title"])
    print("Draft Slug:", res2["draft"]["slug"])
    print("SEO Score:", res2["audit_report"]["seo_score"])
    print("Editorial Score:", res2["audit_report"]["editorial_score"])
    
    # 3. Inspect Campaign Details to see SEO Subagent Telemetry
    req3 = urllib.request.Request(f"http://127.0.0.1:8000/api/v1/campaigns/{cid}")
    res3 = json.loads(urllib.request.urlopen(req3).read().decode("utf-8"))
    seo_log = next(l for l in res3["agent_logs"] if l["agent_name"] == "SEOIntelligenceAgent")
    print("\n--- SEO SUBAGENT TELEMETRY ---")
    print("Status:", seo_log["status"])
    print("Latency:", seo_log["latency_ms"], "ms")
    print("Summary:", seo_log["summary"])
    print("Payload Keys:", list(seo_log["details"].keys()))
    print("Domain Identified:", seo_log["details"].get("domain"))
    print("Primary Keywords:", seo_log["details"].get("primary_keywords"))
    print("Semantic Entities:", seo_log["details"].get("semantic_entities"))

if __name__ == "__main__":
    test_education()
