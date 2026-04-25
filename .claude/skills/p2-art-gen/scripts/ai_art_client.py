#!/usr/bin/env python3
"""ai-art-api.tap4fun.com 客户端：上传 + 生图（同步 REST）。

接口跟 grfal_client 对齐：upload_image / generate / download，
可直接替换 generate.py 里的 GrfalClient 导入。

鉴权：读 ~/.ai-art-auth.json {"api_host": "...", "token": "..."}
依赖：requests + certifi（SSL_CERT_FILE 自动设置）
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import ssl
import sys
import uuid
from pathlib import Path

import certifi
import requests

# 修 Python 3.14 on Mac 的证书问题（系统 CA 不含公司证书链）
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

AUTH_PATH = Path.home() / ".ai-art-auth.json"

# 引擎键 → ai-art-api 服务名（保持跟 grfal 的键名兼容）
ENGINE_TO_SERVICE = {
    "gemini": "nanobanana",   # 谷歌 Nano Banana 2 —— 对齐 grfal 的命名
    "gpt": "gptimage",
    "seedream": "seedream",
    "flux": "kontext",
    "qwen": "qwen",
}
SERVICE_ENDPOINT = {
    "nanobanana": "/pay/google/nano/3.1",
    "gptimage":   "/pay/fal/gpt_image_edit/1.5",
    "seedream":   "/pay/image/seeddream/5",
    "kontext":    "/pay/fal/flux_kontext",
    "qwen":       "/pay/image-edit/aliyun_qwent",
}


class AiArtAuthError(RuntimeError):
    pass


class AiArtAPIError(RuntimeError):
    pass


class AiArtClient:
    """跟 GrfalClient 同接口的 ai-art-api 封装。"""

    def __init__(self, auth_path: Path = AUTH_PATH):
        if not auth_path.exists():
            raise AiArtAuthError(
                f"{auth_path} 不存在。请在 ai-art 系统右上角头像生成 token，然后写入 "
                f'{{"api_host": "https://ai-art-api.tap4fun.com/v2", "token": "..."}}'
            )
        cfg = json.loads(auth_path.read_text())
        self.base_url = cfg.get("api_host", "https://ai-art-api.tap4fun.com/v2").rstrip("/")
        self.token = cfg["token"]
        self._sess = requests.Session()
        self._sess.headers.update({"Authorization": self.token})

    # ------------------------------------------------------------------ upload
    def upload_image(self, local_path: str | Path) -> str:
        """上传图片到 ai-art-api，返回 fileKey（后续生图请求用它引用）。"""
        p = Path(local_path)
        if not p.exists():
            raise FileNotFoundError(p)
        with p.open("rb") as f:
            r = self._sess.post(
                f"{self.base_url}/upload/base",
                files={"file": (p.name, f, self._mime_for(p))},
                timeout=60,
            )
        r.raise_for_status()
        body = r.json()
        data = body.get("data", body)
        key = data.get("file_key") or data.get("fileKey") or data.get("key")
        if not key:
            raise AiArtAPIError(f"upload succeeded but no fileKey: {body}")
        return key

    @staticmethod
    def _mime_for(p: Path) -> str:
        ext = p.suffix.lower()
        return {
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".gif": "image/gif",
        }.get(ext, "application/octet-stream")

    # ------------------------------------------------------------------ generate
    def generate(
        self,
        prompt: str,
        refs: list[str] | None = None,
        engine: str = "gemini",
        batch: int = 1,
        timeout_s: int = 600,
        on_progress=None,
    ) -> list[str]:
        """生图并返回图片 URL 列表。

        ai-art-api 每次调用产出 1 张；batch>1 时并发多次调用收集结果。
        """
        service = ENGINE_TO_SERVICE.get(engine, engine)
        if service not in SERVICE_ENDPOINT:
            raise AiArtAPIError(f"不支持的引擎/服务: {engine} -> {service}")
        endpoint = SERVICE_ENDPOINT[service]
        refs = refs or []

        if on_progress:
            on_progress(f"调用 {engine}({service}) 生成 {batch} 张…", 0.3)

        def _one() -> str:
            body = self._build_body(service, prompt, refs)
            r = self._sess.post(
                f"{self.base_url}{endpoint}",
                json=body, timeout=timeout_s,
            )
            r.raise_for_status()
            payload = r.json()
            return self._extract_url(payload)

        if batch <= 1:
            url = _one()
            if on_progress:
                on_progress("处理完成", 0.9)
            return [url]

        urls: list[str] = []
        with cf.ThreadPoolExecutor(max_workers=min(batch, 4)) as ex:
            futures = [ex.submit(_one) for _ in range(batch)]
            for i, fut in enumerate(cf.as_completed(futures)):
                urls.append(fut.result())
                if on_progress:
                    on_progress(f"完成 {i+1}/{batch}", 0.3 + 0.6 * (i + 1) / batch)
        return urls

    def _build_body(self, service: str, prompt: str, refs: list[str]) -> dict:
        """按服务拼 request body。refs 是上传后的 fileKey 列表。"""
        common = {"prompt": prompt, "from_source": "skill"}
        if service == "nanobanana":
            body = {**common, "module": "nanobanana",
                    "images": refs, "aspect_ratio": "1:1"}
        elif service == "gptimage":
            body = {**common, "module": "gptimage", "images": refs[:5],
                    "aspect_ratio": "1:1"}
        elif service == "seedream":
            body = {**common, "module": "seedream", "images": refs[:10],
                    "resolution": "2K"}
        elif service == "kontext":
            body = {**common, "module": "kontext", "images": refs[:4]}
        elif service == "qwen":
            body = {**common, "module": "qwen", "images": refs[:1]}
        else:
            raise AiArtAPIError(f"未实现 body 构造: {service}")
        return body

    def _extract_url(self, payload: dict) -> str:
        if not payload.get("success"):
            raise AiArtAPIError(f"生成失败: {payload}")
        data = payload.get("data") or payload.get("result", {}).get("data") or {}
        images = data.get("images") or []
        out_url = data.get("out_url") or data.get("output_url") or ""
        if not images:
            raise AiArtAPIError(f"响应里没有 images: {payload}")
        img = images[0]
        if img.startswith("http"):
            return img
        return f"{out_url.rstrip('/')}/{img.lstrip('/')}" if out_url else img

    # ------------------------------------------------------------------ download
    def download(self, url: str, dest: Path) -> Path:
        if not url.startswith("http"):
            url = f"{self.base_url}{url}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self._sess.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(64 * 1024):
                    f.write(chunk)
        return dest


# --------------------------------------------------------------------- CLI
def _cli():
    import argparse, time
    ap = argparse.ArgumentParser(description="ai-art-api 冒烟测试")
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--engine", default="gemini")
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--out-dir", default="./ai_art_out")
    ap.add_argument("prompt")
    args = ap.parse_args()

    c = AiArtClient()
    refs = [c.upload_image(p) for p in args.ref]
    print(f"uploaded {len(refs)} refs: {refs}", file=sys.stderr)

    def prog(desc, p): print(f"  [{p*100:5.1f}%] {desc}", file=sys.stderr, flush=True)

    urls = c.generate(prompt=args.prompt, refs=refs, engine=args.engine,
                      batch=args.batch, on_progress=prog)
    print(f"got {len(urls)} images", file=sys.stderr)

    out_dir = Path(args.out_dir)
    ts = time.strftime("%Y%m%d_%H%M%S")
    for i, u in enumerate(urls):
        dest = out_dir / f"{ts}_{i}.png"
        c.download(u, dest)
        print(dest)


if __name__ == "__main__":
    _cli()
