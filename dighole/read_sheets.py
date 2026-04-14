# -*- coding: utf-8 -*-
"""读取Google Sheets数据的工具脚本"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_credentials():
    """从 gws 的 python_token.json 加载凭据"""
    creds = Credentials.from_authorized_user_info(
        info=json.load(open(r"C:\Users\liusiyi\.config\gws\python_token.json", encoding="utf-8")),
        scopes=SCOPES,
    )
    if creds.expired:
        creds.refresh(Request())
        # 保存刷新后的 token
        with open(r"C:\Users\liusiyi\.config\gws\python_token.json", "w", encoding="utf-8") as f:
            json.dump({
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
                "universe_domain": creds.universe_domain,
                "account": creds.account,
                "expiry": creds.expiry.isoformat() + "Z" if creds.expiry else None,
            }, f, ensure_ascii=False, indent=2)
        print("Token 已刷新并保存")
    return creds

def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)

def read_range(spreadsheet_id, range_):
    """读取指定范围"""
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_,
    ).execute()
    return result.get("values", [])

def get_sheet_metadata(spreadsheet_id):
    """获取表格元数据（含页签列表）"""
    service = get_sheets_service()
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="sheets(properties(sheetId,title,index))"
    ).execute()
    return spreadsheet.get("sheets", [])

if __name__ == "__main__":
    import sys

    # 1. 读取源数据表：26拓荒节 C列
    src_id = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"
    tab_name = "26拓荒节"
    print(f"=== 源数据表 [{tab_name}] C列 ===")
    values = read_range(src_id, f"'{tab_name}'!C1:C200")
    unique_c = []
    seen = set()
    for row in values:
        if row and row[0]:
            v = row[0].strip()
            if v not in seen:
                seen.add(v)
                unique_c.append(v)
    print(f"去重后共 {len(unique_c)} 个唯一值")
    ids_str = ",".join(unique_c)
    print(f"格式: {ids_str}")

    print()
    # 2. 读取 activity_task_QA 的行数和A_INT_id列，找到 211588136-211588146
    config_id = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"
    sheet_name = "activity_task_QA"

    # 先读A列和E列（前50行看结构，再搜索特定ID范围）
    print(f"=== [{sheet_name}] A列+B列+E列（前20行）===")
    rows_head = read_range(config_id, f"'{sheet_name}'!A:A")
    rows_b = read_range(config_id, f"'{sheet_name}'!B:B")
    rows_e = read_range(config_id, f"'{sheet_name}'!E:E")
    print(f"总行数（A列）: {len(rows_head)}")
    print(f"前5行 B列: {[r[0] if r else '' for r in rows_b[:5]]}")
    print(f"前5行 E列: {[r[0] if r else '' for r in rows_e[:5]]}")

    # 搜索包含 2115881 开头ID的行
    print(f"\n=== 搜索 A_INT_id 包含 2115881 的行 ===")
    target_ids = [str(i) for i in range(211588136, 211588147)]
    found_rows = []
    for i, row in enumerate(rows_b):
        if row and row[0] and str(row[0]) in target_ids:
            e_val = rows_e[i][0] if i < len(rows_e) and rows_e[i] else ""
            a_val = rows_head[i][0] if i < len(rows_head) and rows_head[i] else ""
            found_rows.append((i+1, row[0], a_val, e_val))
            print(f"  行{i+1}: A={a_val} B={row[0]} E={e_val}")

    if not found_rows:
        print("  未找到！尝试扩大搜索范围...")
        # 搜索所有包含211588的行
        for i, row in enumerate(rows_b):
            if row and row[0] and str(row[0]).startswith("211588"):
                e_val = rows_e[i][0] if i < len(rows_e) and rows_e[i] else ""
                a_val = rows_head[i][0] if i < len(rows_head) and rows_head[i] else ""
                print(f"  行{i+1}: A={a_val} B={row[0]} E={e_val}")
