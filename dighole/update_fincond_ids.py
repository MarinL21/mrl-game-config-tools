"""
机甲累充 fincond ids 同步更新工具
重新读取累充规划表C列，去重后更新activity_task中对应行的A_MAP_fincond ids。

Usage:
    python update_fincond_ids.py --dry-run   # 仅预览
    python update_fincond_ids.py              # 实际写入
"""
import argparse
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACTIVITY_TASK_SHEET = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"
LEICHONG_SHEET = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"
TAB_NAME = "activity_task_QA"
LEICHONG_TAB = "26拓荒节"
TARGET_ROW_START = 12545
TARGET_ROW_END = 12555


def get_service():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    creds = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=creds)


def read_new_ids(service):
    data = service.spreadsheets().values().get(
        spreadsheetId=LEICHONG_SHEET,
        range=f"'{LEICHONG_TAB}'!C:C",
    ).execute()
    rows = data.get("values", [])
    c_values = []
    for row in rows:
        if row and row[0]:
            val = row[0].strip()
            if val:
                try:
                    int(val)
                    c_values.append(val)
                except ValueError:
                    pass
    return list(dict.fromkeys(c_values))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    service = get_service()

    print("Step 1: 读取累充规划表C列最新IDs...")
    new_ids = read_new_ids(service)
    new_ids_int = [int(x) for x in new_ids]
    print(f"  去重后 {len(new_ids)} 个")

    print("\nStep 2: 读取当前activity_task行...")
    data = service.spreadsheets().values().get(
        spreadsheetId=ACTIVITY_TASK_SHEET,
        range=f"'{TAB_NAME}'!A{TARGET_ROW_START}:R{TARGET_ROW_END}",
    ).execute()
    rows = data.get("values", [])
    print(f"  读取 {len(rows)} 行")

    print("\nStep 3: 对比并更新fincond ids...")
    updated_rows = []
    for row in rows:
        fincond = json.loads(row[4])
        old_ids = fincond.get("arg", {}).get("ids", [])
        fincond["arg"]["ids"] = new_ids_int
        new_fincond = json.dumps(fincond, separators=(",", ":"), ensure_ascii=False)

        changed = old_ids != new_ids_int
        status = "CHANGED" if changed else "SAME"
        print(f"  ID={row[1]} val={fincond.get('val','')} [{status}] old_ids={len(old_ids)}个 → new_ids={len(new_ids_int)}个")

        new_row = list(row)
        new_row[4] = new_fincond
        updated_rows.append(new_row)

    changes = sum(1 for r, u in zip(rows, updated_rows) if r[4] != u[4])
    print(f"\n  共 {changes} 行有变化")

    if changes == 0:
        print("\n无需更新，已是最新。")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] {changes} 行待更新，未实际写入。")
        return

    print(f"\nStep 4: 写入更新...")
    result = service.spreadsheets().values().update(
        spreadsheetId=ACTIVITY_TASK_SHEET,
        range=f"'{TAB_NAME}'!A{TARGET_ROW_START}:R{TARGET_ROW_END}",
        valueInputOption="RAW",
        body={"values": updated_rows},
    ).execute()
    print(f"  完成！更新 {result.get('updatedCells', 0)} 个单元格")


if __name__ == "__main__":
    main()
