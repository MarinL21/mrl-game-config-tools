import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

ROWS = [
    [
        "EVENT",
        "get_avatar_frame",
        "获取头像框",
        "Get Avatar Frame",
        "Obtenir le cadre d'avatar",
        "Avatarrahmen erhalten",
        "Obter moldura de avatar",
        "取得頭像框",
        "Dapatkan bingkai avatar",
        "รับกรอบรูปอวาตาร์",
        "Obtener marco de avatar",
        "Получить рамку аватара",
        "Avatar çerçevesini al",
        "Nhận khung ảnh đại diện",
        "Ottieni cornice avatar",
        "Odbierz ramkę awatara",
        "احصل على إطار الصورة الرمزية",
        "アバターフレームを取得",
        "아바타 프레임 받기",
        "获取头像框",
    ],
]


def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True,
    )
    out = result.stdout
    creds_data = json.loads(out[out.find("{"):])
    return Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )


def main():
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    staging_sheet_id = None
    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == STAGING_SHEET:
            staging_sheet_id = s["properties"]["sheetId"]
            break

    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
    ).execute()
    existing = result.get("values", [])
    next_row = max(len(existing) + 1, 2)
    end_row = next_row + len(ROWS) - 1

    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{end_row}",
        valueInputOption="RAW",
        body={"values": ROWS},
    ).execute()

    tab_names = [
        s["properties"]["title"] for s in spreadsheet["sheets"]
        if s["properties"]["title"] not in (STAGING_SHEET, "回车检查", "本地化使用说明")
    ]

    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": staging_sheet_id,
                        "startRowIndex": next_row - 1, "endRowIndex": end_row,
                        "startColumnIndex": 0, "endColumnIndex": 1,
                    },
                    "cell": {
                        "dataValidation": {"condition": {"type": "BOOLEAN"}, "strict": True},
                        "userEnteredValue": {"boolValue": False},
                    },
                    "fields": "dataValidation,userEnteredValue",
                }
            },
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": staging_sheet_id,
                        "startRowIndex": next_row - 1, "endRowIndex": end_row,
                        "startColumnIndex": 1, "endColumnIndex": 2,
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
            },
        ]},
    ).execute()
    print(f"Done! Wrote {len(ROWS)} rows (row {next_row}-{end_row})")


if __name__ == "__main__":
    main()
