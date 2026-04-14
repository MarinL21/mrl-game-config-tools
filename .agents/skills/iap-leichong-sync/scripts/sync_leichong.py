"""
IAP 累充表同步工具
从累充规划表读取K列数据，通过iap_template映射config_id，写入iap_config的A_ARR_iap_status字段。

Usage:
    python sync_leichong.py --tab "26复活节" --ids 2013510029,2013510030
    python sync_leichong.py --tab "26复活节"  # 处理整个页签
    python sync_leichong.py --tab "26复活节" --dry-run  # 仅预览不写入
"""

import argparse
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

LEICHONG_SHEET = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"
TEMPLATE_SHEET = "1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY"
CONFIG_SHEET = "1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc"
TEMPLATE_TAB = "iap_template_QA"
CONFIG_TAB = "iap_config_QA"


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


def read_leichong(service, tab_name, target_ids=None):
    data = service.spreadsheets().values().get(
        spreadsheetId=LEICHONG_SHEET,
        range=f"'{tab_name}'!A:K",
    ).execute()
    rows = data.get("values", [])
    id_to_k = {}
    for row in rows:
        if not row or not row[0].startswith("2013"):
            continue
        if target_ids and row[0] not in target_ids:
            continue
        k_val = row[10] if len(row) > 10 else ""
        if k_val:
            id_to_k[row[0]] = k_val
    return id_to_k


def read_template(service, target_ids):
    data = service.spreadsheets().values().get(
        spreadsheetId=TEMPLATE_SHEET,
        range=f"'{TEMPLATE_TAB}'!A:D",
    ).execute()
    rows = data.get("values", [])
    id_to_config = {}
    for row in rows[1:]:
        if row and row[0] in target_ids:
            id_to_config[row[0]] = row[2] if len(row) > 2 else ""
    return id_to_config


def read_config(service, config_ids):
    data = service.spreadsheets().values().get(
        spreadsheetId=CONFIG_SHEET,
        range=f"'{CONFIG_TAB}'!A:M",
    ).execute()
    rows = data.get("values", [])
    header = rows[0]

    status_col = -1
    for i, h in enumerate(header):
        if h == "A_ARR_iap_status":
            status_col = i
            break

    config_to_row = {}
    for row_idx, row in enumerate(rows[1:], start=2):
        if row and row[0] in config_ids:
            current = row[status_col] if len(row) > status_col else ""
            config_to_row[row[0]] = {"row_idx": row_idx, "current": current}
    return config_to_row, status_col


def main():
    parser = argparse.ArgumentParser(description="IAP 累充表同步工具")
    parser.add_argument("--tab", required=True, help="累充表页签名，如 '26复活节'")
    parser.add_argument("--ids", help="逗号分隔的2013xxxx ID，不传则处理整个页签")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写入")
    args = parser.parse_args()

    target_ids = set(args.ids.split(",")) if args.ids else None
    service = get_service()

    print("Step 1: 读取累充表...")
    id_to_k = read_leichong(service, args.tab, target_ids)
    print(f"  找到 {len(id_to_k)} 条记录")

    print("\nStep 2: 查询 iap_template config_id...")
    id_to_config = read_template(service, set(id_to_k.keys()))
    for tid, cid in id_to_config.items():
        print(f"  {tid} -> {cid}")

    print("\nStep 3: 定位 iap_config 行...")
    config_ids = set(id_to_config.values())
    config_rows, status_col = read_config(service, config_ids)

    updates = []
    col_letter = chr(65 + status_col)
    print(f"\nStep 4: 准备更新 (A_ARR_iap_status = {col_letter}列)...")
    for tid in sorted(id_to_k.keys()):
        k_val = id_to_k[tid]
        config_id = id_to_config.get(tid, "")
        info = config_rows.get(config_id, {})
        row_idx = info.get("row_idx", 0)
        current = info.get("current", "")

        changed = current != k_val
        status = "CHANGED" if changed else "SAME"
        print(f"  {tid} -> config={config_id} row={row_idx} [{status}]")

        if changed and row_idx > 0:
            updates.append({
                "range": f"'{CONFIG_TAB}'!{col_letter}{row_idx}",
                "values": [[k_val]],
            })

    if not updates:
        print("\n无需更新。")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] 共 {len(updates)} 个单元格待更新，未实际写入。")
        return

    print(f"\nStep 5: 写入 {len(updates)} 个单元格...")
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=CONFIG_SHEET,
        body={"valueInputOption": "RAW", "data": updates},
    ).execute()
    print(f"  完成，更新 {result.get('totalUpdatedCells', 0)} 个单元格")


if __name__ == "__main__":
    main()
