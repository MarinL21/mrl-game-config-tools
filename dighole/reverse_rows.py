import json, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

result = subprocess.run(['gws','auth','export','--unmasked'], capture_output=True, text=True, encoding='utf-8', shell=True)
creds_data = json.loads(result.stdout.strip())
creds = Credentials(token=None, refresh_token=creds_data['refresh_token'], token_uri='https://oauth2.googleapis.com/token', client_id=creds_data['client_id'], client_secret=creds_data['client_secret'], scopes=['https://www.googleapis.com/auth/spreadsheets'])
service = build('sheets', 'v4', credentials=creds)

SHEET = '1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY'
TAB = 'activity_task_QA'

data = service.spreadsheets().values().get(
    spreadsheetId=SHEET,
    range=f"'{TAB}'!A12545:R12555",
).execute()
rows = data.get('values', [])
print(f"读取 {len(rows)} 行，当前顺序:")
for r in rows:
    print(f"  ID={r[1]}")

rows.reverse()
print("反转后（从小到大）:")
for r in rows:
    print(f"  ID={r[1]}")

result = service.spreadsheets().values().update(
    spreadsheetId=SHEET,
    range=f"'{TAB}'!A12545:R12555",
    valueInputOption="RAW",
    body={"values": rows},
).execute()
print(f"写入完成: {result.get('updatedCells', 0)} 个单元格")
