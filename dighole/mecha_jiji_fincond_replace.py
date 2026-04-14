# -*- coding: utf-8 -*-
"""
机甲累充配置 fincond 替换工具
- 从源表（累充规划表）的指定页签读取C列，去重
- 找到目标表（activity_task_QA）中对应行（211588136-211588146）
- 倒序复制这11行，ID从211590000开始递增
- 替换E列 A_MAP_fincond 中的 ids 字段
- 插入到目标表末尾
"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import re

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CONFIG_ID = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"   # activity_task_QA
SRC_ID    = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"   # 累充规划表
SHEET_NAME = "activity_task_QA"

CRED_PATH = r"C:\Users\liusiyi\.config\gws\python_token.json"

# 源配置
SRC_TAB = "26拓荒节"          # 源页签
NEW_FESTIVAL = "26拓荒节"      # 替换后的节日名（本次不变）

# 目标行范围
SRC_ID_START = 211588136
SRC_ID_END   = 211588146       # 含

# 新ID起始
NEW_ID_START = 211590000


def get_creds():
    info = json.load(open(CRED_PATH, encoding="utf-8"))
    creds = Credentials.from_authorized_user_info(info, scopes=SCOPES)
    if creds.expired:
        creds.refresh(Request())
        save_token(creds)
        print("Token 已刷新")
    return creds

def save_token(creds):
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

def get_sheets():
    return build("sheets", "v4", credentials=get_creds())

def read_range(sheet_name_or_id, range_):
    """读取范围数据，返回 values 列表"""
    svc = get_sheets()
    result = svc.spreadsheets().values().get(
        spreadsheetId=CONFIG_ID if sheet_name_or_id == SHEET_NAME else SRC_ID,
        range=f"'{sheet_name_or_id}'!{range_}" if isinstance(sheet_name_or_id, str) and "!" not in sheet_name_or_id and "'" not in sheet_name_or_id else f"{sheet_name_or_id}!{range_}",
    ).execute()
    return result.get("values", [])

def read_col(sheet_name, col, rows=200):
    """读取单列"""
    svc = get_sheets()
    result = svc.spreadsheets().values().get(
        spreadsheetId=CONFIG_ID if sheet_name == SHEET_NAME else SRC_ID,
        range=f"'{sheet_name}'!{col}1:{col}{rows}",
    ).execute()
    return result.get("values", [])


def find_rows_by_id_col(sheet_name, id_col_letter, target_ids):
    """通过ID列搜索目标行，返回 {id: (sheet_row, values)}"""
    svc = get_sheets()
    target_ids_set = set(str(t) for t in target_ids)
    result = svc.spreadsheets().values().get(
        spreadsheetId=CONFIG_ID if sheet_name == SHEET_NAME else SRC_ID,
        range=f"'{sheet_name}'!{id_col_letter}:{id_col_letter}",
    ).execute()
    values = result.get("values", [])
    found = {}
    for i, row in enumerate(values):
        if row and str(row[0]) in target_ids_set:
            found[str(row[0])] = i + 1  # sheet行号（1-based）
    return found


def read_full_rows(sheet_name, row_nums):
    """读取指定行（全部列），返回 {行号: [各列值]}"""
    svc = get_sheets()
    # 构建范围: A行:E行
    row_strs = [f"A{r}:E{r}" for r in row_nums]
    ranges_str = ",".join([f"'{sheet_name}'!{rs}" for rs in row_strs])
    result = svc.spreadsheets().values().batchGet(
        spreadsheetId=CONFIG_ID if sheet_name == SHEET_NAME else SRC_ID,
        ranges=[f"'{sheet_name}'!A{r}:E{r}" for r in row_nums],
    ).execute()
    rows_data = {}
    for idx, vals in enumerate(result.get("valueRanges", [])):
        rows_data[row_nums[idx]] = vals.get("values", [[""]])[0] if vals.get("values") else [""]
    return rows_data


def get_sheet_row_count(sheet_name):
    """获取工作表实际有数据的行数"""
    svc = get_sheets()
    result = svc.spreadsheets().values().get(
        spreadsheetId=CONFIG_ID,
        range=f"'{sheet_name}'!A:A",
    ).execute()
    return len(result.get("values", []))


def update_cells(sheet_name, row, col_letter, value):
    """更新单个单元格"""
    svc = get_sheets()
    body = {
        "values": [[value]]
    }
    result = svc.spreadsheets().values().update(
        spreadsheetId=CONFIG_ID,
        range=f"'{sheet_name}'!{col_letter}{row}",
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()
    return result


def batch_update_cells(sheet_name, updates):
    """批量更新单元格，updates = [(range, value), ...]"""
    svc = get_sheets()
    data = []
    for rng, val in updates:
        data.append({
            "range": f"'{sheet_name}'!{rng}",
            "values": [[val]]
        })
    body = {"valueInputOption": "USER_ENTERED", "data": data}
    result = svc.spreadsheets().values().batchUpdate(
        spreadsheetId=CONFIG_ID,
        body=body,
    ).execute()
    return result


def insert_rows(sheet_name, start_row, count):
    """在指定位置插入空行（通过 dimensionAdd）"""
    svc = get_sheets()
    # 先获取 sheetId
    meta = svc.spreadsheets().get(
        spreadsheetId=CONFIG_ID,
        fields="sheets(properties(sheetId,title))"
    ).execute()
    sheet_id = None
    for s in meta.get("sheets", []):
        if s["properties"]["title"] == sheet_name:
            sheet_id = s["properties"]["sheetId"]
            break
    if sheet_id is None:
        raise ValueError(f"找不到页签: {sheet_name}")

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
    result = svc.spreadsheets().batchUpdate(
        spreadsheetId=CONFIG_ID,
        body=body,
    ).execute()
    return result


def replace_fincond_ids(original_fincond_str, new_ids):
    """替换fincond JSON中的ids字段，保留cat和val"""
    import json
    try:
        obj = json.loads(original_fincond_str)
    except:
        return original_fincond_str
    obj["arg"]["ids"] = new_ids
    return json.dumps(obj, separators=(",", ":"))


def main():
    print("=" * 60)
    print("机甲累充 fincond 替换工具")
    print("=" * 60)

    # Step 1: 读取源C列数据（去重）
    print(f"\n[1] 读取源表 '{SRC_TAB}' C列数据...")
    c_values = read_col(SRC_TAB, "C", rows=300)
    unique_ids = []
    seen = set()
    for row in c_values:
        if row and row[0]:
            v = row[0].strip()
            if v not in seen:
                seen.add(v)
                unique_ids.append(v)
    print(f"    去重后共 {len(unique_ids)} 个ID")
    ids_str = ",".join(unique_ids)
    print(f"    格式: {ids_str[:80]}...")

    # Step 2: 找到源行
    print(f"\n[2] 在 {SHEET_NAME} 中查找行...")
    src_ids = list(range(SRC_ID_START, SRC_ID_END + 1))
    row_map = find_rows_by_id_col(SHEET_NAME, "B", src_ids)
    print(f"    找到 {len(row_map)} 个目标行:")
    for sid in reversed(src_ids):
        sid_str = str(sid)
        if sid_str in row_map:
            print(f"    ID={sid_str} -> 表行{row_map[sid_str]}")
    if len(row_map) != 11:
        print(f"    警告：只找到 {len(row_map)} 行，期望 11 行！")

    # Step 3: 找到源行 fincond 并构建替换（保留 val）
    print(f"\n[3] 读取源行 fincond 字段（保留 cat/val，只替换 ids）...")
    all_new_finconds = []
    for sid in reversed(src_ids):
        sid_str = str(sid)
        sheet_row = row_map.get(sid_str)
        if not sheet_row:
            continue
        # 读取该行 E 列
        svc = get_sheets()
        e_val = svc.spreadsheets().values().get(
            spreadsheetId=CONFIG_ID,
            range=f"'{SHEET_NAME}'!E{sheet_row}:E{sheet_row}",
        ).execute().get("values", [[""]])[0][0]
        # 替换 ids
        new_fincond = replace_fincond_ids(e_val, [int(x) for x in unique_ids])
        all_new_finconds.append((sheet_row, sid, new_fincond))
        print(f"    ID={sid} 行{sheet_row}: val="
              f"{json.loads(new_fincond)['val']} -> ids长度={len(json.loads(new_fincond)['arg']['ids'])}")

    new_ids_list = [int(x) for x in unique_ids]
    print(f"\n    统一 new_ids 共 {len(new_ids_list)} 个")

    # Step 4: 插入新行（扩展表格）
    last_row = get_sheet_row_count(SHEET_NAME)
    insert_start = last_row + 1
    rows_to_insert = 11
    print(f"\n[4] 当前表末尾行: {last_row}，在第{insert_start}行插入{rows_to_insert}行...")
    insert_rows(SHEET_NAME, insert_start, rows_to_insert)
    print(f"    插入完成，表大小扩展至 {last_row + rows_to_insert} 行")

    # Step 5: 读取源行全量数据
    print(f"\n[5] 读取源行全量数据...")
    # 按倒序读取（与 all_new_finconds 顺序一致）
    src_sheet_rows = [row_map[str(sid)] for sid in reversed(src_ids)]
    src_data_map = read_full_rows(SHEET_NAME, src_sheet_rows)
    print(f"    读取了 {len(src_data_map)} 行数据")

    # Step 6: 生成新行（倒序，ID从211590000递增）
    print(f"\n[6] 生成新行数据（倒序，ID从{NEW_ID_START}开始）...")
    new_rows = []
    for i, (sheet_row, orig_id, new_fincond) in enumerate(all_new_finconds):
        src_data = src_data_map.get(sheet_row, [])
        new_id = NEW_ID_START + i
        new_row = list(src_data)
        while len(new_row) < 18:
            new_row.append("")
        new_row[1] = str(new_id)   # B列 = A_INT_id
        new_row[4] = new_fincond    # E列 = A_MAP_fincond（保留原val）
        new_rows.append((insert_start + i, new_row))
        print(f"    新行{insert_start+i}: 旧ID={orig_id} 新ID={new_id}, val={json.loads(new_fincond)['val']}, ids长度={len(json.loads(new_fincond)['arg']['ids'])}")

    # Step 7: 执行写入（RAW模式，防止公式解析）
    # 源行有18列(A-R)，全部写入
    src_col_count = 18  # A~R
    print(f"\n[7] 写入 {len(new_rows)} 行到 {SHEET_NAME}（A-R列，RAW模式）...")
    svc = get_sheets()
    total_cells = 0
    for new_row_num, row_data in new_rows:
        # 补齐到 src_col_count 列
        padded = list(row_data)
        while len(padded) < src_col_count:
            padded.append("")
        body = {"values": [padded[:src_col_count]]}
        result = svc.spreadsheets().values().update(
            spreadsheetId=CONFIG_ID,
            range=f"'{SHEET_NAME}'!A{new_row_num}:R{new_row_num}",
            valueInputOption="RAW",
            body=body,
        ).execute()
        updated = result.get("updatedCells", 0)
        total_cells += updated
        print(f"    行{new_row_num}: 写入 {updated} 个单元格")
    print(f"    共计 {total_cells} 个单元格已更新")

    print("\n" + "=" * 60)
    print("操作完成！")
    print(f"已插入 {len(new_rows)} 行，ID范围: {NEW_ID_START} - {NEW_ID_START + len(new_rows) - 1}")
    print(f"请前往表格核对: https://docs.google.com/spreadsheets/d/{CONFIG_ID}/edit#gid=1484652723")
    print("=" * 60)


if __name__ == "__main__":
    main()
