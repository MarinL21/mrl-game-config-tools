#!/usr/bin/env python3
"""从 gallery.html 反向重建 gallery_data.json（race condition 救灾用）"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "grfal"
HTML_PATH = OUTPUT_DIR / "gallery.html"
DATA_PATH = OUTPUT_DIR / "gallery_data.json"

ENGINE_LABEL_TO_KEY = {
    "nano-banana": "gemini",
    "GPT-Image-1": "gpt",
    "Seedream-4": "seedream",
    "Flux-1-Schnell": "flux",
    "Qwen-Image": "qwen",
}

def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    batches = []

    batch_re = re.compile(
        r'<div class="batch">\s*'
        r'<div class="batch-meta">(?P<meta>.*?)</div>\s*'
        r'<div class="batch-prompt">(?P<prompt>.*?)</div>\s*'
        r'(?P<rest>.*?)'
        r'(?=<div class="batch">|$)',
        re.DOTALL,
    )
    meta_field_re = re.compile(r'<span>([^<]+):?\s*<b>([^<]+)</b></span>')
    ts_only_re = re.compile(r'<span><b>([^<]+)</b></span>')
    refs_block_re = re.compile(r'<div class="refs">(.*?)</div>\s*<div class="grid">', re.DOTALL)
    ref_re = re.compile(r'<img src="([^"]+)" alt="[^"]+"><span class="ref-label">[^：:]+[：:]\s*([^<]+)</span>')
    cell_re = re.compile(
        r'<div class="cell"><img src="(?P<thumb>[^"]+)"[^>]*>\s*'
        r'<div class="badge"[^>]*>(?P<eng>[^<]+)</div>',
        re.DOTALL,
    )

    for m in batch_re.finditer(html):
        meta_html = m.group("meta")
        prompt = m.group("prompt").strip()
        rest = m.group("rest")

        # 时间戳：第一个 <span><b>...</b></span>（无前缀冒号）
        ts_match = ts_only_re.search(meta_html)
        timestamp = ts_match.group(1).strip() if ts_match else ""

        # 引擎/张数/耗时（带前缀）
        engine = ""
        count = 0
        duration = ""
        for k, v in meta_field_re.findall(meta_html):
            k = k.strip()
            v = v.strip()
            if k.startswith("引擎"):
                engine = v
            elif k.startswith("张数"):
                try: count = int(v)
                except: count = 0
            elif k.startswith("耗时"):
                duration = v

        # refs
        refs = []
        rb = refs_block_re.search(rest)
        if rb:
            for src, name in ref_re.findall(rb.group(1)):
                refs.append({"src": src, "name": name.strip()})

        # cells
        cells = []
        module = None
        for cm in cell_re.finditer(rest):
            thumb = cm.group("thumb")
            eng_label = cm.group("eng").strip()
            # thumbs/images/{module}/xxx.jpg → src 是 images/{module}/xxx.png
            tparts = thumb.split("/")
            if len(tparts) >= 4 and tparts[0] == "thumbs" and tparts[1] == "images":
                if module is None:
                    module = tparts[2]
                src = "/".join(tparts[1:])  # images/{module}/xxx.jpg
                src = src.rsplit(".", 1)[0] + ".png"
            else:
                src = thumb  # fallback
            cells.append({
                "thumb": thumb,
                "engine_label": eng_label,
                "src": src,
                "abs": str((OUTPUT_DIR / src).resolve()),
            })

        if module is None:
            # 最后的兜底：从 prompt 关键词猜不靠谱，直接跳过这个坏 batch
            print(f"[skip] 无 module: ts={timestamp} prompt={prompt[:30]}")
            continue

        batches.append({
            "module": module,
            "timestamp": timestamp,
            "engine": engine,
            "count": count or len(cells),
            "duration": duration,
            "prompt": prompt,
            "refs": refs,
            "cells": cells,
        })

    print(f"恢复出 {len(batches)} 批")
    by_mod = {}
    for b in batches:
        by_mod[b["module"]] = by_mod.get(b["module"], 0) + 1
    print("by_module:", by_mod)

    DATA_PATH.write_text(json.dumps(batches, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已写入 {DATA_PATH}")

if __name__ == "__main__":
    main()
