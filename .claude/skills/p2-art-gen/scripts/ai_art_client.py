#!/usr/bin/env python3
"""grfal-api adapter，保持跟旧 AiArtClient 接口兼容。

旧 ai-art-api.tap4fun.com 已被 ban，改走 grfal-api skill 的 call_grfal.py CLI。
对外类签名（AiArtClient.upload_image / generate / download）一字不变，
所以 generate.py / gallery_server.py / 网页端不用动。

鉴权：call_grfal.py 自管理 token（~/.config/grfal-api/token_store.json，30 天有效）。
依赖：certifi + subprocess。Py3.14 Mac 自动注入 SSL_CERT_FILE。
"""
from __future__ import annotations

import json
import os
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path

import certifi

# Py3.14 on Mac 系统 CA 不含公司证书链
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

# 定位 grfal-api skill 的 CLI（相对当前文件，不 hardcode 用户名）
HERE = Path(__file__).resolve()
SKILLS_DIR = HERE.parents[2]  # .claude/skills/
GRFAL_CLI = SKILLS_DIR / "grfal-api" / "scripts" / "call_grfal.py"

# 旧 engine 名 → grfal 的 model 名（grfal 用同名，留映射给以后扩展）
ENGINE_TO_MODEL = {
    "gemini": "gemini",
    "gpt": "gpt",
    "seedream": "seedream",
    "flux": "flux",
    "qwen": "qwen",
}

# 兼容老代码（generate.py 等以前 import 这两个常量）
ENGINE_TO_SERVICE = {k: k for k in ENGINE_TO_MODEL}
SERVICE_ENDPOINT = {k: "/grfal" for k in ENGINE_TO_MODEL}

# 旧 "1:1" 等 → grfal 的 aspect_ratio 字符串
# grfal 不支持的（如 3:2/2:3）回退到最接近的，未列的走 auto
ASPECT_TO_GRFAL = {
    "1:1": "square_hd",
    "16:9": "landscape_16_9",
    "9:16": "portrait_16_9",
    "4:3": "landscape_4_3",
    "3:4": "portrait_4_3",
    "3:2": "landscape_4_3",
    "2:3": "portrait_4_3",
    "21:9": "landscape_21_9",
    "9:21": "portrait_21_9",
}


class AiArtAuthError(RuntimeError):
    pass


class AiArtAPIError(RuntimeError):
    pass


def _parse_grfal_stdout(s: str) -> dict | None:
    """call_grfal.py 可能在 stdout 输出多个 JSON 对象（warnings + 最终结果）。
    流式解析，取最后一个能完整解析的 JSON 对象作为最终结果。"""
    dec = json.JSONDecoder()
    last = None
    i, n = 0, len(s)
    while i < n:
        while i < n and s[i].isspace():
            i += 1
        if i >= n:
            break
        try:
            obj, j = dec.raw_decode(s, i)
            last = obj
            i = j
        except json.JSONDecodeError:
            # 跳到下一行重试
            nxt = s.find("\n", i)
            if nxt == -1:
                break
            i = nxt + 1
    return last


