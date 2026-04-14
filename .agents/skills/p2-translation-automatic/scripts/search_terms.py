"""
游戏术语直查工具 - 直连 Google Sheet 实时检索。
从 ITEM 表优先开始检索，找到中文原文对应的官方翻译。
用法: python search_terms.py "运输车" "豪华宴会券" "加速" ...
"""
import json
import subprocess
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
SKIP_TABS = {"AI翻译暂存", "回车检查", "本地化使用说明", "AI翻译页签", "页签说明", "checkncwj"}

PRIORITY_TABS = ["ITEM", "HERO", "BUILDING", "MAP", "BUFF", "SOLDIER", "RESEARCH", "RSS"]

LANG_NAMES = {
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


def search(sheets_api, terms):
    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets.properties.title"
    ).execute()

    all_tabs = [s["properties"]["title"] for s in spreadsheet["sheets"]]
    data_tabs = [t for t in all_tabs if t not in SKIP_TABS]

    ordered_tabs = []
    for pt in PRIORITY_TABS:
        if pt in data_tabs:
            ordered_tabs.append(pt)
    for dt in data_tabs:
        if dt not in ordered_tabs:
            ordered_tabs.append(dt)

    ranges = [f"'{tab}'!A:T" for tab in ordered_tabs]

    batch_size = 20
    all_results = {term: [] for term in terms}

    for batch_start in range(0, len(ranges), batch_size):
        batch_ranges = ranges[batch_start:batch_start + batch_size]
        batch_tabs = ordered_tabs[batch_start:batch_start + batch_size]

        result = sheets_api.values().batchGet(
            spreadsheetId=SPREADSHEET_ID,
            ranges=batch_ranges,
        ).execute()

        for i, value_range in enumerate(result.get("valueRanges", [])):
            tab_name = batch_tabs[i]
            values = value_range.get("values", [])

            for j, row in enumerate(values):
                if j == 0 or len(row) < 4:
                    continue
                cn_text = row[2].strip() if len(row) > 2 and row[2] else ""
                if not cn_text:
                    continue

                key_id = row[1].strip() if len(row) > 1 and row[1] else ""

                for term in terms:
                    if term == cn_text:
                        match_type = "EXACT"
                    elif term in cn_text:
                        match_type = "CONTAINS"
                    elif cn_text in term:
                        match_type = "PART_OF"
                    else:
                        continue

                    translations = {}
                    for col_idx, lang in LANG_NAMES.items():
                        if col_idx < len(row) and row[col_idx]:
                            translations[lang] = row[col_idx].strip()

                    all_results[term].append({
                        "match_type": match_type,
                        "tab": tab_name,
                        "row": j + 1,
                        "id": key_id,
                        "cn": cn_text,
                        "translations": translations,
                    })

    for term in terms:
        matches = all_results[term]
        matches.sort(key=lambda x: (
            0 if x["match_type"] == "EXACT" else 1 if x["match_type"] == "PART_OF" else 2,
            PRIORITY_TABS.index(x["tab"]) if x["tab"] in PRIORITY_TABS else 99,
            x["row"],
        ))

    return all_results


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print('Usage: python search_terms.py "term1" "term2" ...')
        return

    terms = sys.argv[1:]
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

    print(f"Searching {len(terms)} terms across all tabs (ITEM first)...\n")
    results = search(sheets_api, terms)

    for term, matches in results.items():
        exact = [m for m in matches if m["match_type"] == "EXACT"]
        contains = [m for m in matches if m["match_type"] == "CONTAINS"]
        part_of = [m for m in matches if m["match_type"] == "PART_OF"]

        print(f"{'='*60}")
        print(f"🔍 Term: '{term}'")

        if exact:
            print(f"\n  ✅ EXACT MATCHES ({len(exact)}) — USE THESE:")
            for m in exact[:3]:
                t = m["translations"]
                print(f"    [{m['tab']}/{m['id']}] row {m['row']}")
                print(f"      cn: {t.get('cn','')}")
                print(f"      en: {t.get('en','')}")
                print(f"      fr: {t.get('fr','')}  de: {t.get('de','')}")
                print(f"      jp: {t.get('jp','')}  kr: {t.get('kr','')}")
                print(f"      zh: {t.get('zh','')}  sp: {t.get('sp','')}")
                print(f"      ru: {t.get('ru','')}  tr: {t.get('tr','')}")
                print(f"      vi: {t.get('vi','')}  th: {t.get('th','')}")
                print(f"      po: {t.get('po','')}  id: {t.get('id','')}")
                print(f"      it: {t.get('it','')}  pl: {t.get('pl','')}")
                print(f"      ar: {t.get('ar','')}")
        elif part_of:
            print(f"\n  🔶 PARTIAL (term is part of existing text, {len(part_of)}):")
            for m in part_of[:5]:
                print(f"    [{m['tab']}/{m['id']}] '{m['cn']}' → en:'{m['translations'].get('en','')}'")
        elif contains:
            print(f"\n  🔷 CONTAINS (existing text contains this term, {len(contains)}):")
            for m in contains[:5]:
                print(f"    [{m['tab']}/{m['id']}] '{m['cn']}' → en:'{m['translations'].get('en','')}'")
        else:
            print(f"\n  ❌ No matches found — generate new translation")

        print()


if __name__ == "__main__":
    main()
