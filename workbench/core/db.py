#!/usr/bin/env python3
"""工作台 · 数据层（SQLite）。

一个库装所有模块，表名按模块加前缀（gallery_* / 后续 numeric_* / pkg_* …），
这样以后并模块进来不用改动已有数据。
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DB_F = DATA / "workbench.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS gallery_asset (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  sha1        TEXT UNIQUE NOT NULL,       -- 内容指纹，重复投喂自动去重
  kind        TEXT NOT NULL,              -- image | video
  filename    TEXT,                       -- 原始文件名（保留线索）
  path        TEXT NOT NULL,              -- 相对 data/ 的存放路径
  thumb       TEXT,                       -- 相对 data/ 的缩略图路径
  width       INTEGER, height INTEGER,
  duration    REAL,                       -- 视频时长(秒)
  bytes       INTEGER,
  game        TEXT DEFAULT '',            -- 游戏
  category    TEXT DEFAULT '',            -- 外观类别
  title       TEXT DEFAULT '',            -- 这件外观叫什么
  tags        TEXT DEFAULT '',            -- 逗号分隔自由标签
  note        TEXT DEFAULT '',            -- 备注：为什么好看 / 想借鉴什么
  source_url  TEXT DEFAULT '',
  rating      INTEGER DEFAULT 0,          -- 0-3 星
  status      TEXT DEFAULT 'new',         -- new 待标注 | done 已标注
  created_at  TEXT, updated_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_ga_game   ON gallery_asset(game);
CREATE INDEX IF NOT EXISTS ix_ga_cat    ON gallery_asset(category);
CREATE INDEX IF NOT EXISTS ix_ga_status ON gallery_asset(status);

-- 分类池：game / category，网页上可增删改，不写死在代码里
CREATE TABLE IF NOT EXISTS gallery_tax (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  kind  TEXT NOT NULL,                    -- game | category
  name  TEXT NOT NULL,
  alias TEXT DEFAULT '',                  -- 别名/英文名，搜索和 AI 预标用
  sort  INTEGER DEFAULT 100,
  UNIQUE(kind, name)
);
"""

_local = threading.local()


def conn() -> sqlite3.Connection:
    c = getattr(_local, "c", None)
    if c is None:
        DATA.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(DB_F, check_same_thread=False)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA foreign_keys=ON")
        _local.c = c
    return c


def init() -> None:
    c = conn()
    c.executescript(SCHEMA)
    c.commit()
    seed_taxonomy()


def seed_taxonomy() -> None:
    """首次启动把 taxonomy.json 的初始池播进库；已存在的不动（用户改过的优先）。"""
    f = ROOT / "taxonomy.json"
    if not f.exists():
        return
    tax = json.loads(f.read_text(encoding="utf-8"))
    c = conn()
    for kind, key in (("game", "games"), ("category", "categories")):
        for i, item in enumerate(tax.get(key, [])):
            name = item["name"] if isinstance(item, dict) else item
            alias = item.get("alias", "") if isinstance(item, dict) else ""
            c.execute(
                "INSERT OR IGNORE INTO gallery_tax(kind,name,alias,sort) VALUES(?,?,?,?)",
                (kind, name, alias, i * 10),
            )
    c.commit()


def rows(sql: str, args: tuple = ()) -> list[dict]:
    return [dict(r) for r in conn().execute(sql, args).fetchall()]


def one(sql: str, args: tuple = ()) -> dict | None:
    r = conn().execute(sql, args).fetchone()
    return dict(r) if r else None


def run(sql: str, args: tuple = ()) -> sqlite3.Cursor:
    c = conn()
    cur = c.execute(sql, args)
    c.commit()
    return cur
