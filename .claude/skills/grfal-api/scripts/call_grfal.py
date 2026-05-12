#!/usr/bin/env python3
"""GRFal API Caller - Direct HTTP interface to GRFal AI tools.

Calls GRFal tools via POST /api/call (sync).
Supports local file → base64 conversion for file inputs.
Supports long-lived token auth with auto-refresh and automatic device flow.

Usage:
    python call_grfal.py --tool generate_image --params '{"prompt": "a cat", "model": "gemini"}'
    python call_grfal.py --tool remove_background --file image_paths=C:/path/photo.png
    python call_grfal.py --tool generate_video --params '{"prompt":"sunset"}' --timeout 600
    python call_grfal.py --list-tools

Auth (zero-config):
    First run automatically opens browser for device flow authorization.
    Use --no-auth-interactive to disable auto browser auth.

Auth setup (manual/headless):
    python call_grfal.py --auth-bootstrap          # Get tokens via active login session
    python call_grfal.py --set-refresh-token <tok>  # Or manually save a refresh token
"""

import argparse
import base64
import json
import mimetypes
import os
import re
import ssl
import sys
import tempfile
import time
import urllib.request
import urllib.error
import webbrowser

# 内网固定域名（DNS → 公司代理 172.20.90.129 → 后端 172.20.90.45:6018）
# 使用公司代理的 DigiCert 正式证书，无需跳过验证
DEFAULT_API_URL = "https://grfal.tap4fun.com"
# 和域名指向同一后端的 IP（可以互相重写 URL）
SAME_HOST_IP = "http://172.20.90.45:6018"
# 回退 URL 列表（按优先级排序）
FALLBACK_URLS = [
    "http://172.20.90.45:6018",   # 主后端 IP（和域名同后端，可重写）
    "http://172.20.90.200:6018",  # 旧服务器 IP（独立机器，不重写）
]
DEFAULT_TIMEOUT = 300  # 5 minutes
MAX_FILE_SIZE_MB = 20  # Warn above this size
MAX_RETRIES = 2  # Retry on transient network errors
RETRY_DELAY = 2  # Seconds between retries

VIDEO_TOOLS = {
    "generate_video", "video_upscale", "video_modify", "video_to_audio",
    "video_lipsync", "video_portrait", "video_avatar", "video_reframe",
    "video_remove_background", "video_speed", "export_sbs_video",
    "creative_workflow", "train_model",
}

# 使用异步轮询模式的工具（长时间任务）
ASYNC_TOOLS = VIDEO_TOOLS | {"generate_3d"}

# 超长任务默认用后台模式（只提交，需手动 --check-task 查询结果）
# 这些工具通常需要 10+ 分钟，轮询等待体验差
# 基于 usage log 分析：>50% 调用超过 10 分钟的工具
BACKGROUND_TOOLS = {
    # 视频类（已验证耗时长）
    "video_avatar",      # 中位 9.5m, 41% >10min
    "video_lipsync",     # 中位 1.8m, 但失败重试可能很长
    "video_portrait",    # 自导自演，经常 30min+
    "generate_video",    # sora 85% >10min, veo3 6% >10min
    "video_upscale",     # 43% >5min, 29% >10min
    "video_modify",      # 45% >5min, 20% >10min
    # 训练类
    "train_model",       # 中位 40.6m, 77% >10min
    # 其他长任务
    "screenshot_localization",  # 中位 23.5m, 76% >10min
    "pdf_enhancement",          # 中位 12.1m, 62% >10min
}

# 轮询配置
POLL_INITIAL_WAIT = 30    # 提交后首次等待 30 秒
POLL_INTERVAL = 15        # 之后每 15 秒轮询一次

ALL_TOOLS = [
    "generate_image", "generate_video", "generate_3d",
    "upscale_image", "remove_background", "replace_background",
    "image_resize", "image_remove_lighting",
    "image_group_photo", "image_camera_angle", "image_keyframe",
    "image_layered", "image_split",
    "lora_generation", "kontext_lora",
    "video_upscale", "video_modify", "video_to_audio",
    "video_lipsync", "video_portrait", "video_avatar",
    "video_reframe", "video_remove_background", "video_speed",
    "export_sbs_video",
    "virtual_tryon", "describe_media", "synthesize_card",
    "correct_yellow_tint", "vector_generation",
    "screenshot_localization", "pdf_enhancement", "pdf_compression",
    "reduce_face", "train_model", "creative_workflow",
]

# Token cache file for long-lived auth
TOKEN_STORE_DIR = os.path.join(os.path.expanduser("~"), ".config", "grfal-api")
TOKEN_STORE_PATH = os.path.join(TOKEN_STORE_DIR, "token_store.json")
# Refresh early: treat token as expired 5 minutes before actual expiry
TOKEN_EXPIRY_BUFFER = 300

