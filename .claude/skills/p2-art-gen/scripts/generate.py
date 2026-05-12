#!/usr/bin/env python3
"""p2-art-gen 三模块入口：ui / chest / item。

默认每次 8 张 = gpt × 4 + gemini × 4 并发。

用法：
    python3 generate.py chest --prompt "..." [--batch 8]
    python3 generate.py item  --prompt "..." [--theme "拓荒节"]
    python3 generate.py ui    --prompt "..." --competitor /path/screenshot.png
    python3 generate.py chest --prompt "..." --engines gpt        # 单引擎
    python3 generate.py chest --prompt "..." --engines seedream,flux  # 自定义组合

支持引擎：gpt / gemini / seedream / flux / vidu / wan / runway / qwen /
         ideogram / hunyuan / grok / zimage / firered
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import random
import sys
import time
from pathlib import Path

from ai_art_client import AiArtClient as GrfalClient  # drop-in，保留变量名不改
from gallery import append_batch

MANIFEST_NAME = "manifest.json"

SKILL_DIR = Path(__file__).resolve().parent.parent        # .../.claude/skills/p2-art-gen
ANCHORS_DIR = SKILL_DIR / "anchors"
PROJECT_ROOT = SKILL_DIR.parent.parent.parent             # 项目根（游戏运营策划工具/）
OUTPUT_ROOT = PROJECT_ROOT / "output" / "grfal"

# 一句话风格指令，放在 prompt 最前面
STYLE_PREFIX = {
    "ui": "保留参考竞品的整体构图、UI 节奏和视觉层级，但替换为 P2 卡通 3D 游戏画风。图标上不要有任何文字。",
    "chest": "仅借鉴图片的绘画风格，不要照抄形状，生成道具自选箱，箱子样式自由发挥。图标上不要有任何文字。",
    "item": "参考绘画风格，帮我生成 {prompt} 道具，正面平视图。图标上不要有任何文字。",
    "dighole": "参考绘画风格，按照图1的形状，生成图2及之后绘画风格的 {prompt}，不要背景。只给我道具图标，正面平视图。图标上不要有任何文字。",
}

BATCH_PER_CALL = 4     # 单次调用最多 4 张
MAX_CONCURRENT = 4     # 同时在飞的请求上限


IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def _module_root(module: str) -> Path:
    return ANCHORS_DIR / {"ui": "ui_panel", "chest": "chest", "item": "item", "dighole": "dighole"}[module]


def _load_manifest(folder: Path) -> dict | None:
    """读 subcategory 目录下的 manifest.json（节日语义元数据）；不存在返回 None。"""
    mf = folder / MANIFEST_NAME
    if not mf.exists():
        return None
    try:
        return json.loads(mf.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ! manifest.json 解析失败 ({mf}): {e}", file=sys.stderr)
        return None


def _filter_by_festival(candidates: list[Path], manifest: dict, festival: str) -> list[Path]:
    """按 festival 过滤候选锚点。规则：
    - 锚点 festivals 列表包含 festival 或 '*'（通用） → 入选
    - 不在 manifest 中的图（未打标签） → 也入选（向后兼容，不阻断新加图）
    - festival 命中 manifest['_festivals'] 校验，不在则报错（规避拼写错）
    """
    anchors_meta = manifest.get("anchors", {})
    valid_festivals = manifest.get("_festivals", [])
    if valid_festivals and festival not in valid_festivals:
        raise ValueError(
            f"--festival '{festival}' 不在合法节日清单：{valid_festivals}"
        )
    out = []
    for p in candidates:
        meta = anchors_meta.get(p.name)
        if meta is None:
            out.append(p)  # 未标记的图保留（manifest 未覆盖）
            continue
        festivals = meta.get("festivals", [])
        if festival in festivals or "*" in festivals:
            out.append(p)
    return out


def pick_anchors(module: str, subcategory: str | None = None,
                 explicit: list[str] | None = None, count: int = 1,
                 exclude: list[str] | None = None,
                 festival: str | None = None) -> list[Path]:
    """挑 P2 锚点。优先级：explicit > subcategory + festival 过滤 + 随机 > 顶层随机。

    - subcategory: 子文件夹名（如 "节日道具自选箱"）
    - festival: 节日名（如 "登月节"）。当 subcategory 下有 manifest.json 时，按节日语义过滤
    - explicit: 显式文件名列表（最高优先级，绕过 festival 过滤）
    - count: 不显式时随机挑几张；subcategory 默认 3，否则 1
    - exclude: 文件名列表（不含路径），随机抽取时剔除
    """
    root = _module_root(module)
    folder = root / subcategory if subcategory else root
    if subcategory and not folder.is_dir():
        available = sorted(p.name for p in root.iterdir() if p.is_dir())
        raise FileNotFoundError(
            f"subcategory 不存在: {folder}\n已有子分类: {available or '(无)'}"
        )

    exclude_set = {x.strip() for x in (exclude or []) if x.strip()}

    if explicit:
        out = []
        for name in explicit:
            if name in exclude_set:
                raise ValueError(f"锚点 {name} 同时出现在 --anchor 和 --exclude 里，请二选一")
            p = folder / name
            if not p.exists():
                p = root / name  # 兼容用户传顶层文件名
            if not p.exists():
                raise FileNotFoundError(f"锚点不存在: {name}（已在 {folder} 和 {root} 搜索）")
            out.append(p)
        return out

    candidates = [
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMG_EXT and p.name not in exclude_set
    ]

    # festival 语义过滤（仅当 subcategory 下有 manifest 时生效）
    manifest = _load_manifest(folder) if subcategory else None
    if festival and manifest:
        before = len(candidates)
        candidates = _filter_by_festival(candidates, manifest, festival)
        print(
            f"  · 锚点节日过滤 [{festival}]: {before} → {len(candidates)} 张",
            file=sys.stderr,
        )
        for p in candidates:
            tag = manifest.get("anchors", {}).get(p.name, {}).get("tag", "")
            print(f"      ✓ {p.name}  {tag}", file=sys.stderr)
    elif festival and not manifest:
        print(
            f"  ! 警告：传了 --festival {festival} 但 {folder} 无 manifest.json，跳过过滤",
            file=sys.stderr,
        )
    elif manifest and not festival and subcategory:
        # 有 manifest 但没传 festival → 强制要求传，避免再被节日专属图污染
        sys.exit(
            f"!! {folder} 有 manifest.json 但未传 --festival。"
            f"\n   节日子分类必须指定节日（如 --festival 登月节），否则会被其他节日专属图污染。"
            f"\n   合法节日：{manifest.get('_festivals', [])}"
        )

    if not candidates:
        raise FileNotFoundError(
            f"{folder} 无任何锚点图（festival={festival}, exclude={sorted(exclude_set) or '无'}）"
        )
    k = min(count, len(candidates))
    return random.sample(candidates, k)


def list_subcategories(module: str) -> list[str]:
    root = _module_root(module)
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir())


def build_prompt(module: str, user_prompt: str, theme: str | None) -> str:
    template = STYLE_PREFIX[module]
    user_prompt = user_prompt.strip()
    # 模板模式：含 {prompt} 占位符 → 嵌入用户输入
    if "{prompt}" in template:
        result = template.replace("{prompt}", user_prompt)
        if theme:
            result += f"。主题：{theme}"
        return result
    # 前缀模式（默认）：拼接
    parts = [template, user_prompt]
    if theme:
        parts.append(f"主题：{theme}")
    return "。".join(p for p in parts if p)


def plan_rounds(engines: list[str], total_batch: int) -> list[tuple[str, int]]:
    """把 total_batch 在 engines 间均分，再按 BATCH_PER_CALL 拆成多轮。

    返回列表，每项 = (engine, count_this_round)。
    """
    n = len(engines)
    per = total_batch // n
    extra = total_batch - per * n
    plans: list[tuple[str, int]] = []
    for i, eng in enumerate(engines):
        want = per + (1 if i < extra else 0)
        while want > 0:
            take = min(BATCH_PER_CALL, want)
            plans.append((eng, take))
            want -= take
    return plans


def run_one_call(client: GrfalClient, prompt: str, ref_paths: list[str],
                 engine: str, batch: int, label: str, timeout_s: int = 600,
                 aspect_ratio: str = "1:1") -> tuple[str, list[str]]:
    def _print(desc, p):
        print(f"  [{label}][{p*100:5.1f}%] {desc}", file=sys.stderr, flush=True)
    urls = client.generate(
        prompt=prompt, refs=ref_paths,
        engine=engine, batch=batch,
        timeout_s=timeout_s,
        on_progress=_print,
        aspect_ratio=aspect_ratio,
    )
    return engine, urls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module", choices=["ui", "chest", "item", "dighole"])
    ap.add_argument("--prompt", help="生图提示词（--list-subcategories 时可省略）")
    ap.add_argument("--theme", default="")
    ap.add_argument("--competitor", help="ui 模块必需：竞品截图路径")
    ap.add_argument("--subcategory", help='P2 锚点子分类文件夹名（如 "节日道具自选箱"）；不给则从模块顶层挑')
    ap.add_argument("--festival", help='节日名（如 "登月节"）。subcategory 下有 manifest.json 时按节日语义过滤锚点。带 manifest 的子分类必须传')
    ap.add_argument("--anchor", help="逗号分隔的显式锚点文件名，优先级最高，绕过 festival 过滤。例：151105075.png")
    ap.add_argument("--exclude", help="逗号分隔的排除文件名（随机抽取时剔除）")
    ap.add_argument("--ref-count", type=int, default=0,
                    help="随机挑几张锚点参考图；0=默认 3 张")
    ap.add_argument("--engines", default="gemini",
                    help="逗号分隔的引擎键，默认 gemini（Nano Banana 2）单引擎；需要对比可传 gpt,gemini")
    ap.add_argument("--batch", type=int, default=4, help="总张数（会均分到各引擎），默认 4")
    ap.add_argument("--timeout", type=int, default=600,
                    help="单次 grfal SSE 等待超时秒数；并发多/队列堵时调大（默认 600）")
    ap.add_argument("--no-p2-anchor", action="store_true",
                    help="ui 模块专用：只用竞品截图不加 P2 锚点")
    ap.add_argument("--list-subcategories", action="store_true",
                    help="只列出当前模块下可用的 subcategory 文件夹然后退出")
    ap.add_argument("--aspect-ratio", default="1:1",
                    help="输出图长宽比，例：1:1 / 4:3 / 1:2 / 16:9（dighole 一般跟形状走）")
    args = ap.parse_args()

    if args.list_subcategories:
        subs = list_subcategories(args.module)
        print(f"模块 {args.module} 下的 subcategory：")
        for s in subs:
            print(f"  - {s}")
        if not subs:
            print("  (无)")
        sys.exit(0)

    if not args.prompt:
        sys.exit("--prompt 必填（或用 --list-subcategories 只查看子分类）")

    engines = [e.strip() for e in args.engines.split(",") if e.strip()]
    if not engines:
        sys.exit("--engines 不能为空")

    # 解析 ref_count 自动默认（每次 3 张差异化 ref）
    ref_count = args.ref_count or 3
    explicit_names = [s.strip() for s in args.anchor.split(",") if s.strip()] if args.anchor else None
    exclude_names = [s.strip() for s in args.exclude.split(",") if s.strip()] if args.exclude else None

    # 参考图
    ref_local_paths: list[Path] = []
    if args.module == "ui":
        if not args.competitor:
            sys.exit("ui 模块必须 --competitor <竞品截图路径>")
        comp = Path(args.competitor).expanduser()
        if not comp.exists():
            sys.exit(f"竞品图不存在: {comp}")
        ref_local_paths.append(comp)
        if not args.no_p2_anchor:
            ref_local_paths.extend(pick_anchors(
                "ui", subcategory=args.subcategory,
                explicit=explicit_names, count=ref_count, exclude=exclude_names,
                festival=args.festival,
            ))
    else:
        ref_local_paths.extend(pick_anchors(
            args.module, subcategory=args.subcategory,
            explicit=explicit_names, count=ref_count, exclude=exclude_names,
            festival=args.festival,
        ))

    prompt = build_prompt(args.module, args.prompt, args.theme or None)
    print(f"→ prompt: {prompt}", file=sys.stderr)
    print(f"→ refs:   {[p.name for p in ref_local_paths]}", file=sys.stderr)
    print(f"→ engines={engines}  batch={args.batch}", file=sys.stderr)

    client = GrfalClient()
    ref_paths = [client.upload_image(p) for p in ref_local_paths]
    print(f"→ uploaded {len(ref_paths)} refs", file=sys.stderr)

    plans = plan_rounds(engines, args.batch)
    print(f"→ plan: {plans} ({len(plans)} parallel calls)", file=sys.stderr)

    t0 = time.time()
    results: list[tuple[str, str]] = []  # [(engine, url), ...]
    with cf.ThreadPoolExecutor(max_workers=min(MAX_CONCURRENT, len(plans))) as ex:
        futures = [
            ex.submit(run_one_call, client, prompt, ref_paths, eng, n, f"{eng}-R{i+1}", args.timeout, args.aspect_ratio)
            for i, (eng, n) in enumerate(plans)
        ]
        for fut in cf.as_completed(futures):
            try:
                eng, urls = fut.result()
                for u in urls:
                    results.append((eng, u))
            except Exception as e:
                print(f"  !! 批次失败: {e}", file=sys.stderr)
    dt = time.time() - t0
    print(f"→ 完成 {len(results)}/{args.batch} 张，用时 {dt:.0f}s", file=sys.stderr)
    if not results:
        sys.exit("全部批次失败，终止")

    # 下载（带 engine 标签）
    # ts 含 PID 后缀，避免多个并行进程同秒启动时文件名冲突
    import os as _os
    ts = time.strftime("%Y%m%d_%H%M%S") + f"_{_os.getpid()}"
    local_dir = OUTPUT_ROOT / "images" / args.module
    local_dir.mkdir(parents=True, exist_ok=True)
    items: list[dict] = []  # [{"path": relpath, "engine": eng}, ...]
    for i, (eng, url) in enumerate(results):
        dest = local_dir / f"{ts}_{eng}_{i:02d}.png"
        client.download(url, dest)
        rel = str(dest.relative_to(OUTPUT_ROOT))
        items.append({"path": rel, "engine": eng})
        print(f"  ↓ [{eng}] {dest.name}", file=sys.stderr)

    append_batch(
        OUTPUT_ROOT / "gallery.html",
        module=args.module,
        timestamp=ts,
        prompt=prompt,
        engines=engines,
        ref_paths=[str(p) for p in ref_local_paths],
        items=items,
        duration_s=dt,
    )
    print(f"\n✅ gallery: {OUTPUT_ROOT / 'gallery.html'}")
    print(f"✅ images:  {local_dir}/")
    print(json.dumps({
        "module": args.module,
        "gallery": str(OUTPUT_ROOT / "gallery.html"),
        "images": [(OUTPUT_ROOT / it["path"]).as_posix() for it in items],
        "by_engine": {
            eng: sum(1 for it in items if it["engine"] == eng) for eng in engines
        },
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
