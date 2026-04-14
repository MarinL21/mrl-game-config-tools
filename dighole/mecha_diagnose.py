"""诊断：确认源行和目标行"""
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
BASE = f"https://sheets.googleapis.com/v4/spreadsheets/{JIACHE_ID}/values"

def read(rng):
    url = BASE + "/" + urllib.parse.quote(rng)
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get("values", [])

# 读取B列的全部行（用于确认总行数）
b_all = read("activity_task_QA!B:B")
print(f"B列总行数: {len(b_all)}")

# 读取A列全部行（确认A列是不是全是0）
a_all = read("activity_task_QA!A:A")
zero_count = sum(1 for row in a_all if row and row[0] == "0")
print(f"A列中值为'0'的行数: {zero_count}")
print(f"A列最后5行: {[row[0] if row else '空' for row in a_all[-5:]]}")

# 确认读取12501:12511范围时的B列值
test_rows = read(f"activity_task_QA!A12501:R12511")
print(f"\n读取A12501:R12511，共{len(test_rows)}行:")
for i, row in enumerate(test_rows):
    b_val = row[1] if len(row) > 1 else "空"
    print(f"  源行{12501+i}: B={b_val}")

# 确认表尾数据
print(f"\n表格末尾（B列最后10行）:")
for i, row in enumerate(b_all[-10:]):
    actual_row = len(b_all) - 9 + i
    print(f"  行{actual_row}: B={row[0] if row else '空'}")

# 重新搜索211588136在B列的精确位置
print(f"\n搜索B列中值为211588136的行:")
for i, row in enumerate(b_all):
    if row and len(row) > 0:
        try:
            v = int(row[0])
            if v == 211588136:
                print(f"  在数组索引{i}（Excel行{i+1}）")
        except: pass

# 搜索B列最大值
b_ints = []
for row in b_all:
    if row and len(row) > 0:
        try:
            b_ints.append((int(row[0]), b_all.index(row)+1))
        except: pass
if b_ints:
    b_ints.sort()
    print(f"\nB列最大非零值: {b_ints[-1][0]} (行{b_ints[-1][1]})")
    print(f"B列最小非零值: {b_ints[0][0]} (行{b_ints[0][1]})")
    print(f"B列共有 {len(b_ints)} 个非零值")