class AiArtClient:
    """grfal-api adapter 实现，对外接口跟原 AiArtClient 一致。"""

    def __init__(self, auth_path: Path | None = None):
        # auth_path 仅为保留旧签名，实际不用（grfal-api 自管理 token）
        if not GRFAL_CLI.exists():
            raise AiArtAuthError(
                f"找不到 grfal-api CLI: {GRFAL_CLI}\n"
                f"请先安装：npx skills add git@git.tap4fun.com:skills/grfal-api.git "
                f"--skill grfal-api --agent claude-code"
            )

    # ------------------------------------------------------------------ upload
    def upload_image(self, local_path: str | Path) -> str:
        """grfal-api 不需要预上传，--file reference_images=<path> 自动 base64。
        这里把本地路径当 'fileKey' 返回，generate() 拿到后透传即可。"""
        p = Path(local_path)
        if not p.exists():
            raise FileNotFoundError(p)
        return str(p.resolve())

    # ------------------------------------------------------------------ generate
    def generate(
        self,
        prompt: str,
        refs: list[str] | None = None,
        engine: str = "gemini",
        batch: int = 1,
        timeout_s: int = 600,
        on_progress=None,
        aspect_ratio: str = "1:1",
    ) -> list[str]:
        """生图并返回图片 URL 列表。grfal 一次调用 num_images=batch 出 N 张。"""
        model = ENGINE_TO_MODEL.get(engine, engine)
        refs = refs or []
        batch = max(1, int(batch))

        params: dict = {"prompt": prompt, "model": model, "num_images": batch}
        ar = ASPECT_TO_GRFAL.get(aspect_ratio)
        if ar:
            params["aspect_ratio"] = ar
        # 留空字段会被 grfal 自动推断；只在已知映射时显式传

        cmd = [
            "python3", str(GRFAL_CLI),
            "--tool", "generate_image",
            "--params", json.dumps(params, ensure_ascii=False),
            "--timeout", str(timeout_s),
        ]
        for ref in refs:
            cmd += ["--file", f"reference_images={ref}"]

        if on_progress:
            on_progress(f"调用 grfal/{model} 生成 {batch} 张…", 0.3)

        env = {**os.environ, "SSL_CERT_FILE": certifi.where()}
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=timeout_s + 60, check=False, env=env,
            )
        except subprocess.TimeoutExpired:
            raise AiArtAPIError(f"grfal call_grfal.py 超时 ({timeout_s}s)")

        last_obj = _parse_grfal_stdout(proc.stdout)
        if not last_obj:
            raise AiArtAPIError(
                f"grfal 返回无法解析:\nSTDOUT(tail):\n{proc.stdout[-800:]}\n"
                f"STDERR(tail):\n{proc.stderr[-400:]}"
            )

        if not last_obj.get("success"):
            err = last_obj.get("error") or str(last_obj)
            raise AiArtAPIError(f"grfal 生成失败: {err}")

        urls = last_obj.get("result") or []
        if isinstance(urls, str):
            urls = [urls]
        if not urls:
            raise AiArtAPIError(f"grfal success=true 但 result 为空: {last_obj}")

        if on_progress:
            on_progress(f"完成 {len(urls)} 张", 0.95)

        return urls

    # ------------------------------------------------------------------ download
    def download(self, url: str, dest: Path) -> Path:
        """grfal 输出 URL 应该是公网可达的；用 certifi cert 走 HTTPS。"""
        dest.parent.mkdir(parents=True, exist_ok=True)
        ctx = ssl.create_default_context(cafile=certifi.where())
        req = urllib.request.Request(url, headers={"User-Agent": "p2-art-gen/grfal-adapter"})
        with urllib.request.urlopen(req, timeout=180, context=ctx) as r, dest.open("wb") as f:
            while True:
                chunk = r.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)
        return dest


# --------------------------------------------------------------------- CLI
def _cli():
    import argparse
    import time

    ap = argparse.ArgumentParser(description="grfal-api adapter 冒烟测试")
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--engine", default="gemini")
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--aspect-ratio", default="1:1")
    ap.add_argument("--out-dir", default="./ai_art_out")
    ap.add_argument("prompt")
    args = ap.parse_args()

    c = AiArtClient()
    refs = [c.upload_image(p) for p in args.ref]
    print(f"refs: {refs}", file=sys.stderr)

    def prog(desc, p):
        print(f"  [{p*100:5.1f}%] {desc}", file=sys.stderr, flush=True)

    urls = c.generate(
        prompt=args.prompt, refs=refs, engine=args.engine,
        batch=args.batch, aspect_ratio=args.aspect_ratio, on_progress=prog,
    )
    print(f"got {len(urls)} images", file=sys.stderr)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    for i, u in enumerate(urls):
        dest = out_dir / f"{ts}_{i}.png"
        c.download(u, dest)
        print(dest)


if __name__ == "__main__":
    _cli()
