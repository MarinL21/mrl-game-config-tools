"""
扫描 Google Sheet 所有页签，建立翻译记忆库。
中文原文 -> 各语种已有翻译，用于保持翻译风格一致。
"""
import json
import subprocess

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
SKIP_TABS = {"AI翻译暂存", "回车检查", "本地化使用说明", "AI翻译页签", "页签说明", "checkncwj"}
OUTPUT_FILE = "translation_memory.json"

# Target tab column order: ID_int, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns
LANG_COLS = {
    2: "cn", 3: "en", 4: "fr", 5: "de", 6: "po", 7: "zh",
    8: "id", 9: "th", 10: "sp", 11: "ru", 12: "tr", 13: "vi",
    14: "it", 15: "pl", 16: "ar", 17: "jp", 18: "kr", 19: "cns",
}


def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8",
        shell=True,
    )
    return json.loads(result.stdout.strip())


def main():
    creds_data = get_credentials()
    credentials = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets.properties.title"
    ).execute()

    tab_names = [s["properties"]["title"] for s in spreadsheet["sheets"]]
    data_tabs = [t for t in tab_names if t not in SKIP_TABS]

    print(f"Scanning {len(data_tabs)} tabs for translation memory...")

    # Batch read: columns C~T (cn through cns) from all tabs
    ranges = [f"'{tab}'!A:T" for tab in data_tabs]
    result = sheets_api.values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=ranges,
    ).execute()

    # cn_text -> {lang: translation, _source_tab: tab, _source_id: id}
    tm = {}
    total = 0

    for i, value_range in enumerate(result.get("valueRanges", [])):
        tab_name = data_tabs[i]
        values = value_range.get("values", [])
        tab_count = 0

        for j, row in enumerate(values):
            if j == 0:
                continue
            if len(row) < 4:
                continue

            cn_text = row[2].strip() if len(row) > 2 else ""
            if not cn_text:
                continue

            entry = {}
            for col_idx, lang in LANG_COLS.items():
                if col_idx < len(row) and row[col_idx]:
                    entry[lang] = row[col_idx].strip()

            if "en" not in entry:
                continue

            key_id = row[1].strip() if len(row) > 1 else ""

            if cn_text not in tm:
                tm[cn_text] = {
                    **entry,
                    "_tab": tab_name,
                    "_id": key_id,
                }
                tab_count += 1
            # If already exists, keep the first one (don't overwrite)

        total += tab_count
        if tab_count > 0:
            print(f"  {tab_name}: {tab_count} unique cn entries")

    # Save
    output = {
        "total_entries": len(tm),
        "entries": tm,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {len(tm)} unique Chinese texts with translations")
    print(f"Saved to {OUTPUT_FILE}")

    # Show some examples
    print("\n--- Examples ---")
    examples = ["确认", "取消", "购买", "升级", "完成", "返回", "加速", "领取"]
    for ex in examples:
        if ex in tm:
            e = tm[ex]
            print(f"  '{ex}' -> en:'{e.get('en','')}' fr:'{e.get('fr','')}' (from {e['_tab']}/{e['_id']})")
        else:
            print(f"  '{ex}' -> NOT FOUND")


if __name__ == "__main__":
    main()
