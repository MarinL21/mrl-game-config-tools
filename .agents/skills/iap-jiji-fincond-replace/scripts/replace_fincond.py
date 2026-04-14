# -*- coding: utf-8 -*-
"""
机甲累充配置 fincond 替换工具（参数化版）

规则要点：
  - 源行按 B 列 ID 升序（如 211588136→211588145）整行复制，行内容顺序不变。
  - 新行 B 列 ID 从 new_id_start 起连续递增（与行顺序一致）。
  - E 列 A_MAP_fincond：仅替换 JSON 内 arg.ids 数组，其它键（cat/val/op 等）不动。
  - 除 E 列外：按累充表页签将文案中的「复活节」等替换为目标节日名（如拓荒节）。

参数说明：
  --src-tab        源页签名（累充规划表中的节日页签，如"26拓荒节"）
  --dry-run        仅预览，不实际写入
  --src-id-start   源ID起始值（默认211588136）
  --src-id-end     源ID结束值（默认211588145，含）
  --new-id-start   新ID起始值（默认211589990）
  --verify         验证模式：读取已插入行并校验
  --delete         删除模式：删除表尾最近插入的 N 行（N=源行数）
"""
import argparse
import json
import re
import sys

# ============ 固定配置 ============
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
CONFIG_ID = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"  # activity_task_QA
SRC_ID    = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"  # 累充规划表
SHEET_NAME = "activity_task_QA"
CRED_PATH = r"C:\Users\liusiyi\.config\gws\python_token.json"

# ============ Google Sheets API ============
def get_creds():
    info = json.load(open(CRED_PATH, encoding="utf-8"))
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials.from_authorized_user_info(info, scopes=SCOPES)
    if creds.expired:
        creds.refresh(Request())
        _save_token(creds)
        print("Token 已刷新并保存")
    return creds

def _save_token(creds):
    info = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
        "universe_domain": creds.universe_domain,
        "account": creds.account,
        "expiry": creds.expiry.isoformat() + "Z" if creds.expiry else None,
    }
    with open(CRED_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

def get_svc():
    from googleapiclient.discovery import build
    return build("sheets", "v4", credentials=get_creds())

def get_sheet_row_count(sheet_name):
    svc = get_svc()
    result = svc.spreadsheets().values().get(
        spreadsheetId=CONFIG_ID,
        range=f"'{sheet_name}'!A:A",
    ).execute()
    return len(result.get("values", []))

def find_rows_by_id_col(sheet_name, id_col_letter, target_ids):
    svc = get_svc()
    target_ids_set = set(str(t) for t in target_ids)
    result = svc.spreadsheets().values().get(
        spreadsheetId=CONFIG_ID,
        range=f"'{sheet_name}'!{id_col_letter}:{id_col_letter}",
    ).execute()
    values = result.get("values", [])
    found = {}
    for i, row in enumerate(values):
        if row and str(row[0]) in target_ids_set:
            found[str(row[0])] = i + 1  # sheet行号（1-based）
    return found

def insert_rows(sheet_name, start_row, count):
    svc = get_svc()
    meta = svc.spreadsheets().get(
        spreadsheetId=CONFIG_ID,
        fields="sheets(properties(sheetId,title))"
    ).execute()
    sheet_id = None
    for s in meta.get("sheets", []):
        if s["properties"]["title"] == sheet_name:
            sheet_id = s["properties"]["sheetId"]
            break
    body = {
        "requests": [{
            "insertDimension": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": start_row - 1,
                    "endIndex": start_row - 1 + count,
                },
                "inheritFromBefore": False,
            }
        }]
    }
    return svc.spreadsheets().batchUpdate(spreadsheetId=CONFIG_ID, body=body).execute()

def delete_rows(sheet_name, start_row, count):
    svc = get_svc()
    meta = svc.spreadsheets().get(
        spreadsheetId=CONFIG_ID,
        fields="sheets(properties(sheetId,title))"
    ).execute()
    sheet_id = None
    for s in meta.get("sheets", []):
        if s["properties"]["title"] == sheet_name:
            sheet_id = s["properties"]["sheetId"]
            break
    body = {
        "requests": [{
            "deleteDimension": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": start_row - 1,
                    "endIndex": start_row - 1 + count,
                }
            }
        }]
    }
    return svc.spreadsheets().batchUpdate(spreadsheetId=CONFIG_ID, body=body).execute()

