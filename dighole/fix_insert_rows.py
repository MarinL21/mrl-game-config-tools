# -*- coding: utf-8 -*-
"""删除 activity_task_QA 中指定范围的行"""
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

def delete_rows(sheet_name, start_row, count):
    svc = get_sheets()
    meta = svc.spreadsheets().get(
        spreadsheetId=CONFIG_ID,
        fields="sheets(properties(sheetId,title))"
    ).execute()
    sheet_id = None
    for s in meta.get("sheets", []):
        if s["properties"]["title"] == sheet_name:
            sheet_id = s["properties"]["sheetId"]
            break
    print(f"  sheetId={sheet_id}")
    body = {
        "requests": [{
            "deleteDimension": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": start_row - 1,
                    "endIndex": start_row - 1 + count,
                }
            }
        }]
    }
    result = svc.spreadsheets().batchUpdate(
        spreadsheetId=CONFIG_ID,
        body=body,
    ).execute()
    print(f"  删除完成: {result}")

if __name__ == "__main__":
    # 删除 12545-12555（11行，错误写入的）
    print("删除 activity_task_QA 12545-12555 行...")
    delete_rows("activity_task_QA", 12545, 11)
