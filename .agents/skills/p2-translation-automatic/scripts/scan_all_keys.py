"""
扫描 Google Sheet 所有页签的 ID 列，生成本地键值索引文件。
用于生成新 key 时检测重复。
"""
import json
import subprocess
import sys
from collections import defaultdict

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
SKIP_TABS = {"AI翻译暂存", "回车检查", "本地化使用说明", "AI翻译页签", "页签说明", "checkncwj"}
OUTPUT_FILE = "all_existing_keys.json"


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

    # Get all tab names
    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets.properties.title"
    ).execute()

    tab_names = [s["properties"]["title"] for s in spreadsheet["sheets"]]
    data_tabs = [t for t in tab_names if t not in SKIP_TABS]

    print(f"Found {len(data_tabs)} data tabs to scan")

    # Batch read: get column B (ID) from all tabs at once
    ranges = [f"'{tab}'!B:B" for tab in data_tabs]
    result = sheets_api.values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=ranges,
    ).execute()

    all_keys = {}  # key -> tab_name
    duplicates = defaultdict(list)  # key -> [tab1, tab2, ...]
    total = 0

    for i, value_range in enumerate(result.get("valueRanges", [])):
        tab_name = data_tabs[i]
        values = value_range.get("values", [])
        tab_count = 0
        for j, row in enumerate(values):
            if j == 0:
                continue  # skip header
            if not row or not row[0]:
                continue
            key = str(row[0]).strip()
            if not key:
                continue
            if key in all_keys:
                duplicates[key].append(tab_name)
                if len(duplicates[key]) == 1:
                    duplicates[key].insert(0, all_keys[key])
            else:
                all_keys[key] = tab_name
            tab_count += 1
        total += tab_count
        print(f"  {tab_name}: {tab_count} keys")

    # Save to JSON
    output = {
        "total_keys": len(all_keys),
        "total_tabs": len(data_tabs),
        "keys": {k: v for k, v in sorted(all_keys.items())},
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {total} entries, {len(all_keys)} unique keys")
    print(f"Saved to {OUTPUT_FILE}")

    if duplicates:
        print(f"\nWARNING: {len(duplicates)} keys exist in multiple tabs:")
        for key, tabs in list(duplicates.items())[:20]:
            print(f"  '{key}' in: {', '.join(tabs)}")


if __name__ == "__main__":
    main()
