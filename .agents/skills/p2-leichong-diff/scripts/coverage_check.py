#!/usr/bin/env python3
"""P2 节日累充覆盖核查工具。

输入：节日 tab 名 + 该节日全部活动 2112 ID 清单（带 type/name）
输出：每个活动反向追溯到的 2011 IAP 引用，与累充源表 C 列做差 → 缺失清单。

用法：
  python3 coverage_check.py all      --festival-tab "26拓荒节" --inputs inputs.yaml --out report.md
  python3 coverage_check.py fetch    --festival-tab "26拓荒节"
  python3 coverage_check.py trace    --inputs inputs.yaml
  python3 coverage_check.py report   --inputs inputs.yaml --out report.md
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: pip install pyyaml")

# === Sheet 配置 ===
LEICHONG_SRC_ID = "1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E"

SHEETS = {
    "2112": {"id": "1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E", "tab": "activity_config_qa"},
    "2121": {"id": "1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc", "tab": "activity_special_QA"},
    "2122": {"id": "1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M", "tab": "activity_rank_rule（QA）"},
    "2115": {"id": "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY", "tab": "activity_task_QA"},
    "2135": {"id": "1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc", "tab": "activity_event_pkg"},
    "2013": {"id": "1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY", "tab": "iap_template_QA"},
    "2011": {"id": "1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc", "tab": "iap_config_QA"},
}

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_TTL_SECONDS = 24 * 3600

P_IAP = re.compile(r"\b(2011\d{6})\b")
P_2135 = re.compile(r"\b(2135\d{4})\b")
P_2013 = re.compile(r"\b(2013\d{5,6})\b")
P_2121 = re.compile(r"\b(2121\d{4,5})\b")
P_2115 = re.compile(r"\b(211[5-8]\d{6})\b")


def cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    safe = key.replace("/", "_").replace("!", "_")
    return CACHE_DIR / f"{safe}.json"


def fetch_sheet(sheet_id: str, tab: str, force: bool = False) -> list:
    key = f"{sheet_id}__{tab}"
    p = cache_path(key)
    if not force and p.exists() and time.time() - p.stat().st_mtime < CACHE_TTL_SECONDS:
        return json.loads(p.read_text())["values"]
    print(f"  [gws] reading {tab} from {sheet_id[:12]}...", file=sys.stderr)
    rng = f"{tab}!A1:BZ"
    cmd = ["gws", "sheets", "+read", "--spreadsheet", sheet_id, "--range", rng, "--format", "json"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    p.write_text(json.dumps(data, ensure_ascii=False))
    return data.get("values", [])


def fetch_all(festival_tab: str, force: bool = False) -> dict:
    cache = {}
    for key, cfg in SHEETS.items():
        cache[key] = fetch_sheet(cfg["id"], cfg["tab"], force)
    cache["leichong"] = fetch_sheet(LEICHONG_SRC_ID, festival_tab, force)
    return cache


def index_by_col(rows, col, skip_header=True):
    out = {}
    start = 1 if skip_header else 0
    for r in rows[start:]:
        if r and len(r) > col and r[col]:
            k = r[col].strip()
            if k:
                out[k] = r
    return out


def parse_components(s):
    if not s:
        return []
    try:
        arr = json.loads(s)
    except Exception:
        return []
    out = []
    for el in arr:
        if isinstance(el, dict):
            out.append({"typ": el.get("typ") or el.get("type"),
                        "id": el.get("id"),
                        "args": el.get("args") or {}})
    return out


def parse_leichong_tab(rows):
    """累充源表 1 个节日 tab：
    - row 11 (index 10) 是参考池：A 列长串逗号分隔 IDs
    - row 14+ (index 13+) 是数据行：A 列 2013xxx / C 列 2011xxx

    返回 (set_A, set_pool)。
    """
    set_A = set()
    set_pool = set()
    for r in rows[13:]:
        if not r or len(r) < 3 or not r[0]:
            continue
        if not re.match(r"^2013\d+$", r[0].strip()):
            continue
        if r[2] and re.match(r"^201\d{6,}$", r[2].strip()):
            set_A.add(r[2].strip())
    # 参考池：row 11 (index 10) 列内 ID 散布
    if len(rows) > 10 and rows[10]:
        text = "|".join(rows[10])
        for m in re.findall(r"\d{9,}", text):
            set_pool.add(m)
    return set_A, set_pool


def trace_activity(act, idx_2112, idx_2121, idx_2122, idx_2115, idx_2135, idx_2013, valid_iap):
    act_id = act["id"]
    if act_id not in idx_2112:
        return {"id": act_id, "name": act.get("name", ""), "type": act.get("type", ""),
                "iaps": [], "trace_log": ["ERROR: act_id not in 2112"], "status": "NOT_IN_2112"}

    comps = parse_components(idx_2112[act_id][8])
    iap_set, log, visited = set(), [], set()

    def collect(text):
        new = {m for m in P_IAP.findall(text) if m in valid_iap}
        return new

    def visit_2121(rid, depth=0):
        if rid in visited or depth > 4:
            return
        visited.add(rid)
        if rid not in idx_2121:
            log.append(f"  2121 {rid} NOT FOUND")
            return
        r = idx_2121[rid]
        text = "|".join(c or "" for c in r)
        new = collect(text)
        if new:
            iap_set.update(new)
            log.append(f"  2121 {rid}({r[2] if len(r) > 2 else '?'}): +{len(new)} IAP")
        if len(r) > 2 and r[2] == "task_group":
            try:
                tasks = json.loads(r[10]) if len(r) > 10 and r[10] else []
                if isinstance(tasks, list):
                    for tid in tasks:
                        visit_2115(str(tid), depth + 1)
            except Exception:
                pass
        for cell in r:
            cell = cell or ""
            for m in P_2135.findall(cell):
                visit_2135(m, depth + 1)
            for m in P_2013.findall(cell):
                visit_2013(m, depth + 1)
            for m in P_2121.findall(cell):
                if m != rid:
                    visit_2121(m, depth + 1)
            for m in P_2115.findall(cell):
                visit_2115(m, depth + 1)

    def visit_2122(rid, depth=0):
        if rid in visited or depth > 4:
            return
        visited.add(rid)
        if rid not in idx_2122:
            log.append(f"  2122 {rid} NOT FOUND")
            return
        r = idx_2122[rid]
        text = "|".join(c or "" for c in r)
        new = collect(text)
        if new:
            iap_set.update(new)
            log.append(f"  2122 {rid}: +{len(new)} IAP")
        for cell in r:
            cell = cell or ""
            for m in P_2135.findall(cell):
                visit_2135(m, depth + 1)
            for m in P_2115.findall(cell):
                visit_2115(m, depth + 1)
            for m in P_2121.findall(cell):
                visit_2121(m, depth + 1)
            for m in P_2013.findall(cell):
                visit_2013(m, depth + 1)

    def visit_2115(rid, depth=0):
        if rid in visited or depth > 4:
            return
        visited.add(rid)
        if rid not in idx_2115:
            log.append(f"  2115 {rid} NOT FOUND")
            return
        r = idx_2115[rid]
        text = "|".join(c or "" for c in r)
        new = collect(text)
        if new:
            iap_set.update(new)
            log.append(f"  2115 {rid}: +{len(new)} IAP")
        for cell in r:
            cell = cell or ""
            for m in P_2135.findall(cell):
                visit_2135(m, depth + 1)
            for m in P_2013.findall(cell):
                visit_2013(m, depth + 1)
            for m in P_2121.findall(cell):
                visit_2121(m, depth + 1)

    def visit_2135(rid, depth=0):
        if rid in visited or depth > 4:
            return
        visited.add(rid)
        if rid not in idx_2135:
            log.append(f"  2135 {rid} NOT FOUND")
            return
        r = idx_2135[rid]
        iap = r[2].strip() if len(r) > 2 and r[2] else "0"
        if iap and iap != "0" and iap in valid_iap:
            iap_set.add(iap)
            log.append(f"  2135 {rid}: iap={iap}")

    def visit_2013(rid, depth=0):
        if rid in visited or depth > 4:
            return
        visited.add(rid)
        if rid not in idx_2013:
            log.append(f"  2013 {rid} NOT FOUND")
            return
        r = idx_2013[rid]
        cfg = r[2].strip() if len(r) > 2 and r[2] else "0"
        if cfg and cfg in valid_iap:
            iap_set.add(cfg)
            log.append(f"  2013 {rid}: cfg={cfg}")

    for c in comps:
        cid = str(c["id"]) if c["id"] is not None else ""
        if not cid:
            continue
        if cid in valid_iap:
            iap_set.add(cid)
            log.append(f'comp {c["typ"]}: direct IAP {cid}')
            continue
        if cid.startswith("2011") and len(cid) == 10:
            continue
        if cid.startswith("2121"):
            visit_2121(cid)
        elif cid.startswith("2122"):
            visit_2122(cid)
        elif cid.startswith("2135"):
            visit_2135(cid)
        elif cid.startswith("2013"):
            visit_2013(cid)
        elif cid.startswith("211") and len(cid) == 9:
            visit_2115(cid)
        elif cid.startswith("212120"):
            visit_2121(cid)

    return {"id": act_id, "name": act.get("name", ""), "type": act.get("type", ""),
            "iaps": sorted(iap_set), "trace_log": log, "comp_count": len(comps),
            "status": "OK"}


def cmd_fetch(args):
    fetch_all(args.festival_tab, force=args.no_cache)
    print(f"Fetched 8 sheets to {CACHE_DIR}/")


def cmd_trace(args):
    inputs = yaml.safe_load(open(args.inputs))
    festival_tab = inputs["festival_tab"]
    activities = inputs["activities"]
    cache = fetch_all(festival_tab, force=args.no_cache)

    idx = {
        "2112": index_by_col(cache["2112"], 0),
        "2121": index_by_col(cache["2121"], 0),
        "2122": index_by_col(cache["2122"], 1),
        "2115": index_by_col(cache["2115"], 1),
        "2135": index_by_col(cache["2135"], 0),
        "2013": index_by_col(cache["2013"], 0),
    }
    valid_iap = {r[0].strip() for r in cache["2011"][1:] if r and r[0]}
    set_A, set_pool = parse_leichong_tab(cache["leichong"])

    print(f"set_A (源表 C 列 unique 2011): {len(set_A)}", file=sys.stderr)
    print(f"set_pool (源表 row 11 参考池): {len(set_pool)}", file=sys.stderr)
    print(f"valid 2011 IAPs in iap_config_QA: {len(valid_iap)}", file=sys.stderr)

    results = []
    for act in activities:
        r = trace_activity(act, idx["2112"], idx["2121"], idx["2122"],
                           idx["2115"], idx["2135"], idx["2013"], valid_iap)
        missing = sorted(set(r["iaps"]) - set_A)
        in_pool = [x for x in missing if x in set_pool]
        not_in_pool = [x for x in missing if x not in set_pool]
        r["missing"] = missing
        r["missing_in_pool"] = in_pool
        r["missing_not_in_pool"] = not_in_pool
        r["in_set_A"] = sorted(set(r["iaps"]) & set_A)
        results.append(r)

    out = {"festival_tab": festival_tab,
           "set_A_size": len(set_A),
           "set_pool_size": len(set_pool),
           "results": results}
    out_path = Path(args.out_json or (CACHE_DIR / "trace_result.json"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote {out_path}")


def cmd_report(args):
    in_path = Path(args.in_json or (CACHE_DIR / "trace_result.json"))
    if not in_path.exists():
        sys.exit(f"ERROR: trace result not found at {in_path}. Run `trace` first.")
    data = json.loads(in_path.read_text())
    festival_tab = data["festival_tab"]
    results = data["results"]
    set_A_size = data["set_A_size"]
    set_pool_size = data["set_pool_size"]

    union_missing = set()
    union_in_pool = set()
    union_not_in_pool = set()
    for r in results:
        union_missing.update(r["missing"])
        union_in_pool.update(r["missing_in_pool"])
        union_not_in_pool.update(r["missing_not_in_pool"])

    lines = []
    lines.append(f"# {festival_tab} 累充覆盖核查报告\n")
    lines.append(f"- 累充源表 C 列基线 (set_A): **{set_A_size}** IDs")
    lines.append(f"- 头部参考池 (row 11): **{set_pool_size}** IDs")
    lines.append(f"- 本次扫描活动数: **{len(results)}**")
    lines.append(f"- **总缺失 (去重)**: **{len(union_missing)}** IDs")
    lines.append(f"  - A. 参考池已知 (待整理): {len(union_in_pool)}")
    lines.append(f"  - B. 参考池盲点 (高优先级): {len(union_not_in_pool)}\n")

    lines.append("## 全局缺失分类\n")
    lines.append(f"### A. 已在参考池 row 11 (PM 知道，待拷到 C 列) — {len(union_in_pool)} 个\n")
    for x in sorted(union_in_pool):
        lines.append(f"- `{x}`")
    if not union_in_pool:
        lines.append("- (无)")

    lines.append(f"\n### B. 参考池也没有 (真盲点，需 PM 重新评估) — {len(union_not_in_pool)} 个\n")
    for x in sorted(union_not_in_pool):
        lines.append(f"- `{x}`")
    if not union_not_in_pool:
        lines.append("- (无)")

    lines.append("\n## 活动汇总表\n")
    lines.append("| 活动 ID | 类型 | IAP 引用 | 已在 set_A | 缺失 (A池) | 缺失 (B盲点) |")
    lines.append("|---|---|---|---|---|---|")
    for r in results:
        lines.append(f"| {r['id']} | {r['type']} | {len(r['iaps'])} | "
                     f"{len(r['in_set_A'])} | {len(r['missing_in_pool'])} | "
                     f"{len(r['missing_not_in_pool'])} |")

    lines.append("\n## 按活动分组的缺失明细\n")
    any_missing = False
    for r in results:
        if not r["missing"]:
            continue
        any_missing = True
        lines.append(f"### {r['id']} ({r['type']}) — {r['name']}")
        lines.append(f"- 引用 IAP 总数: {len(r['iaps'])}")
        if r["missing_in_pool"]:
            lines.append(f"- A. 参考池已知 {len(r['missing_in_pool'])} 个:")
            for x in r["missing_in_pool"]:
                lines.append(f"  - `{x}`")
        if r["missing_not_in_pool"]:
            lines.append(f"- B. 参考池盲点 {len(r['missing_not_in_pool'])} 个:")
            for x in r["missing_not_in_pool"]:
                lines.append(f"  - `{x}`")
        lines.append("")
    if not any_missing:
        lines.append("- (所有活动 IAP 引用都已在累充表中)\n")

    zero = [r for r in results if not r["iaps"]]
    if zero:
        lines.append("## 0 IAP 引用的活动 (一般正常，确认非漏配)\n")
        for r in zero:
            lines.append(f"- `{r['id']}` ({r['type']}) {r['name']}")
        lines.append("")

    bad = [r for r in results if r["status"] != "OK"]
    if bad:
        lines.append("## 解析失败 (需人工检查)\n")
        for r in bad:
            lines.append(f"- `{r['id']}`: {r['status']}")

    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.out}")


def cmd_all(args):
    cmd_trace(args)
    cmd_report(args)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch")
    p_fetch.add_argument("--festival-tab", required=True)
    p_fetch.add_argument("--no-cache", action="store_true")
    p_fetch.set_defaults(func=cmd_fetch)

    p_trace = sub.add_parser("trace")
    p_trace.add_argument("--inputs", required=True)
    p_trace.add_argument("--out-json")
    p_trace.add_argument("--no-cache", action="store_true")
    p_trace.set_defaults(func=cmd_trace)

    p_report = sub.add_parser("report")
    p_report.add_argument("--in-json")
    p_report.add_argument("--out", required=True)
    p_report.set_defaults(func=cmd_report)

    p_all = sub.add_parser("all")
    p_all.add_argument("--festival-tab", help="(unused, taken from inputs)")
    p_all.add_argument("--inputs", required=True)
    p_all.add_argument("--out", required=True)
    p_all.add_argument("--out-json")
    p_all.add_argument("--in-json")
    p_all.add_argument("--no-cache", action="store_true")
    p_all.set_defaults(func=cmd_all)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
