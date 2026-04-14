import json
import subprocess

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"


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

    # Read last 10 rows of EVENT tab to see ID_int format
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="EVENT!A1:D5",
    ).execute()
    values = result.get("values", [])
    print("=== EVENT header + first rows ===")
    for i, row in enumerate(values):
        print(f"  Row {i+1}: {row}")

    # Get all ID_int values from column A
    result2 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="EVENT!A:A",
    ).execute()
    all_ids = result2.get("values", [])
    print(f"\n=== EVENT total rows: {len(all_ids)} ===")
    print(f"  Header: {all_ids[0] if all_ids else 'N/A'}")

    # Show last 5 ID_int values
    print(f"\n=== Last 10 ID_int values ===")
    for row in all_ids[-10:]:
        print(f"  {row[0] if row else '(empty)'}")

    # Also list all sheet tabs
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets.properties.title,sheets.properties.sheetId"
    ).execute()
    print("\n=== All sheet tabs ===")
    for s in spreadsheet["sheets"]:
        print(f"  {s['properties']['title']} (id={s['properties']['sheetId']})")


if __name__ == "__main__":
    main()
