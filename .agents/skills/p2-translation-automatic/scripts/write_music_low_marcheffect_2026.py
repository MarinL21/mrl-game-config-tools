"""
Push 音乐节 2026 · 低级行军特效『绮梦应援』2 条文案到 AI翻译暂存 页签。
"""
import json
import subprocess

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

# 每行格式: [目标页签, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROWS = [
    [
        "ITEM",
        "music_marcheffect_low_2026",
        "绮梦应援",
        "Dreamlit Cheer",
        "Acclamation Féerique",
        "Traumlicht-Jubel",
        "Torcida Encantada",
        "綺夢應援",
        "Sorakan Impian",
        "เสียงเชียร์แห่งฝัน",
        "Vítores Oníricos",
        "Грёзы Овации",
        "Düşsel Tezahürat",
        "Reo Hò Huyền Mộng",
        "Acclamazione Onirica",
        "Rozmarzony Aplauz",
        "هتاف الأحلام",
        "夢幻の応援",
        "몽환의 응원",
        "绮梦应援",
    ],
    [
        "ITEM",
        "music_marcheffect_low_2026_desc",
        "炫彩流光伴你一路出征",
        "Radiant ribbons light your every march.",
        "Des rubans radieux illuminent chaque marche.",
        "Strahlende Lichtbänder begleiten jeden Marsch.",
        "Fitas radiantes iluminam cada marcha.",
        "炫彩流光伴你一路出征",
        "Pita cahaya gemilang menyertai setiap langkahmu.",
        "ริบบิ้นแสงเจิดจ้าส่องทุกย่างก้าวเดินทัพ",
        "Cintas radiantes iluminan cada marcha.",
        "Сияющие ленты озаряют каждый марш.",
        "Parıldayan kurdeleler her yürüyüşüne eşlik eder.",
        "Dải ánh sáng rực rỡ soi bước hành quân.",
        "Nastri radiosi illuminano ogni marcia.",
        "Promienne wstęgi rozświetlają każdy marsz.",
        "أشرطة متألقة تضيء كل مسيرة.",
        "煌めく光のリボンが行軍を彩る。",
        "찬란한 빛의 리본이 행군을 수놓는다.",
        "炫彩流光伴你一路出征",
    ],
]


def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8",
    )
    out = result.stdout
    idx = out.find("{")
    creds_data = json.loads(out[idx:])
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
    if staging_sheet_id is None:
        raise RuntimeError(f"Staging sheet '{STAGING_SHEET}' not found")

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
        s["properties"]["title"]
        for s in spreadsheet["sheets"]
        if s["properties"]["title"] not in (STAGING_SHEET, "回车检查", "本地化使用说明")
    ]

    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": staging_sheet_id,
                            "startRowIndex": next_row - 1,
                            "endRowIndex": end_row,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1,
                        },
                        "cell": {
                            "dataValidation": {
                                "condition": {"type": "BOOLEAN"},
                                "strict": True,
                            },
                            "userEnteredValue": {"boolValue": False},
                        },
                        "fields": "dataValidation,userEnteredValue",
                    }
                },
                {
                    "setDataValidation": {
                        "range": {
                            "sheetId": staging_sheet_id,
                            "startRowIndex": next_row - 1,
                            "endRowIndex": end_row,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2,
                        },
                        "rule": {
                            "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [
                                    {"userEnteredValue": t} for t in tab_names
                                ],
                            },
                            "showCustomUi": True,
                            "strict": False,
                        },
                    }
                },
            ]
        },
    ).execute()
    print(f"Done! Wrote {len(ROWS)} rows (row {next_row}-{end_row})")


if __name__ == "__main__":
    main()