# Device flow polling config
DEVICE_POLL_DEFAULT_INTERVAL = 5  # seconds between polls
DEVICE_POLL_MAX_WAIT = 300  # 5 minutes max wait for user authorization


MIME_MAP = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
    ".tiff": "image/tiff", ".tif": "image/tiff",
    ".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime",
    ".avi": "video/x-msvideo", ".mkv": "video/x-matroska",
    ".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg",
    ".flac": "audio/flac", ".aac": "audio/aac",
    ".glb": "model/gltf-binary", ".gltf": "model/gltf+json",
    ".obj": "text/plain", ".fbx": "application/octet-stream",
    ".pdf": "application/pdf", ".zip": "application/zip",
}


def get_base_url(args_url):
    """Resolve base URL: --url > env var > default (domain URL)."""
    if args_url:
        return args_url.rstrip("/")
    env_url = os.environ.get("GRFAL_API_URL")
    if env_url:
        return env_url.rstrip("/")
    return DEFAULT_API_URL


def _load_token_store():
    """Load cached tokens from disk. Returns dict or empty dict."""
    try:
        with open(TOKEN_STORE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _save_token_store(data):
    """Atomically save token store to disk."""
    os.makedirs(TOKEN_STORE_DIR, mode=0o700, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=TOKEN_STORE_DIR, suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, TOKEN_STORE_PATH)
        os.chmod(TOKEN_STORE_PATH, 0o600)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _cached_access_token():
    """Return cached access_token if it exists and is not expired."""
    store = _load_token_store()
    access = store.get("access_token")
    expires_at = store.get("expires_at", 0)
    if access and time.time() < expires_at - TOKEN_EXPIRY_BUFFER:
        return access
    return None


def _refresh_token_value():
    """Return refresh token from env or cache."""
    env_rt = os.environ.get("GRFAL_REFRESH_TOKEN")
    if env_rt:
        return env_rt
    store = _load_token_store()
    return store.get("refresh_token")


def _do_token_refresh(base_url, refresh_token, insecure=False):
    """Call /auth/agent-token/refresh to get new access+refresh tokens.

    Returns (access_token, refresh_token, expires_in) or None on failure.
    """
    url = f"{base_url}/auth/agent-token/refresh"
    payload = json.dumps({"refresh_token": refresh_token}).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    ssl_context = None
    if base_url.startswith("https://"):
        ssl_context = ssl.create_default_context()
        if insecure:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(json.dumps({"warning": f"Token refresh failed: {e}"}), file=sys.stderr)
        return None

    new_access = data.get("access_token")
    new_refresh = data.get("refresh_token")
    expires_in = data.get("expires_in", 43200)  # default 12h

    if not new_access:
        print(json.dumps({"warning": f"Token refresh returned no access_token: {data}"}), file=sys.stderr)
        return None

    # Save to cache
    store = _load_token_store()
    store["access_token"] = new_access
    if new_refresh:
        store["refresh_token"] = new_refresh
    store["expires_at"] = int(time.time()) + expires_in
    _save_token_store(store)

    print(json.dumps({"info": "Token refreshed and cached successfully"}), file=sys.stderr)
    return new_access


def _do_auth_bootstrap(base_url, insecure=False):
    """Call /auth/agent-token to get initial access+refresh tokens.

    Requires an active login session (cookie-based). For same-machine usage.
    Returns True on success.
    """
    url = f"{base_url}/auth/agent-token"
    req = urllib.request.Request(url, method="GET")

    ssl_context = None
    if base_url.startswith("https://"):
        ssl_context = ssl.create_default_context()
        if insecure:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(json.dumps({
            "success": False,
            "error": f"Auth bootstrap failed (HTTP {e.code}): {body[:500]}. "
                     "Ensure you have an active login session on this machine."
        }))
        return False
    except Exception as e:
        print(json.dumps({"success": False, "error": f"Auth bootstrap failed: {e}"}))
        return False

    access = data.get("access_token")
    refresh = data.get("refresh_token")
    expires_in = data.get("expires_in", 43200)

    if not access or not refresh:
        print(json.dumps({
            "success": False,
            "error": f"Auth bootstrap returned incomplete tokens: {data}"
        }))
        return False

    store = {
        "access_token": access,
        "refresh_token": refresh,
        "expires_at": int(time.time()) + expires_in,
    }
    _save_token_store(store)

    # Try upgrading to long-lived token (silently fails if server doesn't support it)
    _try_upgrade_to_long_lived_token(base_url, access, insecure=insecure)

    # Re-read store in case upgrade succeeded
    final_store = _load_token_store()
    final_expires_in = final_store.get("expires_at", 0) - int(time.time())

    print(json.dumps({
        "success": True,
        "message": "Auth bootstrap successful. Tokens cached.",
        "token_store": TOKEN_STORE_PATH,
        "access_expires_in": f"{final_expires_in // 86400}d" if final_expires_in > 86400 else f"{expires_in // 3600}h",
        "refresh_note": "Refresh token is valid for 30 days and will auto-renew.",
    }, indent=2))
    return True


def _is_interactive():
    """Check if we're in an interactive environment (stdin is a tty)."""
    try:
        return sys.stdin.isatty()
    except Exception:
        return False


def _do_device_flow_auth(base_url, insecure=False):
    """Automatic interactive auth via device flow.

    1. POST /auth/agent-token/device/start → device_code, verification_url, etc.
    2. Open browser to verification_url (or print URL on failure)
    3. Poll POST /auth/agent-token/device/poll with device_code
    4. On success, save tokens to token_store.json and return access_token
    """
    ssl_context = _get_ssl_context(base_url, insecure)

    # Step 1: Start device flow
    start_url = f"{base_url}/auth/agent-token/device/start"
    req = urllib.request.Request(
        start_url, data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(json.dumps({"warning": f"Device flow start failed: {e}"}), file=sys.stderr)
        return None

    device_code = data.get("device_code")
    verification_url = data.get("verification_url")
    user_code = data.get("user_code")
    interval = data.get("interval", DEVICE_POLL_DEFAULT_INTERVAL)
    expires_in = data.get("expires_in", DEVICE_POLL_MAX_WAIT)

    if not device_code or not verification_url:
        print(json.dumps({"warning": f"Device flow returned incomplete data: {data}"}), file=sys.stderr)
        return None

    # Step 2: Try to open browser, fall back to printing URL
    browser_opened = False
    try:
        browser_opened = webbrowser.open(verification_url)
    except Exception:
        pass

    if browser_opened:
        print(json.dumps({"info": "Browser opened for authorization."}), file=sys.stderr)
    else:
        print(json.dumps({"info": "Could not open browser automatically."}), file=sys.stderr)

    print(f"\n  Please visit: {verification_url}", file=sys.stderr)
    if user_code:
        print(f"  Enter code:   {user_code}", file=sys.stderr)
    print("  Waiting for authorization...\n", file=sys.stderr)

    # Step 3: Poll for authorization
    poll_url = f"{base_url}/auth/agent-token/device/poll"
    start_time = time.time()

    while time.time() - start_time < expires_in:
        time.sleep(interval)

        poll_payload = json.dumps({"device_code": device_code}).encode("utf-8")
        poll_req = urllib.request.Request(
            poll_url, data=poll_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(poll_req, timeout=30, context=ssl_context) as resp:
                poll_data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            try:
                poll_data = json.loads(body)
            except json.JSONDecodeError:
                print(json.dumps({"warning": f"Device poll error: HTTP {e.code}"}), file=sys.stderr)
                continue

            # Handle standard device flow error codes
            error_code = poll_data.get("error")
            if error_code == "authorization_pending":
                continue
            elif error_code == "slow_down":
                interval = min(interval + 5, 30)
                continue
            elif error_code == "expired_token":
                print(json.dumps({"warning": "Device code expired. Please try again."}), file=sys.stderr)
                return None
            elif error_code == "access_denied":
                print(json.dumps({"warning": "Authorization denied by user."}), file=sys.stderr)
                return None
            else:
                print(json.dumps({"warning": f"Device poll error: {poll_data}"}), file=sys.stderr)
                continue
        except Exception as e:
            print(json.dumps({"warning": f"Device poll failed: {e}"}), file=sys.stderr)
            continue

        # Success - got tokens
        access = poll_data.get("access_token")
        refresh = poll_data.get("refresh_token")
        exp_in = poll_data.get("expires_in", 43200)

        if access:
            store = {
                "access_token": access,
                "expires_at": int(time.time()) + exp_in,
            }
            if refresh:
                store["refresh_token"] = refresh
            _save_token_store(store)
            print(json.dumps({
                "info": "Device flow auth successful. Tokens cached.",
                "token_store": TOKEN_STORE_PATH,
            }), file=sys.stderr)
            # Try upgrading to long-lived token (silently fails if server doesn't support it)
            _try_upgrade_to_long_lived_token(base_url, access, insecure=insecure)
            return _cached_access_token() or access

    print(json.dumps({"warning": "Device flow timed out waiting for authorization."}), file=sys.stderr)
    return None


def _try_upgrade_to_long_lived_token(base_url, access_token, insecure=False):
    """Try to upgrade access_token to a long-lived token via /auth/agent-token/upgrade.

    On success, overwrites token_store with the long-lived token.
    On failure (server doesn't support it, network error), silently returns without changes.
    """
    url = f"{base_url}/auth/agent-token/upgrade"
    req = urllib.request.Request(
        url, data=b"{}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
        method="POST",
    )

    ssl_context = _get_ssl_context(base_url, insecure)

    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(json.dumps({"info": f"Long-lived token upgrade skipped: {e}"}), file=sys.stderr)
        return

    long_access = data.get("access_token")
    long_expires_in = data.get("expires_in")
    if not long_access or not long_expires_in:
        return

    store = {
        "access_token": long_access,
        "expires_at": int(time.time()) + long_expires_in,
    }
    _save_token_store(store)
    print(json.dumps({
        "info": f"Upgraded to long-lived token ({long_expires_in // 86400}d).",
    }), file=sys.stderr)


def _sign_jwt():
    """Auto-sign a short-lived JWT using GRFAL_AGENT_JWT_SECRET."""
    try:
        import jwt
    except ImportError:
        print(json.dumps({
            "warning": "PyJWT not installed, cannot auto-sign JWT. pip install PyJWT"
        }), file=sys.stderr)
        return None

    secret = os.environ.get("GRFAL_AGENT_JWT_SECRET")
    if not secret:
        return None

    now = int(time.time())
    ttl = int(os.environ.get("GRFAL_AGENT_JWT_TTL", "300"))
    username = os.environ.get("GRFAL_AGENT_USERNAME", "openclaw-skill")

    claims = {
        "sub": os.environ.get("GRFAL_AGENT_USER_ID", "openclaw-skill"),
        "username": username,
        "name": username,
        "iat": now,
        "exp": now + ttl,
    }

    # scopes: comma or space separated
    scopes_raw = os.environ.get("GRFAL_AGENT_SCOPES", "")
    if scopes_raw:
        claims["scopes"] = [s.strip() for s in scopes_raw.replace(",", " ").split() if s.strip()]
    else:
        claims["scopes"] = []

    # optional issuer / audience
    iss = os.environ.get("GRFAL_AGENT_JWT_ISSUER")
    if iss:
        claims["iss"] = iss
    aud = os.environ.get("GRFAL_AGENT_JWT_AUDIENCE")
    if aud:
        claims["aud"] = aud

    return jwt.encode(claims, secret, algorithm="HS256")


def get_bearer_token(cli_token=None, base_url=None, insecure=False, auth_interactive=True):
    """Resolve bearer token (priority high→low):
    1. --bearer-token CLI arg
    2. GRFAL_BEARER_TOKEN env
    3. Cached access_token (if not expired)
    4. Refresh via GRFAL_REFRESH_TOKEN or cached refresh_token
    5. Fallback: auto-sign JWT (legacy)
    6. Interactive device flow (if auth_interactive=True and tty available)
    """
    # 1. CLI
    if cli_token:
        return cli_token
    # 2. Env
    env_token = os.environ.get("GRFAL_BEARER_TOKEN")
    if env_token:
        return env_token
    # 3. Cached access token
    cached = _cached_access_token()
    if cached:
        return cached
    # 4. Refresh flow
    rt = _refresh_token_value()
    if rt and base_url:
        refreshed = _do_token_refresh(base_url, rt, insecure=insecure)
        if refreshed:
            _try_upgrade_to_long_lived_token(base_url, refreshed, insecure=insecure)
            return _cached_access_token() or refreshed
    # 5. Legacy JWT signing
    jwt_token = _sign_jwt()
    if jwt_token:
        return jwt_token
    # 6. Interactive device flow (automatic browser authorization)
    if auth_interactive and base_url:
        if _is_interactive():
            print(json.dumps({
                "info": "No token available. Starting automatic device flow authorization..."
            }), file=sys.stderr)
            device_token = _do_device_flow_auth(base_url, insecure=insecure)
            if device_token:
                return device_token
        else:
            print(json.dumps({
                "warning": "No token available. Non-interactive environment detected. "
                           "Run interactively to auto-authorize via browser, "
                           "or use --auth-bootstrap / --set-refresh-token."
            }), file=sys.stderr)
    return None


def _build_headers(content_type="application/json", bearer_token=None):
    """Build HTTP headers with optional Authorization."""
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    return headers


def _format_auth_error(status_code, body):
    """Format helpful error message for 401/403 auth failures."""
    hint = ""
    if status_code == 401:
        hint = (
            " | Auth hint: re-run the command in an interactive terminal — "
            "the script will automatically open a browser for authorization. "
            "Use --no-auth-interactive to disable auto browser auth. "
            "Alternative: --auth-bootstrap (requires active login session), "
            "--set-refresh-token <token>, or GRFAL_BEARER_TOKEN env var."
        )
    elif status_code == 403:
        hint = (
            " | Scope hint: token may be expired. Try re-authorizing via device flow "
            "(re-run in interactive terminal) or --auth-bootstrap to re-bootstrap. "
            "Check GRFAL_AGENT_SCOPES and permissions for this operation."
        )
    return f"HTTP {status_code}: {body[:500]}{hint}"


def rewrite_urls(result, from_url, to_url):
    """Rewrite URLs in result (for fallback mode where IP was used)."""
    if not result or not from_url or not to_url:
        return result
    json_str = json.dumps(result, ensure_ascii=False)
    json_str = json_str.replace(from_url, to_url)
    return json.loads(json_str)


def absolutize_output_urls(result, prefix_url):
    """给后端返回的 /api/output/... 相对路径前缀为 prefix_url，得到可直达 URL。

    服务端切到 gradio.Server 后，/api/call 返回的是相对路径（如
    "/api/output/xxx.png"），需要由客户端按请求来源补全 host。
    """
    if not result or not prefix_url:
        return result
    prefix = prefix_url.rstrip("/")
    json_str = json.dumps(result, ensure_ascii=False)
    # 只对以 / 开头且 host 段缺失的 /api/output/... 前缀化
    json_str = re.sub(
        r'"(\\?/api/output/[^"]+)"',
        lambda m: f'"{prefix}{m.group(1)}"',
        json_str,
    )
    return json.loads(json_str)


def file_to_base64(file_path):
    """Convert local file to base64 data URI."""
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {abs_path}")

    # Check file size
    size_mb = os.path.getsize(abs_path) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        print(
            json.dumps({
                "warning": f"File is {size_mb:.1f}MB (>{MAX_FILE_SIZE_MB}MB). "
                           f"Consider using a public URL instead for better performance."
            }),
            file=sys.stderr,
        )

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(abs_path)
    if not mime_type:
        ext = os.path.splitext(abs_path)[1].lower()
        mime_type = MIME_MAP.get(ext, "application/octet-stream")

    with open(abs_path, "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def inject_files(params, file_args):
    """Inject local files as base64 data URIs into params.

    file_args: list of "param_key=file_path" strings.
    Multiple files with the same key are collected into a list.
    """
    if not file_args:
        return params

    file_map = {}
    for entry in file_args:
        if "=" not in entry:
            raise ValueError(
                f"Invalid --file format: '{entry}'. Expected: param_key=file_path"
            )
        key, path = entry.split("=", 1)
        b64 = file_to_base64(path)

        if key in file_map:
            if isinstance(file_map[key], list):
                file_map[key].append(b64)
            else:
                file_map[key] = [file_map[key], b64]
        else:
            file_map[key] = b64

    # Merge into params (file values override existing keys)
    for key, value in file_map.items():
        # If param already has a list value and we have a single file, wrap in list
        existing = params.get(key)
        if isinstance(existing, list) and not isinstance(value, list):
            existing.append(value)
        else:
            params[key] = value

    return params


def call_api(base_url, tool_name, params, timeout, insecure=False, bearer_token=None):
    """Make HTTP POST to GRFal /api/call endpoint with retry."""
    url = f"{base_url}/api/call"
    payload = json.dumps({"tool": tool_name, "params": params}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers=_build_headers(bearer_token=bearer_token),
        method="POST",
    )

    # SSL context for HTTPS (handle self-signed certs)
    ssl_context = None
    if base_url.startswith("https://"):
        ssl_context = ssl.create_default_context()
        if insecure:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            # HTTP errors are not retryable (business logic errors)
            body = e.read().decode("utf-8", errors="replace")
            if e.code in (401, 403):
                return {"success": False, "error": _format_auth_error(e.code, body)}
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"success": False, "error": f"HTTP {e.code}: {body[:500]}"}
        except urllib.error.URLError as e:
            reason = str(e.reason)
            # SSL certificate errors - give helpful message
            if "CERTIFICATE_VERIFY_FAILED" in reason or "certificate" in reason.lower():
                return {
                    "success": False,
                    "error": f"SSL certificate error: {reason}. "
                             f"Use --insecure to skip verification, or install the CA certificate.",
                }
            # Connection errors may be transient - retry
            last_error = f"Connection failed: {reason}. Is GRFal running at {base_url}?"
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return {"success": False, "error": last_error}
        except Exception as e:
            error_name = type(e).__name__
            error_str = str(e).lower()
            if "timeout" in error_name.lower() or "timed out" in error_str:
                # Timeout is not retryable (task is still running on server)
                return {
                    "success": False,
                    "error": f"Request timed out after {timeout}s. "
                             f"Try increasing --timeout or using a simpler request.",
                }
            # Other errors may be transient - retry
            last_error = f"{error_name}: {e}"
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return {"success": False, "error": last_error}

    return {"success": False, "error": last_error or "Unknown error"}


def _get_ssl_context(base_url, insecure=False):
    """获取 SSL 上下文"""
    if not base_url.startswith("https://"):
        return None
    ssl_context = ssl.create_default_context()
    if insecure:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context


def submit_async_task(base_url, tool_name, params, insecure=False, bearer_token=None):
    """提交异步任务，返回 task_id"""
    url = f"{base_url}/api/async/submit"
    payload = json.dumps({"tool": tool_name, "params": params}).encode("utf-8")

    req = urllib.request.Request(
        url, data=payload,
        headers=_build_headers(bearer_token=bearer_token),
        method="POST",
    )

    ssl_context = _get_ssl_context(base_url, insecure)

    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code in (401, 403):
            return {"success": False, "error": _format_auth_error(e.code, body)}
        return {"success": False, "error": f"Submit failed: HTTP {e.code}: {body[:500]}"}
    except Exception as e:
        return {"success": False, "error": f"Submit failed: {e}"}


def poll_task_status(base_url, task_id, insecure=False, bearer_token=None):
    """查询任务状态"""
    url = f"{base_url}/api/async/status/{task_id}"
    req = urllib.request.Request(url, method="GET",
                                headers=_build_headers(content_type=None, bearer_token=bearer_token))

    ssl_context = _get_ssl_context(base_url, insecure)

    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code in (401, 403):
            return {"success": False, "error": _format_auth_error(e.code, body)}
        return {"success": False, "error": f"Poll failed: HTTP {e.code}: {body[:500]}"}
    except Exception as e:
        return {"success": False, "error": f"Poll failed: {e}"}


def get_task_result(base_url, task_id, insecure=False, bearer_token=None):
    """获取任务结果"""
    url = f"{base_url}/api/async/result/{task_id}?delete=true"
    req = urllib.request.Request(url, method="GET",
                                headers=_build_headers(content_type=None, bearer_token=bearer_token))

    ssl_context = _get_ssl_context(base_url, insecure)

    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl_context) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code in (401, 403):
            return {"success": False, "error": _format_auth_error(e.code, body)}
        return {"success": False, "error": f"Get result failed: HTTP {e.code}: {body[:500]}"}
    except Exception as e:
        return {"success": False, "error": f"Get result failed: {e}"}


def view_server_logs(base_url, filename, lines, insecure=False, bearer_token=None):
    """查看服务器日志"""
    url = f"{base_url}/api/logs/view/{filename}?lines={lines}"
    req = urllib.request.Request(url, method="GET",
                                headers=_build_headers(content_type=None, bearer_token=bearer_token))

    ssl_context = _get_ssl_context(base_url, insecure)

    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code in (401, 403):
            return {"success": False, "error": _format_auth_error(e.code, body)}
        return {"success": False, "error": f"HTTP {e.code}: {body[:500]}"}
    except Exception as e:
        return {"success": False, "error": f"View logs failed: {e}"}


def call_api_async(base_url, tool_name, params, timeout, insecure=False, bearer_token=None):
    """异步 API 调用（提交 + 轮询）"""

    # 1. 提交任务
    submit_result = submit_async_task(base_url, tool_name, params, insecure, bearer_token=bearer_token)

    if not submit_result.get("success"):
        return submit_result

    task_id = submit_result["task_id"]
    print(json.dumps({"info": f"Task submitted: {task_id}"}), file=sys.stderr)

    # 2. 初始等待
    print(json.dumps({"info": f"Waiting {POLL_INITIAL_WAIT}s..."}), file=sys.stderr)
    time.sleep(POLL_INITIAL_WAIT)

    # 3. 轮询循环
    start_time = time.time()
    poll_count = 0

    while True:
        elapsed = time.time() - start_time

        # 检查超时
        if elapsed > timeout:
            return {
                "success": False,
                "error": f"Polling timed out after {int(elapsed)}s. Task may still be running on server.",
                "task_id": task_id,
            }

        # 查询状态
        poll_count += 1
        status = poll_task_status(base_url, task_id, insecure, bearer_token=bearer_token)

        if not status.get("success"):
            print(json.dumps({"warning": f"Poll #{poll_count} failed: {status.get('error')}"}), file=sys.stderr)
            time.sleep(POLL_INTERVAL)
            continue

        task_status = status.get("status", "unknown")
        progress = status.get("progress", "")
        server_elapsed = status.get("elapsed_seconds", 0)

        print(json.dumps({
            "info": f"Poll #{poll_count}: {task_status} ({server_elapsed:.0f}s) {progress}"
        }), file=sys.stderr)

        # 检查完成状态
        if task_status == "completed":
            return get_task_result(base_url, task_id, insecure, bearer_token=bearer_token)

        elif task_status == "failed":
            return get_task_result(base_url, task_id, insecure, bearer_token=bearer_token)

        # 等待下次轮询
        time.sleep(POLL_INTERVAL)


def main():
    parser = argparse.ArgumentParser(
        description="Call GRFal AI tools via HTTP API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               '  python call_grfal.py --tool generate_image --params \'{"prompt":"a cat"}\'\n'
               "  python call_grfal.py --tool remove_background --file image_paths=photo.png\n"
               "  python call_grfal.py --list-tools\n",
    )
    parser.add_argument("--tool", help="Tool name (e.g., generate_image)")
    parser.add_argument("--params", default="{}", help="JSON params string")
    parser.add_argument("--url", default=None, help="GRFal base URL (overrides env/default)")
    parser.add_argument(
        "--file", action="append", dest="files",
        help="Local file to inject as base64: param_key=file_path (repeatable)",
    )
    parser.add_argument(
        "--timeout", type=int, default=None,
        help="Timeout in seconds (default: 300 for images, 600 for video)",
    )
    parser.add_argument(
        "--public-url", default=None,
        help="Override URL prefix for result rewriting. Use --public-url none to disable rewriting.",
    )
    parser.add_argument(
        "--list-tools", action="store_true",
        help="List all available tool names",
    )
    parser.add_argument(
        "--insecure", action="store_true",
        help="Skip SSL certificate verification (for self-signed certs)",
    )
    parser.add_argument(
        "--sync", action="store_true",
        help="Force synchronous mode (disable polling for async tools)",
    )
    parser.add_argument(
        "--submit-only", action="store_true",
        help="Submit task and return immediately with task_id (no polling)",
    )
    parser.add_argument(
        "--check-task", metavar="TASK_ID",
        help="Check status or get result of a previously submitted task",
    )
    parser.add_argument(
        "--view-logs", nargs="?", const="systemd-journal", metavar="FILENAME",
        help="View server logs (default: systemd-journal). Options: systemd-journal, grfal_YYYYMMDD.log",
    )
    parser.add_argument(
        "--log-lines", type=int, default=200,
        help="Number of log lines to fetch (default: 200)",
    )
    parser.add_argument(
        "--bearer-token", default=None,
        help="Bearer token for API auth (overrides GRFAL_BEARER_TOKEN env var)",
    )
    parser.add_argument(
        "--auth-bootstrap", action="store_true",
        help="Bootstrap auth: call /auth/agent-token to get initial access+refresh tokens "
             "(requires active login session on this machine)",
    )
    parser.add_argument(
        "--set-refresh-token", metavar="TOKEN", default=None,
        help="Save a refresh token to local cache for auto-renewal",
    )
    parser.add_argument(
        "--auth-interactive", action="store_true", default=None,
        help="Enable automatic browser-based device flow auth (default: enabled)",
    )
    parser.add_argument(
        "--no-auth-interactive", action="store_true",
        help="Disable automatic browser-based device flow auth",
    )
    args = parser.parse_args()

    # Resolve auth_interactive: CLI flags > env var > default (True)
    if args.no_auth_interactive:
        args.auth_interactive = False
    elif args.auth_interactive is None:
        env_val = os.environ.get("GRFAL_AUTH_INTERACTIVE", "").strip()
        if env_val in ("0", "false", "no", "off"):
            args.auth_interactive = False
        else:
            args.auth_interactive = True

    # List tools mode
    if args.list_tools:
        print(json.dumps({"tools": ALL_TOOLS}, indent=2))
        return

    base_url = get_base_url(args.url)

    # --set-refresh-token: save refresh token to local cache and exit
    if args.set_refresh_token:
        store = _load_token_store()
        store["refresh_token"] = args.set_refresh_token
        _save_token_store(store)
        print(json.dumps({
            "success": True,
            "message": "Refresh token saved to local cache.",
            "token_store": TOKEN_STORE_PATH,
            "next": "The script will auto-refresh access tokens using this refresh token.",
        }, indent=2))
        return

    # --auth-bootstrap: get initial token pair from server
    if args.auth_bootstrap:
        ok = _do_auth_bootstrap(base_url, insecure=args.insecure)
        sys.exit(0 if ok else 1)

    bearer_token = get_bearer_token(
        args.bearer_token, base_url=base_url, insecure=args.insecure,
        auth_interactive=args.auth_interactive,
    )

    # View logs mode
    if args.view_logs is not None:
        result = view_server_logs(base_url, args.view_logs, args.log_lines, args.insecure,
                                  bearer_token=bearer_token)
        if result.get("success"):
            # Print log content directly for readability
            print(result.get("content", ""))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result.get("success") else 1)

    # Check task mode: query status or get result
    if args.check_task:
        task_id = args.check_task
        status = poll_task_status(base_url, task_id, args.insecure, bearer_token=bearer_token)
        if not status.get("success"):
            print(json.dumps(status, ensure_ascii=False, indent=2))
            sys.exit(1)

        task_status = status.get("status")
        if task_status in ("completed", "failed"):
            # Task done, get result
            result = get_task_result(base_url, task_id, args.insecure, bearer_token=bearer_token)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(0 if result.get("success") else 1)
        else:
            # Task still running
            print(json.dumps(status, ensure_ascii=False, indent=2))
            sys.exit(0)

    # Validate required args
    if not args.tool:
        parser.error("--tool is required (use --list-tools to see available tools)")

    # Parse params
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"Invalid JSON params: {e}"}))
        sys.exit(1)

    # Inject local files
    try:
        params = inject_files(params, args.files)
    except (FileNotFoundError, ValueError) as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

    # Determine timeout
    timeout = args.timeout
    if timeout is None:
        timeout = 1800 if args.tool in VIDEO_TOOLS else DEFAULT_TIMEOUT

    # Submit-only mode: just submit and return task_id
    # 自动对 BACKGROUND_TOOLS 启用（除非用 --sync 强制同步）
    use_background = (
        args.submit_only
        or (args.tool in BACKGROUND_TOOLS and not args.sync)
    )

    if use_background:
        result = submit_async_task(base_url, args.tool, params, args.insecure,
                                   bearer_token=bearer_token)
        if result.get("success"):
            # Add estimated time hint
            result["hint"] = "Use --check-task <task_id> to check status later"
            if args.tool in BACKGROUND_TOOLS and not args.submit_only:
                result["note"] = f"{args.tool} is a long-running task, using background mode automatically"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result.get("success") else 1)

    # 决定使用同步还是异步模式
    use_async = (
        args.tool in ASYNC_TOOLS
        and not args.sync
    )

    # Call API with auto-fallback
    used_fallback_url = None  # Track which fallback URL was used
    # 域名使用公司代理的正式证书，正常验证即可
    if use_async:
        print(json.dumps({"info": f"Using async polling mode for {args.tool}"}), file=sys.stderr)
        result = call_api_async(base_url, args.tool, params, timeout,
                                insecure=args.insecure, bearer_token=bearer_token)
    else:
        result = call_api(base_url, args.tool, params, timeout,
                          insecure=args.insecure, bearer_token=bearer_token)

    # Auto-fallback: if domain fails with connection error, try fallback IPs
    if not result.get("success") and not args.url:
        error_msg = result.get("error", "").lower()
        # Only fallback on connection errors, not timeouts or business errors
        if "connection" in error_msg or "resolve" in error_msg or "ssl" in error_msg:
            for fallback_url in FALLBACK_URLS:
                print(json.dumps({"info": f"Trying fallback: {fallback_url}"}), file=sys.stderr)
                result = call_api(fallback_url, args.tool, params, timeout,
                                  insecure=True, bearer_token=bearer_token)
                if result.get("success"):
                    used_fallback_url = fallback_url
                    break
                # If this fallback also failed with connection error, try next
                fallback_error = result.get("error", "").lower()
                if not ("connection" in fallback_error or "resolve" in fallback_error):
                    break  # Non-connection error, don't try more fallbacks

    # URL rewriting
    if result.get("success"):
        source_url = used_fallback_url if used_fallback_url else base_url
        if args.public_url and args.public_url.lower() != "none":
            # User specified explicit public URL
            result = rewrite_urls(result, source_url, args.public_url.rstrip("/"))
        elif source_url == SAME_HOST_IP:
            # 只对和域名同机器的 IP 重写为域名
            # 其他 IP（如旧服务器）保持原样，因为文件在不同机器上
            result = rewrite_urls(result, source_url, DEFAULT_API_URL)

        # 服务端改用 gradio.Server 后 /api/output/... 返回的是相对路径，
        # 按调用来源补全为可直达 URL（优先 --public-url，其次请求的 base_url）
        prefix = (
            args.public_url.rstrip("/")
            if args.public_url and args.public_url.lower() != "none"
            else source_url
        )
        result = absolutize_output_urls(result, prefix)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
