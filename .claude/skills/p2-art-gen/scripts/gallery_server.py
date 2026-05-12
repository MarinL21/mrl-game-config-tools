#!/usr/bin/env python3
"""P2 art-gen 工作台后端（多模块版）。

支持 module = chest（节日道具自选箱）/ item（活动道具）双 tab。
每个 module 各自独立：
- _user_picks/  当前轮 ref
- _user_lib/    我的常用库
- 风格卡片      过滤展示
- 历史批次      module 字段区分
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_file, abort

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent
PROJECT_ROOT = SCRIPTS_DIR.parents[3]
SVN_ROOT = Path.home() / "AssetsSVN" / "P2_UI_CUT"
OUTPUT_DIR = PROJECT_ROOT / "output" / "grfal"
DATA_FILE = OUTPUT_DIR / "gallery_data.json"
CARDS_FILE = OUTPUT_DIR / "style_cards.json"
FAVS_FILE = OUTPUT_DIR / "favorites.json"
DIGHOLE_THEMES_FILE = OUTPUT_DIR / "dighole_themes.json"
DIGHOLE_SHAPE_FILE = SCRIPTS_DIR.parent / "anchors" / "dighole" / "_shape_ref" / "_current.png"
APP_HTML = SCRIPTS_DIR / "gallery_app.html"

ALLOW_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VALID_MODULES = {"chest", "item", "dighole", "ui", "frame"}
MODULE_LABEL = {"chest": "节日道具自选箱", "item": "活动道具", "dighole": "挖孔道具", "ui": "界面 UI", "frame": "底板"}

DEFAULT_CARDS = [
    {"prompt": "远古沉船", "module": "chest"},
    {"prompt": "深渊鲛人", "module": "chest"},
    {"prompt": "珊瑚精灵", "module": "chest"},
    {"prompt": "深海机械", "module": "chest"},
]

TASKS: dict[str, dict] = {}
TASK_LOCK = threading.Lock()

app = Flask(__name__, static_folder=None)


# ---------- helpers ----------

def _module(default: str = "chest") -> str:
    m = (request.args.get("module") or "").strip()
    if not m:
        body = request.get_json(silent=True) if request.method != "GET" else None
        if body:
            m = (body.get("module") or "").strip()
    if m not in VALID_MODULES:
        m = default
    return m


def picks_dir(module: str) -> Path:
    return SKILL_DIR / "anchors" / module / "_user_picks"


def comp_dir(module: str) -> Path:
    """竞品池：按形状/结构走的 ref（dighole 等结构敏感模块用）"""
    return SKILL_DIR / "anchors" / module / "_competitor"


def lib_dir(module: str) -> Path:
    return SKILL_DIR / "anchors" / module / "_user_lib"


def _safe_under(target: Path, root: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _read_batches() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_into(target_dir: Path, src_bytes_or_path, base_name: str) -> str:
    target_dir.mkdir(parents=True, exist_ok=True)
    base = Path(base_name).name
    dst = target_dir / base
    if dst.exists():
        stem, suf = dst.stem, dst.suffix
        n = 2
        while (target_dir / f"{stem}_{n}{suf}").exists():
            n += 1
        dst = target_dir / f"{stem}_{n}{suf}"
    if isinstance(src_bytes_or_path, Path):
        shutil.copy2(src_bytes_or_path, dst)
    else:
        dst.write_bytes(src_bytes_or_path)
    return dst.name


def _list_dir(d: Path) -> list[dict]:
    d.mkdir(parents=True, exist_ok=True)
    return [
        {"name": p.name, "size": p.stat().st_size}
        for p in sorted(d.iterdir(), key=lambda x: x.name.lower())
        if p.is_file() and p.suffix.lower() in ALLOW_EXT
    ]


# ---------- 风格卡片（含 module）----------

def _read_cards() -> list[dict]:
    if not CARDS_FILE.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        seeded = [{**c, "id": i + 1} for i, c in enumerate(DEFAULT_CARDS)]
        CARDS_FILE.write_text(json.dumps(seeded, ensure_ascii=False, indent=2), encoding="utf-8")
        return seeded
    try:
        cards = json.loads(CARDS_FILE.read_text(encoding="utf-8"))
        # 旧格式自动迁移：没 prompt 的 → 拼接 name；没 module 的 → 默认 chest
        migrated = False
        for c in cards:
            if "prompt" not in c:
                c["prompt"] = c.get("name") or "未命名"
                c.pop("name", None); c.pop("elements", None); c.pop("palette", None)
                migrated = True
            if "module" not in c:
                c["module"] = "chest"
                migrated = True
        if migrated:
            CARDS_FILE.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
        return cards
    except Exception:
        return []


def _write_cards(cards: list[dict]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CARDS_FILE.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- 收藏（favorites） ----------

def _read_favs() -> set[str]:
    if not FAVS_FILE.exists():
        return set()
    try:
        raw = json.loads(FAVS_FILE.read_text(encoding="utf-8"))
        return set(raw) if isinstance(raw, list) else set()
    except Exception:
        return set()


def _write_favs(s: set[str]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FAVS_FILE.write_text(json.dumps(sorted(s), ensure_ascii=False, indent=2), encoding="utf-8")


def _favs_summary(favs: set[str]) -> dict:
    """统计 favs 在各 module 下命中数（用于 tab badge）"""
    by_module = {m: 0 for m in VALID_MODULES}
    for b in _read_batches():
        m = b.get("module")
        if m not in by_module:
            continue
        for c in b.get("cells") or []:
            if c.get("src") in favs:
                by_module[m] += 1
    return {"total": len(favs), "by_module": by_module}


@app.get("/api/favorites")
def api_favorites():
    """返回收藏全集 + 统计，供前端打星 / tab 角标用。"""
    favs = _read_favs()
    return jsonify({"srcs": sorted(favs), **_favs_summary(favs)})


@app.post("/api/favorites/toggle")
def api_favorites_toggle():
    body = request.get_json(silent=True) or {}
    src = (body.get("src") or "").strip().lstrip("/")
    if not src:
        return jsonify({"error": "src required"}), 400
    favs = _read_favs()
    if src in favs:
        favs.remove(src); favorited = False
    else:
        favs.add(src); favorited = True
    _write_favs(favs)
    return jsonify({"src": src, "favorited": favorited, **_favs_summary(favs)})


@app.post("/api/favorites/sync_open")
def api_favorites_sync_open():
    """把所有收藏图片归类复制到 favorites_export/，按 module 分子目录，
    写 manifest.txt 记录 prompt，最后在 Finder 打开。"""
    favs = _read_favs()
    if not favs:
        return jsonify({"error": "收藏为空"}), 400

    folder = OUTPUT_DIR / "favorites_export"
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)

    src_to_meta: dict[str, tuple[str, str]] = {}
    for b in _read_batches():
        m = b.get("module", "unknown")
        prompt = b.get("prompt", "") or ""
        for c in (b.get("cells") or []):
            s = c.get("src")
            if s in favs:
                src_to_meta[s] = (m, prompt)

    manifest_lines = ["# module/filename\tprompt"]
    copied = 0
    missing = 0
    for src in sorted(favs):
        rel = src.lstrip("/")
        full = OUTPUT_DIR / rel
        if not full.exists():
            missing += 1
            continue
        m, prompt = src_to_meta.get(src, ("unknown", ""))
        sub = folder / m
        sub.mkdir(parents=True, exist_ok=True)
        dest = sub / full.name
        # 同名重复（极少见）加序号
        if dest.exists():
            stem, suf = dest.stem, dest.suffix
            i = 1
            while (sub / f"{stem}_{i}{suf}").exists():
                i += 1
            dest = sub / f"{stem}_{i}{suf}"
        shutil.copy2(full, dest)
        manifest_lines.append(f"{m}/{dest.name}\t{prompt}")
        copied += 1

    (folder / "manifest.txt").write_text("\n".join(manifest_lines), encoding="utf-8")

    open_err = None
    try:
        subprocess.Popen(["open", str(folder)])
    except Exception as e:
        open_err = str(e)

    return jsonify({
        "folder": str(folder),
        "count": copied,
        "missing": missing,
        "open_error": open_err,
    })


@app.get("/api/favorites/list")
def api_favorites_list():
    """收藏 tab 数据：按原 batch 分组，只保留收藏 cell。"""
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(50, int(request.args.get("per_page", 5))))
    keyword = (request.args.get("q") or "").strip().lower()
    favs = _read_favs()
    out = []
    for b in _read_batches():
        kept = [c for c in (b.get("cells") or []) if c.get("src") in favs]
        if not kept:
            continue
        if keyword and keyword not in (b.get("prompt", "") or "").lower():
            continue
        out.append({**b, "cells": kept})
    out = list(reversed(out))
    total = len(out)
    total_pages = max(1, (total + per_page - 1) // per_page)
    s, e = (page - 1) * per_page, page * per_page
    return jsonify({"batches": out[s:e], "page": page, "per_page": per_page,
                    "total": total, "total_pages": total_pages})


# ---------- 挖孔道具：让 Claude 想主题 ----------

def _read_dh_themes() -> dict:
    if not DIGHOLE_THEMES_FILE.exists():
        return {}
    try:
        return json.loads(DIGHOLE_THEMES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_dh_themes(d: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DIGHOLE_THEMES_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


@app.post("/api/dighole/scaffold")
def api_dighole_scaffold():
    body = request.get_json(silent=True) or {}
    direction = (body.get("direction") or "").strip()
    n = max(1, min(20, int(body.get("n", 6))))
    shape_ascii = (body.get("shape_ascii") or "").strip()
    shape_w = int(body.get("shape_w") or 0)
    shape_h = int(body.get("shape_h") or 0)
    shape_cells = int(body.get("shape_cells") or 0)
    notes = (body.get("notes") or "").strip()
    if not direction:
        return jsonify({"error": "方向不能为空"}), 400

    notes_block = f"\n📝 用户补充：\n{notes}\n" if notes else ""
    scaffold = (
        f"帮我想 {n} 个挖孔小游戏的活动道具主题，方向是【{direction}】。形状由 web 端竞品池图直接传达，你不用考虑形状，只想题材就行。\n"
        f"{notes_block}\n"
        f"格式（对齐活动道具 item 规范）：每个主题 = 「道具名，简单道具描述」，逗号分隔，整段 12-25 字。\n"
        f"  示例（不同形状参考）：\n"
        f"    1×4 长条 → 「青铜匕首，刀身有锈蚀刻纹的窄刃直刀」\n"
        f"    2×2 方块 → 「黄铜罗盘，铜壳镶宝石指针带刻度盘」\n"
        f"    L 形    → 「机械扳手，锯齿夹口配伸缩柄」\n\n"
        f"硬要求：\n"
        f"  - 视觉上要适配这个形状（长条→剑/卷轴/管道；方→箱/罐/卡；L→拐杖/曲管/扳手 …）\n"
        f"  - 描述要落在「材质 + 形态特征」，例如「金属拼接带焊接痕迹」「水晶柱嵌岩石母矿」\n"
        f"  - 不要写颜色（颜色由参考图画风决定，prompt 写死会冲突）\n"
        f"  - 主题之间形态各异，不要全「宝箱/钥匙」系\n"
        f"  - 符合「{direction}」氛围\n\n"
        f"出完后调 POST http://localhost:8765/api/dighole/themes，body：\n"
        f'  {{"direction":"{direction}","themes":[{{"prompt":"道具名1，简单描述1"}}, ...]}}\n\n'
        f"我会在 web 上看到主题候选，点一下就填到输入框，▶ 跑图直接用。"
    )
    return jsonify({"scaffold": scaffold, "direction": direction})


@app.post("/api/dighole/themes")
def api_dighole_themes_save():
    body = request.get_json(silent=True) or {}
    direction = (body.get("direction") or "").strip()
    themes = body.get("themes") or []
    if not direction or not isinstance(themes, list) or not themes:
        return jsonify({"error": "direction 和 themes 必填"}), 400
    norm = []
    for t in themes:
        p = ((t.get("prompt") or t.get("name") or "").strip()) if isinstance(t, dict) else str(t).strip()
        if p:
            norm.append({"prompt": p})
    if not norm:
        return jsonify({"error": "themes 没有有效项"}), 400
    data = _read_dh_themes()
    data[direction] = {"themes": norm, "ts": int(time.time())}
    _write_dh_themes(data)
    return jsonify({"saved": len(norm), "direction": direction})


@app.post("/api/dighole/save_shape")
def api_dighole_save_shape():
    """前端把网格形状渲染成 PNG 上传，作为生图时的 ref-0（外形约束）。"""
    f = request.files.get("shape")
    if not f:
        return jsonify({"error": "shape file required"}), 400
    DIGHOLE_SHAPE_FILE.parent.mkdir(parents=True, exist_ok=True)
    f.save(str(DIGHOLE_SHAPE_FILE))
    return jsonify({"saved": True, "size": DIGHOLE_SHAPE_FILE.stat().st_size, "path": str(DIGHOLE_SHAPE_FILE)})


@app.get("/api/dighole/themes")
def api_dighole_themes_get():
    direction = (request.args.get("direction") or "").strip()
    data = _read_dh_themes()
    if direction:
        return jsonify(data.get(direction) or {"themes": [], "ts": 0})
    return jsonify(data)


# ---------- index ----------

@app.get("/")
def index():
    if not APP_HTML.exists():
        return "gallery_app.html 缺失", 500
    resp = send_file(APP_HTML)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp


# ---------- batches ----------

@app.get("/api/batches")
def api_batches():
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(50, int(request.args.get("per_page", 5))))
    module = (request.args.get("module") or "").strip()  # 不限默认全部
    keyword = (request.args.get("q") or "").strip().lower()
    data = _read_batches()
    if module and module in VALID_MODULES:
        data = [b for b in data if b.get("module") == module]
    if keyword:
        data = [b for b in data if keyword in b.get("prompt", "").lower()]
    data = list(reversed(data))
    total = len(data)
    total_pages = max(1, (total + per_page - 1) // per_page)
    s, e = (page - 1) * per_page, page * per_page
    return jsonify({"batches": data[s:e], "page": page, "per_page": per_page,
                    "total": total, "total_pages": total_pages})


# ---------- output / SVN / refs / lib 静态代理 ----------

def _sniff_image_mime(p: Path) -> str | None:
    """按 magic bytes 给正确的 Content-Type，避免 .png 后缀但内容是 JPEG 的错配。"""
    try:
        with p.open("rb") as f:
            head = f.read(12)
    except Exception:
        return None
    if head.startswith(b"\xff\xd8\xff"): return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"): return "image/png"
    if head.startswith(b"GIF87a") or head.startswith(b"GIF89a"): return "image/gif"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP": return "image/webp"
    return None


@app.get("/output/<path:rel>")
def output_file(rel: str):
    target = OUTPUT_DIR / rel
    if not target.is_file() or not _safe_under(target, OUTPUT_DIR):
        abort(404)
    mt = _sniff_image_mime(target) if target.suffix.lower() in ALLOW_EXT else None
    return send_file(target, mimetype=mt) if mt else send_file(target)


@app.get("/svn/<path:rel>")
def svn_file(rel: str):
    target = SVN_ROOT / rel
    if not target.is_file() or not _safe_under(target, SVN_ROOT):
        abort(404)
    return send_file(target)


@app.get("/comp/<module>/<name>")
def comp_file(module: str, name: str):
    if module not in VALID_MODULES or "/" in name or "\\" in name:
        abort(400)
    target = comp_dir(module) / name
    if not target.is_file() or not _safe_under(target, comp_dir(module)):
        abort(404)
    return send_file(target)


@app.get("/refs/<module>/<name>")
def refs_file(module: str, name: str):
    if module not in VALID_MODULES or "/" in name or "\\" in name:
        abort(400)
    target = picks_dir(module) / name
    if not target.is_file() or not _safe_under(target, picks_dir(module)):
        abort(404)
    return send_file(target)


@app.get("/lib/<module>/<name>")
def lib_file(module: str, name: str):
    if module not in VALID_MODULES or "/" in name or "\\" in name:
        abort(400)
    target = lib_dir(module) / name
    if not target.is_file() or not _safe_under(target, lib_dir(module)):
        abort(404)
    return send_file(target)


# ---------- SVN 浏览 ----------

@app.get("/api/svn/list")
def api_svn_list():
    rel = (request.args.get("path") or "").strip().lstrip("/")
    target = (SVN_ROOT / rel) if rel else SVN_ROOT
    if not target.exists() or not _safe_under(target, SVN_ROOT):
        abort(404)
    if not target.is_dir():
        abort(400)
    items = []
    for child in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        if child.name.startswith(".") or child.name == ".svn":
            continue
        items.append({
            "name": child.name,
            "path": str(child.relative_to(SVN_ROOT)),
            "is_dir": child.is_dir(),
            "is_image": child.is_file() and child.suffix.lower() in ALLOW_EXT,
        })
    parent = str(Path(rel).parent) if rel else None
    if parent == ".":
        parent = ""
    return jsonify({"path": rel, "parent": parent, "items": items})


# ---------- _competitor（竞品池，按 module 区分；按形状/结构走的 ref） ----------

@app.get("/api/comp/list")
def api_comp_list():
    m = _module()
    return jsonify({"module": m, "items": _list_dir(comp_dir(m)), "dir": str(comp_dir(m))})


@app.post("/api/comp/upload")
def api_comp_upload():
    m = (request.args.get("module") or "dighole")
    if m not in VALID_MODULES:
        m = "dighole"
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "no files"}), 400
    saved, skipped = [], []
    for f in files:
        if not f.filename:
            continue
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOW_EXT:
            skipped.append({"name": f.filename, "reason": f"非图片 ({ext})"})
            continue
        saved.append({"name": _save_into(comp_dir(m), f.read(), f.filename)})
    return jsonify({"saved": saved, "skipped": skipped, "module": m})


@app.post("/api/comp/import_svn")
def api_comp_import_svn():
    body = request.get_json(silent=True) or {}
    m = body.get("module", "dighole")
    if m not in VALID_MODULES:
        m = "dighole"
    paths = body.get("paths") or []
    saved, skipped = [], []
    for rel in paths:
        rel = (rel or "").lstrip("/")
        src = SVN_ROOT / rel
        if not src.is_file() or not _safe_under(src, SVN_ROOT) or src.suffix.lower() not in ALLOW_EXT:
            skipped.append({"name": rel, "reason": "无效"})
            continue
        saved.append({"name": _save_into(comp_dir(m), src, src.name), "from": rel})
    return jsonify({"saved": saved, "skipped": skipped, "module": m})


@app.post("/api/comp/clear")
def api_comp_clear():
    m = _module()
    d = comp_dir(m)
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in d.iterdir():
        if p.is_file() and p.suffix.lower() in ALLOW_EXT:
            p.unlink()
            n += 1
    return jsonify({"cleared": n, "module": m})


@app.post("/api/comp/delete")
def api_comp_delete():
    body = request.get_json(silent=True) or {}
    m = body.get("module", "dighole")
    if m not in VALID_MODULES:
        m = "dighole"
    name = (body.get("name") or "").strip()
    if not name or "/" in name or "\\" in name:
        return jsonify({"error": "invalid name"}), 400
    target = comp_dir(m) / name
    if target.is_file() and _safe_under(target, comp_dir(m)):
        target.unlink()
        return jsonify({"deleted": name, "module": m})
    return jsonify({"error": "not found"}), 404


# ---------- _user_picks（当前 ref，按 module 区分） ----------

@app.get("/api/refs/list")
def api_refs_list():
    m = _module()
    return jsonify({"module": m, "items": _list_dir(picks_dir(m)), "dir": str(picks_dir(m))})


@app.post("/api/refs/upload")
def api_refs_upload():
    m = (request.args.get("module") or "chest")
    if m not in VALID_MODULES:
        m = "chest"
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "no files"}), 400
    saved, skipped = [], []
    for f in files:
        if not f.filename:
            continue
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOW_EXT:
            skipped.append({"name": f.filename, "reason": f"非图片 ({ext})"})
            continue
        saved.append({"name": _save_into(picks_dir(m), f.read(), f.filename)})
    return jsonify({"saved": saved, "skipped": skipped, "module": m})


@app.post("/api/refs/import_svn")
def api_refs_import_svn():
    body = request.get_json(silent=True) or {}
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    paths = body.get("paths") or []
    saved, skipped = [], []
    for rel in paths:
        rel = (rel or "").lstrip("/")
        src = SVN_ROOT / rel
        if not src.is_file() or not _safe_under(src, SVN_ROOT) or src.suffix.lower() not in ALLOW_EXT:
            skipped.append({"name": rel, "reason": "无效"})
            continue
        saved.append({"name": _save_into(picks_dir(m), src, src.name), "from": rel})
    return jsonify({"saved": saved, "skipped": skipped, "module": m})


@app.post("/api/refs/import_lib")
def api_refs_import_lib():
    body = request.get_json(silent=True) or {}
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    names = body.get("names") or []
    saved, skipped = [], []
    for n in names:
        if not n or "/" in n or "\\" in n:
            skipped.append({"name": n, "reason": "invalid"})
            continue
        src = lib_dir(m) / n
        if not src.is_file():
            skipped.append({"name": n, "reason": "not found"})
            continue
        saved.append({"name": _save_into(picks_dir(m), src, src.name)})
    return jsonify({"saved": saved, "skipped": skipped, "module": m})


@app.post("/api/refs/clear")
def api_refs_clear():
    m = _module()
    d = picks_dir(m)
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in d.iterdir():
        if p.is_file() and p.suffix.lower() in ALLOW_EXT:
            p.unlink()
            n += 1
    return jsonify({"cleared": n, "module": m})


@app.post("/api/refs/delete")
def api_refs_delete():
    body = request.get_json(silent=True) or {}
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    name = (body.get("name") or "").strip()
    if not name or "/" in name or "\\" in name:
        return jsonify({"error": "invalid name"}), 400
    target = picks_dir(m) / name
    if target.is_file() and _safe_under(target, picks_dir(m)):
        target.unlink()
        return jsonify({"deleted": name, "module": m})
    return jsonify({"error": "not found"}), 404


# ---------- _user_lib（常用库，按 module 区分） ----------

@app.get("/api/lib/list")
def api_lib_list():
    m = _module()
    return jsonify({"module": m, "items": _list_dir(lib_dir(m)), "dir": str(lib_dir(m))})


@app.post("/api/lib/upload")
def api_lib_upload():
    m = (request.args.get("module") or "chest")
    if m not in VALID_MODULES:
        m = "chest"
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "no files"}), 400
    saved, skipped = [], []
    for f in files:
        if not f.filename:
            continue
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOW_EXT:
            skipped.append({"name": f.filename, "reason": f"非图片 ({ext})"})
            continue
        saved.append({"name": _save_into(lib_dir(m), f.read(), f.filename)})
    return jsonify({"saved": saved, "skipped": skipped, "module": m})


@app.post("/api/lib/import_svn")
def api_lib_import_svn():
    body = request.get_json(silent=True) or {}
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    paths = body.get("paths") or []
    saved, skipped = [], []
    for rel in paths:
        rel = (rel or "").lstrip("/")
        src = SVN_ROOT / rel
        if not src.is_file() or not _safe_under(src, SVN_ROOT) or src.suffix.lower() not in ALLOW_EXT:
            skipped.append({"name": rel, "reason": "无效"})
            continue
        saved.append({"name": _save_into(lib_dir(m), src, src.name), "from": rel})
    return jsonify({"saved": saved, "skipped": skipped, "module": m})


@app.post("/api/lib/delete")
def api_lib_delete():
    body = request.get_json(silent=True) or {}
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    name = (body.get("name") or "").strip()
    if not name or "/" in name or "\\" in name:
        return jsonify({"error": "invalid name"}), 400
    target = lib_dir(m) / name
    if target.is_file() and _safe_under(target, lib_dir(m)):
        target.unlink()
        return jsonify({"deleted": name, "module": m})
    return jsonify({"error": "not found"}), 404


@app.post("/api/lib/rename")
def api_lib_rename():
    """重命名 lib 里的图。new_name 用户写不带扩展名也行，自动从原文件继承扩展名。"""
    body = request.get_json(silent=True) or {}
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    old = (body.get("name") or "").strip()
    new_raw = (body.get("new_name") or "").strip()
    if not old or "/" in old or "\\" in old or not new_raw or "/" in new_raw or "\\" in new_raw:
        return jsonify({"error": "invalid name"}), 400
    src = lib_dir(m) / old
    if not src.is_file() or not _safe_under(src, lib_dir(m)):
        return jsonify({"error": "not found"}), 404
    # 保留原扩展名，防止用户改成 .gif 等无效扩展
    src_ext = Path(old).suffix
    new_stem = Path(new_raw).stem.strip()
    if not new_stem:
        return jsonify({"error": "新名字为空"}), 400
    new_name = new_stem + src_ext
    if new_name == old:
        return jsonify({"old": old, "new": new_name, "module": m, "noop": True})
    dst = lib_dir(m) / new_name
    if dst.exists():
        return jsonify({"error": f"已存在 {new_name}"}), 409
    src.rename(dst)
    return jsonify({"old": old, "new": new_name, "module": m})


# ---------- 风格卡片 CRUD（按 module 过滤）----------

@app.get("/api/cards/list")
def api_cards_list():
    m = _module()
    cards = [c for c in _read_cards() if c.get("module", "chest") == m]
    return jsonify({"cards": cards, "module": m})


@app.post("/api/cards/save")
def api_cards_save():
    body = request.get_json(silent=True) or {}
    prompt = (body.get("prompt") or "").strip()
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    if not prompt:
        return jsonify({"error": "方向不能为空"}), 400
    cards = _read_cards()
    cid = body.get("id")
    if cid:
        for c in cards:
            if c.get("id") == cid:
                c["prompt"] = prompt
                c["module"] = m
                _write_cards(cards)
                return jsonify({"card": c, "action": "update"})
        return jsonify({"error": "card 不存在"}), 404
    new_id = max([c.get("id", 0) for c in cards] + [0]) + 1
    new_card = {"id": new_id, "prompt": prompt, "module": m}
    cards.append(new_card)
    _write_cards(cards)
    return jsonify({"card": new_card, "action": "create"})


@app.post("/api/cards/scaffold")
def api_cards_scaffold():
    body = request.get_json(silent=True) or {}
    direction = (body.get("direction") or "").strip()
    extra_notes = (body.get("extra_notes") or "").strip()
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    n = max(1, min(50, int(body.get("n", 4))))
    if not direction:
        return jsonify({"error": "方向不能为空"}), 400
    cards = [c for c in _read_cards() if c.get("module", "chest") == m]
    existing = "、".join(c.get("prompt", "") for c in cards) if cards else "（暂无）"
    module_label = "节日道具自选箱" if m == "chest" else "活动道具图标"
    extra_block = f"\n📝 用户补充需求：\n{extra_notes}\n" if extra_notes else ""
    scaffold = (
        f"帮我想 {n} 个 P2 {module_label}方向，主题是【{direction}】。\n"
        f"已有方向（避免重复）：{existing}\n"
        f"{extra_block}\n"
        f"每个方向 = 「主题（4-8 字）+ 一句简短描述（15-30 字，给 AI 一些素材但不写死配色）」，逗号分隔。\n"
        f"示范：\n"
        f"  深海节 龙宫琉璃金，金色镂空雕饰配龙鳞龙柱与水波纹\n"
        f"  圣诞节 红绿暖光，绿松冬青缠绕铃铛与金边蝴蝶结\n"
        f"  万圣节 南瓜骷髅，橙黑撞色加蜘蛛网与魔法烟雾\n"
        f"  春节 红金祥云，红绸缠绕铜钱与吊穗灯笼细节\n\n"
        f"⚠ 禁止写「主题XX+XX+XX；配色XX」这种结构化拆字段——一句自然语言描述即可。\n"
        f"AI 端 STYLE_PREFIX 已固化「仅借鉴绘画风格、不要照抄形状、生成{module_label}、不要文字」，你只管写主题+描述。\n\n"
        f"出完后直接调 POST http://localhost:8765/api/cards/save_batch 入库，body：\n"
        f'  {{"module":"{m}","cards":[{{"prompt":"主题 描述..."}}, ...]}}\n\n'
        f"我会在 web 上自动看到新卡片。"
    )
    return jsonify({"scaffold": scaffold, "module": m})


@app.post("/api/cards/save_batch")
def api_cards_save_batch():
    """批量入库新风格。body: {module, cards: [{prompt}, ...]}"""
    body = request.get_json(silent=True) or {}
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    new_cards = body.get("cards") or []
    if not isinstance(new_cards, list) or not new_cards:
        return jsonify({"error": "cards 必须是非空数组"}), 400
    cards = _read_cards()
    next_id = max([c.get("id", 0) for c in cards] + [0]) + 1
    saved, skipped = [], []
    for nc in new_cards:
        prompt = (nc.get("prompt") or nc.get("name") or "").strip()
        nm = nc.get("module") or m
        if nm not in VALID_MODULES:
            nm = m
        if not prompt:
            skipped.append({"prompt": "?", "reason": "prompt 为空"})
            continue
        cards.append({"id": next_id, "prompt": prompt, "module": nm})
        saved.append({"id": next_id, "prompt": prompt, "module": nm})
        next_id += 1
    _write_cards(cards)
    return jsonify({"saved": saved, "skipped": skipped})


@app.post("/api/cards/delete")
def api_cards_delete():
    body = request.get_json(silent=True) or {}
    cid = body.get("id")
    if not cid:
        return jsonify({"error": "id 必填"}), 400
    cards = _read_cards()
    new_cards = [c for c in cards if c.get("id") != cid]
    if len(new_cards) == len(cards):
        return jsonify({"error": "card 不存在"}), 404
    _write_cards(new_cards)
    return jsonify({"deleted": cid})


# ---------- 触发生图 ----------

@app.post("/api/generate")
def api_generate():
    body = request.get_json(silent=True) or {}
    prompt = (body.get("prompt") or "").strip()
    m = body.get("module", "chest")
    if m not in VALID_MODULES:
        m = "chest"
    batch = max(1, min(8, int(body.get("batch", 2))))
    aspect_ratio = (body.get("aspect_ratio") or "1:1").strip()
    if not prompt:
        return jsonify({"error": "方向不能为空"}), 400

    pd = picks_dir(m)
    pick_files = [p for p in pd.glob("*") if p.is_file() and p.suffix.lower() in ALLOW_EXT] if pd.exists() else []
    cd = comp_dir(m)
    comp_files = [p for p in cd.glob("*") if p.is_file() and p.suffix.lower() in ALLOW_EXT] if cd.exists() else []
    if not pick_files and not comp_files:
        return jsonify({"error": f"{MODULE_LABEL.get(m, m)} 的画风/竞品池都没 ref，先选 ref"}), 400

    # ref 顺序：[...comp_files（按形状走，图1+），...pick_files（按画风走，图2+）]
    # 竞品池用绝对路径喂进去，让 AI 优先按它们的结构走
    anchor_args = [str(p) for p in comp_files] + [p.name for p in pick_files]
    ref_count = len(anchor_args)

    # 极简模式：让 STYLE_PREFIX 自身去说话，不再做服务端 prompt 二次注入
    task_id = uuid.uuid4().hex[:10]
    cmd = [
        "python3", "generate.py", m,
        "--subcategory", "_user_picks",
        "--anchor", ",".join(anchor_args),
        "--prompt", prompt,
        "--engines", "gemini",
        "--batch", str(batch),
        "--ref-count", str(ref_count),
        "--timeout", "1800",
        "--aspect-ratio", aspect_ratio,
    ]
    with TASK_LOCK:
        TASKS[task_id] = {
            "status": "running", "started": time.time(),
            "module": m, "prompt": prompt, "batch": batch, "ref_count": ref_count,
        }

    def run():
        try:
            proc = subprocess.run(cmd, cwd=str(SCRIPTS_DIR), capture_output=True, text=True, timeout=1900)
            ok = proc.returncode == 0
            last_json = None
            for line in reversed(proc.stdout.strip().splitlines()):
                if line.startswith("{"):
                    try:
                        last_json = json.loads(line); break
                    except Exception:
                        continue
            with TASK_LOCK:
                TASKS[task_id].update({
                    "status": "done" if ok else "error",
                    "ended": time.time(),
                    "stdout_tail": "\n".join(proc.stdout.strip().splitlines()[-12:]),
                    "stderr_tail": "\n".join(proc.stderr.strip().splitlines()[-12:]),
                    "result": last_json,
                })
        except Exception as e:
            with TASK_LOCK:
                TASKS[task_id].update({"status": "error", "ended": time.time(), "stderr_tail": str(e)})

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"task_id": task_id, "module": m, "prompt": prompt, "ref_count": ref_count, "batch": batch})


@app.get("/api/status/<task_id>")
def api_status(task_id: str):
    with TASK_LOCK:
        info = TASKS.get(task_id)
    if not info:
        return jsonify({"error": "unknown task"}), 404
    return jsonify(info)


# ---------- entry ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"→ P2 art-gen workbench: http://localhost:{port}/")
    print(f"  data: {DATA_FILE}  ({len(_read_batches())} 批)")
    print(f"  modules: {VALID_MODULES}")
    print(f"  SVN: {SVN_ROOT}")
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
