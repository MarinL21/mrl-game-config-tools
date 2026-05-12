#!/usr/bin/env python3
"""
以科技节2026参考行为模板，apply PATCH 后写入拓荒节测试页签。
核心原则：未显式 PATCH 的字段 = 参考行原样（自动继承 ""/NULL/{}/[] 约定）。
"""
import json, subprocess, sys, re

def gws(args):
    r = subprocess.run(["gws"]+args, capture_output=True, text=True)
    out = r.stdout.strip()
    if out.startswith("Using keyring"):
        out = out.split("\n",1)[1] if "\n" in out else ""
    if r.returncode != 0:
        print(f"[gws ERR] {r.stderr}", file=sys.stderr); sys.exit(1)
    return out

def read_range(sid, rng):
    out = gws(["sheets","+read","--spreadsheet",sid,"--range",rng,"--format","json"])
    return json.loads(out)

def write_values(sid, rng, values):
    body = {"values":values,"majorDimension":"ROWS"}
    gws(["sheets","spreadsheets","values","update",
         "--params", json.dumps({"spreadsheetId":sid,"range":rng,"valueInputOption":"RAW"}),
         "--json", json.dumps(body)])

# 紧凑 JSON（跟正式表一致）
def cj(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",",":"))

# ========== 参考源 + patch ==========

TABLES = {
  "2112": {
    "sid": "1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E",
    "src_tab": "activity_config_qa",
    "test_tab": "activity_config_TEST_labor2026",
    "header_cols": 25,  # A:Y
    "range_letter": "Y",
    "refs": {
      "march":  1641,  # 科技节 21127569 行军特效礼包
      "unite":  1642,  # 科技节 21127570 联动礼包
    },
  },
  "2135": {
    "sid": "1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc",
    "src_tab": "activity_event_pkg",
    "test_tab": "activity_event_pkg_TEST_labor2026",
    "header_cols": 13,
    "range_letter": "M",
    "refs": {"march": 4677},  # 科技节 21359396
  },
  "2011": {
    "sid": "1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc",
    "src_tab": "iap_config_QA",
    "test_tab": "iap_config_TEST_labor2026",
    "header_cols": 20,
    "range_letter": "T",
    "refs": {"march": 5021},  # 2011500696
  },
  "2013": {
    "sid": "1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY",
    "src_tab": "iap_template_QA",
    "test_tab": "iap_template_TEST_labor2026",
    "header_cols": 31,
    "range_letter": "AE",
    "refs": {"march": 9267},  # 2013510996
  },
  "2121": {
    "sid": "1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc",
    "src_tab": "activity_special_QA",
    "test_tab": "activity_special_TEST_labor2026",
    "header_cols": 15,
    "range_letter": "O",
    "refs": {"unite": 2761},  # 科技节 21217498
  },
}

# 测试 ID
IDS = {
  "march_actv":21129001, "unite_actv":21129002,
  "pkg_2135":21359990,   "iap_2011":2011510011, "tpl_2013":2013560124,
  "unite_2121":21219624, "emoji_tpl_existing":2013560123,  # 已落 QA 的拓荒节行军表情 IAP 模板
}

# 行军特效永久版 item_id 和联动头像框 item_id 用占位
PH = {"march_effect_forever":111110328, "unite_avatar_frame":111110329}

# 拓荒节可复用的 item_id（来自最终清单）
LABOR = {"festival_item":11112150, "festival_box":111110325, "growth":11118663, "alliance_chest":11114316, "xp":11161002}

# 拓荒节 show_hud（和行军表情最终版 21129000 一致）
LABOR_SHOW_HUD = 21680031

def patch_row(ref_row, hdr_map, patches):
    """以 ref_row 为基础，按 patches 覆写指定字段。返回新 row。"""
    row = list(ref_row)
    # pad 到 header 长度
    while len(row) < len(hdr_map): row.append("")
    for field, val in patches.items():
        idx = hdr_map[field]
        row[idx] = str(val) if not isinstance(val, str) else val
    return row

def read_header(t):
    data = read_range(t["sid"], f'{t["src_tab"]}!A1:{t["range_letter"]}1')
    return data["values"][0]

def read_ref_row(t, row_num):
    data = read_range(t["sid"], f'{t["src_tab"]}!A{row_num}:{t["range_letter"]}{row_num}')
    row = data["values"][0]
    return row