def read_cell(sheet_name, row, col):
    svc = get_svc()
    result = svc.spreadsheets().values().get(
        spreadsheetId=CONFIG_ID,
        range=f"'{sheet_name}'!{col}{row}:{col}{row}",
    ).execute()
    vals = result.get("values", [[""]])
    return vals[0][0] if vals and vals[0] else ""

def read_full_rows(sheet_name, row_nums, max_col="R"):
    svc = get_svc()
    results = {}
    for r in row_nums:
        result = svc.spreadsheets().values().get(
            spreadsheetId=CONFIG_ID,
            range=f"'{sheet_name}'!A{r}:{max_col}{r}",
        ).execute()
        results[r] = result.get("values", [[""]])[0] if result.get("values") else [""]
    return results

def replace_fincond_ids(fincond_str, new_ids):
    try:
        obj = json.loads(fincond_str)
    except:
        return fincond_str
    obj["arg"]["ids"] = new_ids
    return json.dumps(obj, separators=(",", ":"))


def festival_label_from_tab(tab: str) -> str:
    """从页签如「26拓荒节」取出节日简称「拓荒节」（去掉前导数字）。"""
    tab = (tab or "").strip()
    return re.sub(r"^\d+", "", tab)


def apply_festival_text_to_cell(val, target_label: str):
    """非 fincond 列：按累充页签将文案中的「复活节」改为目标节日（如拓荒节）。"""
    if not isinstance(val, str) or not val.strip():
        return val
    if target_label == "拓荒节" and "复活节" in val:
        return val.replace("复活节", "拓荒节")
    return val


# ============ 核心流程 ============
def do_replace(src_tab, src_id_start, src_id_end, new_id_start, dry_run=False):
    ROWS_COUNT = src_id_end - src_id_start + 1
    COL_COUNT = 18  # A~R
    target_label = festival_label_from_tab(src_tab)

    # Step 1: 读取源C列
    print(f"\n[1] 读取源表 '{src_tab}' C列...")
    svc = get_svc()
    result = svc.spreadsheets().values().get(
        spreadsheetId=SRC_ID,
        range=f"'{src_tab}'!C1:C300",
    ).execute()
    c_values = result.get("values", [])
    unique_ids = []
    seen = set()
    for row in c_values:
        if row and row[0]:
            v = row[0].strip()
            if v not in seen:
                seen.add(v)
                unique_ids.append(v)
    print(f"    去重后共 {len(unique_ids)} 个ID")

    # Step 2: 找到源行（按 ID 升序，行内容顺序与源配置一致）
    print(f"\n[2] 在 {SHEET_NAME} 中查找行...")
    src_ids = list(range(src_id_start, src_id_end + 1))
    row_map = find_rows_by_id_col(SHEET_NAME, "B", src_ids)
    print(f"    找到 {len(row_map)} 个目标行")
    if len(row_map) != ROWS_COUNT:
        print(f"    警告：期望 {ROWS_COUNT} 行，实际找到 {len(row_map)} 行")

    # Step 3: 读取源行 fincond（保留 val/cat/op，仅替换 arg.ids）
    print(f"\n[3] 读取并构建新 fincond（仅替换 arg.ids）...")
    all_fincond = []
    for sid in src_ids:
        sid_str = str(sid)
        sheet_row = row_map.get(sid_str)
        if not sheet_row:
            continue
        e_val = read_cell(SHEET_NAME, sheet_row, "E")
        new_fincond = replace_fincond_ids(e_val, [int(x) for x in unique_ids])
        obj = json.loads(new_fincond)
        print(f"    ID={sid} 行{sheet_row}: val={obj['val']}, ids长度={len(obj['arg']['ids'])}")
        all_fincond.append((sheet_row, sid, new_fincond))

    # Step 4: 确定插入位置
    last_row = get_sheet_row_count(SHEET_NAME)
    insert_start = last_row + 1
    print(f"\n[4] 插入位置: 行{insert_start}")

    if dry_run:
        print(f"\n[DRY RUN] 预览新行:")
        for i, (_, orig_id, fincond) in enumerate(all_fincond):
            new_id = new_id_start + i
            obj = json.loads(fincond)
            print(f"    新行{insert_start+i}: ID={new_id}, val={obj['val']}, ids={len(obj['arg']['ids'])}个")
        print("\n[DRY RUN 结束] 添加 --dry-run=false 来实际执行")
        return

    # Step 5: 插入新行
    print(f"\n[5] 插入 {ROWS_COUNT} 行到 {SHEET_NAME}...")
    insert_rows(SHEET_NAME, insert_start, ROWS_COUNT)
    print(f"    插入完成，表格扩展至 {last_row + ROWS_COUNT} 行")

    # Step 6: 读取源行全量数据（与 src_ids 同序，不颠倒行内容）
    print(f"\n[6] 读取源行全量数据(A-R)...")
    src_sheet_rows = [row_map[str(sid)] for sid in src_ids if str(sid) in row_map]
    src_data_map = read_full_rows(SHEET_NAME, src_sheet_rows, "R")

    # Step 7: 写入新行
    print(f"\n[7] 写入 {ROWS_COUNT} 行...")
    total = 0
    for i, (sheet_row, orig_id, new_fincond) in enumerate(all_fincond):
        new_row_num = insert_start + i
        new_id = new_id_start + i
        src_data = src_data_map.get(sheet_row, [])
        padded = list(src_data)
        while len(padded) < COL_COUNT:
            padded.append("")
        for ci in range(COL_COUNT):
            if ci == 4:
                continue
            padded[ci] = apply_festival_text_to_cell(padded[ci], target_label)
        padded[1] = str(new_id)    # B列: A_INT_id
        padded[4] = new_fincond    # E列: 仅更新 fincond（上面未改 E 列复制体）
        body = {"values": [padded[:COL_COUNT]]}
        result = get_svc().spreadsheets().values().update(
            spreadsheetId=CONFIG_ID,
            range=f"'{SHEET_NAME}'!A{new_row_num}:R{new_row_num}",
            valueInputOption="RAW",
            body=body,
        ).execute()
        updated = result.get("updatedCells", 0)
        total += updated
        print(f"    行{new_row_num}: ID={new_id} -> {updated} cells")

    print(f"\n{'='*60}")
    print(f"完成！共写入 {total} 个单元格")
    print(f"新ID范围: {new_id_start} - {new_id_start + ROWS_COUNT - 1}")
    print(f"请前往核对: https://docs.google.com/spreadsheets/d/{CONFIG_ID}/edit#gid=1484652723")

