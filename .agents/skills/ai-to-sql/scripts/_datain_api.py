#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datain API 公共模块，提供鉴权、游戏列表、SQL 执行等基础能力。"""

import os
import sys
import requests

DATAIN_API_URL = "https://datain-api.tap4fun.com/public_api/sql-lab"

# 用户侧名称 ↔ API 侧名称映射
# API 侧用 TRINO / A3_TRINO，用户侧统一用 TRINO_AWS / TRINO_HF
_DS_TO_API = {"TRINO_AWS": "TRINO", "TRINO_HF": "A3_TRINO"}
_DS_FROM_API = {"TRINO": "TRINO_AWS", "A3_TRINO": "TRINO_HF"}


def to_api_datasource(ds):
    """将用户侧 datasource 名称转换为 API 侧名称。"""
    return _DS_TO_API.get(ds, ds)


def from_api_datasource(ds):
    """将 API 侧 datasource 名称转换为用户侧名称。"""
    return _DS_FROM_API.get(ds, ds)


_games_cache = None
_tables_cache = None


def get_api_key():
    """从环境变量获取 DATAIN_API_KEY，未设置则提示用户并退出。"""
    key = os.environ.get("DATAIN_API_KEY")
    if not key:
        print(
            "错误：未检测到环境变量 DATAIN_API_KEY，请按以下步骤获取并配置：\n"
            "\n"
            "1. 权限申请：钉钉工作台 -> T4F审批 -> datain 权限申请\n"
            "2. 已有权限用户：打开 https://datain.tap4fun.com/ -> 个人中心 -> 设置 -> APP KEY\n"
            "3. 复制 APP KEY 发送给我，我来设置本机的环境变量 DATAIN_API_KEY（会持久化保存，下次无需重复设置）",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def fetch_games():
    """调用 Datain games API 获取当前用户的游戏列表和权限信息（带缓存）。"""
    global _games_cache
    if _games_cache is not None:
        return _games_cache

    api_key = get_api_key()
    resp = requests.get(
        f"{DATAIN_API_URL}/games",
        params={"api_key": api_key},
        timeout=15,
    )
    resp.raise_for_status()
    body = resp.json()
    if not body.get("success"):
        raise RuntimeError(f"Datain games API 错误: {body.get('message')}")

    data = body["data"]
    is_all = data.get("isAll", False)
    games = []
    game_cds = []
    for g in data.get("games", []):
        game_cd = int(g["value"])
        game_cds.append(game_cd)
        games.append({
            "game_cd": game_cd,
            "name": g["name"],
            "datasource": from_api_datasource(g["datasource"]),
        })

    _games_cache = {
        "is_all": is_all,
        "game_cds": game_cds,
        "games": games,
    }
    return _games_cache


def execute_sql(sql, datasource="TRINO_AWS"):
    """调用 Datain SQL execute API 执行 SQL 并返回结果。"""
    api_key = get_api_key()
    api_ds = to_api_datasource(datasource)
    resp = requests.post(
        f"{DATAIN_API_URL}/sql/execute",
        params={"api_key": api_key},
        json={"sql": sql, "datasource": api_ds},
        headers={"Content-Type": "application/json"},
        timeout=600,
    )

    # 优先从 body 提取错误信息，避免 raise_for_status 丢失细节
    try:
        body = resp.json()
    except Exception:
        resp.raise_for_status()
        raise RuntimeError(f"Datain SQL API 返回非 JSON 响应 (HTTP {resp.status_code})")

    if not body.get("success"):
        code = body.get("code", "")
        msg = body.get("message") or "未知错误"
        raise RuntimeError(
            f"SQL 执行失败 (HTTP {resp.status_code}, code={code}): {msg}\n"
            f"失败 SQL: {sql}"
        )

    return body.get("data") or []


def fetch_tables():
    """调用 Datain tables API 获取用户有权限的表列表（带缓存）。格式: catalog.layer.table"""
    global _tables_cache
    if _tables_cache is not None:
        return _tables_cache

    api_key = get_api_key()
    resp = requests.get(
        f"{DATAIN_API_URL}/tables",
        params={"api_key": api_key},
        timeout=15,
    )
    resp.raise_for_status()
    body = resp.json()
    if not body.get("success"):
        raise RuntimeError(f"Datain tables API 错误: {body.get('message')}")
    _tables_cache = body.get("data") or []
    return _tables_cache
