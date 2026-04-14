#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 Datain API 探索 Trino 表结构。自动处理 TRINO_HF 环境 catalog 前缀。"""

import json
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _datain_api import fetch_tables, execute_sql

DEFAULT_DATASOURCE = "TRINO_AWS"


def resolve_table_name(table_name, datasource="TRINO_AWS"):
    """解析实际查询用的表名（处理 TRINO_HF 环境 catalog 前缀）。

    table_name: 两段式 layer.table（如 ods.user_login）或三段式 catalog.layer.table
    返回: 实际用于 DESCRIBE 的表名
    """
    parts = table_name.split(".")
    if len(parts) == 3:
        # 三段式: catalog.layer.table
        # TRINO_AWS 环境默认 hive，不需要 catalog 前缀
        if datasource == "TRINO_AWS":
            return f"{parts[1]}.{parts[2]}"
        # TRINO_HF 环境默认 iceberg，hive 的需要前缀
        if parts[0] == "iceberg":
            return f"{parts[1]}.{parts[2]}"
        return table_name  # hive.xxx.xxx 保留前缀
    elif len(parts) == 2:
        if datasource == "TRINO_AWS":
            return table_name
        else:
            # TRINO_HF: 查 tables 列表判断是否需要加 hive. 前缀
            layer, tbl = parts
            tables = fetch_tables()
            tables_set = set(tables)
            iceberg_full = f"iceberg.{layer}.{tbl}"
            if iceberg_full in tables_set:
                return table_name
            else:
                return f"hive.{layer}.{tbl}"
    else:
        return table_name


def describe_table(table_name, datasource="TRINO_AWS"):
    """通过 Datain API 执行 DESCRIBE 获取表结构。"""
    rows = execute_sql(f"DESCRIBE {table_name}", datasource)
    columns = []
    partitions = []
    for row in rows:
        col_name = (row.get("Column") or "").strip()
        col_type = (row.get("Type") or "").strip()
        col_extra = (row.get("Extra") or "").strip()
        col_comment = (row.get("Comment") or "").strip()
        if not col_name or col_name.startswith("#"):
            continue
        entry = {"name": col_name, "type": col_type}
        if col_comment:
            entry["comment"] = col_comment
        if "partition" in col_extra.lower():
            partitions.append(entry)
        else:
            columns.append(entry)
    return {"table": table_name, "columns": columns, "partitions": partitions}


def explore(table_names, datasource=None):
    ds = datasource or DEFAULT_DATASOURCE
    results = []
    for t in table_names:
        t = t.strip()
        if not t:
            continue
        try:
            actual = resolve_table_name(t, ds)
            info = describe_table(actual, ds)
            if actual != t:
                info["original"] = t
            results.append(info)
        except Exception as e:
            results.append({"table": t, "error": str(e)})
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="探索 Trino 表结构（自动处理 catalog 前缀）")
    parser.add_argument("--tables", required=True, help="逗号分隔的表名，如 ods.user_login,dl.user_daily")
    parser.add_argument("--datasource", default=DEFAULT_DATASOURCE,
                        choices=["TRINO_AWS", "TRINO_HF"],
                        help="数据源环境：TRINO_AWS（老游戏）或 TRINO_HF（新游戏），默认 TRINO_AWS")
    args = parser.parse_args()

    tables = args.tables.split(",")
    results = explore(tables, args.datasource)
    print(json.dumps(results, ensure_ascii=False, indent=2))
