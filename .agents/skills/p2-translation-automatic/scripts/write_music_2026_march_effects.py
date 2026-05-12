"""
Push 音乐节 2026 行军特效 4 条文案到 AI翻译暂存 页签。
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
        "music_marcheffect_high_2026",
        "朱祭夜音",
        "Crimson Night Drums",
        "Tambours de la Nuit Pourpre",
        "Trommeln der Purpurnacht",
        "Tambores da Noite Carmesim",
        "朱祭夜音",
        "Gendang Malam Merah",
        "กลองราตรีสีแดง",
        "Tambores de la Noche Carmesí",
        "Барабаны Багряной Ночи",
        "Kızıl Gecenin Davulları",
        "Trống Đêm Thâm Đỏ",
        "Tamburi della Notte Cremisi",
        "Bębny Szkarłatnej Nocy",
        "طبول الليل القرمزي",
        "朱夜祭の太鼓",
        "주홍빛 밤의 북소리",
        "朱祭夜音",
    ],
    [
        "ITEM",
        "music_marcheffect_high_2026_desc",
        "朱伞鼓动，同赴夜祭！",
        "Crimson umbrellas, pounding drums—join the night festival!",
        "Ombrelles pourpres, tambours battants : en avant, à la fête nocturne !",
        "Purpurne Schirme, pochende Trommeln – auf zum Nachtfest!",
        "Guarda-sóis carmesim e tambores ressoantes — rumo ao festival noturno!",
        "朱傘鼓動，同赴夜祭！",
        "Payung merah, tabuhan gendang—mari ke festival malam!",
        "ร่มสีแดง เสียงกลองครื้นเครง—ไปงานเทศกาลราตรีกัน!",
        "Sombrillas carmesíes y tambores resonantes: ¡al festival nocturno!",
        "Багряные зонты, гремящие барабаны — на ночной праздник!",
        "Kızıl şemsiyeler, gürleyen davullar—gece şenliğine doğru!",
        "Ô đỏ thẫm, trống dồn dập—cùng đến lễ hội đêm!",
        "Ombrelli cremisi, tamburi battenti: al festival notturno!",
        "Szkarłatne parasole, huczące bębny — ruszamy na nocne święto!",
        "مظلات قرمزية وطبول مدوية—إلى مهرجان الليل!",
        "朱の傘と太鼓の響き――夜祭へいざ！",
        "주홍빛 우산과 울리는 북소리—밤의 축제로!",
        "朱伞鼓动，同赴夜祭！",
    ],
    [
        "ITEM",
        "music_marcheffect_low_2026",
        "荧光追行",
        "Neon Parade",
        "Parade Néon",
        "Neon-Parade",
        "Desfile Neon",
        "熒光追行",
        "Pawai Neon",
        "ขบวนพาเหรดนีออน",
        "Desfile Neón",
        "Неоновый Парад",
        "Neon Geçidi",
        "Diễu Hành Huỳnh Quang",
        "Parata al Neon",
        "Neonowa Parada",
        "استعراض النيون",
        "ネオンパレード",
        "네온 퍼레이드",
        "荧光追行",
    ],
    [
        "ITEM",
        "music_marcheffect_low_2026_desc",
        "挥舞应援棒，节拍不停歇！",
        "Wave your glow sticks—the beat never stops!",
        "Agitez les bâtons lumineux, le rythme ne s'arrête pas !",
        "Schwenkt die Leuchtstäbe—der Beat hört nie auf!",
        "Agitem os bastões luminosos — a batida não para!",
        "揮舞應援棒，節拍不停歇！",
        "Ayunkan stik cahaya—irama tak pernah berhenti!",
        "โบกแท่งเรืองแสง—จังหวะไม่หยุด!",
        "¡Agita las barras luminosas, el ritmo no se detiene!",
        "Размахивайте светящимися палочками — ритм не остановить!",
        "Işık çubuklarını sallayın—ritim hiç durmaz!",
        "Vẫy gậy phát sáng—nhịp điệu không dừng!",
        "Agitate i bastoni luminosi—il ritmo non si ferma!",
        "Machajcie świetlnymi pałeczkami — rytm nie ustaje!",
        "لوّحوا بالعصي المضيئة—الإيقاع لا يتوقف!",
        "ペンライトを振ろう、ビートは止まらない！",
        "야광봉을 흔들어라, 비트는 멈추지 않는다!",
        "挥舞应援棒，节拍不停歇！",
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
