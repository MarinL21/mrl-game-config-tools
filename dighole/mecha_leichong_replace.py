"""机甲累充配置替换工具 - 完整流程"""
import json
import urllib.request
import urllib.parse

# ========== 配置 ==========
JIACHE_ID = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"
FINCOND_ID = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"

# 读取 refresh token
with open(r"C:\Users\liusiyi\.config\gws\python_token.json", "r", encoding="utf-8") as f:
    token_data = json.load(f)

CLIENT_ID = token_data["client_id"]
CLIENT_SECRET = token_data["client_secret"]
REFRESH_TOKEN = token_data["refresh_token"]

def refresh_token():
    """用 refresh_token 获取新的 access_token"""
    url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["access_token"]

def api_get(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def get_sheets(spreadsheet_id, fields="sheets.properties(sheetId,title,index)"):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}?fields={urllib.parse.quote(fields)}"
    result = api_get(url)
    return sorted(result.get("sheets", []), key=lambda x: x["properties"]["index"])

def read_range(spreadsheet_id, range_):
    """读取范围，返回 values 或 None"""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{urllib.parse.quote(range_)}"
    try:
        result = api_get(url)
        return result.get("values")
    except Exception as e:
        print(f"    读取失败: {e}")
        return None

def write_range(spreadsheet_id, range_, values, value_input_option="USER_ENTERED"):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{urllib.parse.quote(range_)}?valueInputOption={value_input_option}"
    body = json.dumps({"values": values}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

ACCESS_TOKEN = refresh_token()
print("Token 刷新成功！\n")

# ========== 步骤1：获取机甲累充表的页签列表 ==========
print("=" * 60)
print("步骤1：机甲累充配置表 - 页签列表")
print("=" * 60)
jiache_sheets = get_sheets(JIACHE_ID)
for s in jiache_sheets:
    p = s["properties"]
    print(f"  [{p['index']}] {p['title']}")

# ========== 步骤2：获取 fincond 表的页签列表 ==========
print("\n" + "=" * 60)
print("步骤2：fincond 表 - 页签列表（查找拓荒节）")
print("=" * 60)
fincond_sheets = get_sheets(FINCOND_ID)
for s in fincond_sheets:
    p = s["properties"]
    print(f"  [{p['index']}] {p['title']}")

# ========== 步骤3：从机甲累充表读取 activity_task_QA 页签的列头和211588136-211588146行 ==========
print("\n" + "=" * 60)
print("步骤3：读取机甲累充表 activity_task_QA 的列头")
print("=" * 60)

# 读取 A1:AZ1 获取列头
header_vals = read_range(JIACHE_ID, "activity_task_QA!A1:AZ1")
if header_vals:
    print(f"共 {len(header_vals[0])} 列：")
    for i, col in enumerate(header_vals[0]):
        if col:
            print(f"  列{i+1} ({chr(64+i+1) if i<26 else 'A'+chr(64+i-25)}): {col}")

