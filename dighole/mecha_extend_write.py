"""扩展机甲累充表 + 写入新行"""
import json
import urllib.request
import urllib.parse

JIACHE_ID = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"
FINCOND_ID = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"
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

# ========== 步骤1：获取 activity_task_QA 的 sheetId ==========
print("=== 获取 sheetId ===")
url = f"https://sheets.googleapis.com/v4/spreadsheets/{JIACHE_ID}?fields=sheets.properties(sheetId,title,index)"
req = urllib.request.Request(url)
req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
with urllib.request.urlopen(req) as r:
    result = json.loads(r.read())
for s in result.get("sheets", []):
    p = s["properties"]
    if p["title"] == "activity_task_QA":
        sheet_id = p["sheetId"]
        print(f"activity_task_QA: sheetId={sheet_id}")
        break

# ========== 步骤2：批量追加15行 ==========
print("\n=== 追加15行 ===")
url2 = f"https://sheets.googleapis.com/v4/spreadsheets/{JIACHE_ID}:batchUpdate"
body = json.dumps({
    "requests": [{
        "appendDimension": {
            "sheetId": sheet_id,
            "dimension": "ROWS",
            "length": 15
        }
    }]
}).encode("utf-8")
req2 = urllib.request.Request(url2, data=body, method="POST")
req2.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
req2.add_header("Content-Type", "application/json")
try:
    with urllib.request.urlopen(req2) as r:
        resp = json.loads(r.read())
        print(f"追加行成功!")
except urllib.error.HTTPError as e:
    err = e.read().decode("utf-8")
    print(f"追加行失败: {err[:800]}")

# ========== 步骤3：读取 fincond C列 ==========
print("\n=== 读取 fincond C列 ===")
url3 = f"https://sheets.googleapis.com/v4/spreadsheets/{FINCOND_ID}/values/26%E6%8B%93%E8%8D%92%E8%8A%82!C:C"
req3 = urllib.request.Request(url3)
req3.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
with urllib.request.urlopen(req3) as r:
    result3 = json.loads(r.read())
all_ids = []
for row in result3.get("values", []):
    if row and row[0]:
        v = str(row[0]).strip()
        if v:
            all_ids.append(v)
unique_ids = list(dict.fromkeys(all_ids))
print(f"去重后: {len(unique_ids)} 个ID")

# ========== 步骤4：读取源行并写入 ==========
print("\n=== 读取源行 12501:12511 ===")
BASE_URL = f"https://sheets.googleapis.com/v4/spreadsheets/{JIACHE_ID}/values"
url4 = BASE_URL + "/" + urllib.parse.quote("activity_task_QA!A12501:R12511")
req4 = urllib.request.Request(url4)
req4.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
with urllib.request.urlopen(req4) as r:
    src_rows = json.loads(r.read()).get("values", [])
print(f"读取到 {len(src_rows)} 行")

src_rows_rev = list(reversed(src_rows))
old_festival = "2026复活节"
new_festival = "27拓荒节"

print("\n=== 写入新行 ===")
for i, row in enumerate(src_rows_rev):
    src_row_num = 12511 - i
    old_id = int(row[1]) if len(row) > 1 else 0
    new_id = 211590000 + i
    comment = row[2] if len(row) > 2 else ""
    fincond_old = row[4] if len(row) > 4 else "{}"
    
    try:
        fc = json.loads(fincond_old)
        val = fc.get("val", 0)
        op = fc.get("op", "ge")
        cat = fc.get("cat", 101412053)
    except:
        val, op, cat = 0, "ge", 101412053
    
    new_fc = {"cat": cat, "arg": {"ids": unique_ids}, "val": val, "op": op}
    new_fincond = json.dumps(new_fc)
    new_comment = comment.replace(old_festival, new_festival)
    
    full_row = list(row)
    while len(full_row) < 18:
        full_row.append("")
    full_row = full_row[:18]
    full_row[1] = str(new_id)
    full_row[2] = new_comment
    full_row[4] = new_fincond
    
    dst_row = 12545 + i
    dst_range = f"activity_task_QA!A{dst_row}:R{dst_row}"
    put_url = BASE_URL + "/" + urllib.parse.quote(dst_range) + "?valueInputOption=USER_ENTERED"
    body2 = json.dumps({"values": [full_row]}).encode("utf-8")
    req5 = urllib.request.Request(put_url, data=body2, method="PUT")
    req5.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    req5.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req5) as r:
            resp = json.loads(r.read())
            print(f"  [{i+1}/11] ID={new_id} -> 行{dst_row} 成功 (cells={resp.get('updatedCells','?')})")
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        print(f"  [{i+1}/11] ID={new_id} -> 行{dst_row} 失败: {err[:300]}")

print("\n=== 完成 ===")
