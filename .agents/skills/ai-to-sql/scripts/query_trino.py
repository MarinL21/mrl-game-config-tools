#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 Datain API 执行 Trino SQL 并返回 JSON 格式结果。"""

import json
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _datain_api import execute_sql as api_execute_sql

DEFAULT_DATASOURCE = "TRINO_AWS"

# 禁止执行的危险关键字
_DANGEROUS_PATTERN = re.compile(
    r"\b(DROP|ALTER|DELETE|INSERT|UPDATE|CREATE|TRUNCATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def execute_sql(sql, limit=100, datasource=None):
    sql = sql.strip().rstrip(";")
    if _DANGEROUS_PATTERN.search(sql):
        raise ValueError("仅允许执行 SELECT / EXPLAIN / SHOW / DESCRIBE 语句")

    ds = datasource or DEFAULT_DATASOURCE
    rows = api_execute_sql(sql, ds)

    if not rows:
        return {"columns": [], "data": [], "row_count": 0}

    columns = list(rows[0].keys())
    limited = rows[:limit]
    return {"columns": columns, "data": limited, "row_count": len(limited)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="执行 Trino SQL 并返回结果")
    parser.add_argument("--sql", required=True, help="待执行的 SQL 语句")
    parser.add_argument("--limit", type=int, default=100, help="返回行数限制，默认 100")
    parser.add_argument("--datasource", default=DEFAULT_DATASOURCE,
                        choices=["TRINO_AWS", "TRINO_HF"],
                        help="数据源环境：TRINO_AWS（老游戏）或 TRINO_HF（新游戏），默认 TRINO_AWS")
    args = parser.parse_args()

    try:
        result = execute_sql(args.sql, args.limit, args.datasource)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
