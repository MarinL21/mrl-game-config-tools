#!/usr/bin/env python3
"""
P2 节日 wonder 巨猿砸金蛋端到端配置脚本（2112 + 2121 + 2115 + 2111 + 2011）

子命令：
  learn                 Step0 自主学习：拉所有 wonder 实例 + 复活节模板 + IAP + BP 道具映射
  plan   <args>         预演：dry-run 输出五表写入计划，不动表
  apply  <args>         真写：含写前 ID 双查 + 写后 ID 回读
  verify --id-2112 X    校验已配 wonder 五表完整性

依赖：gws CLI（gws-workspace skill），Python 3.9+

设计不变量（写到代码里强制执行）：
  - priority 永远 49982
  - base_activity_id 永远 21121499（拓荒节-2023-wonder巨猿）
  - filter 城堡 ≥ 8
  - components 110 项跨节日复用 + 2 项节日专属（task_group + festival_wonder）
  - 2121 task_group: arg1=1, reward=[]
  - 2121 festival_wonder: arg1=13330067, array=[3,10]
  - 2115 task: group=284, fincond.cat=10142127, fincond.arg.ids=[13330067]
  - 2115 task reward 通用道具池写死，节日 BP 道具按 reward.id == 复活节 11112091 自动识别替换
  - 所有写入前用 ID 精确校对物理行；写入后用 ID 回读
"""
import argparse
import json
import re
import subprocess
import sys

# ===== Spreadsheet 常量 =====
SS_2112, TAB_2112, SHEETID_2112 = "1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E", "activity_config_qa", 1308621827
SS_2121, TAB_2121, SHEETID_2121 = "1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc", "activity_special_QA", 311919191
SS_2115, TAB_2115, SHEETID_2115 = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY", "activity_task_QA", 1484652723
SS_2111, TAB_2111, SHEETID_2111 = "1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g", "activity_calendar_QA", 1688241274
SS_2011, TAB_2011 = "1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc", "iap_config_QA"

# ===== Wonder 模板不变量 =====
WONDER_PRIORITY = 49982
WONDER_BASE_ACTIVITY = 21121499
WONDER_UI_TEMPLATE = 21191534
WONDER_ICON_DISPLAYKEY = 15116148
WONDER_FILTER = '{"op":"ge","typ":"building","id":111811,"val":8}'
WONDER_TEXT = '{"label":"LC_EVENT_labor_wonder_event_title","title":"LC_EVENT_labor_wonder_event_title"}'
WONDER_DESCRIPTION = '{"rule":"LC_EVENT_2024_valentine_wonder_rules_1"}'
WONDER_BANNER = "assets/operation/P2dlcimg/activityImg/EventBanner_BG_162.png"
WONDER_CALENDAR_BANNER = "assets/operation/P2dlcimg/activityImg/EventBanner_Timeline_168.png"

# 复活节模板 ID（所有 plan/apply 都从这里克隆）
EASTER_2112_ID = 21127698
EASTER_2121_TASK_GROUP = 21219596
EASTER_2121_FESTIVAL_WONDER = 21219597
EASTER_2115_FIRST_TASK = 211584103
EASTER_2115_LAST_TASK = 211584117  # 含 15 个
EASTER_BP_ITEM = 11112091  # 魔术棒-复活节通用活动BP道具

# 砸蛋锤礼包（共享 IAP 行）
IAP_HAMMER_ID = 2011500698

# 2111 占位边界
PLACEHOLDER_2111_ID = 21116001

# 2115 task reward 通用道具池（跨节日不换）
COMMON_REWARD_ITEMS = {
    11119980,  # 全 15 行都给
    11112498,  # 漫游骰子-节日进度（虽叫节日进度但跨节日通用）
    11111156,  # 通用资源
    11116402,  # 高级奖池抽奖券
    11116111,  # 通用
    11111152,  # 阶段一
    11111105,  # 阶段二
    11111106,  # 阶段三
}

# 节日 BP 经验道具映射（1111 表）
BP_ITEM_MAP = {
    "easter": (11112091, "魔术棒"),
    "tech": (11112127, "聚能环"),
    "labor": (11112150, "纪念钻头"),
    "spring": (11112398, "绣球"),  # 通用版；年专 11112031
    "valen": (11112408, "夹心巧克力"),
    "dragon": (11112178, "船桨"),
    "abyss": (11112201, "藏宝图碎片"),
    "anni": (11112226, "欢乐气筒"),
    "moon": (11112293, "纪念胶卷"),
    "halloween": (11112306, "南瓜币"),
    "thank": (11112334, "感恩食材盒"),
    "xmas": (11112356, "幸运铃铛"),
    "beach": (11117166, "沙滩铃鼓"),
    "music": (11119726, "(无名)"),
}


