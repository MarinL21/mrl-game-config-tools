#!/usr/bin/env python3
"""
P2 节日主城特效累充三件套（个人/服务器/联盟）端到端配置脚本。

涉及 6 张表 25 行：
  1168 access_group ×1  →  jump_link.expr.id 引用
  2122 rank        ×4  →  task fincond + components rank
  2121 special     ×3  →  jump_link / actv_show_rank / countdown
  2115 task        ×11 →  11 档累充
  2112 main        ×3  →  个人 / 服务器 / 联盟
  2111 calendar    ×3  →  调度行

子命令：
  learn                    Step0：拉春节三件套模板 + 6 表 max ID + 占位符行
  plan   <args>            Dry-run：6 表完整写入计划，不动表
  apply  <args>            真写：按依赖顺序 1168→2122→2121→2115→2112→2111
  verify <args>            校验三件套完整性 + 依赖闭环

依赖：gws CLI（gws-workspace skill），Python 3.9+

设计不变量（写到代码里强制）：
  - 个人版 base=21127335 / 服务器版 base=21127336 / 联盟版 base=21127566
  - 个人 ui_template=21191310 / 服务器 ui_template=21191311 / 联盟 ui_template=参数（默认占位 21191428）
  - filter 全统一: building 111811 ge 6
  - description.rule = LC_EVENT_tech_cityeffect_actv_rule
  - 累充统计 cat=10148028（春节起新机制）
  - 11 档累充 val + reward 沿用星球套2025
  - 通用组件 ID 全部锁死见下
"""
import argparse
import json
import subprocess
import time
import sys

# ===== Spreadsheet 常量 =====
SS_2112, TAB_2112, SHEETID_2112 = "1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E", "activity_config_qa", 1308621827
SS_2111, TAB_2111, SHEETID_2111 = "1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g", "activity_calendar_QA", 1688241274
SS_2122, TAB_2122, SHEETID_2122 = "1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M", "activity_rank_rule（QA）", 483238343
SS_2121, TAB_2121, SHEETID_2121 = "1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc", "activity_special_QA", 311919191
SS_2115, TAB_2115, SHEETID_2115 = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY", "activity_task_QA", 1484652723
SS_1168, TAB_1168, SHEETID_1168 = "1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA", "get_access_group（杜绝手搓）", 0

# ===== 春节三件套 模板 ID（patch 源）=====
TEMPLATE_PERSONAL = "21127582"   # 春节2026 主城特效累充个人
TEMPLATE_SERVER   = "21127583"   # 春节2026 主城特效累充服务器
TEMPLATE_ALLIANCE = "21127703"   # 春节2026 主城特效累充联盟
SPRING_RANK_FOR_IAP_IDS = "21222393"  # 春节累充统计 rank（用于 clone-spring 占位）

# ===== 三版固定字段 =====
BASE_PERSONAL  = "21127335"
BASE_SERVER    = "21127336"
BASE_ALLIANCE  = "21127566"
UITPL_PERSONAL = "21191310"
UITPL_SERVER   = "21191311"
UITPL_ALLIANCE_DEFAULT = "21191428"   # 春节联盟占位

PRIORITY_PERSONAL = "49999"
PRIORITY_SERVER   = "49998"
PRIORITY_ALLIANCE = "49998"

FILTER_COMMON = '{"op":"ge","typ":"building","id":111811,"val":6}'
DESCRIPTION_COMMON = '{"rule":"LC_EVENT_tech_cityeffect_actv_rule"}'
RULE_DESC_LC = "LC_EVENT_tech_cityeffect_recharge_task_title"

# ===== 通用组件 ID（不变）=====
LUCKY_REWARD_IDS = ["21217083", "21217084", "21217085"]
LUCKY_COST_ID    = "21217391"
RETAKE_ID        = "21371220"
# 服务器版
SVR_PACKAGE_ID   = "21357332"
SVR_PROGRESS_IDS = ["21217392", "21217393", "21217394", "21217395", "21217396", "21217397"]
SVR_FINAL_IDS    = ["21217398", "21217399"]
SVR_SHOW_RANK_ID = "21215722"
SVR_COUNTDOWN_ID = "21217099"
# 联盟版
ALC_PREVIEW_ID   = "21218445"
ALC_PACKAGE_ID   = "21357712"
ALC_JUMP_LINK_ID = "21217390"   # 联盟版 jump_link 跨节日复用
ALC_PROGRESS_IDS = ["21218438", "21218439", "21218440", "21218441"]
ALC_FINAL_IDS    = ["21218442", "21218443"]
ALC_SHOW_RANK_ID = "21218446"
ALC_DESCRIPTION_ID = "21219017"

# ===== 11 档累充 task 模板 =====
TASK_VALS = [1250, 2500, 5000, 12500, 25000, 50000, 100000, 175000, 300000, 500000, 750000]

