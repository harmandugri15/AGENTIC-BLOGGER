import urllib.request
import json

cids = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/api/v1/campaigns").read().decode())
cid = cids[0]["id"]
print("Testing humanization loop on campaign:", cid)

req = urllib.request.Request(
    f"http://127.0.0.1:8000/api/v1/campaigns/{cid}/humanize",
    data=b"{}",
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode())
print(f"Initial AI Detection Score: {res['initial_ai_score']}%")
print(f"Final AI Detection Score:   {res['final_ai_score']}%")
print(f"Final Human Score:          {res['final_human_score']}%")
print(f"Total Loops:                {res['iterations_count']}")
for step in res["loop_history"]:
    print(f"  Loop {step['iteration']}: AI Prob = {step['ai_probability']}%, CV = {step['burstiness_cv']} | {step['action']}")
