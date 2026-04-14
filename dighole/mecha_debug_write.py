"""机甲累充配置替换 - 诊断写入错误"""
import json
import urllib.request
import urllib.parse

JIACHE_ID = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"

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

ACCESS_TOKEN = refresh()
BASE_URL = f"https://sheets.googleapis.com/v4/spreadsheets/{JIACHE_ID}/values"

# fincond ids
unique_ids = ['2011500699', '2011500700', '2011500701', '2011500702', '2011500703',
    '2011500704', '2011500705', '2011500706', '2011500707', '2011500708']

# 构造一个短fincond测试
short_fc = {"cat": 101412053, "arg": {"ids": unique_ids}, "val": 1250, "op": "ge"}
short_fincond = json.dumps(short_fc)
print(f"短fincond长度: {len(short_fincond)}")
print(f"短fincond: {short_fincond}")

# 完整fincond
full_fc = {"cat": 101412053, "arg": {"ids": ['2011500699'] * 101}, "val": 1250, "op": "ge"}
full_fincond = json.dumps(full_fc)
print(f"完整fincond长度: {len(full_fincond)}")

# 测试写入一行（只写B和E列）
test_row = ["0", "211590000", "27拓荒节节日累充-1250", "", short_fincond,
            "", "", "", "", "", "", "", "", "", "", "", "", ""]

# 确保18列
while len(test_row) < 18:
    test_row.append("")

print(f"行长度: {len(test_row)}")
print(f"B列: {test_row[1]}")
print(f"E列前50: {test_row[4][:50]}")

# 尝试写入第一行
url = BASE_URL + "/activity_task_QA!A12545:R12545" + "?valueInputOption=USER_ENTERED"
body = json.dumps({"values": [test_row]}).encode("utf-8")
print(f"请求体长度: {len(body)}")

req = urllib.request.Request(url, data=body, method="PUT")
req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
req.add_header("Content-Type", "application/json")
try:
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
        print(f"成功: {resp}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8")
    print(f"失败: HTTP {e.code}")
    print(f"错误体: {err_body[:2000]}")
