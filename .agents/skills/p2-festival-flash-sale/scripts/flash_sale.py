#!/usr/bin/env python3
"""
P2 节日限时抢购端到端配置脚本（2112 + 2111 + 2013）

子命令：
  learn                  Step0 自主学习：拉 21127716/717 模板 + 2111 占位 + 2013 当前奖励道具扫描
  plan   <args>          预演：dry-run 输出三表写入计划，不动表
  apply  <args>          真写：含写前 ID-row 校对 + 写后 ID 回读
  verify <args>          校验已配限抢三表完整性 + 红英雄 0 容忍扫描

依赖：gws CLI（gws-workspace skill），Python 3.9+

设计不变量（写到代码里强制）：
  - priority 永远 59999
  - base_activity_id 永远 21127385（情人节遗留 base，全节日共用）
  - components 全节日复用 21127716/717 模板（packages 21353311-326 + tasks 211572527-31 + flash_sale_*  21217182-89 + retake 21371262）
  - 节日专属字段只有 4 个：constant / comment / show_hud / 2013 节日道具
  - 2111 calendar 必须紧贴 21116001 占位符之前，禁用 21117XXX 段
  - 红色英雄 3 个 ID（11116272/11116390/11116391）verify 阶段 0 容忍
"""
import argparse
import json
import re
import subprocess
import sys

# ===== Spreadsheet 常量 =====
SS_2112, TAB_2112, SHEETID_2112 = "1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E", "activity_config_qa", 1308621827
SS_2111, TAB_2111, SHEETID_2111 = "1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g", "activity_calendar_QA", 1688241274
SS_2013, TAB_2013, SHEETID_2013 = "1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY", "iap_template_QA", 155071134

# ===== 限抢模板不变量 =====
FLASH_TEMPLATE_S6_ID = "21127716"   # 科技节 S6 — 25 列模板源
FLASH_TEMPLATE_S35_ID = "21127717"  # 科技节 S3-5
FLASH_BASE_ACTIVITY = "21127385"
FLASH_PRIORITY = "59999"
FLASH_DEFAULT_BANNER = "assets/operation/P2dlcimg/activityImg/EventBanner_BG_425.png"

# 14 个共用 2013 模板 ID
FLASH_2013_IDS = [str(x) for x in range(2013500354, 2013500368)]

# 4 个含节日自选宝箱的 2013 ID（用 111110XXX 占的槽位）
FLASH_2013_FESTIVAL_BOX_SLOTS = [
    "2013500355",  # S6-19.99 A
    "2013500359",  # S6-99.99 A
    "2013500362",  # S3-5-19.99 A
    "2013500366",  # S3-5-99.99 A
]

# 红色英雄三件套（永远必须移除）
RED_HERO_ITEMS = {11116272, 11116390, 11116391}

# 2111 占位
PLACEHOLDER_2111_ID = "21116001"


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


def insert_rows_before(ss, sheet_id, row_1based, count=1):
    body = {"requests": [{
        "insertDimension": {
            "range": {"sheetId": sheet_id, "dimension": "ROWS",
                      "startIndex": row_1based - 1, "endIndex": row_1based - 1 + count},
            "inheritFromBefore": True,
        }
    }]}
    return _gws("sheets", "spreadsheets", "batchUpdate",
                "--params", json.dumps({"spreadsheetId": ss}),
                "--json", json.dumps(body))


def find_row_by_id(ss, tab, target, col="A"):
    d = values_get(ss, f"{tab}!{col}:{col}")
    rows = [i + 1 for i, r in enumerate(d.get("values", []))
            if r and str(r[0]) == str(target)]
    if len(rows) > 1:
        raise RuntimeError(f"ID collision in {tab}!{col}: {target} at rows {rows}")
    return rows[0] if rows else None


def assert_id_at_row(ss, tab, row, expected, col="A"):
    rng = f"{tab}!{col}{row}:{col}{row}"
    d = values_get(ss, rng)
    actual = d.get("values", [[None]])[0][0] if d.get("values") else None
    if str(actual) != str(expected):
        raise AssertionError(f"ID mismatch at {rng}: expected {expected}, got {actual}")


