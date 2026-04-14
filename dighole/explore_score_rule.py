"""探查 21223500 附近已有数据 + 读取完整 score_rule"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SHEET_ID = "1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M"
TAB = "activity_rank_rule（QA）"


def get_service():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    creds = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=creds)


def main():
    service = get_service()

    # 读取1004-1007行完整数据
    print("读取第1004-1007行...")
    data = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB}'!A1004:Q1007",
    ).execute()
    rows = data.get("values", [])
    for row in rows:
        rid = row[1] if len(row) > 1 else "N/A"
        comment = row[2] if len(row) > 2 else "N/A"
        score_rule = row[3] if len(row) > 3 else "N/A"
        print(f"\nID={rid}, comment={comment}")
        print(f"  score_rule (full): {score_rule}")


if __name__ == "__main__":
    main()
