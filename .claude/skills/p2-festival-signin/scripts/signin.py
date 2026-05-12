#!/usr/bin/env python3
"""
P2 节日签到端到端配置脚本（2112 + 2111 + 2115）

子命令：
  learn                  Step0 自主学习：拉最新 2026 签到模板 + 2115 task pool + 2111 占位
  plan   <args>          预演：dry-run 输出三表写入计划，不动表
  apply  <args>          真写：含写前 ID-row 校对 + 写后 ID 回读
  verify --id-2112 X     校验已配签到三表完整性

依赖：gws CLI（gws-workspace skill），Python 3.9+

设计不变量（写到代码里强制执行）：
  - priority 永远 49991
  - base_activity_id 永远 21121590
  - components = 21 个通用 task (211552230-211552250) + login_complement(21215260)
  - 节日专属字段只有 4 个：constant / ui_template(K) / show_hud(R) / banner_url(N)
  - 2115 task pool 由 SIGNIN_TASK_IDS 锁死；BP 进度道具自动按"reward 中 item id 不在通用池"识别
  - 所有写入前用 ID 精确校对物理行；写入后用 ID 回读
"""
import argparse
import json
import re
import subprocess
import sys

# ===== Spreadsheet 常量（master_kb 来源，2026-04 校对过） =====
SS_2112, TAB_2112, SHEETID_2112 = "1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E", "activity_config_qa", 1308621827
SS_2111, TAB_2111, SHEETID_2111 = "1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g", "activity_calendar_QA", 1688241274
SS_2115, TAB_2115 = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY", "activity_task_QA"

# ===== 签到模板不变量 =====
SIGNIN_TASK_IDS = list(range(211552230, 211552251))  # 21 通用 task
LOGIN_COMPLEMENT_ID = 21215260
SIGNIN_BASE_ACTIVITY = 21121590
SIGNIN_PRIORITY = 49991
SIGNIN_DEFAULT_BANNER = "assets/operation/P2dlcimg/activityImg/EventBanner_BG_408.png"
SIGNIN_MINI_BANNER = "assets/operation/P2dlcimg/activityImg/EventBanner_Timeline_145.png"

# 21 个通用签到 task 的"通用道具池"——出现在这里说明跟节日无关
COMMON_REWARD_ITEMS = {
    11112498,  # 漫游骰子-节日进度活动（通用游戏道具）
    11116604,  # 收藏品-橙色升星
    11116258,  # 碎片-艾玛
    11117068,  # 军备零件箱
    19345004,  # material
    11114330,  # 高级资源自选宝箱
    11116402,  # 高级奖池抽奖券
}

# 2111 占位边界：所有节日 calendar 必须写在它之前
PLACEHOLDER_2111_ID = 21116001