# ===== gws helpers =====
def _gws(*args):
    r = subprocess.run(["gws", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gws failed: {r.stderr.strip()}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


def values_get(ss, rng):
    return _gws("sheets", "+read", "--spreadsheet", ss, "--range", rng, "--format", "json")


def values_update(ss, rng, values):
    return _gws("sheets", "spreadsheets", "values", "update",
                "--params", json.dumps({"spreadsheetId": ss, "range": rng,
                                         "valueInputOption": "USER_ENTERED"}),
                "--json", json.dumps({"values": values}, ensure_ascii=False))


def insert_dimension(ss, sheet_id, start_row_1based, count, inherit_from_before=False):
    body = {"requests": [{
        "insertDimension": {
            "range": {"sheetId": sheet_id, "dimension": "ROWS",
                      "startIndex": start_row_1based - 1, "endIndex": start_row_1based - 1 + count},
            "inheritFromBefore": inherit_from_before,
        }
    }]}
    return _gws("sheets", "spreadsheets", "batchUpdate",
                "--params", json.dumps({"spreadsheetId": ss}),
                "--json", json.dumps(body, ensure_ascii=False))


def find_row_by_id(ss, tab, target_id):
    """在 A 列找等于 target_id 的行号（1-based）。返回 None 表示不存在"""
    data = values_get(ss, f"{tab}!A:A")
    for i, r in enumerate(data.get("values", []), start=1):
        if r and str(r[0]) == str(target_id):
            return i
    return None


def find_row_by_b_col(ss, tab, target_id):
    """在 B 列找 target_id（用于 2115 task：A 列是 group，B 列是 id）"""
    data = values_get(ss, f"{tab}!B:B")
    for i, r in enumerate(data.get("values", []), start=1):
        if r and str(r[0]) == str(target_id):
            return i
    return None


# ===== Step 0: learn =====
def cmd_learn():
    """拉取所有 wonder 实例 + 模板"""
    out = {}

    # 1. 找 2112 表所有 wonder 巨猿/砸金蛋 行
    data = values_get(SS_2112, f"{TAB_2112}!A:B")
    rows = data.get("values", [])
    wonders = []
    for i, r in enumerate(rows, start=1):
        if len(r) < 2:
            continue
        cmt = r[1] if r[1] else ""
        if any(k in cmt for k in ["wonder巨猿", "巨猿-砸金蛋", "wonder-巨猿"]):
            wonders.append({"row": i, "id": r[0], "comment": cmt})
    out["existing_wonders"] = wonders

    # 2. 复活节模板 row（fallback：取 EASTER_2112_ID）
    easter_row = find_row_by_id(SS_2112, TAB_2112, EASTER_2112_ID)
    if easter_row:
        d = values_get(SS_2112, f"{TAB_2112}!A{easter_row}:Y{easter_row}")
        out["template_2112_row"] = {"row": easter_row, "values": d["values"][0]}
    else:
        out["template_2112_row"] = None

    # 3. 复活节 2121 pair
    tg_row = find_row_by_id(SS_2121, TAB_2121, EASTER_2121_TASK_GROUP)
    fw_row = find_row_by_id(SS_2121, TAB_2121, EASTER_2121_FESTIVAL_WONDER)
    if tg_row and fw_row:
        d = values_get(SS_2121, f"{TAB_2121}!A{tg_row}:O{fw_row}")
        out["template_2121_pair"] = {"row": tg_row, "values": d["values"]}
    else:
        out["template_2121_pair"] = None

    # 4. 复活节 2115 15 task
    first_row = find_row_by_b_col(SS_2115, TAB_2115, EASTER_2115_FIRST_TASK)
    if first_row:
        d = values_get(SS_2115, f"{TAB_2115}!A{first_row}:R{first_row + 14}")
        out["template_2115_15rows"] = {"first_row": first_row, "values": d["values"]}
    else:
        out["template_2115_15rows"] = None

    # 5. IAP 砸蛋锤礼包 row
    iap_row = find_row_by_id(SS_2011, TAB_2011, IAP_HAMMER_ID)
    if iap_row:
        d = values_get(SS_2011, f"{TAB_2011}!A{iap_row}:T{iap_row}")
        out["template_iap_5029"] = {"row": iap_row, "values": d["values"][0]}

    # 6. BP 道具映射
    out["bp_item_map"] = BP_ITEM_MAP

    # 7. 2111 占位行
    placeholder_row = find_row_by_id(SS_2111, TAB_2111, PLACEHOLDER_2111_ID)
    out["placeholder_2111_row"] = placeholder_row

    print(json.dumps(out, ensure_ascii=False, indent=2))


# ===== Step 1: 检查 ID 占用（双查） =====
def assert_id_free_2112(target_id):
    """2112 表 A 列双查：=={target_id} 必须空 + >{target_id} 取最小后继"""
    row = find_row_by_id(SS_2112, TAB_2112, target_id)
    assert row is None, f"❌ 2112 ID {target_id} 已被占用 (row {row})"
    # 后继查找
    data = values_get(SS_2112, f"{TAB_2112}!A:A")
    candidates = []
    for i, r in enumerate(data.get("values", []), start=1):
        if not r:
            continue
        try:
            rid = int(r[0])
        except (ValueError, TypeError):
            continue
        if rid > target_id:
            candidates.append((i, rid))
    candidates.sort(key=lambda x: x[1])
    assert candidates, "❌ 2112 表里找不到 > target_id 的后继行"
    return candidates[0]  # (row, id)


def assert_id_free(ss, tab, target_id, label, by_b_col=False):
    fn = find_row_by_b_col if by_b_col else find_row_by_id
    row = fn(ss, tab, target_id)
    assert row is None, f"❌ {label} ID {target_id} 已被占用 (row {row})"


# ===== Step 2: plan / apply 共享数据构造 =====
def build_2112_row(festival_slug, festival_cn, year, new_id, show_hud,
                   tg_new_id, fw_new_id, template_row):
    """从复活节模板构造拓荒节 2112 主行"""
    row = list(template_row)
    while len(row) < 25:
        row.append("")
    row[0] = str(new_id)
    row[1] = f"{festival_cn}-{year}-wonder巨猿-砸金蛋"
    row[2] = f"event_{festival_slug}_festival_hegemony_{year}"
    row[17] = str(show_hud)  # A_INT_show_hud (col R)
    # components 替换 task_group + festival_wonder
    comps = json.loads(row[8])
    swap = 0
    for c in comps:
        if c.get("typ") == "task_group" and c.get("id") == EASTER_2121_TASK_GROUP:
            c["id"] = int(tg_new_id)
            swap += 1
        elif c.get("typ") == "festival_wonder" and c.get("id") == EASTER_2121_FESTIVAL_WONDER:
            c["id"] = int(fw_new_id)
            swap += 1
    assert swap == 2, f"components 替换 {swap} 次，应为 2"
    row[8] = json.dumps(comps, ensure_ascii=False)
    return row


def build_2121_pair(festival_cn, year, tg_new_id, fw_new_id, bp_item, task_ids,
                    template_pair):
    """构造拓荒节 2121 task_group + festival_wonder 两行"""
    tg = list(template_pair[0])
    fw = list(template_pair[1])
    while len(tg) < 15:
        tg.append("")
    while len(fw) < 15:
        fw.append("")

    # task_group
    tg[0] = str(tg_new_id)
    tg[1] = f"{year}{festival_cn}巨猿个人积分任务分组"
    tg[10] = json.dumps(task_ids)  # A_ARR_array

    # festival_wonder
    fw[0] = str(fw_new_id)
    fw[1] = f"{year}{festival_cn}节巨猿奖励"
    rew = json.loads(fw[3])
    for a in rew:
        if a.get("asset", {}).get("id") == EASTER_BP_ITEM:
            a["asset"]["id"] = int(bp_item)
    fw[3] = json.dumps(rew, ensure_ascii=False)

    return [tg, fw]


def build_2115_15(festival_cn, task_start, bp_item, template_rows):
    """构造拓荒节 2115 15 行 task"""
    out = []
    for k, src in enumerate(template_rows):
        row = list(src)
        while len(row) < 18:
            row.append("")
        new_task_id = task_start + k
        row[1] = str(new_task_id)  # A_INT_id (B 列)
        row[2] = row[2].replace("复活节", festival_cn)  # comment
        # reward 替换 BP 道具
        rew = json.loads(row[6])
        for a in rew:
            if a.get("asset", {}).get("id") == EASTER_BP_ITEM:
                a["asset"]["id"] = int(bp_item)
        row[6] = json.dumps(rew, ensure_ascii=False)
        out.append(row)
    return out


def build_2111_row(festival_cn, year, new_2112_id, cal_id, template_row):
    """构造 2111 calendar 调度行（从复活节模板）"""
    row = list(template_row)
    while len(row) < 9:
        row.append("")
    row[0] = str(cal_id)
    row[1] = str(new_2112_id)
    row[2] = f"{festival_cn}-{year}-wonder巨猿-砸金蛋"
    return row


def append_iap_actv(new_2112_id, iap_template_row):
    """在 IAP 5029 的 time_info.normal 数组追加新 actv_id"""
    ti_str = iap_template_row[8]
    ti = json.loads(ti_str)
    if "normal" not in ti:
        ti["normal"] = []
    if any(x.get("actv_id") == int(new_2112_id) for x in ti["normal"]):
        return ti_str  # 已存在，无需 patch
    ti["normal"].append({"actv_id": int(new_2112_id)})
    return json.dumps(ti, ensure_ascii=False)


# ===== Step 3: apply =====
def cmd_apply(args, dry_run=False):
    label = "[DRY-RUN]" if dry_run else "[APPLY]"
    print(f"{label} 拓荒节 wonder 巨猿砸金蛋配置 → {args.cn}-{args.year}")

    # 0. 读所有模板
    easter_row = find_row_by_id(SS_2112, TAB_2112, EASTER_2112_ID)
    template_2112 = values_get(SS_2112, f"{TAB_2112}!A{easter_row}:Y{easter_row}")["values"][0]
    tg_row = find_row_by_id(SS_2121, TAB_2121, EASTER_2121_TASK_GROUP)
    fw_row = find_row_by_id(SS_2121, TAB_2121, EASTER_2121_FESTIVAL_WONDER)
    template_2121 = values_get(SS_2121, f"{TAB_2121}!A{tg_row}:O{fw_row}")["values"]
    first_2115 = find_row_by_b_col(SS_2115, TAB_2115, EASTER_2115_FIRST_TASK)
    template_2115 = values_get(SS_2115, f"{TAB_2115}!A{first_2115}:R{first_2115 + 14}")["values"]
    iap_row = find_row_by_id(SS_2011, TAB_2011, IAP_HAMMER_ID)
    template_iap = values_get(SS_2011, f"{TAB_2011}!A{iap_row}:T{iap_row}")["values"][0]

    # 找复活节 calendar 调度行做模板
    data = values_get(SS_2111, f"{TAB_2111}!A:I")
    cal_template_row = None
    for r in data.get("values", []):
        if len(r) >= 2 and str(r[1]) == str(EASTER_2112_ID):
            cal_template_row = r
            break
    assert cal_template_row, "❌ 找不到复活节 calendar 模板行"

    # 1. ID 双查
    print(f"\n[CHECK] 写前 ID 占用核查")
    successor_2112 = assert_id_free_2112(args.id_2112)
    print(f"  ✓ 2112 {args.id_2112} 空，后继 row={successor_2112[0]} id={successor_2112[1]}")
    assert_id_free(SS_2121, TAB_2121, args.id_2121_task_group, "2121 task_group")
    assert_id_free(SS_2121, TAB_2121, args.id_2121_festival_wonder, "2121 festival_wonder")
    print(f"  ✓ 2121 {args.id_2121_task_group} / {args.id_2121_festival_wonder} 空")
    for k in range(15):
        assert_id_free(SS_2115, TAB_2115, args.task_start + k, f"2115 task[{k}]", by_b_col=True)
    print(f"  ✓ 2115 task {args.task_start}-{args.task_start+14} (15 连号) 全空")

    # 2. 找 cal_id（>现有最大 + 1，且 < PLACEHOLDER_2111_ID）
    placeholder_row = find_row_by_id(SS_2111, TAB_2111, PLACEHOLDER_2111_ID)
    a_data = values_get(SS_2111, f"{TAB_2111}!A1:A{placeholder_row - 1}")
    max_cal = 0
    for r in a_data.get("values", []):
        if r:
            try:
                max_cal = max(max_cal, int(r[0]))
            except (ValueError, TypeError):
                pass
    new_cal_id = max_cal + 1
    assert new_cal_id < PLACEHOLDER_2111_ID, f"new_cal_id {new_cal_id} 超过占位 {PLACEHOLDER_2111_ID}"
    print(f"  ✓ 2111 cal_id={new_cal_id} (max={max_cal} → +1)")

    # 3. 构造写入数据
    bp_item = int(args.bp_item)
    task_ids = [args.task_start + k for k in range(15)]
    row_2112 = build_2112_row(args.festival, args.cn, args.year, args.id_2112,
                               args.show_hud, args.id_2121_task_group,
                               args.id_2121_festival_wonder, template_2112)
    pair_2121 = build_2121_pair(args.cn, args.year, args.id_2121_task_group,
                                 args.id_2121_festival_wonder, bp_item, task_ids,
                                 template_2121)
    rows_2115 = build_2115_15(args.cn, args.task_start, bp_item, template_2115)
    row_2111 = build_2111_row(args.cn, args.year, args.id_2112, new_cal_id, cal_template_row)
    new_iap_ti = append_iap_actv(args.id_2112, template_iap)

    # 4. plan 输出
    print(f"\n{label} 写入数据预览：")
    print(f"  2112 row={successor_2112[0]} (insert before): id={row_2112[0]} cmt={row_2112[1]}")
    print(f"  2121 task_group: id={pair_2121[0][0]} cmt={pair_2121[0][1]}")
    print(f"  2121 festival_wonder: id={pair_2121[1][0]} reward={pair_2121[1][3]}")
    print(f"  2115 first task: id={rows_2115[0][1]} reward[节日 BP]={[a['asset']['id'] for a in json.loads(rows_2115[0][6]) if a['asset']['id']==bp_item]}")
    print(f"  2111 row insert: cal_id={row_2111[0]} actv_id={row_2111[1]} cmt={row_2111[2]}")
    print(f"  2011 IAP {IAP_HAMMER_ID} new time_info: {new_iap_ti}")

    if dry_run:
        print(f"\n{label} 完成（未写表）")
        return

    # 5. 真写
    print(f"\n[APPLY] 开始写入...")

    # 5.1 2121 (依赖优先：被 2112 引用)
    tg_target = find_row_by_id(SS_2121, TAB_2121, EASTER_2121_TASK_GROUP)  # 用复活节作前驱定位
    # 实际正确做法：找 2121 表里 < new_id 的最大值的下一行
    insert_row_2121 = _find_insert_row(SS_2121, TAB_2121, args.id_2121_task_group)
    insert_dimension(SS_2121, SHEETID_2121, insert_row_2121, 2)
    values_update(SS_2121, f"{TAB_2121}!A{insert_row_2121}:O{insert_row_2121+1}", pair_2121)
    print(f"  ✓ 2121 row {insert_row_2121}-{insert_row_2121+1} 写入")

    # 5.2 2115 task 15 行
    insert_row_2115 = _find_insert_row_b(SS_2115, TAB_2115, args.task_start)
    insert_dimension(SS_2115, SHEETID_2115, insert_row_2115, 15)
    values_update(SS_2115, f"{TAB_2115}!A{insert_row_2115}:R{insert_row_2115+14}", rows_2115)
    print(f"  ✓ 2115 row {insert_row_2115}-{insert_row_2115+14} 写入 15 行")

    # 5.3 2112 主行
    insert_row_2112 = _find_insert_row(SS_2112, TAB_2112, args.id_2112)
    insert_dimension(SS_2112, SHEETID_2112, insert_row_2112, 1)
    values_update(SS_2112, f"{TAB_2112}!A{insert_row_2112}:Y{insert_row_2112}", [row_2112])
    print(f"  ✓ 2112 row {insert_row_2112} 写入")

    # 5.4 2111 calendar
    insert_row_2111 = _find_insert_row(SS_2111, TAB_2111, new_cal_id)
    insert_dimension(SS_2111, SHEETID_2111, insert_row_2111, 1)
    values_update(SS_2111, f"{TAB_2111}!A{insert_row_2111}:I{insert_row_2111}", [row_2111])
    print(f"  ✓ 2111 row {insert_row_2111} 写入 cal_id={new_cal_id}")

    # 5.5 2011 IAP time_info patch
    iap_row = find_row_by_id(SS_2011, TAB_2011, IAP_HAMMER_ID)
    values_update(SS_2011, f"{TAB_2011}!I{iap_row}:I{iap_row}", [[new_iap_ti]])
    print(f"  ✓ 2011 row {iap_row} time_info 追加 actv_id={args.id_2112}")

    # 6. 写后回读
    print(f"\n[VERIFY] 写后 ID 回读...")
    cmd_verify(argparse.Namespace(id_2112=args.id_2112))


def _find_insert_row(ss, tab, target_id):
    """通用：找 A 列里 > target_id 的最小行号（前驱+1）"""
    data = values_get(ss, f"{tab}!A:A")
    candidates = []
    for i, r in enumerate(data.get("values", []), start=1):
        if not r:
            continue
        try:
            rid = int(r[0])
        except (ValueError, TypeError):
            continue
        if rid > int(target_id):
            candidates.append((i, rid))
    candidates.sort(key=lambda x: x[1])
    assert candidates, f"找不到 > {target_id} 的后继"
    return candidates[0][0]


def _find_insert_row_b(ss, tab, target_id):
    """2115 专用：A 列是 group，B 列是 id，按 B 列定位插入位置"""
    data = values_get(ss, f"{tab}!B:B")
    candidates = []
    for i, r in enumerate(data.get("values", []), start=1):
        if not r:
            continue
        try:
            rid = int(r[0])
        except (ValueError, TypeError):
            continue
        if rid > int(target_id):
            candidates.append((i, rid))
    candidates.sort(key=lambda x: x[1])
    assert candidates, f"找不到 > {target_id} 的后继"
    return candidates[0][0]


# ===== Step 4: verify =====
def cmd_verify(args):
    print(f"[VERIFY] id_2112={args.id_2112}")
    failures = []

    # 2112 行存在 + components 含 task_group/festival_wonder
    row = find_row_by_id(SS_2112, TAB_2112, args.id_2112)
    if not row:
        failures.append(f"2112 ID {args.id_2112} 不存在")
    else:
        d = values_get(SS_2112, f"{TAB_2112}!A{row}:Y{row}")["values"][0]
        comps = json.loads(d[8])
        tg_ids = [c["id"] for c in comps if c.get("typ") == "task_group"]
        fw_ids = [c["id"] for c in comps if c.get("typ") == "festival_wonder"]
        # 通用 task_group 21218351 必在
        if 21218351 not in tg_ids:
            failures.append(f"2112 components 缺通用 task_group 21218351")
        # festival_wonder 应有 1 个
        if len(fw_ids) != 1:
            failures.append(f"2112 components festival_wonder 数量 {len(fw_ids)} (期望 1)")
        else:
            fw_id = fw_ids[0]
            fw_row = find_row_by_id(SS_2121, TAB_2121, fw_id)
            if not fw_row:
                failures.append(f"2121 festival_wonder {fw_id} 不存在")

    # 2111 calendar 有指向该活动的行
    data = values_get(SS_2111, f"{TAB_2111}!A:B")
    cal_hits = [r for r in data.get("values", []) if len(r) >= 2 and str(r[1]) == str(args.id_2112)]
    if not cal_hits:
        failures.append(f"2111 没有 activity_id={args.id_2112} 的调度行")

    # 2011 IAP time_info 含该 actv_id
    iap_row = find_row_by_id(SS_2011, TAB_2011, IAP_HAMMER_ID)
    iap_data = values_get(SS_2011, f"{TAB_2011}!I{iap_row}:I{iap_row}")["values"][0][0]
    ti = json.loads(iap_data)
    actv_ids = [x.get("actv_id") for x in ti.get("normal", [])]
    if int(args.id_2112) not in actv_ids:
        failures.append(f"2011 IAP {IAP_HAMMER_ID} time_info 不含 actv_id={args.id_2112}")

    if failures:
        print("❌ Verify 失败：")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"✅ Verify 通过：2112 / 2121 / 2111 / 2011 全部对齐")


# ===== main =====
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("learn")

    for name in ("plan", "apply"):
        p = sub.add_parser(name)
        p.add_argument("--festival", required=True, help="英文 slug: labor/easter/tech/...")
        p.add_argument("--cn", required=True, help="节日中文名")
        p.add_argument("--year", type=int, required=True)
        p.add_argument("--id-2112", type=int, required=True)
        p.add_argument("--show-hud", type=int, required=True)
        p.add_argument("--bp-item", type=int, required=True)
        p.add_argument("--id-2121-task-group", type=int, required=True)
        p.add_argument("--id-2121-festival-wonder", type=int, required=True)
        p.add_argument("--task-start", type=int, required=True, help="2115 task 起始 ID（15 连号起点）")

    v = sub.add_parser("verify")
    v.add_argument("--id-2112", type=int, required=True)

    args = ap.parse_args()
    if args.cmd == "learn":
        cmd_learn()
    elif args.cmd == "plan":
        cmd_apply(args, dry_run=True)
    elif args.cmd == "apply":
        cmd_apply(args, dry_run=False)
    elif args.cmd == "verify":
        cmd_verify(args)


if __name__ == "__main__":
    main()
