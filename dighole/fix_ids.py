import json
import subprocess

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

# Old ID -> New ID (remove event_ prefix)
ID_MAP = {
    "event_cool_treasure_title": "cool_treasure_title",
    "event_cool_treasure_label": "cool_treasure_label",
    "event_eliminate_method": "eliminate_method",
    "event_tool_catch_all": "tool_catch_all",
    "event_tool_freeze": "tool_freeze",
    "event_tool_line_view": "tool_line_view",
    "event_tool_blind_flip": "tool_blind_flip",
    "event_flip_cost": "flip_cost",
    "event_exchange_shop": "exchange_shop",
    "event_achievement_pack": "achievement_pack",
    "event_decoration_gift": "decoration_gift",
    "event_collected_rewards": "collected_rewards",
    "event_collect_all_chest": "collect_all_chest",
    "event_hot_events": "hot_events",
    "event_normal_events": "normal_events",
    "event_tournament": "tournament",
    "event_selected_tab": "selected_tab",
    "event_prob_detail": "prob_detail",
}


def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8",
        shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
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

    # Read current ID column (C column = index 3 in staging, but now it's column C = index 2 after removing ID_int)
    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!C2:C24",
    ).execute()
    old_ids = result.get("values", [])

    new_ids = []
    for row in old_ids:
        old_id = row[0] if row else ""
        new_id = ID_MAP.get(old_id, old_id)
        new_ids.append([new_id])

    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!C2:C{1 + len(new_ids)}",
        valueInputOption="RAW",
        body={"values": new_ids},
    ).execute()

    changed = sum(1 for o, n in zip(old_ids, new_ids) if o != n)
    print(f"Done! Updated {changed} IDs (removed event_ prefix)")
    for o, n in zip(old_ids, new_ids):
        old_v = o[0] if o else ""
        new_v = n[0]
        if old_v != new_v:
            print(f"  {old_v} -> {new_v}")


if __name__ == "__main__":
    main()
