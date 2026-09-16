#!/usr/bin/env python3
"""模块 · 竞品外观库（gallery）。

投喂三条路：收件箱扫描 / 网页拖拽上传 / 贴链接（占位，抓取另说）。
标签两条路：网页手改 / AI 预标（contact sheet 拼图 → 一次看一版 → 批量写回）。
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

from core import db, media

ROOT = Path(__file__).resolve().parent.parent.parent
INBOX = ROOT / "inbox"
DATA = ROOT / "data"
SHEETS = DATA / "sheets"

router = APIRouter(prefix="/api/gallery", tags=["gallery"])

EDITABLE = ("game", "category", "title", "tags", "note", "source_url", "rating", "status")


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ───────────────────────── 元信息 ─────────────────────────
@router.get("/meta")
def meta():
    counts_g = {r["game"]: r["n"] for r in db.rows(
        "SELECT game, COUNT(*) n FROM gallery_asset GROUP BY game")}
    counts_c = {r["category"]: r["n"] for r in db.rows(
        "SELECT category, COUNT(*) n FROM gallery_asset GROUP BY category")}
    tax = db.rows("SELECT kind,name,alias FROM gallery_tax ORDER BY sort, id")
    total = db.one("SELECT COUNT(*) n FROM gallery_asset")["n"]
    pending = db.one("SELECT COUNT(*) n FROM gallery_asset WHERE status='new'")["n"]
    vids = db.one("SELECT COUNT(*) n FROM gallery_asset WHERE kind='video'")["n"]
    inbox_n = len([p for p in INBOX.rglob("*")
                   if p.is_file() and media.kind_of(p) and not p.name.startswith(".")])
    return {
        "games": [{**t, "count": counts_g.get(t["name"], 0)} for t in tax if t["kind"] == "game"],
        "categories": [{**t, "count": counts_c.get(t["name"], 0)} for t in tax if t["kind"] == "category"],
        "total": total, "pending": pending, "videos": vids, "images": total - vids,
        "inbox": inbox_n,
        # 库里出现过、但分类池里没有的值（AI 预标可能造出新词），前端也要能筛
        "loose_games": sorted(g for g in counts_g if g and g not in
                              {t["name"] for t in tax if t["kind"] == "game"}),
        "loose_categories": sorted(c for c in counts_c if c and c not in
                                   {t["name"] for t in tax if t["kind"] == "category"}),
    }


# ───────────────────────── 列表 ─────────────────────────
@router.get("/assets")
def assets(game: str = "", category: str = "", status: str = "", kind: str = "",
           q: str = "", tag: str = "", limit: int = 300, offset: int = 0):
    where, args = [], []
    if game:
        where.append("game=?"); args.append(game)
    if category:
        where.append("category=?"); args.append(category)
    if status:
        where.append("status=?"); args.append(status)
    if kind:
        where.append("kind=?"); args.append(kind)
    if tag:
        where.append("(','||tags||',') LIKE ?"); args.append(f"%,{tag},%")
    if q:
        where.append("(title LIKE ? OR tags LIKE ? OR note LIKE ? OR filename LIKE ? "
                     "OR game LIKE ? OR category LIKE ?)")
        args += [f"%{q}%"] * 6
    sql = "SELECT * FROM gallery_asset"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY (status='new') DESC, id DESC LIMIT ? OFFSET ?"
    args += [limit, offset]
    items = db.rows(sql, tuple(args))
    cnt_sql = "SELECT COUNT(*) n FROM gallery_asset" + (" WHERE " + " AND ".join(where) if where else "")
    total = db.one(cnt_sql, tuple(args[:-2]))["n"]
    return {"items": items, "total": total, "offset": offset, "limit": limit}


# ───────────────────────── 投喂 ─────────────────────────
def _ingest(path: Path, move: bool, extra: dict | None = None) -> dict:
    info = media.store(path, move=move)
    exist = db.one("SELECT * FROM gallery_asset WHERE sha1=?", (info["sha1"],))
    if exist:
        return {"dup": True, "id": exist["id"], "filename": info["filename"]}
    f = {**info, **(extra or {})}
    cur = db.run(
        """INSERT INTO gallery_asset
           (sha1,kind,filename,path,thumb,width,height,duration,bytes,
            game,category,title,tags,note,source_url,created_at,updated_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (f["sha1"], f["kind"], f["filename"], f["path"], f["thumb"], f["width"], f["height"],
         f["duration"], f["bytes"], f.get("game", ""), f.get("category", ""), f.get("title", ""),
         f.get("tags", ""), f.get("note", ""), f.get("source_url", ""), now(), now()),
    )
    return {"dup": False, "id": cur.lastrowid, "filename": info["filename"]}


