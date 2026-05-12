#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2 1011 i18n 表全量重建工具。

i18n 不能用 id-patch（key 是字符串、跨多 tab、要写多个 lang 文件），
只能整体从 sheet 拉所有页签，按语言切分写入 fo/i18n/{lang}.tsv 或 cn/i18n/cn.tsv。

源 sheet 结构（每个页签）：
  col0 = ID_int (index_int)
  col1 = ID (LC_Key 短名)
  col2..N = 各语言列（cn / en / fr / de / ...）

输出 tsv 结构（每语言一份）：
  header: id\tvalue\tindex_int\n
  每行: {tab_name}_{ID}\t{lang_value}\t{ID_int}\n
"""

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict

# 不要写死 tab 列表 —— fw_gsheet_config 索引里的 23 个是 N 年前的快照，
# 现在 sheet 实际有 42 个 tab（多了 ARENA/HERO/KVK/IAP/METRO/SATELLITE/SITUATION/
# SOCIAL/PUSH/ART/CHINA/minigame/Operation Mail 等业务页签）。
# 改为运行时动态发现 + header 结构判断业务 tab。

# 已知的内部辅助 tab，固定跳过
INTERNAL_TAB_NAMES = {
    "AI翻译暂存", "回车检查", "本地化使用说明", "AI翻译页签", "页签检查",
    "checkncwj",
}

FO_SHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
CN_SHEET_ID = "1x7E76B9U2CWzOgbuk60F6oEDo_4Lkz1MnRJYSA9m_CM"


def list_all_tabs(sheet_id):
    """动态列出 sheet 全部 tab：返回 [(title, sheet_id), ...]。"""
    cmd = [
        "gws", "sheets", "spreadsheets", "get",
        "--params", json.dumps({
            "spreadsheetId": sheet_id,
            "fields": "sheets(properties(sheetId,title,index))",
        }),
        "--format", "json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"gws list tabs failed: {res.stderr}")
    data = json.loads(res.stdout)
    out = []
    for s in data.get("sheets", []):
        p = s.get("properties", {})
        out.append((p.get("title"), str(p.get("sheetId"))))
    return out


def read_tab(sheet_id, tab_name, max_retry=3):
    """用 gws 读单个页签全量。带 retry —— gws 偶发 SSL/network 抖动会丢包。"""
    cmd = [
        "gws", "sheets", "spreadsheets", "values", "get",
        "--params", json.dumps({
            "spreadsheetId": sheet_id,
            "range": f"'{tab_name}'!A:Z",
        }),
        "--format", "json",
    ]
    last_err = ""
    for attempt in range(1, max_retry + 1):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            try:
                return json.loads(res.stdout).get("values", [])
            except json.JSONDecodeError as e:
                last_err = f"JSONDecode: {e}; stdout head={res.stdout[:200]!r}"
        else:
            last_err = res.stderr.strip()
        print(f"  [retry {attempt}/{max_retry}] tab {tab_name}: {last_err[:120]}", flush=True)
        import time; time.sleep(2 * attempt)
    raise RuntimeError(f"gws read {tab_name} failed after {max_retry} retries: {last_err}")


def is_business_tab(tab_name, headers):
    """业务 tab 判断：header 必须是 [ID_int, ID, <lang>, <lang>, ...] 形式。

    内部辅助 tab（说明文档/检查工具/AI 暂存）一律跳过。
    """
    if tab_name in INTERNAL_TAB_NAMES:
        return False, "internal_tab_blacklist"
    if not headers or len(headers) < 3:
        return False, "header_too_short"
    h0 = (headers[0] or "").strip()
    h1 = (headers[1] or "").strip()
    if h0 != "ID_int" or h1 != "ID":
        return False, f"header_mismatch:{h0!r}/{h1!r}"
    return True, "ok"


def process(sheet_id, only_langs=None):
    """动态发现所有 tab → 按 header 形态过滤业务 tab → 按 lang 聚合。

    Returns: dict[lang] -> list[(key, value, index_int)]
    重复 key（同 lang 内不同 index_int）会报错停下来。
    """
    all_tabs = list_all_tabs(sheet_id)
    print(f"  discovered {len(all_tabs)} tabs in sheet")

    per_lang = defaultdict(list)
    seen = defaultdict(dict)  # lang -> {key: index_int}
    duplicates = defaultdict(list)
    used_tabs = []
    skipped_tabs = []

    for tab_name, _gid in all_tabs:
        rows = read_tab(sheet_id, tab_name)
        if not rows:
            skipped_tabs.append((tab_name, "empty"))
            continue
        headers = rows[0]
        ok, reason = is_business_tab(tab_name, headers)
        if not ok:
            skipped_tabs.append((tab_name, reason))
            continue
        used_tabs.append(tab_name)
        # col0 = ID_int, col1 = ID, col2.. = lang columns
        lang_cols = []
        for col_idx in range(2, len(headers)):
            lang = headers[col_idx].strip()
            if not lang:
                continue
            if only_langs and lang not in only_langs:
                continue
            lang_cols.append((col_idx, lang))

        for row in rows[1:]:
            if not row or not row[0].strip():
                continue
            try:
                index_int = row[0].strip()
                lc_id = row[1].strip() if len(row) > 1 else ""
            except IndexError:
                continue
            if not lc_id:
                continue
            key = f"{tab_name}_{lc_id}"
            for col_idx, lang in lang_cols:
                value = row[col_idx] if col_idx < len(row) else ""
                if key in seen[lang] and seen[lang][key] != index_int:
                    duplicates[lang].append((key, seen[lang][key], index_int))
                    continue
                seen[lang][key] = index_int
                per_lang[lang].append((key, value, index_int))

    if duplicates:
        for lang, dups in duplicates.items():
            print(f"[ERROR] duplicate keys in {lang}: {len(dups)}", file=sys.stderr)
            for k, old, new in dups[:5]:
                print(f"  {k}: index_int {old} vs {new}", file=sys.stderr)
        raise SystemExit(2)

    print(f"  used {len(used_tabs)} business tabs: {','.join(used_tabs)}")
    if skipped_tabs:
        print(f"  skipped {len(skipped_tabs)}:")
        for name, reason in skipped_tabs:
            print(f"    - {name} ({reason})")

    return per_lang


def escape_value(v):
    """sheet cell 内若有真换行/制表符（误输入 Enter），转义成字面两字符。

    仓库历史 tsv 里换行都是字面 `\\n`（双字符），runtime 自己解。不转义会切碎 tsv 行。
    注意：不能 escape 反斜杠 —— sheet 里已经是字面 `\\n`，再转就变 `\\\\n`。
    """
    return (v or "").replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n").replace("\t", "\\t")


def write_tsv(out_dir, lang, rows):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{lang}.tsv")
    # 仓库历史按 key 字母序存储（GSheetDownloader 老脚本的最终落盘顺序）。
    # 不排序会导致整文件 diff，掩盖真实增量。
    rows_sorted = sorted(rows, key=lambda r: r[0])
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("id\tvalue\tindex_int\n")
        for key, value, idx in rows_sorted:
            f.write(f"{key}\t{escape_value(value)}\t{idx}\n")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", choices=["fo", "cn"], required=True,
                    help="fo=国际服(18 lang) / cn=国服(只 cn.tsv)")
    ap.add_argument("--out-root", default="/Users/marinl/gdconfig",
                    help="gdconfig repo 根目录")
    ap.add_argument("--sheet-id", default=None,
                    help="覆盖默认 SheetID（默认按 --server 选 fo/cn 对应 ID）")
    ap.add_argument("--lang", default=None,
                    help="只重建特定 lang（逗号分隔），调试用；默认全部")
    args = ap.parse_args()

    sheet_id = args.sheet_id or (FO_SHEET_ID if args.server == "fo" else CN_SHEET_ID)
    only_langs = set(args.lang.split(",")) if args.lang else None
    if args.server == "cn" and not only_langs:
        only_langs = {"cn"}  # cn 仓库只保留 cn.tsv

    out_dir = os.path.join(args.out_root, args.server, "i18n")

    print(f"[1011 rebuild] server={args.server} sheet={sheet_id}")
    print(f"  out_dir={out_dir}")
    print(f"  langs={'all' if not only_langs else sorted(only_langs)}")

    per_lang = process(sheet_id, only_langs)

    written = []
    for lang, rows in sorted(per_lang.items()):
        path = write_tsv(out_dir, lang, rows)
        written.append((lang, len(rows), path))
        print(f"  ✓ {lang}.tsv {len(rows)} rows")

    print(f"\n{len(written)} file(s) written.")


if __name__ == "__main__":
    main()
