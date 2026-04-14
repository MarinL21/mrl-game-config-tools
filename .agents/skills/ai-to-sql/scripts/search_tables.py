#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""关键字模糊搜索当前用户权限内的表。"""

import json
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _datain_api import fetch_tables, fetch_games
from get_game_info import _to_view_tables, _is_snapshot_table


def search(keyword):
    """在权限表列表中模糊匹配关键字（大小写不敏感）。

    - 排除以 _yyyymmdd 结尾的快照表
    - 非全权限用户返回视图占位格式的表名
    """
    tables = fetch_tables()
    data = fetch_games()
    if not data["is_all"]:
        tables = _to_view_tables(tables)
    kw = keyword.lower()
    return [t for t in tables if kw in t.lower() and not _is_snapshot_table(t)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="搜索权限内的表")
    parser.add_argument("--keyword", required=True, help="搜索关键字，如 login、asset")
    args = parser.parse_args()

    results = search(args.keyword)
    print(json.dumps(results, ensure_ascii=False, indent=2))
