"""
机甲累充 score_rule 配置替换工具
复制21222521-21222523到新ID(从21223500开始)，
替换21222521、21222523的A_ARR_score_rule中ids，更改节日名称。

Usage:
    python score_rule_sync.py --dry-run
    python score_rule_sync.py
"""
import argparse
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

RANK_SHEET = "1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M"
LEICHONG_SHEET = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"
TAB = "activity_rank_rule（QA）"
LEICHONG_TAB = "26拓荒节"

SOURCE_IDS = ["21222521", "21222522", "21222523"]
IDS_TO_REPLACE = {"21222521", "21222523"}
NEW_START_ID = 21223500
FESTIVAL_OLD = "复活节"
FESTIVAL_NEW = "拓荒节"
SOURCE_ROW_START = 1004
SOURCE_ROW_END = 1006


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

    print("\nStep 2: 读取源行 21222521-21222523...")
    data = service.spreadsheets().values().get(
        spreadsheetId=RANK_SHEET,
        range=f"'{TAB}'!A{SOURCE_ROW_START}:Q{SOURCE_ROW_END}",
    ).execute()
    source_rows = data.get("values", [])
    print(f"  读取 {len(source_rows)} 行")

    count = len(source_rows)
    print(f"\nStep 3: 构造新行（到21223500结束，共{count}行升序）...")
    new_rows = []
    for i, src in enumerate(source_rows):
        new_id = str(NEW_START_ID - count + 1 + i)
        new_row = list(src)
        while len(new_row) < 17:
            new_row.append("")

        old_id = new_row[1]
        new_row[1] = new_id

        old_comment = new_row[2]
        new_comment = old_comment.replace(FESTIVAL_OLD, FESTIVAL_NEW)
        new_row[2] = new_comment

        if old_id in IDS_TO_REPLACE:
            score_rule = json.loads(new_row[3])
            for rule in score_rule:
                if "ids" in rule:
                    old_ids_count = len(rule["ids"])
                    rule["ids"] = new_ids_int
            new_row[3] = json.dumps(score_rule, separators=(",", ":"), ensure_ascii=False)
            print(f"  [{i+1}] {old_id} → {new_id} [REPLACE ids: {old_ids_count}→{len(new_ids_int)}个]")
        else:
            print(f"  [{i+1}] {old_id} → {new_id} [KEEP ids]")

        print(f"       comment: {old_comment} → {new_comment}")
        new_rows.append(new_row)

    print("  最终行顺序:")
    for r in new_rows:
        print(f"    ID={r[1]} - {r[2]}")

    # 找到写入位置
    b_col = service.spreadsheets().values().get(
        spreadsheetId=RANK_SHEET,
        range=f"'{TAB}'!B:B",
    ).execute()
    total_rows = len(b_col.get("values", []))

    write_row = total_rows + 1
    # 检查21223500是否已占位（空行）
    for idx, row in enumerate(b_col.get("values", [])):
        if row and row[0] == "21223500":
            write_row = idx + 1
            break

    print(f"\nStep 4: 将写入第{write_row}行起...")

    if args.dry_run:
        print(f"\n[DRY RUN] 共 {len(new_rows)} 行待写入，未实际写入。")
        for i, row in enumerate(new_rows):
            print(f"\n  行{i+1} 预览:")
            print(f"    A_INT_group: {row[0]}")
            print(f"    A_INT_id: {row[1]}")
            print(f"    N_STR_comment: {row[2]}")
            display = row[3][:100] + "..." if len(str(row[3])) > 100 else row[3]
            print(f"    A_ARR_score_rule: {display}")
        return

    print(f"\nStep 5: 写入 {len(new_rows)} 行...")
    result = service.spreadsheets().values().update(
        spreadsheetId=RANK_SHEET,
        range=f"'{TAB}'!A{write_row}:Q{write_row + len(new_rows) - 1}",
        valueInputOption="RAW",
        body={"values": new_rows},
    ).execute()
    print(f"  完成！更新 {result.get('updatedRows', 0)} 行, {result.get('updatedCells', 0)} 个单元格")
    print(f"  写入范围: {result.get('updatedRange', '')}")


if __name__ == "__main__":
    main()