# ===== 学习 =====
def learn():
    out = {}

    # 2112 拉 21127716/21127717 模板
    s6_row = find_row_by_id(SS_2112, TAB_2112, FLASH_TEMPLATE_S6_ID)
    s35_row = find_row_by_id(SS_2112, TAB_2112, FLASH_TEMPLATE_S35_ID)
    if not s6_row or not s35_row:
        raise RuntimeError(f"2112 template rows not found: 21127716={s6_row} 21127717={s35_row}")
    d6 = values_get(SS_2112, f"{TAB_2112}!A{s6_row}:Y{s6_row}")
    d35 = values_get(SS_2112, f"{TAB_2112}!A{s35_row}:Y{s35_row}")
    out["2112_template_s6"] = {"row": s6_row, "values": d6["values"][0]}
    out["2112_template_s3_5"] = {"row": s35_row, "values": d35["values"][0]}

    # 2111 占位行 + 节日区最后一个 ID
    d = values_get(SS_2111, f"{TAB_2111}!A:B")
    placeholder_row = None
    last_id = None
    for i, r in enumerate(d.get("values", [])):
        if r and str(r[0]) == PLACEHOLDER_2111_ID:
            placeholder_row = i + 1
            prev = d["values"][i - 1] if i > 0 else None
            if prev:
                last_id = prev[0]
            break
    if placeholder_row is None:
        raise RuntimeError(f"2111 placeholder {PLACEHOLDER_2111_ID} not found")
    out["2111_placeholder_row"] = placeholder_row
    out["2111_last_festival_id"] = last_id
    out["2111_next_id_s6"] = str(int(last_id) + 1) if last_id else None
    out["2111_next_id_s3_5"] = str(int(last_id) + 2) if last_id else None

    # 2013 14 个模板的当前 R 列扫描
    rewards = {}
    red_hero_present = []
    festival_box_slots = {}
    for tid in FLASH_2013_IDS:
        row = find_row_by_id(SS_2013, TAB_2013, tid)
        if row is None:
            raise RuntimeError(f"2013 template {tid} not found")
        d = values_get(SS_2013, f"{TAB_2013}!R{row}:R{row}")
        v = d.get("values", [[""]])[0][0] if d.get("values") else ""
        rewards[tid] = {"row": row, "other_items": v}
        # 红英雄扫描
        for hid in RED_HERO_ITEMS:
            if f'"id":{hid}' in v:
                red_hero_present.append({"2013_id": tid, "row": row, "red_hero_item": hid})
        # 节日自选宝箱槽位识别（只看 4 个已知槽位）
        if tid in FLASH_2013_FESTIVAL_BOX_SLOTS:
            m = re.search(r'"typ":"item","id":(11111\d+),"val":(\d+)', v)
            if m:
                festival_box_slots[tid] = {"current_box_id": int(m.group(1)), "val": int(m.group(2)), "row": row}
    out["2013_reward_scan"] = rewards
    out["2013_red_hero_present"] = red_hero_present
    out["2013_festival_box_slots"] = festival_box_slots

    return out


# ===== 计划 =====
def build_2112_row(template_values, new_id, comment, constant, show_hud):
    if len(template_values) != 25:
        raise RuntimeError(f"2112 template has {len(template_values)} cols, expected 25")
    row = list(template_values)
    row[0] = str(new_id)
    row[1] = comment
    row[2] = constant
    row[17] = str(show_hud)
    return row


def build_2111_row(new_calendar_id, activity_id, comment):
    return [
        str(new_calendar_id),
        str(activity_id),
        comment,
        '{"typ":"schema","id":[1,2,3,4,5,6]}',
        '{"typ":"time","is_ark":1}',
        "{}", "{}", "0", "0",
    ]


