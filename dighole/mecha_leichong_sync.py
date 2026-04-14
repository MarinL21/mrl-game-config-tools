"""
机甲累充配置替换工具
从累充规划表读取27拓荒节的C列IDs，复制211588136-211588146的行，
从211590000开始倒序排列，替换fincond中的ids和节日名称。

Usage:
    python mecha_leichong_sync.py --dry-run   # 仅预览
    python mecha_leichong_sync.py              # 实际写入
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

SOURCE_IDS = [str(i) for i in range(211588136, 211588147)]
NEW_START_ID = 211590000
FESTIVAL_OLD = "2026复活节"
FESTIVAL_NEW = "2026拓荒节"
LEICHONG_TAB = "26拓荒节"


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
    """读取27拓荒节C列数据，去重"""
    data = service.spreadsheets().values().get(
        spreadsheetId=LEICHONG_SHEET,
        range=f"'{LEICHONG_TAB}'!C:C",
    ).execute()
    rows = data.get("values", [])
    c_values = []
    for row in rows:
        if row and row[0]:
            val = row[0].strip()
            if val and not val.startswith("iap") and not val.startswith("C") and not val.startswith("机甲"):
                try:
                    int(val)
                    c_values.append(val)
                except ValueError:
                    pass
    return list(dict.fromkeys(c_values))


def read_source_rows(service):
    """读取211588136-211588146的完整行数据"""
    b_col = service.spreadsheets().values().get(
        spreadsheetId=ACTIVITY_TASK_SHEET,
        range=f"'{TAB_NAME}'!B:B",
    ).execute()
    b_values = b_col.get("values", [])

    source_id_set = set(SOURCE_IDS)
    found = {}
    for idx, row in enumerate(b_values):
        if row and row[0] in source_id_set:
            found[row[0]] = idx + 1

    if not found:
        return [], 0

    min_row = min(found.values())
    max_row = max(found.values())
    full = service.spreadsheets().values().get(
        spreadsheetId=ACTIVITY_TASK_SHEET,
        range=f"'{TAB_NAME}'!A{min_row}:AG{max_row}",
    ).execute()
    rows = full.get("values", [])

    source_rows = []
    for row in rows:
        if len(row) > 1 and row[1] in source_id_set:
            source_rows.append(row)

    total_rows = len(b_values)
    return source_rows, total_rows


def replace_fincond_ids(fincond_str, new_ids):
    """替换fincond JSON中的ids数组"""
    fincond = json.loads(fincond_str)
    if "arg" in fincond and "ids" in fincond["arg"]:
        fincond["arg"]["ids"] = [int(x) for x in new_ids]
    return json.dumps(fincond, separators=(",", ":"), ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    service = get_service()

    print("Step 1: 读取27拓荒节C列IDs...")
    new_ids = read_new_ids(service)
    print(f"  去重后 {len(new_ids)} 个: {','.join(new_ids[:5])}...{','.join(new_ids[-3:])}")

    print("\nStep 2: 读取源行 211588136-211588146...")
    source_rows, total_rows = read_source_rows(service)
    print(f"  找到 {len(source_rows)} 行，表总行数 {total_rows}")

    if len(source_rows) != 11:
        print(f"  ERROR: 预期11行，实际{len(source_rows)}行")
        return

    print("\nStep 3: 构造新行（从211590000开始倒序）...")
    new_rows = []
    for i, src in enumerate(source_rows):
        new_id = str(NEW_START_ID - i)
        new_row = list(src)

        while len(new_row) < 18:
            new_row.append("")

        old_id = new_row[1]
        new_row[1] = new_id

        old_comment = new_row[2]
        new_comment = old_comment.replace(FESTIVAL_OLD, FESTIVAL_NEW)
        new_row[2] = new_comment

        old_fincond = new_row[4]
        new_fincond = replace_fincond_ids(old_fincond, new_ids)
        new_row[4] = new_fincond

        print(f"  [{i+1}] {old_id} → {new_id}")
        print(f"       comment: {old_comment} → {new_comment}")
        fincond_obj = json.loads(new_fincond)
        ids_count = len(fincond_obj.get("arg", {}).get("ids", []))
        val = fincond_obj.get("val", "")
        print(f"       fincond: ids={ids_count}个, val={val}")

        new_rows.append(new_row)

    append_start_row = total_rows + 1
    print(f"\nStep 4: 将追加到第{append_start_row}行起...")

    if args.dry_run:
        print(f"\n[DRY RUN] 共 {len(new_rows)} 行待写入，未实际写入。")
        print("\n预览第1行完整数据：")
        for i, val in enumerate(new_rows[0]):
            col_name = ["A_INT_group", "A_INT_id", "N_STR_comment", "A_MAP_showcond",
                        "A_MAP_fincond", "A_INT_pretrace", "A_ARR_reward", "A_STR_task_desc",
                        "A_MAP_task_label_1", "A_MAP_task_label_2", "A_INT_display_order",
                        "A_INT_displaykey", "A_MAP_filter", "A_INT_daily_reset", "A_STR_banner",
                        "S_INT_redpoint_off", "A_INT_country_use_type", "A_INT_can_ad_reward"][i] if i < 18 else f"col{i}"
            display = val[:80] + "..." if len(str(val)) > 80 else val
            print(f"    {col_name}: {display}")
        return

    print(f"\nStep 5: 写入 {len(new_rows)} 行...")
    write_range = f"'{TAB_NAME}'!A{append_start_row}"
    result = service.spreadsheets().values().update(
        spreadsheetId=ACTIVITY_TASK_SHEET,
        range=write_range,
        valueInputOption="RAW",
        body={"values": new_rows},
    ).execute()
    print(f"  完成！更新 {result.get('updatedRows', 0)} 行, {result.get('updatedCells', 0)} 个单元格")
    print(f"  写入范围: {result.get('updatedRange', '')}")


if __name__ == "__main__":
    main()