def ensure_test_tab(t):
    """保证测试页签存在且紧贴 QA 主页签右侧。若不存在则创建并写入表头。"""
    meta = json.loads(gws(["sheets","spreadsheets","get",
                           "--params", json.dumps({"spreadsheetId": t["sid"]}),
                           "--format","json"]))
    name_to_prop = {sh["properties"]["title"]: sh["properties"] for sh in meta.get("sheets",[])}
    main_idx = name_to_prop.get(t["src_tab"], {}).get("index")
    if main_idx is None:
        raise RuntimeError(f"main tab not found: {t['src_tab']}")
    target_idx = main_idx + 1
    if t["test_tab"] in name_to_prop:
        cur_idx = name_to_prop[t["test_tab"]]["index"]
        if cur_idx != target_idx:
            body = {"requests":[{"updateSheetProperties":{
                "properties":{"sheetId": name_to_prop[t["test_tab"]]["sheetId"],"index":target_idx},
                "fields":"index"}}]}
            gws(["sheets","spreadsheets","batchUpdate",
                 "--params", json.dumps({"spreadsheetId":t["sid"]}),
                 "--json", json.dumps(body)])
            print(f"[OK] {t['test_tab']}: moved idx {cur_idx} -> {target_idx}")
        else:
            print(f"[OK] {t['test_tab']}: already at idx {target_idx}")
        return
    # 新建，直接贴着主页签
    body = {"requests":[{"addSheet":{"properties":{"title":t["test_tab"],"index":target_idx}}}]}
    gws(["sheets","spreadsheets","batchUpdate",
         "--params", json.dumps({"spreadsheetId":t["sid"]}),
         "--json", json.dumps(body)])
    # 写表头（从源页签 copy）
    hdr = read_header(t)
    write_values(t["sid"], f'{t["test_tab"]}!A1:{t["range_letter"]}1', [hdr])
    print(f"[OK] {t['test_tab']}: created at idx {target_idx} + header written")

def do_2112():
    t = TABLES["2112"]
    hdr = read_header(t)
    hdr_map = {h:i for i,h in enumerate(hdr)}
    march_ref = read_ref_row(t, t["refs"]["march"])
    unite_ref = read_ref_row(t, t["refs"]["unite"])

    # 科技节特效 filter 里 iap_purchases.id = 2013510996 → 换成拓荒节测试的 2013560124
    march_filter = json.loads(march_ref[hdr_map["A_MAP_filter"]])
    for arg in march_filter.get("args", []):
        if arg.get("typ") == "iap_purchases":
            arg["id"] = IDS["tpl_2013"]

    march_patch = {
      "A_INT_id": IDS["march_actv"],
      "S_STR_comment": "拓荒节2026-行军特效礼包",
      "A_STR_constant": "event_march_effect_2026_labor",
      "A_MAP_filter": cj(march_filter),
      "A_ARR_activity_components": cj([{"typ":"package","id":IDS["pkg_2135"]}]),
      "A_INT_show_hud": LABOR_SHOW_HUD,
    }
    unite_patch = {
      "A_INT_id": IDS["unite_actv"],
      "S_STR_comment": "联动礼包-2026拓荒节",
      "A_STR_constant": "event_unite_3labor_2026",
      "A_ARR_activity_components": cj([{"typ":"unite_pkg","id":IDS["unite_2121"]}]),
      "A_INT_show_hud": LABOR_SHOW_HUD,
    }
    march_new = patch_row(march_ref, hdr_map, march_patch)
    unite_new = patch_row(unite_ref, hdr_map, unite_patch)
    # 写入测试页签 Row 2 / Row 3（Row 1 已是表头）
    write_values(t["sid"], f'{t["test_tab"]}!A2:{t["range_letter"]}3', [march_new, unite_new])
    print(f"[OK] 2112: rebuilt 2 rows")

def do_2135():
    t = TABLES["2135"]
    hdr = read_header(t); hdr_map = {h:i for i,h in enumerate(hdr)}
    ref = read_ref_row(t, t["refs"]["march"])
    patch = {
      "A_INT_id": IDS["pkg_2135"],
      "N_STR_comment": "2026拓荒节行军特效礼包",
      "A_INT_iap": IDS["iap_2011"],
    }
    new = patch_row(ref, hdr_map, patch)
    write_values(t["sid"], f'{t["test_tab"]}!A2:{t["range_letter"]}2', [new])
    print(f"[OK] 2135: rebuilt 1 row")