def replace_box_in_other_items(raw_json_str, old_box_id, new_box_id):
    """把 R 列 other_items 字符串里的 typ:item id=old_box_id 替换为 new_box_id（保留数量 + 其他 setting）。"""
    pattern = rf'("typ":"item","id":){old_box_id}(,)'
    new = re.sub(pattern, rf'\g<1>{new_box_id}\g<2>', raw_json_str)
    return new


def compute_plan(args, learned=None):
    learned = learned or learn()

    # 2112 ID 未占用 + 计算前驱插入位置（数值前驱+1）
    for new_id in (args.id_2112_s6, args.id_2112_s3_5):
        if find_row_by_id(SS_2112, TAB_2112, new_id) is not None:
            raise RuntimeError(f"2112 id {new_id} already occupied")
    d = values_get(SS_2112, f"{TAB_2112}!A:A")
    target_min = int(args.id_2112_s6)
    insert_row_2112 = None
    for i, r in enumerate(d.get("values", [])):
        if not r:
            continue
        try:
            n = int(r[0])
        except ValueError:
            continue
        if n > target_min:
            insert_row_2112 = i + 1
            break
    if insert_row_2112 is None:
        raise RuntimeError("could not find 2112 insertion row")

    s6_row = build_2112_row(
        learned["2112_template_s6"]["values"],
        args.id_2112_s6,
        f"{args.cn}-限时抢购-S6-通用皮（1、2期",
        f"event_{args.festival}_flash_sale_s6",
        args.show_hud,
    )
    s35_row = build_2112_row(
        learned["2112_template_s3_5"]["values"],
        args.id_2112_s3_5,
        f"{args.cn}-限时抢购-S3-5-通用皮（3期",
        f"event_{args.festival}_flash_sale_s3_5",
        args.show_hud,
    )

    # 2111 calendar 落位 + 段位
    new_2111_s6 = learned["2111_next_id_s6"]
    new_2111_s35 = learned["2111_next_id_s3_5"]
    for cid in (new_2111_s6, new_2111_s35):
        if find_row_by_id(SS_2111, TAB_2111, cid) is not None:
            raise RuntimeError(f"2111 calendar id {cid} already occupied")

    # 2013 4 处 R 列改动（如果给了 festival-select-box）
    box_changes = []
    if args.festival_select_box:
        for slot, info in learned["2013_festival_box_slots"].items():
            old_id = info["current_box_id"]
            new_v = replace_box_in_other_items(
                learned["2013_reward_scan"][slot]["other_items"],
                old_id,
                int(args.festival_select_box),
            )
            box_changes.append({
                "2013_id": slot,
                "row": info["row"],
                "range": f"{TAB_2013}!R{info['row']}",
                "old_box_id": old_id,
                "new_box_id": int(args.festival_select_box),
                "val": info["val"],
                "new_value": new_v,
            })

    plan = {
        "festival": args.festival,
        "cn": args.cn,
        "show_hud": args.show_hud,
        "2112": {
            "insert_before_row": insert_row_2112,
            "s6": {"id": str(args.id_2112_s6), "row": s6_row},
            "s3_5": {"id": str(args.id_2112_s3_5), "row": s35_row},
            "template_source": (FLASH_TEMPLATE_S6_ID, FLASH_TEMPLATE_S35_ID),
        },
        "2111": {
            "insert_before_row": learned["2111_placeholder_row"],
            "s6": {"calendar_id": new_2111_s6, "row": build_2111_row(new_2111_s6, args.id_2112_s6, f"{args.cn}-限时抢购-S6-通用皮（1、2期")},
            "s3_5": {"calendar_id": new_2111_s35, "row": build_2111_row(new_2111_s35, args.id_2112_s3_5, f"{args.cn}-限时抢购-S3-5-通用皮（3期")},
        },
        "2013_box_changes": box_changes,
        "warnings": [],
    }

    if learned["2013_red_hero_present"]:
        plan["warnings"].append({
            "kind": "RED_HERO_PRESENT_IN_2013",
            "detail": learned["2013_red_hero_present"],
            "remediation": "本节日如禁投红色英雄，请用户先在 2013 移除这些 item id 再 apply",
        })

    return plan


