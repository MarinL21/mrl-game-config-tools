"""机甲累充配置替换 - 完整执行"""
import json
import urllib.request
import urllib.parse

JIACHE_ID = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"
FINCOND_ID = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"

with open(r"C:\Users\liusiyi\.config\gws\python_token.json", "r", encoding="utf-8") as f:
    t = json.load(f)

def refresh():
    data = urllib.parse.urlencode({
        "client_id": t["client_id"],
        "client_secret": t["client_secret"],
        "refresh_token": t["refresh_token"],
        "grant_type": "refresh_token"
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]

def api_get(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def api_put(base_url, sheet_range, values):
    url = base_url + "/" + urllib.parse.quote(sheet_range) + "?valueInputOption=USER_ENTERED"
    body = json.dumps({"values": values}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

ACCESS_TOKEN = refresh()
BASE_URL = f"https://sheets.googleapis.com/v4/spreadsheets/{JIACHE_ID}/values"

# ========== 读取 fincond 26拓荒节 C列 ==========
print("=== 读取 fincond 26拓荒节 C列 ===")
sheet_name = "26" + urllib.parse.quote("拓荒节")
url_fincond = f"https://sheets.googleapis.com/v4/spreadsheets/{FINCOND_ID}/values/{sheet_name}!C:C"
result = api_get(url_fincond)
c_vals = result.get("values", [])
all_ids = []
for row in c_vals:
    if row and row[0]:
        v = str(row[0]).strip()
        if v:
            all_ids.append(v)
unique_ids = list(dict.fromkeys(all_ids))
print(f"fincond C列：共{len(all_ids)}个值，去重后{len(unique_ids)}个")
new_ids_str = ",".join(unique_ids)

# ========== 读取源行 12501:12511（211588136-211588146，共11行） ==========
print("\n=== 读取源行 12501:12511（211588136-211588146）===")
src_range = f"activity_task_QA!A12501:R12511"
result2 = api_get(BASE_URL + "/" + urllib.parse.quote(src_range))
src_rows = result2.get("values", [])
print(f"读取到 {len(src_rows)} 行")

# 倒序处理
src_rows_rev = list(reversed(src_rows))  # 211588146 -> 211588136

old_festival = "2026复活节"
new_festival = "27拓荒节"

print("\n=== 执行写入 ===")
for i, row in enumerate(src_rows_rev):
    src_row_num = 12511 - i
    old_id = int(row[1]) if len(row) > 1 else 0
    new_id = 211590000 + i
    comment = row[2] if len(row) > 2 else ""
    fincond_old = row[4] if len(row) > 4 else "{}"
    
    # 解析fincond JSON
    try:
        fc = json.loads(fincond_old)
        val = fc.get("val", 0)
        op = fc.get("op", "ge")
        cat = fc.get("cat", 101412053)
    except:
        val, op, cat = 0, "ge", 101412053
    
    # 构建新fincond
    new_fc = {"cat": cat, "arg": {"ids": unique_ids}, "val": val, "op": op}
    new_fincond = json.dumps(new_fc)
    
    # 替换节日名
    new_comment = comment.replace(old_festival, new_festival)
    
    # 完整行（A-R共18列）
    full_row = list(row)
    while len(full_row) < 18:
        full_row.append("")
    full_row = full_row[:18]
    
    # 更新B、C、E列
    full_row[1] = str(new_id)   # B列 = 新ID
    full_row[2] = new_comment   # C列 = 新comment
    full_row[4] = new_fincond  # E列 = 新fincond
    
    print(f"\n[{i+1}/11] 源行{src_row_num}(ID={old_id}) -> 新ID={new_id}, val={val}")
    print(f"  comment: {comment} -> {new_comment}")
    print(f"  fincond ids: {len(unique_ids)}个 (去重后)")
    
    # 写入目标行
    dst_row = 12545 + i
    dst_range = f"activity_task_QA!A{dst_row}:R{dst_row}"
    
    try:
        resp = api_put(BASE_URL, dst_range, [full_row])
        print(f"  -> 写入成功! updatedCells={resp.get('updatedCells', '?')}")
    except Exception as e:
        print(f"  -> 写入失败: {e}")

print(f"\n=== 完成! 共写入 {len(src_rows_rev)} 行: ID 211590000 ~ 211590010 ===")
