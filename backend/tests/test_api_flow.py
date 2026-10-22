import urllib.request
import json

def test():
    # 1. Create campaign
    data = json.dumps({
        "name": "AI in Healthcare Enterprise Blog",
        "target_query": "Create a blog on the best use cases of AI in healthcare",
        "target_audience": "Healthcare CIOs and Clinical Informaticists",
        "brand_tone": "Authoritative, Clinically Nuanced"
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/campaigns",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    cid = res["id"]
    print(f"1. Campaign created successfully: ID {cid}")

    # 2. Execute pipeline
    req2 = urllib.request.Request(
        f"http://127.0.0.1:8000/api/v1/campaigns/{cid}/execute",
        data=b"{}",
        headers={"Content-Type": "application/json"}
    )
    res2 = json.loads(urllib.request.urlopen(req2).read().decode("utf-8"))
    print(f"2. Pipeline executed! Status: {res2['status']}, Score: {res2['overall_score']}/100")
    print(f"   Draft title: {res2['draft']['title']}")
    print(f"   Audit grades: Factuality {res2['audit_report']['factuality_score']}%, Editorial {res2['audit_report']['editorial_score']}%")

    # 3. Get export bundle
    req3 = urllib.request.Request(f"http://127.0.0.1:8000/api/v1/campaigns/{cid}/export")
    res3 = json.loads(urllib.request.urlopen(req3).read().decode("utf-8"))
    print("3. Multi-format export generated:")
    print("   Executive Summary preview:", res3["executive_summary"][:140].replace("\n", " "))
    print("   LinkedIn Post preview:", res3["linkedin_thought_leadership"][:140].replace("\n", " "))
    print("   FAQ count:", len(res3["key_takeaways_faq"]))
    print("SUCCESS: End-to-end API verification passed!")

if __name__ == "__main__":
    test()
