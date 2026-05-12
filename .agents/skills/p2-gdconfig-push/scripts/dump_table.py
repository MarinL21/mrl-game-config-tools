#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2 整表覆盖工具（对齐老 GSheetDownloader 的语义）。

适用于"传 X 表到分支"无具体 id 列表的场景：
  下载 sheet 指定页签 → 切 country_use_type 行 + 剥列 → 剥非 S 的 STR_comment 列
  → 整文件覆盖 fo/config/{name}.tsv

不做 patch（id 列表场景请用 merge_rows.py 或 patch_tsv.py）。
不做 cn（用户偏好：所有表默认只 fo）。
不做 i18n（i18n 走 rebuild_i18n.py）。

参数：
  --table 1511      表号；脚本去 fw_gsheet_config 索引自动解 SheetID + 文件名
  --tab 显式指定页签；不指定时按经验默认（{file}_QA 优先，回退 {file}）
  --out-root /Users/marinl/gdconfig

或显式：--sheet-id ... --file-name ... --tab ...
"""

import argparse
import json
import os
import subprocess
import sys

INDEX_SHEET_ID = "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c"
INDEX_TAB = "fw_gsheet_config"


def gws_get(sheet_id, rng):
    cmd = [
        "gws", "sheets", "spreadsheets", "values", "get",
        "--params", json.dumps({"spreadsheetId": sheet_id, "range": rng}),
        "--format", "json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"gws get {rng} failed: {res.stderr}")
    return json.loads(res.stdout).get("values", [])


def list_tabs(sheet_id):
    cmd = [
        "gws", "sheets", "spreadsheets", "get",
        "--params", json.dumps({
            "spreadsheetId": sheet_id,
            "fields": "sheets(properties(title,index))",
        }),
        "--format", "json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"gws list tabs failed: {res.stderr}")
    return [s["properties"]["title"] for s in json.loads(res.stdout).get("sheets", [])]


def lookup_table(table_no):
    """从 fw_gsheet_config 解 (file_name, sheet_id, mode)。"""
    rows = gws_get(INDEX_SHEET_ID, f"{INDEX_TAB}!A:F")
    for r in rows:
        if len(r) > 1 and r[1].startswith(f"{table_no}_"):
            file_name = r[2]
            sheet_id = r[3]
            mode = r[5] if len(r) > 5 else "0"
            return file_name, sheet_id, mode
    raise RuntimeError(f"table {table_no} not in fw_gsheet_config")


def pick_default_tab(sheet_id, file_name):
    """按经验找权威页签。优先级：
      1. 精确名：{file}_QA / {file}_qa / {file}（QA）/ {file}(QA) / {file}
      2. 前缀名：{file}（...）形式（如 1168 的 `get_access_group（杜绝手搓）`），
         但排除明显的非权威标签（测试/备份/已合并/计算/说明等）
    """
    tabs = list_tabs(sheet_id)
    candidates = [
        f"{file_name}_QA",
        f"{file_name}_qa",
        f"{file_name}（QA）",
        f"{file_name}(QA)",
        file_name,
    ]
    for c in candidates:
        if c in tabs:
            return c
    # 前缀匹配：{file}（中文括号备注）。排除明显非权威标记。
    EXCLUDE = ("测试", "TEST", "备份", "已合", "待合", "计算表", "说明", "操作日志", "kvk", "KVK")
    prefixed = [t for t in tabs if t.startswith(file_name) and t != file_name]
    for t in prefixed:
        if not any(x in t for x in EXCLUDE):
            return t
    # 兜底：sheet 只有 1 个 tab（如 Google 默认 `工作表1` / `Sheet1`）
    if len(tabs) == 1:
        return tabs[0]
    raise RuntimeError(f"no QA-style tab found for {file_name!r} in {tabs[:10]}...")


def find_col(headers, name):
    for i, h in enumerate(headers):
        if (h or "").strip() == name:
            return i
    return -1


def find_comment_col_to_strip(headers):
    """找需要剥掉的 comment 列：header 以 _STR_comment 结尾且首字母不是 S/s。"""
    for i, h in enumerate(headers):
        h = (h or "").strip()
        if h.endswith("_STR_comment") and h[:1].lower() != "s":
            return i
    return -1


def split_by_country_use_type(rows, type_idx):
    """老 split_cfg_sheet 语义：
    - value=0 公共（fo+cn 都要）
    - value=1 仅 fo
    - value=2 仅 cn
    返回 fo 行集合（0+1）和 cn 行集合（0+2）。
    """
    headers = rows[0]
    fo_data = [r for r in rows[1:] if len(r) > type_idx and r[type_idx] in ("0", "1", "")]
    cn_data = [r for r in rows[1:] if len(r) > type_idx and r[type_idx] in ("0", "2")]
    return [headers] + fo_data, [headers] + cn_data


def strip_col(rows, col_idx):
    out = []
    for r in rows:
        new = list(r)
        if len(new) > col_idx:
            new.pop(col_idx)
        out.append(new)
    return out


def normalize_row_width(rows, target_width):
    """sheet API 会把尾部全空 cell 截断；写 tsv 前补齐到 header 宽度。"""
    out = []
    for r in rows:
        if len(r) < target_width:
            r = list(r) + [""] * (target_width - len(r))
        out.append(r)
    return out


def write_tsv(path, rows):
    """对齐老 GSheetDownloader 行为：保留目标文件原有的 trailing newline 状态。
    多数仓库 tsv 末尾无 newline，无脑加会触发"末尾行假 diff"。
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    had_trailing_newline = False
    if os.path.exists(path):
        with open(path, "rb") as f:
            f.seek(-1, os.SEEK_END) if os.path.getsize(path) > 0 else None
            try:
                last = f.read(1)
                had_trailing_newline = last == b"\n"
            except OSError:
                pass
    body = "\n".join("\t".join(r) for r in rows)
    if had_trailing_newline:
        body += "\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(body)


