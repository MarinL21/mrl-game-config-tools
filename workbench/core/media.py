#!/usr/bin/env python3
"""工作台 · 媒体层：入库、去重、缩略图。

本机没有 ffmpeg，视频封面走 macOS 自带的 Quick Look（qlmanage），
视频时长自己解析 mp4/mov 的 mvhd box —— 零外部依赖。
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MEDIA = DATA / "media"
THUMBS = DATA / "thumbs"

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".avif", ".heic", ".tiff"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
THUMB_W = 600  # 网格用小图，别拿原图缩放（卡的根源）


def kind_of(p: Path) -> str | None:
    e = p.suffix.lower()
    if e in IMAGE_EXT:
        return "image"
    if e in VIDEO_EXT:
        return "video"
    return None


def sha1_of(p: Path) -> str:
    h = hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ───────────────────────── 视频时长：解析 mvhd ─────────────────────────
def _box(f, end: int, want: bytes):
    """在 [f.tell(), end) 范围内找顶层 box，返回 (内容起点, box 终点)。"""
    while f.tell() + 8 <= end:
        start = f.tell()
        head = f.read(8)
        if len(head) < 8:
            return None
        size = int.from_bytes(head[:4], "big")
        typ = head[4:8]
        hdr = 8
        if size == 1:
            size = int.from_bytes(f.read(8), "big")
            hdr = 16
        elif size == 0:
            size = end - start
        if size < hdr:
            return None
        if typ == want:
            return start + hdr, start + size
        f.seek(start + size)
    return None


def video_meta(p: Path) -> tuple[float | None, int | None, int | None]:
    """(时长秒, 宽, 高)。解析失败返回 (None, None, None)，不影响入库。"""
    try:
        size = p.stat().st_size
        with p.open("rb") as f:
            moov = _box(f, size, b"moov")
            if not moov:
                return None, None, None
            f.seek(moov[0])
            mvhd = _box(f, moov[1], b"mvhd")
            if not mvhd:
                return None, None, None
            f.seek(mvhd[0])
            ver = f.read(1)[0]
            f.read(3)  # flags
            if ver == 1:
                f.read(16)  # creation + modification (8+8)
                timescale = int.from_bytes(f.read(4), "big")
                duration = int.from_bytes(f.read(8), "big")
            else:
                f.read(8)
                timescale = int.from_bytes(f.read(4), "big")
                duration = int.from_bytes(f.read(4), "big")
            secs = round(duration / timescale, 2) if timescale else None
            return secs, None, None
    except Exception:
        return None, None, None


# ───────────────────────── 缩略图 ─────────────────────────
def _shrink_to(src: Path, dst: Path) -> tuple[int, int] | None:
    try:
        with Image.open(src) as im:
            im.seek(0) if getattr(im, "is_animated", False) else None
            w, h = im.size
            im = im.convert("RGB")
            if w > THUMB_W:
                im = im.resize((THUMB_W, max(1, round(h * THUMB_W / w))), Image.LANCZOS)
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.save(dst, "JPEG", quality=82, optimize=True)
            return w, h
    except Exception:
        return None


def _quicklook(src: Path, out_dir: Path) -> Path | None:
    """macOS Quick Look 出封面，视频和 PIL 打不开的图都靠它兜底。"""
    try:
        subprocess.run(
            ["qlmanage", "-t", "-s", str(THUMB_W * 2), "-o", str(out_dir), str(src)],
            capture_output=True, timeout=60, check=False,
        )
    except Exception:
        return None
    hits = list(out_dir.glob("*.png")) + list(out_dir.glob("*.jpg"))
    return hits[0] if hits else None


def make_thumb(src: Path, sha1: str, kind: str) -> tuple[str | None, int | None, int | None]:
    """返回 (相对 data/ 的 thumb 路径, 原图宽, 原图高)。"""
    dst = THUMBS / sha1[:2] / f"{sha1}.jpg"
    if kind == "image":
        wh = _shrink_to(src, dst)
        if wh:
            return str(dst.relative_to(DATA)), wh[0], wh[1]
    with tempfile.TemporaryDirectory() as td:
        ql = _quicklook(src, Path(td))
        if ql:
            wh = _shrink_to(ql, dst)
            if wh:
                # QL 出的是封面，不是原始分辨率；宽高按封面比例记录
                return str(dst.relative_to(DATA)), wh[0], wh[1]
    return None, None, None


# ───────────────────────── 入库 ─────────────────────────
def store(src: Path, move: bool = False) -> dict:
    """把一个文件存进 data/media/，出缩略图，返回可直接写库的字段 dict。"""
    kind = kind_of(src)
    if not kind:
        raise ValueError(f"不支持的格式: {src.suffix}")
    sha1 = sha1_of(src)
    dst = MEDIA / sha1[:2] / f"{sha1}{src.suffix.lower()}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        if move:
            shutil.move(str(src), dst)
        else:
            shutil.copy2(src, dst)
    elif move:
        src.unlink(missing_ok=True)

    thumb, w, h = make_thumb(dst, sha1, kind)
    dur = None
    if kind == "video":
        dur, vw, vh = video_meta(dst)
    return {
        "sha1": sha1,
        "kind": kind,
        "filename": src.name,
        "path": str(dst.relative_to(DATA)),
        "thumb": thumb,
        "width": w,
        "height": h,
        "duration": dur,
        "bytes": dst.stat().st_size,
    }
