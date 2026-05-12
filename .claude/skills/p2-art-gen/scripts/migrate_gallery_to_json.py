#!/usr/bin/env python3
"""一次性：把现有 output/grfal/gallery.html 的 121 批次解析成 gallery_data.json。

新的 gallery_server.py 会从 JSON 读批次渲染，HTML 仅作历史归档。
"""
import json, re, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
GALLERY_HTML = PROJECT_ROOT / "output" / "grfal" / "gallery.html"
GALLERY_JSON = PROJECT_ROOT / "output" / "grfal" / "gallery_data.json"

MODULE_BY_H2 = {
    "活动界面 UI": "ui",
    "宝箱图标": "chest",
    "活动道具": "item",
}


def parse():
    html = GALLERY_HTML.read_text(encoding="utf-8")
    main_m = re.search(r"<main>(.*?)</main>", html, re.S)
    if not main_m:
        sys.exit("找不到 <main>")
    main = main_m.group(1)

    # 按 <h2> 分区切
    sections = re.split(r'<h2[^>]*>([^<]+)</h2>', main)
    # sections = ['', 'h1标题', 'h1后内容', 'h2标题', 'h2后内容', ...]
    batches = []
    i = 1
    while i < len(sections):
        h2 = sections[i].strip()
        body = sections[i + 1] if i + 1 < len(sections) else ""
        module = MODULE_BY_H2.get(h2, h2)
        # 抽该分区里所有 <div class="batch">...直到下一个 batch 或末尾
        # 用一个略宽容的匹配：每个 batch 包含 batch-meta + batch-prompt + refs + grid
        batch_blocks = re.findall(
            r'<div class="batch">.*?(?=<div class="batch">|$)',
            body, re.S
        )
        for blk in batch_blocks:
            b = parse_batch(blk, module)
            if b:
                batches.append(b)
        i += 2

    # 排序：按 timestamp 升序（旧→新），后续 server 端可倒序
    batches.sort(key=lambda b: b.get("timestamp", ""))
    return batches


def parse_batch(blk: str, module: str) -> dict | None:
    # meta: 时间 / 引擎 / 张数 / 耗时
    meta = re.search(
        r'<div class="batch-meta">'
        r'<span><b>([^<]+)</b></span>'
        r'<span>引擎: <b>([^<]+)</b></span>'
        r'<span>张数: <b>(\d+)</b></span>'
        r'(?:<span>耗时: <b>([^<]+)</b></span>)?',
        blk
    )
    if not meta:
        return None
    timestamp = meta.group(1)
    engine_str = meta.group(2)
    count = int(meta.group(3))
    duration = meta.group(4) or ""

    # prompt
    prompt_m = re.search(r'<div class="batch-prompt">(.*?)</div>', blk, re.S)
    prompt = prompt_m.group(1).strip() if prompt_m else ""

    # refs
    refs = re.findall(
        r'<div class="ref"><img src="([^"]+)"[^>]*>'
        r'<span class="ref-label">P2 锚点：([^<]+)</span>',
        blk
    )
    refs_list = [{"src": src, "name": name} for src, name in refs]

    # cells
    cells = re.findall(
        r'<div class="cell">'
        r'<img src="([^"]+)"[^>]*>'
        r'<div class="badge"[^>]*>([^<]+)</div>'
        r'.*?copyImg\(this,\s*\'([^\']+)\'\)'
        r'.*?copyPath\(this,\s*\'([^\']+)\'\)',
        blk, re.S
    )
    cell_list = [
        {"thumb": thumb, "engine_label": engine, "src": src, "abs": abs_path}
        for thumb, engine, src, abs_path in cells
    ]

    return {
        "module": module,
        "timestamp": timestamp,
        "engine": engine_str,
        "count": count,
        "duration": duration,
        "prompt": prompt,
        "refs": refs_list,
        "cells": cell_list,
    }


def main():
    batches = parse()
    GALLERY_JSON.write_text(
        json.dumps(batches, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    by_module = {}
    for b in batches:
        by_module.setdefault(b["module"], 0)
        by_module[b["module"]] += 1
    print(f"✓ 解析 {len(batches)} 个批次写入 {GALLERY_JSON}")
    for m, n in by_module.items():
        print(f"  - {m}: {n} 批")


if __name__ == "__main__":
    main()
