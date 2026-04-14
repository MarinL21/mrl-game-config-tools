# -*- coding: utf-8 -*-
"""验证写入结果"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CONFIG_ID = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"
CRED_PATH = r"C:\Users\liusiyi\.config\gws\python_token.json"

def get_creds():
    info = json.load(open(CRED_PATH, encoding="utf-8"))
    creds = Credentials.from_authorized_user_info(info, scopes=SCOPES)
    if creds.expired:
        creds.refresh(Request())
    return creds

def get_sheets():
    return build("sheets", "v4", credentials=get_creds())

if __name__ == "__main__":
    svc = get_sheets()
    # 读取新插入的11行
    result = svc.spreadsheets().values().get(
        spreadsheetId=CONFIG_ID,
        range="'activity_task_QA'!A12545:R12555",
    ).execute()
    rows = result.get("values", [])
    print(f"=== 验证: 读取到 {len(rows)} 行 ===")
    for i, row in enumerate(rows):
        row_num = 12545 + i
        b_val = row[1] if len(row) > 1 else "(空)"
        e_val = row[4] if len(row) > 4 else "(空)"
        try:
            e_obj = json.loads(e_val)
            ids_count = len(e_obj.get("arg", {}).get("ids", []))
            val = e_obj.get("val", "?")
            cat = e_obj.get("cat", "?")
            print(f"  行{row_num}: B(ID)={b_val}, E(cat={cat},val={val},ids长度={ids_count})")
        except:
            print(f"  行{row_num}: B(ID)={b_val}, E={e_val[:60]}...")
