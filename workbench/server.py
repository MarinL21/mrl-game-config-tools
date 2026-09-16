#!/usr/bin/env python3
"""运营策划工作台 — 后端主入口。

定位：把「SLG 运营 + 商业化」这条线的全部工具收进一个站。
结构是外壳 + 模块：外壳管导航和公共资源，每个模块一个 modules/<key>/api.py 出一个 router，
在下面 MODULES 里加一行就上架。第一个模块 = 竞品外观库（gallery）。

启动：./run.sh          → http://127.0.0.1:8790
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from core import db
from modules.gallery.api import router as gallery_router

DATA = HERE / "data"
STATIC = HERE / "static"
INBOX = HERE / "inbox"

# StaticFiles 在导入期就要求目录存在，所以建目录必须早于 app 定义
for _d in (DATA / "media", DATA / "thumbs", DATA / "sheets", INBOX, STATIC):
    _d.mkdir(parents=True, exist_ok=True)

# ── 模块注册表：加模块 = 加一行 ──────────────────────────────
MODULES = [
    {"key": "gallery", "name": "竞品外观库", "icon": "◫", "ready": True,
     "desc": "竞品外显素材（图 / 视频）按游戏 × 类别汇总"},
    {"key": "festival_ops", "name": "节日运营驾驶舱", "icon": "◷", "ready": False,
     "href": "http://127.0.0.1:8781", "desc": "12 阶段 × 75 能力，待并入"},
    {"key": "numeric", "name": "数值工作台", "icon": "◰", "ready": False,
     "desc": "礼包定价 / ROI / 蒙卡，规划中"},
    {"key": "revenue", "name": "商业化看板", "icon": "◱", "ready": False,
     "desc": "营收回归 / 付费分层，规划中"},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    yield


app = FastAPI(title="运营策划工作台", version="0.1.0", lifespan=lifespan)
app.include_router(gallery_router)


@app.get("/api/modules")
def modules():
    return {"modules": MODULES}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return JSONResponse({"ok": True})


app.mount("/static", StaticFiles(directory=STATIC), name="static")
app.mount("/media", StaticFiles(directory=DATA / "media"), name="media")
app.mount("/thumbs", StaticFiles(directory=DATA / "thumbs"), name="thumbs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.environ.get("WB_HOST", "127.0.0.1"),
                port=int(os.environ.get("WB_PORT", "8790")), log_level="info")