TASK_REWARDS = [
    [{"asset":{"typ":"item","id":11119848,"val":1},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":1},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":2},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11112498,"val":30},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":2},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11118203,"val":1},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":1},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":4},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11114330,"val":4},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":4},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11118203,"val":1},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":1},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":6},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11112498,"val":30},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":6},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11118858,"val":1},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":2},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":8},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11112498,"val":30},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":8},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11118203,"val":5},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":4},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":10},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11112498,"val":30},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":10},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11118203,"val":8},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":6},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":12},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11112498,"val":30},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":12},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11118203,"val":10},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":8},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":14},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11112498,"val":30},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":14},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11118203,"val":20},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":10},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":16},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11112498,"val":30},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":16},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11118203,"val":25},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":12},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":18},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11112498,"val":30},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":18},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11119708,"val":1},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":15},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":20},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11112498,"val":30},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":20},"setting":{"serial_number":1,"ishighlight":False}}],
    [{"asset":{"typ":"item","id":11119844,"val":1},"setting":{"serial_number":5,"ishighlight":False}},{"asset":{"typ":"item","id":11116304,"val":90},"setting":{"serial_number":4,"ishighlight":False}},{"asset":{"typ":"material","id":19345004,"val":450},"setting":{"serial_number":3,"ishighlight":False}},{"asset":{"typ":"item","id":11114330,"val":450},"setting":{"serial_number":2,"ishighlight":False}},{"asset":{"typ":"item","id":11111105,"val":40},"setting":{"serial_number":1,"ishighlight":False}}],
]

TASK_GROUP = "290"
TASK_FINCOND_CAT = 10148028
TASK_SHOWCOND = '{"op":"and","args":[{"op":"ge","typ":"actvstarttime","val":0},{"op":"ge","typ":"building","id":111811,"val":5}]}'

# ===== 2122 rank score_rule.cat =====
RANK_CAT_PERSONAL_SHARED = 101425016   # group=392 / 353
RANK_CAT_SERVER          = 101425015   # group=393
RANK_CAT_ALLIANCE        = 101427041   # group=393
RANK_GROUP_PERSONAL = "392"
RANK_GROUP_SHARED   = "353"
RANK_GROUP_SERVER   = "393"
RANK_GROUP_ALLIANCE = "393"

# ===== 2111 占位符 =====
PLACEHOLDER_2111_ID = "21116001"

# ===== 2115 task ID 段位策略 =====
# 21157xxxx 段：科技节/星球套（211572XXX）
# 21158xxxx 段：春节（211584XXX-211589999 已占满）
# 21159xxxx 段：拓荒节起新建（211595001 起 11 连号；后续节日按 211595012 / 211596xxx 递增）
TASK_ID_BASE = 211595001  # 默认起点；脚本会扫 2115 找下一个连续 11 空号

# ===== 1168 LC =====
ACCESS_GROUP_LC_NAME = '{"typ":"lc","txt":"LC_ITEM_item_cap"}'
ACCESS_GROUP_EFFECT_ID = 11531068   # 1153 累充统计 effect


