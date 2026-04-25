#!/usr/bin/env python3
"""grfal.tap4fun.com 客户端：上传 + 生图 + SSE 结果流解析。

用法：
    from grfal_client import GrfalClient
    c = GrfalClient()
    path = c.upload_image("/path/to/ref.png")
    imgs = c.generate(prompt="...", refs=[path], engine="gpt", batch=2)
    for img_url in imgs: ...

环境：~/.grfal-auth.json 存 session_cookie。过期时在浏览器 F12 重拿。

支持的引擎键（/api/config/image-models 返回）：
    gpt, gemini, seedream, flux, vidu, wan, runway, qwen,
    ideogram, hunyuan, grok, zimage, firered
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Iterable

import requests

AUTH_PATH = Path.home() / ".grfal-auth.json"


class GrfalAuthError(RuntimeError):
    pass


class GrfalAPIError(RuntimeError):
    pass


class GrfalClient:
    def __init__(self, auth_path: Path = AUTH_PATH):
        if not auth_path.exists():
            raise GrfalAuthError(
                f"{auth_path} 不存在。请在浏览器登录 grfal.tap4fun.com/v2/ 后, "
                f"F12 → Application → Cookies，把 grfal_session 的 value 写入 "
                f'{{"session_cookie": "...", "base_url": "https://grfal.tap4fun.com"}}'
            )
        cfg = json.loads(auth_path.read_text())
        self.base_url = cfg.get("base_url", "https://grfal.tap4fun.com").rstrip("/")
        self.session_cookie = cfg["session_cookie"]
        self._sess = requests.Session()
        self._sess.cookies.set("grfal_session", self.session_cookie, domain="grfal.tap4fun.com")
        self._sess.headers.update({
            "Referer": f"{self.base_url}/v2/image/image_generation",
            "Origin": self.base_url,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) p2-art-gen",
        })

    # ------------------------------------------------------------------ upload
    def upload_image(self, local_path: str | Path) -> str:
        """上传参考图，返回 gradio 内部路径（形如 /tmp/gradio/uploads/xxx.png）。"""
        p = Path(local_path)
        if not p.exists():
            raise FileNotFoundError(p)
        with p.open("rb") as f:
            r = self._sess.post(
                f"{self.base_url}/api/upload",
                files={"file": (p.name, f, self._mime_for(p))},
                timeout=60,
            )
        r.raise_for_status()
        body = r.json()
        if not body.get("success"):
            raise GrfalAPIError(f"upload failed: {body}")
        return body["path"]

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
        engine: str = "gpt",
        batch: int = 2,
        timeout_s: int = 600,
        on_progress=None,
    ) -> list[str]:
        """提交生图并阻塞等待，返回所有产出图的 URL 列表。

        refs 为上传后的 gradio 路径列表（来自 upload_image）。
        on_progress: 可选回调，签名 (desc: str, progress: float) -> None。
        """
        refs = refs or []
        submit = self._sess.post(
            f"{self.base_url}/gradio_api/call/generate_image",
            json={"data": [prompt, refs, engine, batch]},
            timeout=30,
        )
        submit.raise_for_status()
        event_id = submit.json()["event_id"]
        return self._poll_sse(event_id, timeout_s=timeout_s, on_progress=on_progress)

    def _poll_sse(self, event_id: str, timeout_s: int, on_progress=None) -> list[str]:
        """订阅 SSE，返回最终图片 URL 列表。"""
        url = f"{self.base_url}/gradio_api/call/generate_image/{event_id}"
        with self._sess.get(url, headers={"Accept": "text/event-stream"}, stream=True, timeout=timeout_s) as r:
            r.raise_for_status()
            event_name = None
            buf: list[str] = []
            for raw in r.iter_lines(decode_unicode=True):
                if raw is None:
                    continue
                if raw == "":
                    # 事件结束
                    if event_name and buf:
                        data = "\n".join(buf)
                        result = self._handle_sse_event(event_name, data, on_progress)
                        if result is not None:
                            return result
                    event_name, buf = None, []
                    continue
                if raw.startswith("event:"):
                    event_name = raw.split(":", 1)[1].strip()
                elif raw.startswith("data:"):
                    buf.append(raw.split(":", 1)[1].lstrip())
        raise GrfalAPIError("SSE 流结束但未收到 complete 事件")

    def _handle_sse_event(self, event: str, data: str, on_progress):
        """解析一个 SSE 事件；返回非 None 表示终止。"""
        if event == "heartbeat":
            return None
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            return None
        if event == "progress":
            if on_progress and isinstance(payload, list) and payload:
                p0 = payload[0]
                on_progress(p0.get("desc", ""), p0.get("progress", 0.0))
            return None
        if event == "complete":
            return self._extract_urls(payload)
        if event == "error":
            raise GrfalAPIError(f"生成失败: {payload}")
        return None

    def _extract_urls(self, payload) -> list[str]:
        """从 complete 事件数据里抽出图片 URL 列表。

        实测格式：[{"result": ["/api/output/...png", ...], "success": bool}]
        """
        if not (isinstance(payload, list) and payload and isinstance(payload[0], dict)):
            raise GrfalAPIError(f"未识别的 complete payload: {payload!r}")
        wrapper = payload[0]
        if not wrapper.get("success", False):
            raise GrfalAPIError(f"生成标记失败: {wrapper}")
        result = wrapper.get("result") or []
        urls: list[str] = []
        for item in result:
            if isinstance(item, str):
                urls.append(item if item.startswith("http") else f"{self.base_url}{item}")
            elif isinstance(item, dict):
                for key in ("url", "path", "name"):
                    v = item.get(key)
                    if isinstance(v, str):
                        urls.append(v if v.startswith("http") else f"{self.base_url}{v}")
                        break
        return urls

    # ------------------------------------------------------------------ download
    def download(self, url: str, dest: Path) -> Path:
        """下载一个 grfal 图片到本地。url 可以是绝对或相对路径。"""
        if not url.startswith("http"):
            url = f"{self.base_url}{url}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self._sess.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(64 * 1024):
                    f.write(chunk)
        return dest


# --------------------------------------------------------------------- CLI
def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="grfal 命令行：跑一次生图保存到本地。")
    ap.add_argument("--ref", action="append", default=[], help="参考图本地路径（可多个）")
    ap.add_argument("--engine", default="gpt", help="引擎键 gpt/gemini/seedream/flux/...")
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--out-dir", default="./grfal_out")
    ap.add_argument("prompt", help="提示词")
    args = ap.parse_args()

    c = GrfalClient()

    def progress(desc, p):
        print(f"  [{p*100:5.1f}%] {desc}", file=sys.stderr, flush=True)

    ref_paths = [c.upload_image(p) for p in args.ref]
    print(f"uploaded {len(ref_paths)} refs", file=sys.stderr)

    urls = c.generate(
        prompt=args.prompt, refs=ref_paths,
        engine=args.engine, batch=args.batch,
        on_progress=progress,
    )
    print(f"got {len(urls)} images:", file=sys.stderr)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    for i, u in enumerate(urls):
        dest = out_dir / f"{ts}_{i}.png"
        c.download(u, dest)
        print(dest)


if __name__ == "__main__":
    _cli()
