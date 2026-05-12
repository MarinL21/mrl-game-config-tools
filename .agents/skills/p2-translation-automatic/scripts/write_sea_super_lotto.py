"""
Write 深海节 wonder 不稳定宝盒 name+desc 到 1011 表 AI翻译暂存。
- name 18 语镜像 ITEM/wonder_item_2026_egg_hammer_desc 中「不稳定宝盒」标准译法
- desc 按 hammer_desc 后半句「使用后可获得不稳定宝盒内全部奖励」句式生成
"""
import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

ROWS = [
    [
        "ITEM",
        "wonder_item_sea_egg_name",
        "不稳定宝盒",
        "Unstable Chest",
        "Coffre Instable",
        "Instabile Truhe",
        "Baú Instável",
        "不穩定寶盒",
        "Peti Tidak Stabil",
        "หีบไม่เสถียร",
        "Cofre Inestable",
        "Нестабильный Сундук",
        "Kararsız Sandık",
        "Rương Bất Ổn",
        "Cassa Instabile",
        "Niestabilna Skrzynia",
        "الصندوق غير المستقر",
        "アンステイブル宝箱",
        "불안정한 상자",
        "不稳定宝盒",
    ],
    [
        "ITEM",
        "wonder_item_sea_egg_desc",
        "开启获得宝盒内奖励",
        "Open it to obtain rewards inside.",
        "Ouvrez-le pour obtenir les récompenses à l'intérieur.",
        "Öffne sie, um die Belohnungen darin zu erhalten.",
        "Abra para obter as recompensas dentro.",
        "開啟取得寶盒內獎勵",
        "Buka untuk mendapatkan hadiah di dalamnya.",
        "เปิดเพื่อรับรางวัลภายใน",
        "Ábrelo para obtener las recompensas dentro.",
        "Откройте, чтобы получить награды внутри.",
        "İçindeki ödülleri almak için aç.",
        "Mở để nhận thưởng bên trong.",
        "Aprilo per ottenere le ricompense all'interno.",
        "Otwórz, aby otrzymać nagrody w środku.",
        "افتحه للحصول على المكافآت بداخله.",
        "開封して中の報酬を獲得します。",
        "열어서 안에 있는 보상을 획득하세요.",
        "开启获得宝盒内奖励",
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
