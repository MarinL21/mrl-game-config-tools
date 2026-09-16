#!/usr/bin/env python3
"""工作台 CLI —— 给 Claude 会话用的固定入口（也可以自己在终端跑）。

典型一轮「投喂 → AI 预标」：
    python3 tools/wb.py scan                 # 收件箱入库
    python3 tools/wb.py sheet                # 待标注拼成一张带编号的图（AI 看一张顶 20 张）
    python3 tools/wb.py tag tags.json        # 把 [{n|id, game, category, title, tags, note}] 写回
    python3 tools/wb.py stat                 # 看进度

tag 的 JSON 用 contact sheet 的编号 n（推荐，跟拼图上的 #1 #2 对得上）或直接用 id 都行。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8790"
ROOT = Path(__file__).resolve().parent.parent
SHEETS = ROOT / "data" / "sheets"


def call(path: str, body=None, method: str | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(BASE + path, data=data,
                  headers={"Content-Type": "application/json"},
                  method=method or ("POST" if data is not None else "GET"))
    with urlopen(req, timeout=300) as r:
        return json.loads(r.read() or "null")


def latest_map() -> list[dict]:
    js = sorted(SHEETS.glob("sheet_*.json"))
    if not js:
        sys.exit("还没生成过 contact sheet，先跑 sheet")
    return json.loads(js[-1].read_text(encoding="utf-8"))


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stat"

    if cmd == "scan":
        r = call("/api/gallery/scan", {})
        print(f"入库 {r['added']}　重复跳过 {r['dups']}　失败 {len(r['failed'])}")
        for f in r["failed"]:
            print("  ✗", f)

    elif cmd == "sheet":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        r = call("/api/gallery/contactsheet", {"limit": limit})
        if not r.get("ok"):
            sys.exit(r.get("msg", "没有待标注的素材"))
        print(f"拼图：{r['sheet']}　共 {r['n']} 件")
        for m in r["map"]:
            print(f"  #{m['n']:>2}  id={m['id']:<5} {m['kind']:5} {m['filename']}")

    elif cmd == "tag":
        raw = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")) if len(sys.argv) > 2 \
            else json.loads(sys.stdin.read())
        mp = {m["n"]: m["id"] for m in latest_map()}
        items = []
        for it in raw:
            aid = it.get("id") or mp.get(it.get("n"))
            if not aid:
                print("跳过（既没 id 也没有效编号 n）：", it)
                continue
            items.append({k: v for k, v in it.items() if k != "n"} | {"id": aid})
        r = call("/api/gallery/tag", items)
        print(f"已写回 {r['n']} 件")

    elif cmd == "stat":
        m = call("/api/gallery/meta")
        print(f"库内 {m['total']} 件（图 {m['images']} / 视频 {m['videos']}）　"
              f"待标注 {m['pending']}　收件箱待扫 {m['inbox']}")
        for key, label in (("games", "游戏"), ("categories", "类别")):
            hit = [t for t in m[key] if t["count"]]
            if hit:
                print(f"  {label}：" + "　".join(f"{t['name']}({t['count']})" for t in hit))

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
