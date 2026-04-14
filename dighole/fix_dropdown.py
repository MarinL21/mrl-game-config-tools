"""修复暂存区所有行的目标页签下拉菜单"""
import json
import subprocess

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"


def main():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds = json.loads(result.stdout.strip())
    credentials = Credentials(
        token=None,
        refresh_token=creds["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=credentials)
    api = service.spreadsheets()

    sp = api.get(spreadsheetId=SPREADSHEET_ID, fields="sheets.properties").execute()
    staging_id = None
    tab_names = []
    for s in sp["sheets"]:
        title = s["properties"]["title"]
        if title == STAGING_SHEET:
            staging_id = s["properties"]["sheetId"]
        elif title not in ("回车检查", "本地化使用说明"):
            tab_names.append(title)

    last_row_result = api.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!A:A",
    ).execute()
    last_row = len(last_row_result.get("values", []))
    if last_row < 2:
        last_row = 2

    api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{
            "setDataValidation": {
                "range": {
                    "sheetId": staging_id,
                    "startRowIndex": 1,
                    "endRowIndex": last_row,
                    "startColumnIndex": 1,
                    "endColumnIndex": 2,
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": t} for t in tab_names],
                    },
                    "showCustomUi": True,
                    "strict": False,
                },
            }
        }]},
    ).execute()

    print(f"Fixed! Added dropdown to rows 2-{last_row} with {len(tab_names)} tabs")


if __name__ == "__main__":
    main()