# ===== gws helpers =====
def _gws(*args):
    r = subprocess.run(["gws", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gws failed:\n  cmd={args[:5]}\n  stderr={r.stderr.strip()}\n  stdout={r.stdout[:300]}")
    out = r.stdout
    if out.startswith("Using keyring"):
        out = out.split("\n", 1)[1] if "\n" in out else "{}"
    return json.loads(out) if out.strip() else {}


def values_get(ss, rng):
    return _gws("sheets", "spreadsheets", "values", "get",
                "--params", json.dumps({"spreadsheetId": ss, "range": rng}))


def values_update(ss, rng, rows):
    return _gws("sheets", "spreadsheets", "values", "update",
                "--params", json.dumps({"spreadsheetId": ss, "range": rng, "valueInputOption": "RAW"}),
                "--json", json.dumps({"values": rows}, ensure_ascii=False))


def get_grid_size(ss, sheet_id):
    res = _gws("sheets", "spreadsheets", "get",
               "--params", json.dumps({"spreadsheetId": ss,
                                       "fields": "sheets(properties(sheetId,gridProperties(rowCount)))"}))
    for s in res.get("sheets", []):
        if s["properties"]["sheetId"] == sheet_id:
            return s["properties"]["gridProperties"]["rowCount"]
    raise RuntimeError(f"sheet_id {sheet_id} not found in {ss}")


def insert_or_append_rows(ss, sheet_id, insert_at_row_1based, n):
    """根据 grid 大小自动选择 insertDimension（中间）或 appendDimension（表尾）。"""
    grid = get_grid_size(ss, sheet_id)
    if insert_at_row_1based <= grid:
        body = {"requests": [{
            "insertDimension": {
                "range": {"sheetId": sheet_id, "dimension": "ROWS",
                          "startIndex": insert_at_row_1based - 1,
                          "endIndex": insert_at_row_1based - 1 + n},
                "inheritFromBefore": False,
            }
        }]}
    else:
        body = {"requests": [{
            "appendDimension": {"sheetId": sheet_id, "dimension": "ROWS", "length": n}
        }]}
    return _gws("sheets", "spreadsheets", "batchUpdate",
                "--params", json.dumps({"spreadsheetId": ss}),
                "--json", json.dumps(body))


def find_row_by_value(ss, tab, target, col_letter="A"):
    d = values_get(ss, f"{tab}!{col_letter}:{col_letter}")
    rows = [i + 1 for i, r in enumerate(d.get("values", []))
            if r and str(r[0]) == str(target)]
    if len(rows) > 1:
        raise RuntimeError(f"ID collision in {tab}!{col_letter}: {target} at rows {rows}")
    return rows[0] if rows else None


def col_letter(n_cols):
    if n_cols <= 26:
        return chr(ord("A") + n_cols - 1)
    first = (n_cols - 1) // 26
    second = (n_cols - 1) % 26
    return chr(ord("A") + first - 1) + chr(ord("A") + second)


# =========================================================================
# Step 0：自主学习
# =========================================================================
def cmd_learn(args):
    out = {}

    # 三件套模板（春节）
    p_row = find_row_by_value(SS_2112, TAB_2112, TEMPLATE_PERSONAL)
    s_row = find_row_by_value(SS_2112, TAB_2112, TEMPLATE_SERVER)
    a_row = find_row_by_value(SS_2112, TAB_2112, TEMPLATE_ALLIANCE)
    out["2112_template"] = {
        "personal_row": p_row, "server_row": s_row, "alliance_row": a_row,
    }
    for tag, row in [("personal", p_row), ("server", s_row), ("alliance", a_row)]:
        if row:
            d = values_get(SS_2112, f"{TAB_2112}!A{row}:Y{row}")
            out["2112_template"][f"{tag}_values"] = d["values"][0]

    # 6 表 max ID
    def max_id_in_col(ss, tab, col):
        d = values_get(ss, f"{tab}!{col}:{col}")
        nums = [int(r[0]) for r in d.get("values", []) if r and r[0].isdigit()]
        return max(nums) if nums else 0

    out["max_ids"] = {
        "2112_col_A": max_id_in_col(SS_2112, TAB_2112, "A"),
        "2111_col_A": max_id_in_col(SS_2111, TAB_2111, "A"),
        "2122_col_B": max_id_in_col(SS_2122, TAB_2122, "B"),
        "2121_col_A": max_id_in_col(SS_2121, TAB_2121, "A"),
        "2115_col_B": max_id_in_col(SS_2115, TAB_2115, "B"),
        "1168_col_A": max_id_in_col(SS_1168, TAB_1168, "A"),
    }

    # 2111 占位符行
    placeholder_row = find_row_by_value(SS_2111, TAB_2111, PLACEHOLDER_2111_ID)
    out["2111_placeholder_row"] = placeholder_row

    # 春节累充统计 rank ids（占位用）
    spring_rank_row = find_row_by_value(SS_2122, TAB_2122, SPRING_RANK_FOR_IAP_IDS, col_letter="B")
    if spring_rank_row:
        d = values_get(SS_2122, f"{TAB_2122}!D{spring_rank_row}")
        sr = json.loads(d["values"][0][0])
        out["spring_iap_ids_count"] = len(sr[0].get("ids", []))

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return out


# =========================================================================
# 数据生成
# =========================================================================
def build_components_personal(p):
    comps = [
        {"typ": "iap_show"},
        {"typ": "city_skin", "id": int(p["city_skin"])},
    ]
    comps += [{"typ": "task", "id": tid} for tid in p["task_ids"]]
    comps += [
        {"typ": "jump_link", "id": int(p["jump_link_id"])},
        *[{"typ": "tech_lucky_reward", "id": int(x)} for x in LUCKY_REWARD_IDS],
        {"typ": "tech_lucky_cost", "id": int(LUCKY_COST_ID)},
        {"typ": "actv_show_rank", "id": int(p["actv_show_rank_id"])},
        {"typ": "rank", "id": int(p["rank_personal_id"])},
        {"typ": "server_recharge_countdown", "id": int(p["countdown_id"])},
        {"typ": "retake", "id": int(RETAKE_ID)},
    ]
    return comps


def build_components_server(p):
    return [
        {"typ": "package", "id": int(SVR_PACKAGE_ID)},
        {"typ": "jump_link", "id": int(p["jump_link_id"])},
        *[{"typ": "server_recharge_progress", "id": int(x)} for x in SVR_PROGRESS_IDS],
        {"typ": "server_recharge_progress_final", "id": int(SVR_FINAL_IDS[0])},
        {"typ": "server_recharge_progress_final_first", "id": int(SVR_FINAL_IDS[1])},
        {"typ": "actv_show_rank", "id": int(SVR_SHOW_RANK_ID)},
        {"typ": "rank", "id": int(p["rank_shared_353_id"])},
        {"typ": "rank", "id": int(p["rank_server_id"])},
        {"typ": "server_recharge_countdown", "id": int(SVR_COUNTDOWN_ID)},
    ]


def build_components_alliance(p):
    return [
        {"typ": "iap_show"},
        {"typ": "preview", "id": int(ALC_PREVIEW_ID)},
        {"typ": "package", "id": int(ALC_PACKAGE_ID)},
        {"typ": "jump_link", "id": int(ALC_JUMP_LINK_ID)},
        *[{"typ": "server_recharge_progress", "id": int(x)} for x in ALC_PROGRESS_IDS],
        {"typ": "server_recharge_progress_final", "id": int(ALC_FINAL_IDS[0])},
        {"typ": "server_recharge_progress_final_first", "id": int(ALC_FINAL_IDS[1])},
        {"typ": "actv_show_rank", "id": int(ALC_SHOW_RANK_ID)},
        {"typ": "rank", "id": int(p["rank_shared_353_id"])},
        {"typ": "rank", "id": int(p["rank_alliance_id"])},
        {"typ": "server_recharge_countdown", "id": int(SVR_COUNTDOWN_ID)},
        {"typ": "description", "id": int(ALC_DESCRIPTION_ID)},
    ]


def build_2112_rows(p):
    """3 行 2112，列序按 25 列 schema。"""
    common_text_kvs = lambda label: f'"label":"{label}","title":"{label}"'

    text_personal = '{"group_label":"' + p["group_label_lc"] + '",' + common_text_kvs(p["personal_lc_name"]) + '}'
    text_server   = '{"group_label":"' + p["group_label_lc"] + '","label":"LC_EVENT_anni3_cityeffect_actv_name_2","title":"LC_EVENT_anni3_cityeffect_actv_name_2"}'
    text_alliance = '{"group_label":"' + p["group_label_lc"] + '","label":"LC_EVENT_cityeffect_actv_name_3","title":"LC_EVENT_cityeffect_actv_name_3"}'

    banner_dir = "assets/operation/P2dlcimg/activityImg/"

    rows = []
    # Personal
    rows.append([
        p["id_personal"],
        f"{p['cn']}{p['year']}-主城特效累充-个人",
        f"event_techFestival_{p['year']}_city_effect_single_{p['festival']}",
        "0", PRIORITY_PERSONAL, BASE_PERSONAL,
        FILTER_COMMON, text_personal,
        json.dumps(build_components_personal(p), separators=(",", ":")),
        DESCRIPTION_COMMON,
        UITPL_PERSONAL, "1", '""',
        banner_dir + p["banner_personal"], "1",
        "0", p["icon_dk"], p["show_hud"],
        "1", "[]", banner_dir + p["cal_banner"],
        "0", '""', "0", "0",
    ])
    # Server
    rows.append([
        p["id_server"],
        f"{p['cn']}{p['year']}-主城特效累充-服务器",
        f"event_techFestival_{p['year']}_city_effect_server_{p['festival']}",
        "0", PRIORITY_SERVER, BASE_SERVER,
        FILTER_COMMON, text_server,
        json.dumps(build_components_server(p), separators=(",", ":")),
        DESCRIPTION_COMMON,
        UITPL_SERVER, "1", '""',
        banner_dir + p["banner_server"], "1",
        "0", p["icon_dk"], p["show_hud"],
        "0", "[]", '""',
        "0", '""', "0", "0",
    ])
    # Alliance
    rows.append([
        p["id_alliance"],
        f"{p['cn']}{p['year']}-主城特效累充-联盟团购",
        f"event_{p['festival']}_{p['year']}_city_effect_alliance",
        "0", PRIORITY_ALLIANCE, BASE_ALLIANCE,
        FILTER_COMMON, text_alliance,
        json.dumps(build_components_alliance(p), separators=(",", ":")),
        DESCRIPTION_COMMON,
        p["alliance_ui_template"], "1", '""',
        banner_dir + p["banner_alliance"], "1",
        "0", p["icon_dk"], p["show_hud"],
        "0", "[]", '""',
        "0", '""', "0", "0",
    ])
    return rows


def build_2111_rows(p):
    base_id = p["calendar_base_id"]
    common = (
        '{"typ":"schema","id":[1,2,3,4,5,6]}',
        '{"typ":"time","is_ark":1}',
        "{}", "{}", "0", "0",
    )
    return [
        [str(base_id+0), p["id_personal"], f"{p['cn']}{p['year']}-主城特效累充-个人", *common],
        [str(base_id+1), p["id_server"],   f"{p['cn']}{p['year']}-主城特效累充-服务器", *common],
        [str(base_id+2), p["id_alliance"], f"{p['cn']}{p['year']}-主城特效累充-联盟团购", *common],
    ]


def build_2122_rows(p):
    """4 个 rank。score_rule.ids 按 source 决定（clone-spring / empty）。"""
    ids_pool = p["score_rule_ids_pool"]   # list of int
    return [
        [
            RANK_GROUP_PERSONAL, p["rank_personal_id"], f"{p['year']}{p['cn']}累充-个人充值排名",
            json.dumps([{"cat": RANK_CAT_PERSONAL_SHARED, "ids": ids_pool, "val": 1, "score": 1}], separators=(",", ":")),
            '{"typ":"overall"}', "1", "5", "392",
            "LC_EVENT_sport_person_rank", "LC_EVENT_rank_total",
            "15112516", "50000",
            f'["{RULE_DESC_LC}"]', "[]", "0", "{}", "22311156",
        ],
        [
            RANK_GROUP_SHARED, p["rank_shared_353_id"], f"{p['cn']}累充-个人充值排名-给服务器+联盟累充用，不下发排名",
            json.dumps([{"cat": RANK_CAT_PERSONAL_SHARED, "ids": ids_pool, "val": 1, "score": 1}], separators=(",", ":")),
            '{"typ":"overall"}', "1", "5", "0",
            "LC_EVENT_sport_person_rank", "LC_EVENT_rank_total",
            "15112516", "50000",
            f'["{RULE_DESC_LC}"]', "[]", "0", "{}", "22311156",
        ],
        [
            RANK_GROUP_SERVER, p["rank_server_id"], f"{p['year']}{p['cn']}累充-服务器充值排名1",
            json.dumps([{"cat": RANK_CAT_SERVER, "ids": [int(p["id_server"])], "val": 1, "score": 1}], separators=(",", ":")),
            '{"typ":"overall"}', "4", "5", "393",
            "LC_EVENT_sport_person_rank", "LC_EVENT_rank_total",
            "15112516", "500000",
            f'["{RULE_DESC_LC}"]', "[]", "0", "{}", "22311156",
        ],
        [
            RANK_GROUP_ALLIANCE, p["rank_alliance_id"], f"{p['year']}{p['cn']}累充-联盟充值排名",
            json.dumps([{"cat": RANK_CAT_ALLIANCE, "ids": [int(p["id_alliance"])], "val": 1, "score": 1}], separators=(",", ":")),
            '{"typ":"overall"}', "2", "5", "433",
            "LC_EVENT_sport_person_rank", "LC_EVENT_rank_total",
            "15112516", "0",
            f'["{RULE_DESC_LC}"]', "[]", "0", "{}", "22311156",
        ],
    ]


def build_2121_rows(p):
    """3 个 special 按 ID 升序：jump_link / actv_show_rank / countdown。"""
    return [
        [
            p["jump_link_id"], f"{p['year']}{p['cn']}-节日累充跳转",
            "jump_link", "[]", '{"id":' + str(p["access_group_id"]) + '}',
            "0", "0", "0", "[]", "NULL", "[]", "[]", "{}", "[]", "0",
        ],
        [
            p["actv_show_rank_id"], f"{p['year']}{p['cn']}累充-个人充值排名",
            "actv_show_rank", "[]", "{}",
            p["rank_personal_id"], "0", "0", "[]", "NULL", "[]", "[]", "{}", "[]", "0",
        ],
        [
            p["countdown_id"], f"{p['year']}{p['cn']}累充开奖倒计时",
            "server_recharge_countdown", "[]", "{}",
            "86400000", "0", "0", "[]", "NULL", "[]", "[]", "{}", "[]", "0",
        ],
    ]


def build_2115_rows(p):
    rows = []
    for i, tid in enumerate(p["task_ids"]):
        val = TASK_VALS[i]
        fincond = json.dumps({
            "cat": TASK_FINCOND_CAT,
            "arg": {"ids": [int(p["rank_personal_id"])]},
            "val": val,
            "op": "ge",
        }, separators=(",", ":"))
        reward = json.dumps(TASK_REWARDS[i], separators=(",", ":"))
        rows.append([
            TASK_GROUP, str(tid), f"主城特效累充-个人任务-{p['festival']}-{val}-{i+1}",
            TASK_SHOWCOND, fincond, "0", reward,
            RULE_DESC_LC, "{}", "{}", "99999", "0", "{}", "0", '""', "0", "0", "0",
        ])
    return rows


def build_1168_row(p):
    access_group = [
        {"id": ACCESS_GROUP_EFFECT_ID, "args": [str(x)]} for x in p["access_group_args"]
    ]
    return [
        str(p["access_group_id"]),
        f"{p['year']}{p['cn']}-主城特效个人累充活动",
        "",
        "non_item",
        json.dumps(access_group, separators=(",", ":")),
        ACCESS_GROUP_LC_NAME,
        "{}",
    ]


# =========================================================================
# 号段自动选择
# =========================================================================
def find_next_continuous_block(ss, tab, col_letter, start_id, length):
    """从 start_id 开始找 length 个连续空号。"""
    d = values_get(ss, f"{tab}!{col_letter}:{col_letter}")
    occupied = set()
    for r in d.get("values", []):
        if r and r[0].isdigit():
            occupied.add(int(r[0]))
    cand = start_id
    while True:
        block = [cand + i for i in range(length)]
        if not any(b in occupied for b in block):
            return block[0]
        cand += 1
        if cand > start_id + 1_000_000:
            raise RuntimeError("找不到 1M 范围内的空号块")


def find_2111_calendar_insert(ss):
    """2111 calendar 节日段：紧贴 21116001 占位符之前，新 ID = (max < 21116000) + 1。"""
    d = values_get(ss, f"{TAB_2111}!A:A")
    placeholder_row = None
    max_festival_id = 0
    for i, r in enumerate(d.get("values", [])):
        if not r or not r[0]:
            continue
        if r[0] == PLACEHOLDER_2111_ID:
            placeholder_row = i + 1
        elif r[0].isdigit():
            n = int(r[0])
            if 21115000 <= n < 21116000 and n > max_festival_id:
                max_festival_id = n
    if not placeholder_row:
        raise RuntimeError("找不到 21116001 占位符")
    return placeholder_row, max_festival_id + 1


def find_id_insert_row(ss, tab, col, target_id):
    """找到 ID 第一个 > target_id 的行，作为插入位置。表尾延伸时返回 grid+1。"""
    d = values_get(ss, f"{tab}!{col}:{col}")
    for i, r in enumerate(d.get("values", [])):
        if r and r[0].isdigit() and int(r[0]) > target_id:
            return i + 1
    # 表尾
    last_data_row = len([r for r in d.get("values", []) if r])
    return last_data_row + 1


def find_liusiyi_range(ss, tab, id_col, comment_col):
    """扫表里 'liusiyi占用' 标记，返回 (start_row_1based, end_row_1based, max_id_in_range)。
    起始行的 ID 一般是区间下限（如 212120000），末尾行的 ID 是区间上限（212130000）。
    新 ID 应取 max_id_in_range + 1（必须 < 末尾行 ID）。"""
    d = values_get(ss, f"{tab}!{id_col}:{comment_col}")
    rows = d.get("values", [])
    starts = []
    for ri, r in enumerate(rows):
        if not r:
            continue
        # 同时支持 col B 和 col C 含 'liusiyi占用'
        for col_idx in [1, 2]:
            if len(r) > col_idx and "liusiyi占用" in str(r[col_idx]):
                starts.append((ri + 1, r[0] if r[0].isdigit() else None))
                break
    if len(starts) < 2:
        return None
    # 取相邻一对作为区间
    s_row, s_id = starts[0]
    e_row, e_id = starts[1]
    # 区间内已用 ID 的 max（看 ID 列）
    max_in_range = int(s_id) if s_id else 0
    for ri in range(s_row, e_row - 1):
        r = rows[ri] if ri < len(rows) else []
        if r and r[0].isdigit():
            n = int(r[0])
            if e_id and n > int(e_id):
                continue
            if n > max_in_range:
                max_in_range = n
    return (s_row, e_row, max_in_range)


# =========================================================================
# Plan / Apply 准备
# =========================================================================
def prepare_plan(args):
    p = {
        "festival": args.festival,
        "cn": args.cn,
        "year": args.year,
        "id_personal": str(args.id_personal),
        "id_server": str(args.id_server),
        "id_alliance": str(args.id_alliance),
        "icon_dk": str(args.icon_dk),
        "show_hud": str(args.show_hud),
        "banner_personal": args.banner_personal,
        "banner_server": args.banner_server,
        "banner_alliance": args.banner_alliance,
        "cal_banner": args.cal_banner,
        "city_skin": str(args.city_skin),
        "access_group_args": [int(x) for x in args.access_group_args.split(",")],
        "alliance_ui_template": str(args.alliance_ui_template) if args.alliance_ui_template else UITPL_ALLIANCE_DEFAULT,
        "personal_lc_name": args.personal_lc_name or f"LC_EVENT_{args.festival}_cityeffect_actv_name",
    }

    # group_label LC：拓荒节特例 (2024labor 跨年沿用)
    if args.group_label_lc:
        p["group_label_lc"] = args.group_label_lc
    elif args.festival == "labor":
        p["group_label_lc"] = "LC_EVENT_2024labor_accum_recharge_event"
    else:
        p["group_label_lc"] = f"LC_EVENT_{args.year}{args.festival}_accum_recharge_event"

    # ---- 自动选号段（1168 / 2122 / 2121 / 2115 / 2111） ----
    # 1168
    d_1168 = values_get(SS_1168, f"{TAB_1168}!A:A")
    max_1168 = max((int(r[0]) for r in d_1168.get("values", []) if r and r[0].isdigit()), default=0)
    p["access_group_id"] = max_1168 + 1

    # 2122
    d_2122 = values_get(SS_2122, f"{TAB_2122}!B:B")
    max_2122 = max((int(r[0]) for r in d_2122.get("values", []) if r and r[0].isdigit()), default=0)
    p["rank_personal_id"]   = str(max_2122 + 1)
    p["rank_shared_353_id"] = str(max_2122 + 2)
    p["rank_server_id"]     = str(max_2122 + 3)
    p["rank_alliance_id"]   = str(max_2122 + 4)

    # 2121（按 ID 升序：jump_link < show_rank < countdown）
    # ⚠️ 必须落在 'liusiyi占用' 区间内（21212xxxx 段），不能用 21219xxx zhangting 段
    rng_2121 = find_liusiyi_range(SS_2121, TAB_2121, "A", "C")
    if not rng_2121:
        raise RuntimeError("2121 找不到 liusiyi 占用区间标记")
    p["liusiyi_2121_end_row"] = rng_2121[1]  # 末尾标记 row（插入位置 = 该 row 之前）
    base = rng_2121[2]
    p["jump_link_id"]      = str(base + 1)
    p["actv_show_rank_id"] = str(base + 2)
    p["countdown_id"]      = str(base + 3)

    # 2115 task：从 TASK_ID_BASE 找连续 11 空号
    p["task_ids"] = list(range(
        find_next_continuous_block(SS_2115, TAB_2115, "B", TASK_ID_BASE, 11),
        find_next_continuous_block(SS_2115, TAB_2115, "B", TASK_ID_BASE, 11) + 11
    ))

    # 2111 calendar
    placeholder_row, next_id = find_2111_calendar_insert(SS_2111)
    p["calendar_placeholder_row"] = placeholder_row
    p["calendar_base_id"] = next_id

    # score_rule.ids 占位
    if args.score_rule_ids_source == "clone-spring":
        spring_rank_row = find_row_by_value(SS_2122, TAB_2122, SPRING_RANK_FOR_IAP_IDS, col_letter="B")
        d = values_get(SS_2122, f"{TAB_2122}!D{spring_rank_row}")
        sr = json.loads(d["values"][0][0])
        p["score_rule_ids_pool"] = sr[0]["ids"]
    else:
        p["score_rule_ids_pool"] = []

    return p


# =========================================================================
# 命令实现：plan / apply / verify
# =========================================================================
def cmd_plan(args):
    p = prepare_plan(args)
    plan = {
        "params": {k: v for k, v in p.items() if k != "score_rule_ids_pool"},
        "score_rule_ids_pool_len": len(p["score_rule_ids_pool"]),
        "writes": {
            "1168": {
                "row": find_id_insert_row(SS_1168, TAB_1168, "A", p["access_group_id"]),
                "data": [build_1168_row(p)],
            },
            "2122": {
                "rows": build_2122_rows(p),
                "insert_at": find_id_insert_row(SS_2122, TAB_2122, "B", int(p["rank_personal_id"])),
            },
            "2121": {
                "rows": build_2121_rows(p),
                "insert_at": find_id_insert_row(SS_2121, TAB_2121, "A", int(p["jump_link_id"])),
            },
            "2115": {
                "rows": build_2115_rows(p),
                "insert_at": find_id_insert_row(SS_2115, TAB_2115, "B", p["task_ids"][0]),
            },
            "2112": {
                "rows": build_2112_rows(p),
                "insert_at": find_id_insert_row(SS_2112, TAB_2112, "A", int(p["id_personal"])),
            },
            "2111": {
                "rows": build_2111_rows(p),
                "insert_at": p["calendar_placeholder_row"],
            },
        },
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2, default=str))
    return plan


def _write_table(name, ss, sheet_id, tab, insert_at, rows, num_cols, id_col_idx):
    """写入 + 立即回读 + 延迟二次校验（防 sheets API 一致性窗口拿到旧值）。"""
    print(f"\n=== {name}: insert_at row {insert_at}, {len(rows)} rows ===")
    insert_or_append_rows(ss, sheet_id, insert_at, len(rows))
    end_row = insert_at + len(rows) - 1
    rng = f"{tab}!A{insert_at}:{col_letter(num_cols)}{end_row}"
    values_update(ss, rng, rows)

    expected_ids = [r[id_col_idx] for r in rows]

    # 回读 #1：立即
    res = values_get(ss, rng)
    got_ids = [r[id_col_idx] if len(r) > id_col_idx else "" for r in res.get("values", [])]
    if got_ids != expected_ids:
        raise AssertionError(f"{name} 即时回读不匹配: expected={expected_ids}, got={got_ids}")

    # 回读 #2：延迟 2s 再读，防 sheets API 写入还未提交的一致性窗口
    time.sleep(2)
    res2 = values_get(ss, rng)
    got_ids2 = [r[id_col_idx] if len(r) > id_col_idx else "" for r in res2.get("values", [])]
    if got_ids2 != expected_ids:
        raise AssertionError(f"{name} 延迟回读不匹配（疑似写入未持久化）: expected={expected_ids}, got={got_ids2}")
    print(f"  ✓ 写入 + 双重回读校验通过：IDs={expected_ids}")


def cmd_apply(args):
    p = prepare_plan(args)
    print("==== APPLY 开始（依赖顺序：1168 → 2122 → 2121 → 2115 → 2112 → 2111） ====")

    # 1) 1168 access_group
    _write_table(
        "1168 access_group", SS_1168, SHEETID_1168, TAB_1168,
        insert_at=find_id_insert_row(SS_1168, TAB_1168, "A", p["access_group_id"]),
        rows=[build_1168_row(p)],
        num_cols=7, id_col_idx=0,
    )

    # 2) 2122 rank
    _write_table(
        "2122 rank", SS_2122, SHEETID_2122, TAB_2122,
        insert_at=find_id_insert_row(SS_2122, TAB_2122, "B", int(p["rank_personal_id"])),
        rows=build_2122_rows(p),
        num_cols=17, id_col_idx=1,
    )

    # 3) 2121 special
    _write_table(
        "2121 special", SS_2121, SHEETID_2121, TAB_2121,
        insert_at=find_id_insert_row(SS_2121, TAB_2121, "A", int(p["jump_link_id"])),
        rows=build_2121_rows(p),
        num_cols=15, id_col_idx=0,
    )

    # 4) 2115 task
    _write_table(
        "2115 task", SS_2115, SHEETID_2115, TAB_2115,
        insert_at=find_id_insert_row(SS_2115, TAB_2115, "B", p["task_ids"][0]),
        rows=build_2115_rows(p),
        num_cols=18, id_col_idx=1,
    )

    # 5) 2112 main
    _write_table(
        "2112 main", SS_2112, SHEETID_2112, TAB_2112,
        insert_at=find_id_insert_row(SS_2112, TAB_2112, "A", int(p["id_personal"])),
        rows=build_2112_rows(p),
        num_cols=25, id_col_idx=0,
    )

    # 6) 2111 calendar
    _write_table(
        "2111 calendar", SS_2111, SHEETID_2111, TAB_2111,
        insert_at=p["calendar_placeholder_row"],
        rows=build_2111_rows(p),
        num_cols=9, id_col_idx=0,
    )

    print("\n✅ 6 张表全部写入并校验通过")
    return p


def cmd_verify(args):
    print(f"=== Verify 三件套 ID: 个人={args.id_personal} 服务器={args.id_server} 联盟={args.id_alliance} ===")
    fails = []
    # 2112 三行存在
    for tag, iid in [("个人", args.id_personal), ("服务器", args.id_server), ("联盟", args.id_alliance)]:
        row = find_row_by_value(SS_2112, TAB_2112, iid, "A")
        if not row:
            fails.append(f"2112 {tag}({iid}) 不存在")
        else:
            print(f"  ✓ 2112 {tag} {iid} -> row {row}")

    # 2111 calendar 三行（按 activity_id 找）
    for tag, iid in [("个人", args.id_personal), ("服务器", args.id_server), ("联盟", args.id_alliance)]:
        row = find_row_by_value(SS_2111, TAB_2111, iid, "B")
        if not row:
            fails.append(f"2111 calendar 引用 {tag}({iid}) 不存在")
        else:
            print(f"  ✓ 2111 -> 2112 {tag} 调度 row {row}")

    # 拉个人版 components 看依赖闭环
    p_row = find_row_by_value(SS_2112, TAB_2112, args.id_personal, "A")
    if p_row:
        d = values_get(SS_2112, f"{TAB_2112}!I{p_row}")
        comps = json.loads(d["values"][0][0])
        # 抽取关键依赖
        rank_id = next((c["id"] for c in comps if c.get("typ") == "rank"), None)
        jump_id = next((c["id"] for c in comps if c.get("typ") == "jump_link"), None)
        # rank 在 2122
        if rank_id:
            r_row = find_row_by_value(SS_2122, TAB_2122, str(rank_id), "B")
            if not r_row:
                fails.append(f"2122 个人 rank {rank_id} 不存在")
            else:
                print(f"  ✓ 2112 个人 rank {rank_id} -> 2122 row {r_row}")
        # jump_link 在 2121
        if jump_id:
            j_row = find_row_by_value(SS_2121, TAB_2121, str(jump_id), "A")
            if not j_row:
                fails.append(f"2121 jump_link {jump_id} 不存在")
            else:
                # 看 jump_link expr.id 是否非 0
                d_e = values_get(SS_2121, f"{TAB_2121}!E{j_row}")
                expr = json.loads(d_e["values"][0][0])
                if expr.get("id", 0) == 0:
                    fails.append(f"2121 jump_link {jump_id} expr.id 还是 0（1168 access_group 占位）")
                else:
                    ag_id = expr["id"]
                    ag_row = find_row_by_value(SS_1168, TAB_1168, str(ag_id), "A")
                    if not ag_row:
                        fails.append(f"1168 access_group {ag_id} 不存在")
                    else:
                        print(f"  ✓ 2121 -> 1168 access_group {ag_id} row {ag_row}")

    if fails:
        print("\n❌ 校验失败:")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("\n✅ 三件套依赖闭环校验通过")


# =========================================================================
# CLI
# =========================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("learn", help="Step0 自主学习")

    common_args = lambda p: (
        p.add_argument("--festival", required=True, help="英文 slug，如 labor / spring"),
        p.add_argument("--cn", required=True, help="节日中文名，如 拓荒节"),
        p.add_argument("--year", required=True, help="年份，如 2026"),
        p.add_argument("--id-personal", type=int, required=True),
        p.add_argument("--id-server", type=int, required=True),
        p.add_argument("--id-alliance", type=int, required=True),
        p.add_argument("--icon-dk", type=int, required=True),
        p.add_argument("--show-hud", type=int, required=True),
        p.add_argument("--banner-personal", required=True, help="EventBanner_BG_xxx.png"),
        p.add_argument("--banner-server", required=True),
        p.add_argument("--banner-alliance", required=True),
        p.add_argument("--cal-banner", required=True, help="EventBanner_Timeline_xxx.png"),
        p.add_argument("--city-skin", type=int, required=True, help="1312 套装最终皮肤 ID"),
        p.add_argument("--access-group-args", required=True,
                       help="1168 access_group 引用的 2112 活动 ID 列表（逗号分隔）。"
                            "🚨 每次必须问用户给定，不要替用户决定——这是当节日跳转的核心付费玩法清单。"
                            "示例：拓荒节2026 = 21127899,21127808,21127806（节日挖孔/推币机/弹珠GACHA）"),
        p.add_argument("--alliance-ui-template", default="", help="联盟版 UI 模板，默认 21191428 春节占位"),
        p.add_argument("--group-label-lc", default="", help="自定义 group_label LC；不传按节日年份生成（拓荒节特例 LC_EVENT_2024labor_accum_recharge_event）"),
        p.add_argument("--personal-lc-name", default="", help="个人版 label/title LC，默认 LC_EVENT_{slug}_cityeffect_actv_name"),
        p.add_argument("--score-rule-ids-source", choices=["clone-spring", "empty"], default="clone-spring"),
    )

    p_plan = sub.add_parser("plan", help="Dry-run，输出 6 表写入计划")
    common_args(p_plan)

    p_apply = sub.add_parser("apply", help="真写：6 表按依赖顺序")
    common_args(p_apply)

    p_verify = sub.add_parser("verify", help="校验三件套完整性")
    p_verify.add_argument("--id-personal", required=True)
    p_verify.add_argument("--id-server", required=True)
    p_verify.add_argument("--id-alliance", required=True)

    args = ap.parse_args()
    if args.cmd == "learn":
        cmd_learn(args)
    elif args.cmd == "plan":
        cmd_plan(args)
    elif args.cmd == "apply":
        cmd_apply(args)
    elif args.cmd == "verify":
        cmd_verify(args)


if __name__ == "__main__":
    main()