def cmd_learn(_args):
    print(json.dumps(learn(), ensure_ascii=False, indent=2))


def cmd_plan(args):
    print(json.dumps(compute_plan(args), ensure_ascii=False, indent=2))


def cmd_apply(args):
    plan = compute_plan(args)
    print(json.dumps(plan, ensure_ascii=False, indent=2))

    if plan["warnings"] and not args.force:
        print("\n[ABORT] warnings present. Re-run with --force after addressing.")
        sys.exit(2)

    print("\n--- applying ---")

    # 2013 box changes（先做，因为不涉及 insert/row 偏移）
    if plan["2013_box_changes"]:
        for c in plan["2013_box_changes"]:
            assert_id_at_row(SS_2013, TAB_2013, c["row"], c["2013_id"])
        values_batch_update(SS_2013, [
            {"range": c["range"], "values": [[c["new_value"]]]} for c in plan["2013_box_changes"]
        ])
        for c in plan["2013_box_changes"]:
            d = values_get(SS_2013, c["range"])
            v = d["values"][0][0]
            if str(c["new_box_id"]) not in v or str(c["old_box_id"]) in v:
                raise AssertionError(f"2013 verify fail at {c['range']}")
        print(f"[OK] 2013: {len(plan['2013_box_changes'])} box-id replacements")

    # 2112 insert 2 rows + write + verify
    p = plan["2112"]
    insert_rows_before(SS_2112, SHEETID_2112, p["insert_before_row"], count=2)
    rng = f"{TAB_2112}!A{p['insert_before_row']}:Y{p['insert_before_row']+1}"
    values_batch_update(SS_2112, [{"range": rng, "values": [p["s6"]["row"], p["s3_5"]["row"]]}])
    assert_id_at_row(SS_2112, TAB_2112, p["insert_before_row"], p["s6"]["id"])
    assert_id_at_row(SS_2112, TAB_2112, p["insert_before_row"] + 1, p["s3_5"]["id"])
    print(f"[OK] 2112: {p['s6']['id']} + {p['s3_5']['id']} written at row {p['insert_before_row']}/{p['insert_before_row']+1}")

    # 2111 insert 2 rows + write + verify
    p = plan["2111"]
    insert_rows_before(SS_2111, SHEETID_2111, p["insert_before_row"], count=2)
    rng = f"{TAB_2111}!A{p['insert_before_row']}:I{p['insert_before_row']+1}"
    values_batch_update(SS_2111, [{"range": rng, "values": [p["s6"]["row"], p["s3_5"]["row"]]}])
    assert_id_at_row(SS_2111, TAB_2111, p["insert_before_row"], p["s6"]["calendar_id"])
    assert_id_at_row(SS_2111, TAB_2111, p["insert_before_row"] + 1, p["s3_5"]["calendar_id"])
    print(f"[OK] 2111: {p['s6']['calendar_id']} + {p['s3_5']['calendar_id']} written at row {p['insert_before_row']}/{p['insert_before_row']+1}")

    print("\n=== ALL DONE ===")