# ===== gws helpers =====
def _gws(*args):
    r = subprocess.run(["gws", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gws failed: {r.stderr.strip()}")
    return json.loads(r.stdout)


def values_get(ss, rng):
    return _gws("sheets", "spreadsheets", "values", "get",
                "--params", json.dumps({"spreadsheetId": ss, "range": rng}))


def values_batch_update(ss, data):
    body = {"valueInputOption": "RAW", "data": data}
    return _gws("sheets", "spreadsheets", "values", "batchUpdate",
                "--params", json.dumps({"spreadsheetId": ss}),
                "--json", json.dumps(body, ensure_ascii=False))


def insert_row_before(ss, sheet_id, row_1based):
    body = {"requests": [{
        "insertDimension": {
            "range": {"sheetId": sheet_id, "dimension": "ROWS",
                      "startIndex": row_1based - 1, "endIndex": row_1based},
            "inheritFromBefore": True
        }
    }]}
    return _gws("sheets", "spreadsheets", "batchUpdate",
                "--params", json.dumps({"spreadsheetId": ss}),
                "--json", json.dumps(body))


def find_rows_by_id(ss, tab, target, col="A"):
    """Return ALL 1-based row numbers where col == target. List can be empty,
    one element (normal), or multiple (ID collision — caller must handle)."""
    d = values_get(ss, f"{tab}!{col}:{col}")
    return [i + 1 for i, r in enumerate(d.get("values", []))
            if r and str(r[0]) == str(target)]


def find_row_by_id(ss, tab, target, col="A"):
    """Return the unique row holding target, raise on duplicate, None if absent."""
    rows = find_rows_by_id(ss, tab, target, col)
    if len(rows) > 1:
        raise RuntimeError(
            f"ID collision in {tab}!{col}: {target} appears at rows {rows}. "
            f"Refuse to operate — fix duplicates first."
        )
    return rows[0] if rows else None


def assert_id_at_row(ss, tab, row, expected, col="A"):
    rng = f"{tab}!{col}{row}:{col}{row}"
    d = values_get(ss, rng)
    actual = d.get("values", [[None]])[0][0] if d.get("values") else None
    if str(actual) != str(expected):
        raise AssertionError(f"ID mismatch at {rng}: expected {expected}, got {actual}")


# ===== 学习 =====
def learn():
    """读三表当前状态，输出可被 plan 复用的 dict。"""
    out = {}

    # 2112 找全部 2026 签到（命名含 "签到-2026"）
    d = values_get(SS_2112, f"{TAB_2112}!A:B")
    signins = []
    for i, r in enumerate(d.get("values", [])):
        if len(r) > 1 and "签到" in r[1] and "2026" in r[1]:
            signins.append({"row": i + 1, "id": r[0], "name": r[1]})
    out["2026_signins"] = signins
    if not signins:
        raise RuntimeError("no 2026 signin found in 2112; can't build template")

    # 取最新（最大 ID）做 25 列模板
    latest = sorted(signins, key=lambda x: int(x["id"]))[-1]
    d = values_get(SS_2112, f"{TAB_2112}!A{latest['row']}:Y{latest['row']}")
    out["template_2112_row"] = d["values"][0]
    out["template_source"] = latest

    # 2115 task pool reward 解析
    d = values_get(SS_2115, f"{TAB_2115}!B:G")
    task_info = {}
    for i, r in enumerate(d.get("values", [])):
        if len(r) >= 1 and str(r[0]).isdigit() and int(r[0]) in SIGNIN_TASK_IDS:
            task_info[int(r[0])] = {
                "row": i + 1,
                "reward": r[5] if len(r) > 5 else "",
            }
    out["2115_task_info"] = task_info
    if len(task_info) != len(SIGNIN_TASK_IDS):
        raise RuntimeError(
            f"2115 task pool incomplete: {len(task_info)}/{len(SIGNIN_TASK_IDS)} "
            f"missing={set(SIGNIN_TASK_IDS) - set(task_info)}"
        )

    # 自动识别 BP 进度道具行（reward 中 item id 不在通用池）
    bp_rows = []
    for tid, info in task_info.items():
        m = re.search(r'"id":(\d+)', info["reward"])
        if m and int(m.group(1)) not in COMMON_REWARD_ITEMS:
            bp_rows.append({"task_id": tid, "row": info["row"], "current_item": int(m.group(1))})
    out["2115_bp_rows"] = sorted(bp_rows, key=lambda x: x["task_id"])

    # 2111 占位 + 当年最后节日
    d = values_get(SS_2111, f"{TAB_2111}!A:B")
    placeholder_row = None
    last_id = None
    for i, r in enumerate(d.get("values", [])):
        if r and str(r[0]) == str(PLACEHOLDER_2111_ID):
            placeholder_row = i + 1
            prev = d["values"][i - 1] if i > 0 else None
            if prev:
                last_id = prev[0]
            break
    if placeholder_row is None:
        raise RuntimeError(f"2111 placeholder {PLACEHOLDER_2111_ID} not found")
    out["2111_placeholder_row"] = placeholder_row
    out["2111_last_festival_id"] = last_id
    out["2111_next_id"] = str(int(last_id) + 1) if last_id else None

    return out


# ===== 计划 =====
def build_components_json(task_ids):
    items = [{"typ": "task", "id": x} for x in task_ids] + \
            [{"typ": "login_complement", "id": LOGIN_COMPLEMENT_ID}]
    return json.dumps(items, ensure_ascii=False, separators=(',', ':'))


def build_2112_row(template, args, components):
    row = list(template)
    if len(row) != 25:
        raise RuntimeError(f"2112 template has {len(row)} cols, expected 25")
    row[0] = str(args.id_2112)
    row[1] = f"{args.cn}签到-2026"
    row[2] = f"event_{args.festival}_login_2026"
    row[8] = components
    row[10] = str(args.ui_template)
    row[13] = args.banner_url or SIGNIN_DEFAULT_BANNER
    row[17] = str(args.show_hud)
    return row


def build_2111_row(args, new_id):
    return [
        str(new_id),
        str(args.id_2112),
        f"{args.cn}签到-2026",
        '{"typ":"schema","id":[1,2,3,4,5,6]}',
        '{"typ":"time","is_ark":1}',
        "{}", "{}", "0", "0",
    ]


def compute_plan(args, learned=None):
    learned = learned or learn()

    if args.signin_mode == "A":
        raise NotImplementedError(
            "Mode A (新建拓荒节专属 21 task) 未实现。"
            "若要用 A，先在 2115 手动复制 211552230-211552250 到下一段空号，"
            "再用 --task-pool 传入新 task id 列表。当前默认 B。"
        )
    task_ids = SIGNIN_TASK_IDS
    components = build_components_json(task_ids)

    # 2112 ID 未占用 + 计算插入位置（数值前驱+1）
    if find_row_by_id(SS_2112, TAB_2112, args.id_2112) is not None:
        raise RuntimeError(f"2112 id {args.id_2112} already occupied")
    d = values_get(SS_2112, f"{TAB_2112}!A:A")
    target = int(args.id_2112)
    insert_row_2112 = None
    for i, r in enumerate(d.get("values", [])):
        if not r:
            continue
        try:
            n = int(r[0])
        except ValueError:
            continue
        if n > target:
            insert_row_2112 = i + 1
            break
    if insert_row_2112 is None:
        raise RuntimeError("could not find insertion row in 2112 (id larger than all existing?)")

    # 2111 新 ID 未占用 + 插入位置 = 占位符行
    new_2111_id = learned["2111_next_id"]
    if find_row_by_id(SS_2111, TAB_2111, new_2111_id) is not None:
        raise RuntimeError(f"2111 id {new_2111_id} already occupied")

    plan = {
        "mode": args.signin_mode,
        "2112": {
            "insert_before_row": insert_row_2112,
            "id": str(args.id_2112),
            "row": build_2112_row(learned["template_2112_row"], args, components),
            "template_source": learned["template_source"],
        },
        "2111": {
            "insert_before_row": learned["2111_placeholder_row"],
            "new_id": new_2111_id,
            "activity_id": str(args.id_2112),
            "row": build_2111_row(args, new_2111_id),
        },
        "2115": [],
    }

    new_reward_tpl = ('[{{"asset":{{"typ":"item","id":{iid},"val":15}},'
                      '"setting":{{"serial_number":5,"ishighlight":false}}}}]')
    for entry in learned["2115_bp_rows"]:
        plan["2115"].append({
            "task_id": entry["task_id"],
            "row": entry["row"],
            "current_item": entry["current_item"],
            "new_item": int(args.bp_item),
            "range": f"{TAB_2115}!G{entry['row']}",
            "value": new_reward_tpl.format(iid=int(args.bp_item)),
        })

    return plan


def cmd_learn(_args):
    print(json.dumps(learn(), ensure_ascii=False, indent=2))


def cmd_plan(args):
    print(json.dumps(compute_plan(args), ensure_ascii=False, indent=2))


def cmd_apply(args):
    plan = compute_plan(args)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    print("\n--- applying ---")

    # 2115：先 ID 校对再写
    for c in plan["2115"]:
        assert_id_at_row(SS_2115, TAB_2115, c["row"], c["task_id"], col="B")
    if plan["2115"]:
        values_batch_update(SS_2115, [
            {"range": c["range"], "values": [[c["value"]]]} for c in plan["2115"]
        ])
        for c in plan["2115"]:
            d = values_get(SS_2115, c["range"])
            v = d["values"][0][0]
            if str(c["new_item"]) not in v or str(c["current_item"]) in v:
                raise AssertionError(f"2115 verify fail at {c['range']}: {v}")
        print(f"[OK] 2115: {len(plan['2115'])} cells updated -> item {args.bp_item}")

    # 2112 insert + write + verify
    p = plan["2112"]
    insert_row_before(SS_2112, SHEETID_2112, p["insert_before_row"])
    rng = f"{TAB_2112}!A{p['insert_before_row']}:Y{p['insert_before_row']}"
    values_batch_update(SS_2112, [{"range": rng, "values": [p["row"]]}])
    assert_id_at_row(SS_2112, TAB_2112, p["insert_before_row"], p["id"])
    print(f"[OK] 2112: id {p['id']} written at row {p['insert_before_row']}")

    # 2111 insert + write + verify
    p = plan["2111"]
    insert_row_before(SS_2111, SHEETID_2111, p["insert_before_row"])
    rng = f"{TAB_2111}!A{p['insert_before_row']}:I{p['insert_before_row']}"
    values_batch_update(SS_2111, [{"range": rng, "values": [p["row"]]}])
    assert_id_at_row(SS_2111, TAB_2111, p["insert_before_row"], p["new_id"])
    print(f"[OK] 2111: id {p['new_id']} -> {p['activity_id']} at row {p['insert_before_row']}")

    print("\n=== ALL DONE ===")


def cmd_verify(args):
    issues = []

    # 2112 — handle duplicates explicitly so verify can surface ID collisions
    rows = find_rows_by_id(SS_2112, TAB_2112, args.id_2112)
    if not rows:
        issues.append(f"2112 id {args.id_2112} NOT FOUND")
        row = None
    elif len(rows) > 1:
        # find the row that looks like a signin (name contains "签到")
        signin_row = None
        for r in rows:
            d = values_get(SS_2112, f"{TAB_2112}!B{r}:B{r}")
            name = d.get("values", [[""]])[0][0] if d.get("values") else ""
            if "签到" in name:
                signin_row = r
                break
        issues.append(f"2112 id {args.id_2112} COLLISION at rows {rows}; verifying signin row {signin_row}")
        row = signin_row
    else:
        row = rows[0]
    if row:
        d = values_get(SS_2112, f"{TAB_2112}!A{row}:Y{row}")
        v = d["values"][0]
        if v[4] != str(SIGNIN_PRIORITY):
            issues.append(f"2112 priority {v[4]} != {SIGNIN_PRIORITY}")
        if v[5] != str(SIGNIN_BASE_ACTIVITY):
            issues.append(f"2112 base_activity {v[5]} != {SIGNIN_BASE_ACTIVITY}")
        if str(LOGIN_COMPLEMENT_ID) not in v[8]:
            issues.append("2112 components missing login_complement")
        for tid in SIGNIN_TASK_IDS:
            if f'"id":{tid}' not in v[8]:
                issues.append(f"2112 components missing task {tid}")
        print(f"[2112] row {row}: id={v[0]} | name={v[1]} | "
              f"constant={v[2]} | ui_template={v[10]} | show_hud={v[17]}")

    # 2111
    d = values_get(SS_2111, f"{TAB_2111}!A:C")
    found_2111 = False
    for i, r in enumerate(d.get("values", [])):
        if len(r) > 1 and r[1] == str(args.id_2112):
            found_2111 = True
            print(f"[2111] row {i+1}: cal_id={r[0]} -> activity_id={r[1]} "
                  f"({r[2] if len(r) > 2 else ''})")
            # 校核位置在占位符之前
            ph_row = find_row_by_id(SS_2111, TAB_2111, PLACEHOLDER_2111_ID)
            if ph_row is None or i + 1 >= ph_row:
                issues.append(f"2111 row {i+1} not before placeholder row {ph_row}")
            break
    if not found_2111:
        issues.append(f"2111 has no calendar row referencing 2112 id {args.id_2112}")

    # 2115 spot check
    d = values_get(SS_2115, f"{TAB_2115}!B:G")
    found_count = 0
    for r in d.get("values", []):
        if len(r) >= 1 and str(r[0]).isdigit() and int(r[0]) in SIGNIN_TASK_IDS:
            found_count += 1
    print(f"[2115] {found_count}/{len(SIGNIN_TASK_IDS)} signin tasks present")
    if found_count != len(SIGNIN_TASK_IDS):
        issues.append(f"2115 task pool incomplete ({found_count}/{len(SIGNIN_TASK_IDS)})")

    if issues:
        print("\n!! ISSUES !!")
        for x in issues:
            print(f"  - {x}")
        sys.exit(1)
    print("\n[OK] all verified")


# ===== CLI =====
def _add_common(p):
    p.add_argument("--festival", required=True, help="english slug, e.g. labor / easter / spring / tech")
    p.add_argument("--cn", required=True, help="中文节日名, e.g. 拓荒节")
    p.add_argument("--id-2112", dest="id_2112", required=True, type=int)
    p.add_argument("--ui-template", dest="ui_template", required=True, type=int)
    p.add_argument("--show-hud", dest="show_hud", required=True, type=int)
    p.add_argument("--bp-item", dest="bp_item", required=True, type=int,
                   help="节日 BP 进度道具 1111 id, e.g. 11112150 纪念钻头-拓荒节通用BP活动道具")
    p.add_argument("--banner-url", dest="banner_url", default=None,
                   help=f"default: {SIGNIN_DEFAULT_BANNER}")
    p.add_argument("--signin-mode", dest="signin_mode", default="B", choices=["A", "B"],
                   help="A=新建专属 21 task（暂未实现）/ B=直改通用 task（默认）")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("learn")
    _add_common(sub.add_parser("plan"))
    _add_common(sub.add_parser("apply"))
    pv = sub.add_parser("verify")
    pv.add_argument("--id-2112", dest="id_2112", required=True, type=int)

    args = p.parse_args()
    {"learn": cmd_learn, "plan": cmd_plan, "apply": cmd_apply, "verify": cmd_verify}[args.cmd](args)


if __name__ == "__main__":
    main()