@router.post("/scan")
def scan():
    """扫收件箱：入库 + 出缩略图 + 原文件移走（收件箱扫完就空）。"""
    INBOX.mkdir(exist_ok=True)
    added, dups, failed = [], [], []
    files = sorted(p for p in INBOX.rglob("*")
                   if p.is_file() and not p.name.startswith("."))
    for p in files:
        if not media.kind_of(p):
            continue
        try:
            r = _ingest(p, move=True)
            (dups if r["dup"] else added).append(r["filename"])
        except Exception as e:
            failed.append(f"{p.name}: {e}")
    # 清掉扫空的子目录
    for d in sorted([d for d in INBOX.rglob("*") if d.is_dir()], reverse=True):
        try:
            d.rmdir()
        except OSError:
            pass
    return {"added": len(added), "dups": len(dups), "failed": failed,
            "added_names": added[:50], "dup_names": dups[:50]}


@router.post("/upload")
async def upload(files: list[UploadFile] = File(...), game: str = Form(""),
                 category: str = Form("")):
    added, dups, failed = 0, 0, []
    tmp_dir = DATA / "_upload"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    for uf in files:
        tmp = tmp_dir / (uf.filename or "unnamed")
        try:
            with tmp.open("wb") as w:
                shutil.copyfileobj(uf.file, w)
            r = _ingest(tmp, move=True, extra={"game": game, "category": category})
            if r["dup"]:
                dups += 1
            else:
                added += 1
        except Exception as e:
            failed.append(f"{uf.filename}: {e}")
        finally:
            tmp.unlink(missing_ok=True)
    return {"added": added, "dups": dups, "failed": failed}


# ───────────────────────── 编辑 ─────────────────────────
class Patch(BaseModel):
    game: str | None = None
    category: str | None = None
    title: str | None = None
    tags: str | None = None
    note: str | None = None
    source_url: str | None = None
    rating: int | None = None
    status: str | None = None


@router.patch("/asset/{aid}")
def patch_asset(aid: int, p: Patch):
    fields = {k: v for k, v in p.model_dump().items() if v is not None}
    if not fields:
        return {"ok": True}
    # 改过游戏或类别就算标注完成
    if ("game" in fields or "category" in fields) and "status" not in fields:
        cur = db.one("SELECT game,category FROM gallery_asset WHERE id=?", (aid,)) or {}
        g = fields.get("game", cur.get("game", ""))
        c = fields.get("category", cur.get("category", ""))
        if g and c:
            fields["status"] = "done"
    sets = ", ".join(f"{k}=?" for k in fields) + ", updated_at=?"
    db.run(f"UPDATE gallery_asset SET {sets} WHERE id=?",
           (*fields.values(), now(), aid))
    return {"ok": True, "asset": db.one("SELECT * FROM gallery_asset WHERE id=?", (aid,))}


class Bulk(BaseModel):
    ids: list[int]
    fields: dict


@router.post("/bulk")
def bulk(b: Bulk):
    fields = {k: v for k, v in b.fields.items() if k in EDITABLE}
    if not fields or not b.ids:
        return {"ok": False, "n": 0}
    if ("game" in fields or "category" in fields) and "status" not in fields:
        fields["status"] = "done"
    sets = ", ".join(f"{k}=?" for k in fields) + ", updated_at=?"
    qs = ",".join("?" * len(b.ids))
    db.run(f"UPDATE gallery_asset SET {sets} WHERE id IN ({qs})",
           (*fields.values(), now(), *b.ids))
    return {"ok": True, "n": len(b.ids)}


class Ids(BaseModel):
    ids: list[int]


@router.post("/delete")
def delete(x: Ids):
    n = 0
    for aid in x.ids:
        a = db.one("SELECT * FROM gallery_asset WHERE id=?", (aid,))
        if not a:
            continue
        for rel in (a["path"], a["thumb"]):
            if rel:
                (DATA / rel).unlink(missing_ok=True)
        db.run("DELETE FROM gallery_asset WHERE id=?", (aid,))
        n += 1
    return {"ok": True, "n": n}


# ───────────────────────── 分类池 ─────────────────────────
class Tax(BaseModel):
    kind: str
    name: str
    alias: str = ""


@router.post("/tax")
def tax_add(t: Tax):
    if t.kind not in ("game", "category"):
        raise HTTPException(400, "kind 只能是 game / category")
    mx = db.one("SELECT COALESCE(MAX(sort),0) m FROM gallery_tax WHERE kind=?", (t.kind,))["m"]
    db.run("INSERT OR IGNORE INTO gallery_tax(kind,name,alias,sort) VALUES(?,?,?,?)",
           (t.kind, t.name.strip(), t.alias, mx + 10))
    return {"ok": True}


