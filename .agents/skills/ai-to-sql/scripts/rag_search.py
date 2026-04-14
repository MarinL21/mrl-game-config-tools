#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调用 rag-service 检索向量库，支持指标参考和公司文档两个知识库。"""

import json
import argparse
import os
import sys
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "..", "config.json")

# 固定检索参数
SEARCH_MODE = "hybrid"
HYBRID_WEIGHT = 0.5
TOKENIZE_QUERY = True
ENABLE_RERANK = True
RERANK_AMPLIFY_FACTOR = 3.0
MAX_TOP_N = 100


_cfg_cache = None


def load_config():
    global _cfg_cache
    if _cfg_cache is None:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _cfg_cache = json.load(f)
    return _cfg_cache


def _search_collection(cfg, project, table, query, top_n=10, where=None):
    """调用 rag-service 单个集合的检索。"""
    url = f"{cfg['rag_service_url']}/api/v1/search"
    headers = {}
    token = cfg.get("rag_service_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "project_name": project,
        "table_name": table,
        "query": query.strip(),
        "top_n": min(top_n, MAX_TOP_N),
        "search_mode": SEARCH_MODE,
        "hybrid_weight": HYBRID_WEIGHT,
        "tokenize_query": TOKENIZE_QUERY,
        "enable_rerank": ENABLE_RERANK,
        "rerank_amplify_factor": RERANK_AMPLIFY_FACTOR,
    }
    if where:
        payload["where"] = where

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", {}).get("results") or []


def search_metrics(query, game_cds=None, top_n=10):
    """检索指标参考 SQL（ai_to_sql.sql_key_metrics_define）。

    强制权限隔离：用户只能检索 game_cd=1000（通用）和自己有权限的游戏的参考 SQL。
    - game_cds 传入时：使用传入值 + 1000
    - game_cds 未传入时：自动获取用户全部有权限的 game_cds + 1000
    - full_access=true 的用户不做过滤（可查看所有参考 SQL）
    """
    from _datain_api import fetch_games

    cfg = load_config()
    coll = cfg["collections"]["metrics"]

    # 获取用户权限信息
    games_data = fetch_games()
    is_all = games_data.get("is_all", False)

    # 全权限用户不做 game_cd 过滤
    if is_all:
        where = None
        if game_cds:
            cd_set = set(game_cds)
            cd_set.add("1000")
            conditions = " OR ".join(f"game_cd='{cd}'" for cd in sorted(cd_set))
            where = conditions
        return _search_collection(cfg, coll["project"], coll["table"], query, top_n, where)

    # 非全权限用户：强制按权限过滤
    user_game_cds = {str(cd) for cd in games_data.get("game_cds", [])}
    if game_cds:
        # 取传入值与用户权限的交集
        cd_set = set(game_cds) & user_game_cds
    else:
        # 未传入则使用用户全部有权限的 game_cds
        cd_set = user_game_cds
    cd_set.add("1000")
    conditions = " OR ".join(f"game_cd='{cd}'" for cd in sorted(cd_set))
    where = conditions
    return _search_collection(cfg, coll["project"], coll["table"], query, top_n, where)


def search_wiki(query, top_n=10):
    """检索公司文档（hr_ai.wiki_doc）。wiki 无 game_cd 概念，不支持游戏过滤。"""
    cfg = load_config()
    coll = cfg["collections"]["wiki"]
    where = "char_length(content)>=30"
    return _search_collection(cfg, coll["project"], coll["table"], query, top_n, where)


def search_all(query, game_cds=None, top_n=10):
    """同时检索指标参考和公司文档，合并返回。"""
    metrics = search_metrics(query, game_cds, top_n)
    wiki = search_wiki(query, top_n)
    return {"metrics": metrics, "wiki": wiki}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="检索向量库（指标参考 + 公司文档）")
    parser.add_argument("--query", required=True, help="检索关键词")
    parser.add_argument("--game_cd", default=None, help="游戏编码，多个用逗号分隔，如 1012,1038。自动包含 1000（通用指标）")
    parser.add_argument("--top_n", type=int, default=40, help="每个知识库返回条数，默认 40，最大 100")
    parser.add_argument(
        "--source", default="all", choices=["metrics", "wiki", "all"],
        help="检索来源：metrics=指标参考, wiki=公司文档, all=全部（默认）",
    )
    args = parser.parse_args()

    if args.top_n < 1 or args.top_n > MAX_TOP_N:
        print(f"top_n 必须在 1~{MAX_TOP_N} 之间", file=sys.stderr)
        sys.exit(1)

    game_cds = [cd.strip() for cd in args.game_cd.split(",")] if args.game_cd else None

    if args.source == "metrics":
        result = search_metrics(args.query, game_cds, args.top_n)
    elif args.source == "wiki":
        result = search_wiki(args.query, args.top_n)
    else:
        result = search_all(args.query, game_cds, args.top_n)

    print(json.dumps(result, ensure_ascii=False, indent=2))
