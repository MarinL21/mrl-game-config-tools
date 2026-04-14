"""
分析指定中文术语在指定页签中的英文翻译频率分布。
用法: python analyze_term.py "阶段" EVENT
      python analyze_term.py "阶段"          (默认搜索所有页签)
"""
import json
import subprocess
import sys
from collections import Counter

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
SKIP_TABS = {"AI翻译暂存", "回车检查", "本地化使用说明", "AI翻译页签", "页签说明", "checkncwj"}

LANG_NAMES = {
    2: "cn", 3: "en", 4: "fr", 5: "de", 6: "po", 7: "zh",
    8: "id", 9: "th", 10: "sp", 11: "ru", 12: "tr", 13: "vi",
    14: "it", 15: "pl", 16: "ar", 17: "jp", 18: "kr", 19: "cns",
}


def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    return json.loads(result.stdout.strip())


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print('Usage: python analyze_term.py "中文术语" [页签名]')
        return

    term = sys.argv[1]
    target_tab = sys.argv[2] if len(sys.argv) > 2 else None

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
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties.title"
    ).execute()
    all_tabs = [s["properties"]["title"] for s in spreadsheet["sheets"]]
    data_tabs = [t for t in all_tabs if t not in SKIP_TABS]

    if target_tab:
        if target_tab not in data_tabs:
            print(f"Tab '{target_tab}' not found.")
            return
        data_tabs = [target_tab]

    ranges = [f"'{tab}'!A:T" for tab in data_tabs]
    batch_size = 20

    # Collect: for each language, count translations containing the term's translation
    # But we focus on English first
    en_variants = Counter()
    all_lang_variants = {lang: Counter() for lang in LANG_NAMES.values()}
    examples = []

    for batch_start in range(0, len(ranges), batch_size):
        batch_ranges = ranges[batch_start:batch_start + batch_size]
        batch_tabs = data_tabs[batch_start:batch_start + batch_size]

        result = sheets_api.values().batchGet(
            spreadsheetId=SPREADSHEET_ID, ranges=batch_ranges
        ).execute()

        for i, value_range in enumerate(result.get("valueRanges", [])):
            tab_name = batch_tabs[i]
            values = value_range.get("values", [])

            for j, row in enumerate(values):
                if j == 0 or len(row) < 4:
                    continue
                cn = row[2].strip() if len(row) > 2 and row[2] else ""
                if term not in cn:
                    continue

                en = row[3].strip() if len(row) > 3 and row[3] else ""
                key_id = row[1].strip() if len(row) > 1 and row[1] else ""

                if en:
                    en_variants[en] += 1

                if cn == term and len(examples) < 3:
                    translations = {}
                    for col_idx, lang in LANG_NAMES.items():
                        if col_idx < len(row) and row[col_idx]:
                            translations[lang] = row[col_idx].strip()
                    examples.append({
                        "tab": tab_name, "id": key_id, "row": j + 1,
                        "translations": translations,
                    })

                for col_idx, lang in LANG_NAMES.items():
                    if col_idx < len(row) and row[col_idx]:
                        val = row[col_idx].strip()
                        if val:
                            all_lang_variants[lang][val] += 1

    scope = f"tab '{target_tab}'" if target_tab else "all tabs"
    print(f"=== Term: '{term}' in {scope} ===\n")

    # Show exact vs contains
    exact_en = Counter()
    contains_en = Counter()
    for en_text, count in en_variants.items():
        # Check if the cn was exactly the term (we'll approximate)
        exact_en[en_text] = count

    print(f"English translation variants (cn contains '{term}'):")
    print(f"{'Translation':<40} {'Count':>5}")
    print("-" * 50)
    for en_text, count in en_variants.most_common(20):
        print(f"  {en_text:<38} {count:>5}")

    # Find the "canonical" translation (most frequent exact match)
    # Re-scan for exact cn == term
    print(f"\n--- Exact match (cn == '{term}') English translations ---")
    exact_counter = Counter()
    for batch_start in range(0, len(ranges), batch_size):
        batch_ranges = ranges[batch_start:batch_start + batch_size]
        batch_tabs = data_tabs[batch_start:batch_start + batch_size]
        result = sheets_api.values().batchGet(
            spreadsheetId=SPREADSHEET_ID, ranges=batch_ranges
        ).execute()
        for i, vr in enumerate(result.get("valueRanges", [])):
            values = vr.get("values", [])
            for j, row in enumerate(values):
                if j == 0 or len(row) < 4:
                    continue
                cn = row[2].strip() if len(row) > 2 and row[2] else ""
                en = row[3].strip() if len(row) > 3 and row[3] else ""
                if cn == term and en:
                    exact_counter[en] += 1

    if exact_counter:
        for en_text, count in exact_counter.most_common():
            print(f"  {en_text:<38} {count:>5}")
        winner = exact_counter.most_common(1)[0]
        print(f"\n✅ CANONICAL: '{term}' → '{winner[0]}' ({winner[1]} occurrences)")
    else:
        print(f"  No exact matches for cn == '{term}'")
        if en_variants:
            winner = en_variants.most_common(1)[0]
            print(f"\n✅ MOST FREQUENT (contains): '{term}' → '{winner[0]}' ({winner[1]})")

    if examples:
        print(f"\n--- Full 18-lang example (first exact match) ---")
        ex = examples[0]
        t = ex["translations"]
        print(f"  Source: {ex['tab']}/{ex['id']} row {ex['row']}")
        for lang in ["cn", "en", "fr", "de", "po", "zh", "id", "th", "sp", "ru", "tr", "vi", "it", "pl", "ar", "jp", "kr", "cns"]:
            print(f"  {lang:>4}: {t.get(lang, '')}")


if __name__ == "__main__":
    main()