@router.post("/tax/delete")
def tax_del(t: Tax):
    db.run("DELETE FROM gallery_tax WHERE kind=? AND name=?", (t.kind, t.name))
    return {"ok": True}


# ───────────────────────── AI 预标：contact sheet ─────────────────────────
class SheetReq(BaseModel):
    ids: list[int] | None = None
    limit: int = 20
    cols: int = 5
    cell: int = 360


@router.post("/contactsheet")
def contactsheet(r: SheetReq):
    """把待标注的图拼成一张带编号的大图 —— AI 看一张顶看 N 张，省 token。

    返回拼图路径 + 编号→id 映射，配合 POST /tag 批量写回。
    """
    if r.ids:
        qs = ",".join("?" * len(r.ids))
        items = db.rows(f"SELECT * FROM gallery_asset WHERE id IN ({qs}) ORDER BY id", tuple(r.ids))
    else:
        items = db.rows("SELECT * FROM gallery_asset WHERE status='new' ORDER BY id LIMIT ?",
                        (r.limit,))
    if not items:
        return {"ok": False, "msg": "没有待标注的素材"}

    cell = r.cell
    cols = max(1, min(r.cols, len(items)))
    rows_n = (len(items) + cols - 1) // cols
    label_h = 28
    W, H = cols * cell, rows_n * (cell + label_h)
    sheet = Image.new("RGB", (W, H), (24, 26, 32))
    dr = ImageDraw.Draw(sheet)

    def _font(sz: int):
        for f in ("/System/Library/Fonts/PingFang.ttc",       # 中文文件名不能显示成方块
                  "/System/Library/Fonts/Hiragino Sans GB.ttc",
                  "/System/Library/Fonts/STHeiti Light.ttc",
                  "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                  "/System/Library/Fonts/Helvetica.ttc"):
            try:
                return ImageFont.truetype(f, sz)
            except Exception:
                continue
        return ImageFont.load_default()

    font, fbig = _font(15), _font(22)

    mapping = []
    for i, a in enumerate(items):
        cx, cy = (i % cols) * cell, (i // cols) * (cell + label_h)
        tp = DATA / (a["thumb"] or "")
        if tp.exists():
            try:
                with Image.open(tp) as im:
                    im = im.convert("RGB")
                    im.thumbnail((cell - 10, cell - 10), Image.LANCZOS)
                    sheet.paste(im, (cx + (cell - im.width) // 2, cy + (cell - im.height) // 2))
            except Exception:
                pass
        # 编号直接压在格子左上角 —— 图再扁也不会跟隔壁的标签串行
        tag = f"#{i + 1}"
        w = int(dr.textlength(tag, font=fbig))
        dr.rectangle([cx + 4, cy + 4, cx + 16 + w, cy + 34], fill=(214, 62, 62))
        dr.text((cx + 10, cy + 7), tag, fill=(255, 255, 255), font=fbig)
        dr.rectangle([cx, cy + cell, cx + cell, cy + cell + label_h], fill=(45, 48, 58))
        mark = "[视频] " if a["kind"] == "video" else ""
        dr.text((cx + 8, cy + cell + 5), f"{tag} {mark}{a['filename'][:26]}",
                fill=(228, 230, 238), font=font)
        dr.line([(cx, cy), (cx, cy + cell + label_h)], fill=(58, 62, 72))
        dr.line([(cx, cy), (cx + cell, cy)], fill=(58, 62, 72))
        mapping.append({"n": i + 1, "id": a["id"], "filename": a["filename"], "kind": a["kind"]})

    SHEETS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = SHEETS / f"sheet_{stamp}.jpg"
    sheet.save(out, "JPEG", quality=88)
    (SHEETS / f"sheet_{stamp}.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "sheet": str(out), "map": mapping, "n": len(items)}


class TagItem(BaseModel):
    id: int
    game: str | None = None
    category: str | None = None
    title: str | None = None
    tags: str | None = None
    note: str | None = None


@router.post("/tag")
def tag(items: list[TagItem]):
    """AI 预标批量写回。写完 status 仍留 new→done 的判断给 patch 逻辑。"""
    n = 0
    for it in items:
        f = {k: v for k, v in it.model_dump().items() if k != "id" and v is not None}
        if not f:
            continue
        if f.get("game") and f.get("category"):
            f["status"] = "done"
        sets = ", ".join(f"{k}=?" for k in f) + ", updated_at=?"
        db.run(f"UPDATE gallery_asset SET {sets} WHERE id=?", (*f.values(), now(), it.id))
        n += 1
    return {"ok": True, "n": n}
