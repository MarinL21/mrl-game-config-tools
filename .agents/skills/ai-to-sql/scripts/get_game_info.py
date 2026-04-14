#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 Datain API 获取当前用户权限范围内的游戏信息和表权限列表。"""

import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _datain_api import fetch_games, fetch_tables

# 已经是视图 schema 的模式：v + 4位数字 或 vd + 4位数字
_VIEW_SCHEMA_RE = re.compile(r'^(v\d{4}|vd\d{4})$')

# 表名以 _yyyymmdd 结尾的快照表，应排除
_SNAPSHOT_SUFFIX_RE = re.compile(r'_\d{8}$')


def _is_snapshot_table(table_name):
    """判断表名是否为日期快照表（以 _yyyymmdd 结尾）。"""
    return bool(_SNAPSHOT_SUFFIX_RE.search(table_name))


def _to_view_tables(tables):
    """将原始表名转换为视图占位格式，供非全权限用户使用。

    转换规则：
    - 排除以 _yyyymmdd 结尾的快照表
    - 已经是视图 schema（v1038/vd5002 等）的表保持原样
    - 其他表 catalog.layer.table → catalog.v{game_cd}.layer_table
    - 使用 v{game_cd} 占位符，去重后排序输出，避免多游戏时表列表膨胀
    """
    result = set()
    for t in tables:
        if _is_snapshot_table(t):
            continue
        parts = t.split(".")
        if len(parts) != 3:
            result.add(t)
            continue
        catalog, layer, tbl = parts
        if _VIEW_SCHEMA_RE.match(layer):
            # 已经是视图，保持原样
            result.add(t)
        else:
            # 转为视图占位格式：catalog.v{game_cd}.layer_table
            result.add(f"{catalog}.v{{game_cd}}.{layer}_{tbl}")
    return sorted(result)


def get_game_info():
    data = fetch_games()
    is_all = data["is_all"]
    if is_all:
        tables_info = "全权限用户，无表限制。可通过 search_tables.py 按关键字搜索具体表名。"
    else:
        tables_info = _to_view_tables(fetch_tables())
    return {
        "full_access": is_all,
        "game_cds": data["game_cds"],
        "games": data["games"],
        "stg_access": is_all,
        "tables": tables_info,
    }


if __name__ == "__main__":
    try:
        result = get_game_info()
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