def do_2011():
    t = TABLES["2011"]
    hdr = read_header(t); hdr_map = {h:i for i,h in enumerate(hdr)}
    ref = read_ref_row(t, t["refs"]["march"])
    patch = {
      "A_INT_id": IDS["iap_2011"],
      "N_STR_pkg_desc": "2026拓荒节-行军特效礼包",
      "A_MAP_time_info": cj({"normal":[{"actv_id":IDS["march_actv"]}]}),
      "A_ARR_iap_status": "[]",   # 测试阶段留空，等累充确认
    }
    new = patch_row(ref, hdr_map, patch)
    write_values(t["sid"], f'{t["test_tab"]}!A2:{t["range_letter"]}2', [new])
    print(f"[OK] 2011: rebuilt 1 row")

def do_2013():
    t = TABLES["2013"]
    hdr = read_header(t); hdr_map = {h:i for i,h in enumerate(hdr)}
    ref = read_ref_row(t, t["refs"]["march"])
    # 奖励数组：替换 item_id,保持结构与正式表一致
    other_items = [
      {"asset":{"typ":"xp","id":LABOR["xp"],"val":5000},"setting":{"serial_number":0,"ishighlight":False}},
      {"asset":{"typ":"item","id":PH["march_effect_forever"],"val":1},"setting":{"serial_number":999,"ishighlight":True}},
      {"asset":{"typ":"item","id":LABOR["festival_item"],"val":20},"setting":{"serial_number":200,"ishighlight":True}},
      {"asset":{"typ":"item","id":LABOR["festival_box"],"val":10},"setting":{"serial_number":100,"ishighlight":True}},
      {"asset":{"typ":"item","id":LABOR["growth"],"val":10},"setting":{"serial_number":10,"ishighlight":False}},
      {"asset":{"typ":"item","id":LABOR["alliance_chest"],"val":1},"setting":{"serial_number":1,"ishighlight":False}},
    ]
    patch = {
      "A_INT_id": IDS["tpl_2013"],
      "A_INT_config_id": IDS["iap_2011"],
      "N_STR_temp_desc": "2026拓荒节-行军特效19.99",
      "A_ARR_other_items": cj(other_items),
    }
    new = patch_row(ref, hdr_map, patch)
    write_values(t["sid"], f'{t["test_tab"]}!A2:{t["range_letter"]}2', [new])
    print(f"[OK] 2013: rebuilt 1 row")

def do_2121():
    t = TABLES["2121"]
    hdr = read_header(t); hdr_map = {h:i for i,h in enumerate(hdr)}
    ref = read_ref_row(t, t["refs"]["unite"])  # 科技节联动 21217498
    # 联动 reward: 保留科技节的 3 项（活动道具/自选箱/成长），仅替换 item_id
    reward = [
      {"asset":{"typ":"item","id":PH["unite_avatar_frame"],"val":1},"setting":{"serial_number":5,"ishighlight":False}},
      {"asset":{"typ":"item","id":LABOR["festival_item"],"val":20},"setting":{"serial_number":5,"ishighlight":False}},
      {"asset":{"typ":"item","id":LABOR["festival_box"],"val":10},"setting":{"serial_number":5,"ishighlight":False}},
      {"asset":{"typ":"item","id":LABOR["growth"],"val":5},"setting":{"serial_number":5,"ishighlight":False}},
    ]
    # expr: 替换 args[].id → 拓荒节两个 2013 模板
    expr = json.loads(ref[hdr_map["A_MAP_expr"]])
    if len(expr.get("args",[])) >= 2:
        expr["args"][0]["id"] = IDS["emoji_tpl_existing"]  # 已落 QA 的拓荒节表情礼包
        expr["args"][1]["id"] = IDS["tpl_2013"]            # 本次测试新建的特效礼包
    patch = {
      "A_INT_id": IDS["unite_2121"],
      "C_STR_comment": "联动礼包-拓荒节2026行军特效表情",
      "A_ARR_reward": cj(reward),
      "A_MAP_expr": cj(expr),
    }
    new = patch_row(ref, hdr_map, patch)
    write_values(t["sid"], f'{t["test_tab"]}!A2:{t["range_letter"]}2', [new])
    print(f"[OK] 2121: rebuilt 1 row")

if __name__ == "__main__":
    # 先保证 5 张测试页签都存在、都紧贴 QA 主页签
    for k in TABLES:
        ensure_test_tab(TABLES[k])
    print()
    do_2112(); do_2135(); do_2011(); do_2013(); do_2121()
    print("All done.")