def process(server, sheet_id, tab, file_name, out_root):
    print(f"[dump] sheet={sheet_id} tab={tab!r} file={file_name} server={server}")
    rows = gws_get(sheet_id, f"'{tab}'!A:ZZ")
    if not rows:
        raise RuntimeError("empty sheet")
    headers = rows[0]
    print(f"  raw: {len(headers)} cols × {len(rows)-1} data rows")

    # 1) split country_use_type 行
    type_idx = find_col(headers, "A_INT_country_use_type")
    if type_idx >= 0:
        fo_rows, cn_rows = split_by_country_use_type(rows, type_idx)
        target_rows = fo_rows if server == "fo" else cn_rows
        # 切完剥列
        target_rows = strip_col(target_rows, type_idx)
        print(f"  split country_use_type col[{type_idx}]: kept {len(target_rows)-1} rows for {server}, then stripped col")
    else:
        target_rows = rows
        print(f"  no country_use_type col -> full table")

    # 2) 剥非 S 开头的 STR_comment 列
    comment_idx = find_comment_col_to_strip(target_rows[0])
    if comment_idx >= 0:
        print(f"  strip non-S comment col[{comment_idx}] = {target_rows[0][comment_idx]!r}")
        target_rows = strip_col(target_rows, comment_idx)
    else:
        print(f"  no non-S STR_comment col to strip")

    target_width = len(target_rows[0])
    target_rows = normalize_row_width(target_rows, target_width)

    out_path = os.path.join(out_root, server, "config", f"{file_name}.tsv")
    write_tsv(out_path, target_rows)
    print(f"  wrote {out_path}: {target_width} cols × {len(target_rows)-1} rows")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", help="表号 e.g. 1511，自动解 SheetID + file")
    ap.add_argument("--sheet-id", help="显式 SheetID（覆盖 --table）")
    ap.add_argument("--file-name", help="tsv 文件名（不带 .tsv）")
    ap.add_argument("--tab", help="源页签名；不指定时按经验默认 {file}_QA / {file}")
    ap.add_argument("--server", choices=["fo", "cn"], default="fo",
                    help="目标 server，默认 fo（用户偏好：所有表默认 fo）")
    ap.add_argument("--out-root", default="/Users/marinl/gdconfig")
    args = ap.parse_args()

    if args.table:
        file_name, sheet_id, mode = lookup_table(args.table)
        print(f"[lookup] table {args.table} → file={file_name} sheet={sheet_id} mode={mode}")
    else:
        sheet_id = args.sheet_id
        file_name = args.file_name
        if not (sheet_id and file_name):
            print("either --table or (--sheet-id + --file-name) is required", file=sys.stderr)
            sys.exit(2)

    tab = args.tab or pick_default_tab(sheet_id, file_name)

    process(args.server, sheet_id, tab, file_name, args.out_root)


if __name__ == "__main__":
    main()
