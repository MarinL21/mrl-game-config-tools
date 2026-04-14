"""验证写入结果"""
import json
import urllib.request
import urllib.parse

JIACHE_ID = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"
with open(r"C:\Users\liusiyi\.config\gws\python_token.json", "r", encoding="utf-8") as f:
    t = json.load(f)

def refresh():
    data = urllib.parse.urlencode({
        "client_id": t["client_id"], "client_secret": t["client_secret"],
        "refresh_token": t["refresh_token"], "grant_type": "refresh_token"
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]

ACCESS_TOKEN = refresh()
BASE_URL = f"https://sheets.googleapis.com/v4/spreadsheets/{JIACHE_ID}/values"

# 读取新写入的行
url = BASE_URL + "/" + urllib.parse.quote("activity_task_QA!A12545:R12555")
req = urllib.request.Request(url)
req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
with urllib.request.urlopen(req) as r:
    rows = json.loads(r.read()).get("values", [])

print("=== 验证写入结果 ===\n")
for i, row in enumerate(rows):
    dst_row = 12545 + i
    new_id = row[1] if len(row) > 1 else "?"
    comment = row[2] if len(row) > 2 else ""
    fincond = row[4] if len(row) > 4 else "{}"
    
    try:
        fc = json.loads(fincond)
        ids = fc.get("arg", {}).get("ids", [])
        val = fc.get("val", "?")
        cat = fc.get("cat", "?")
    except:
        ids = []
        val = "?"
        cat = "?"
    
    print(f"行{dst_row}:")
    print(f"  B(ID)={new_id}")
    print(f"  C(comment)={comment}")
    print(f"  E(fincond): cat={cat}, val={val}, ids数量={len(ids)}")
    print(f"  E前80字符: {fincond[:80]}")
    print()