def cmd_verify(args):
    issues = []

    # 2112 双行
    for label, mid in (("s6", args.id_2112_s6), ("s3_5", args.id_2112_s3_5)):
        row = find_row_by_id(SS_2112, TAB_2112, mid)
        if row is None:
            issues.append(f"2112 {label}={mid} NOT FOUND")
            continue
        d = values_get(SS_2112, f"{TAB_2112}!A{row}:Y{row}")
        v = d["values"][0]
        if v[4] != FLASH_PRIORITY:
            issues.append(f"2112 {mid} priority {v[4]} != {FLASH_PRIORITY}")
        if v[5] != FLASH_BASE_ACTIVITY:
            issues.append(f"2112 {mid} base_activity {v[5]} != {FLASH_BASE_ACTIVITY}")
        if "21217182" not in v[8]:
            issues.append(f"2112 {mid} components missing flash_sale_buy_duration")
        if "21371262" not in v[8]:
            issues.append(f"2112 {mid} components missing retake")
        print(f"[2112 {label}] row {row}: id={v[0]} | name={v[1]} | constant={v[2]} | show_hud={v[17]}")

    # 2111 双行 + 占位边界
    d = values_get(SS_2111, f"{TAB_2111}!A:C")
    found = {"s6": False, "s3_5": False}
    placeholder_row = None
    for i, r in enumerate(d.get("values", [])):
        if r and str(r[0]) == PLACEHOLDER_2111_ID:
            placeholder_row = i + 1
        if len(r) > 1 and r[1] == str(args.id_2112_s6):
            found["s6"] = (i + 1, r)
        if len(r) > 1 and r[1] == str(args.id_2112_s3_5):
            found["s3_5"] = (i + 1, r)
    for label, key in (("s6", args.id_2112_s6), ("s3_5", args.id_2112_s3_5)):
        if not found[label]:
            issues.append(f"2111 {label} no calendar row -> {key}")
        else:
            r, row = found[label]
            if placeholder_row is None or r >= placeholder_row:
                issues.append(f"2111 {label} row {r} not before placeholder row {placeholder_row}")
            print(f"[2111 {label}] row {r}: cal_id={row[0]} -> activity_id={row[1]} ({row[2]})")

    # 2013 红英雄扫描
    learned_red = []
    for tid in FLASH_2013_IDS:
        row = find_row_by_id(SS_2013, TAB_2013, tid)
        if row is None:
            issues.append(f"2013 {tid} NOT FOUND")
            continue
        d = values_get(SS_2013, f"{TAB_2013}!R{row}:R{row}")
        v = d.get("values", [[""]])[0][0] if d.get("values") else ""
        for hid in RED_HERO_ITEMS:
            if f'"id":{hid}' in v:
                learned_red.append((tid, hid))
    if learned_red:
        for tid, hid in learned_red:
            issues.append(f"2013 {tid} contains red-hero item {hid}")
    print(f"[2013] red-hero scan: {'CLEAN' if not learned_red else f'{len(learned_red)} HIT'}")

    if issues:
        print("\n!! ISSUES !!")
        for x in issues:
            print(f"  - {x}")
        sys.exit(1)
    print("\n[OK] all verified")


# ===== CLI =====
def _add_common(p):
    p.add_argument("--festival", required=True, help="english slug, e.g. pioneer / easter / spring / tech")
    p.add_argument("--cn", required=True, help="中文节日名, e.g. 拓荒节")
    p.add_argument("--id-2112-s6", dest="id_2112_s6", required=True, type=int, help="S6 1、2 期 2112 ID, 21127XXX")
    p.add_argument("--id-2112-s3-5", dest="id_2112_s3_5", required=True, type=int, help="S3-5 3 期 2112 ID, 21127XXX")
    p.add_argument("--show-hud", dest="show_hud", required=True, type=int, help="2168 表节日入口图标 ID, 21680XXX")
    p.add_argument("--festival-select-box", dest="festival_select_box", default=None, type=int,
                   help="节日自选宝箱 1111 ID（111110XXX）。给了就替换 4 处 2013 槽位；不给就只新建 2112+2111")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("learn"); sp.set_defaults(func=cmd_learn)

    sp = sub.add_parser("plan"); _add_common(sp); sp.set_defaults(func=cmd_plan)

    sp = sub.add_parser("apply"); _add_common(sp)
    sp.add_argument("--force", action="store_true", help="忽略 warnings (如红英雄存留) 强制写入")
    sp.set_defaults(func=cmd_apply)

    sp = sub.add_parser("verify")
    sp.add_argument("--id-2112-s6", dest="id_2112_s6", required=True, type=int)
    sp.add_argument("--id-2112-s3-5", dest="id_2112_s3_5", required=True, type=int)
    sp.set_defaults(func=cmd_verify)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