def do_verify(new_id_start, rows_count=10):
    print(f"\n=== 验证模式: 读取 ID {new_id_start}-{new_id_start + rows_count - 1} ===")
    svc = get_svc()
    insert_start = get_sheet_row_count(SHEET_NAME) - rows_count + 1
    result = svc.spreadsheets().values().get(
        spreadsheetId=CONFIG_ID,
        range=f"'{SHEET_NAME}'!A{insert_start}:R{insert_start + rows_count - 1}",
    ).execute()
    rows = result.get("values", [])
    for i, row in enumerate(rows):
        row_num = insert_start + i
        b_val = row[1] if len(row) > 1 else "(空)"
        e_val = row[4] if len(row) > 4 else "(空)"
        try:
            obj = json.loads(e_val)
            ids_count = len(obj.get("arg", {}).get("ids", []))
            print(f"  行{row_num}: B={b_val}, cat={obj.get('cat')}, val={obj.get('val')}, ids={ids_count}个")
        except:
            print(f"  行{row_num}: B={b_val}, E解析失败")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="机甲累充 fincond 替换工具")
    parser.add_argument("--src-tab", default="26拓荒节", help="源页签名（累充规划表中的节日页签）")
    parser.add_argument("--src-id-start", type=int, default=211588136, help="源ID起始")
    parser.add_argument("--src-id-end", type=int, default=211588145, help="源ID结束（含）")
    parser.add_argument("--new-id-start", type=int, default=211589990, help="新ID起始")
    parser.add_argument("--dry-run", default="true", help="true=仅预览, false=实际写入")
    parser.add_argument("--verify", action="store_true", help="验证模式")
    parser.add_argument("--delete", action="store_true", help="删除模式")
    args = parser.parse_args()

    dry_run = str(args.dry_run).lower() not in ("false", "0", "no")

    rows_n = args.src_id_end - args.src_id_start + 1

    if args.verify:
        do_verify(args.new_id_start, rows_count=rows_n)
    elif args.delete:
        print(f"删除模式: 删除表尾最近插入的 {rows_n} 行")
        insert_start = get_sheet_row_count(SHEET_NAME) + 1 - rows_n
        if insert_start < 1:
            insert_start = 1
        delete_rows(SHEET_NAME, insert_start, rows_n)
        print("删除完成")
    else:
        do_replace(args.src_tab, args.src_id_start, args.src_id_end,
                    args.new_id_start, dry_run)
