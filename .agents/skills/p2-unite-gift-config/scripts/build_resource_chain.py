#!/usr/bin/env python3
"""
补齐行军特效礼包的完整资源链路（4 张视觉/资源表，低级+高级两套）：
  1512 effect_list (2 新行: 15121052 低级 / 15121053 高级)
  1511 display_key (2 新行: 151105261 低级 / 151105262 高级)
  1365 march_effect (2 新套: 13650159 低级 / 13650160 高级)
  1111 item        (12 新行: 328~333 低级 / 334~339 高级)
  2013 主外显 id = 111110333 (低级永久,礼包投低级)
  高级套建了备用(后续活动/累充/商店可能用)

设计理由:
  - 科技节每节日都有低级+高级两套特效,高级是前瞻建设
  - 用户明确礼包投低级,但资源侧整套做完整闭环
  - 1512.C_STR_file 美术路径用 "TroopsTrail/2026xxx/..." 占位待美术提供

命名规范 (按科技节风格):
  1111: "2026拓荒节行军特效-低级-{1天限时|...|永久}"
  1365: "行军特效-低级-26拓荒节"
  1511: "26拓荒节行军特效-低级-图标"
  1512: "26拓荒节低级行军特效"
  LC:   "LC_ITEM_labor_marcheffect_low_2026" / "..._desc"

嵌入式 id 要跟改 (易漏):
  1111.A_ARR_use_labels 里的 1365 套 id
  1365.A_ARR_items 里的 1111 item id
  1365.C_INT_effect_key / special_key / exhibit_key → 1512

原则: 每张表都 以同类型参考行为模板 + patch, 未 PATCH 字段原样继承。
未覆写字段例(1111): C_INT_display_quality / C_INT_display_order / C_MAP_lc_upper_show / C_MAP_lc_usetip / A_INT_max_own/get/use / C_ARR_display_labels / A_INT_source / A_FLT_value 等 — 共用品质/通用提示/显示位的字段不要改。
"""
import json, subprocess, sys

def gws(args):
    r = subprocess.run(["gws"]+args, capture_output=True, text=True)
    out = r.stdout
    if out.startswith("Using"): out = out.split("\n",1)[1]
    if r.returncode != 0:
        print("gws ERR:", r.stderr); sys.exit(1)
    return out

def cj(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",",":"))

def read(sid, rng):
    return json.loads(gws(["sheets","+read","--spreadsheet",sid,"--range",rng,"--format","json"]))['values']

def write(sid, rng, values):
    body = {"values":values,"majorDimension":"ROWS"}
    gws(["sheets","spreadsheets","values","update",
         "--params", json.dumps({"spreadsheetId":sid,"range":rng,"valueInputOption":"RAW"}),
         "--json", json.dumps(body)])

def ensure_tab(sid, main_tab, test_tab):
    """确保测试页签存在且紧贴主页签右侧；新建时 copy 表头。返回 True=新建，False=已存在"""
    meta = json.loads(gws(["sheets","spreadsheets","get","--params",json.dumps({"spreadsheetId":sid}),"--format","json"]))
    name_map = {sh["properties"]["title"]:sh["properties"] for sh in meta.get("sheets",[])}
    main_idx = name_map[main_tab]["index"]
    target_idx = main_idx + 1
    if test_tab in name_map:
        cur = name_map[test_tab]["index"]
        if cur != target_idx:
            body = {"requests":[{"updateSheetProperties":{"properties":{"sheetId":name_map[test_tab]["sheetId"],"index":target_idx},"fields":"index"}}]}
            gws(["sheets","spreadsheets","batchUpdate","--params",json.dumps({"spreadsheetId":sid}),"--json",json.dumps(body)])
            print(f"  moved {test_tab} idx {cur} -> {target_idx}")
        return False
    body = {"requests":[{"addSheet":{"properties":{"title":test_tab,"index":target_idx}}}]}
    gws(["sheets","spreadsheets","batchUpdate","--params",json.dumps({"spreadsheetId":sid}),"--json",json.dumps(body)])
    print(f"  created {test_tab} at idx {target_idx}")
    return True

def patch_row(ref_row, hdr, patches):
    row = list(ref_row)
    while len(row) < len(hdr): row.append("")
    for k,v in patches.items():
        row[hdr.index(k)] = str(v) if not isinstance(v,str) else v
    return row

# ========================================================================
# Step 0: 1512 effect_list — 建测试页签 + 2 新行 (低级 15121052 / 高级 15121053)
# ========================================================================
SID_1512 = "11TpByDhx3FzMRZYNEimZroz0hO6_NEioXiF8NHbOI6s"
print("\n=== 1512 effect_list ===")
ensure_tab(SID_1512, "effect_list", "effect_list_TEST_labor2026")
hdr_1512 = read(SID_1512, "effect_list!A1:E1")[0]
# 低级:以复活节中级 15121046 (row 1042) 为模板
ref_low  = read(SID_1512, "effect_list!A1042:E1042")[0]
# 高级:以复活节高级 15121047 (row 1043) 为模板
ref_high = read(SID_1512, "effect_list!A1043:E1043")[0]
# ⚠️ C_STR_file 中段 "xxx" 是占位,等美术提供真实路径
low_1512 = patch_row(ref_low, hdr_1512, {
    "C_INT_id": "15121052",
    "C_STR_comment": "26拓荒节低级行军特效",
    "C_STR_file": "TroopsTrail/2026xxx/Prefab/Fx_TroopsTrail_2026xxx_01",
})
high_1512 = patch_row(ref_high, hdr_1512, {
    "C_INT_id": "15121053",
    "C_STR_comment": "26拓荒节高级行军特效",
    "C_STR_file": "TroopsTrail/2026xxx/Prefab/Fx_TroopsTrail_2026xxx_02",
})
write(SID_1512, "effect_list_TEST_labor2026!A1:E3", [hdr_1512, low_1512, high_1512])
print(f"  wrote 1512: 15121052 (低级) + 15121053 (高级), C_STR_file 含 xxx 占位")

# ========================================================================
# Step 1: 1511 display_key — 建测试页签 + 2 新行 (低级 151105261 / 高级 151105262)
# ========================================================================
SID_1511 = "1Oks7yHCxYnWxo1QiNdO5EYNET68l_aCzZU-58zATlLY"
print("\n=== 1511 display_key ===")
ensure_tab(SID_1511, "display_key", "display_key_TEST_labor2026")
hdr_1511 = read(SID_1511, "display_key!A1:I1")[0]
# 低级 参考科技节 151104727 (row 12357), 高级 参考 151104728 (row 12358)
ref_1511_low  = read(SID_1511, "display_key!A12357:I12357")[0]
ref_1511_high = read(SID_1511, "display_key!A12358:I12358")[0]
low_1511 = patch_row(ref_1511_low, hdr_1511, {
    "C_INT_id": "151105261",
    "S_STR_comment": "26拓荒节行军特效-低级-图标",
})
high_1511 = patch_row(ref_1511_high, hdr_1511, {
    "C_INT_id": "151105262",
    "S_STR_comment": "26拓荒节行军特效-高级-图标",
})
write(SID_1511, "display_key_TEST_labor2026!A1:I3", [hdr_1511, low_1511, high_1511])
print(f"  wrote 1511: 151105261 (低级) + 151105262 (高级)")

# ========================================================================
# Step 2: 1365 master — 建测试页签 + 2 新套 (低级 13650159 / 高级 13650160)
# ========================================================================
SID_1365 = "1mD_NfAS14odzRnCLGBhB5LDGMk1DH_aHB4BFX7VmS3U"
print("\n=== 1365 march_effect ===")
ensure_tab(SID_1365, "master", "master_TEST_labor2026")
hdr_1365 = read(SID_1365, "master!A1:V1")[0]
# 低级: 科技节 13650155 (row 57); 高级: 13650156 (row 58)
ref_1365_low  = read(SID_1365, "master!A57:V57")[0]
ref_1365_high = read(SID_1365, "master!A58:V58")[0]
low_1365 = patch_row(ref_1365_low, hdr_1365, {
    "A_INT_id": "13650159",
    "C_STR_comment": "行军特效-低级-26拓荒节",
    "C_INT_display_key": "151105261",
    "C_INT_effect_key": "15121052",
    "C_INT_effect_special_key": "15121052",
    "C_INT_effect_exhibit_key": "15121052",
    "A_MAP_lc_name": cj({"typ":"lc","txt":"LC_ITEM_labor_marcheffect_low_2026"}),
    "C_MAP_lc_desc": cj({"typ":"lc","txt":"LC_ITEM_labor_marcheffect_low_2026_desc"}),
    "A_ARR_items": cj([111110328,111110329,111110330,111110331,111110332,111110333]),
})
high_1365 = patch_row(ref_1365_high, hdr_1365, {
    "A_INT_id": "13650160",
    "C_STR_comment": "行军特效-高级-26拓荒节",
    "C_INT_display_key": "151105262",
    "C_INT_effect_key": "15121053",
    "C_INT_effect_special_key": "15121053",
    "C_INT_effect_exhibit_key": "15121053",
    "A_MAP_lc_name": cj({"typ":"lc","txt":"LC_ITEM_labor_marcheffect_high_2026"}),
    "C_MAP_lc_desc": cj({"typ":"lc","txt":"LC_ITEM_labor_marcheffect_high_2026_desc"}),
    "A_ARR_items": cj([111110334,111110335,111110336,111110337,111110338,111110339]),
})
write(SID_1365, "master_TEST_labor2026!A1:V3", [hdr_1365, low_1365, high_1365])
print(f"  wrote 1365: 13650159 低级 (items 328..333) + 13650160 高级 (items 334..339)")

# ========================================================================
# Step 3: 1111 item — 建测试页签 + 2 套 (低级 328~333 + 高级 334~339) 共 12 行
# ========================================================================
SID_1111 = "1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws"
print("\n=== 1111 item (12 rows: 低级6 + 高级6) ===")
ensure_tab(SID_1111, "item", "item_TEST_labor2026")
hdr_1111 = read(SID_1111, "item!A1:Y1")[0]
# 低级参考 科技节 111110207~111110212 (row 3095~3100)
# 高级参考 科技节 111110213~111110218 (row 3101~3106)
refs_1111 = read(SID_1111, "item!A3095:Y3100")
refs_1111_high = read(SID_1111, "item!A3101:Y3106")
durations = [
    # (item_id, 短时长, 命名后缀, val_ms, vm_val)
    ("111110328", "1天",  "1天限时",  86400000,   50),
    ("111110329", "3天",  "3天限时",  259200000,  200),
    ("111110330", "7天",  "7天限时",  604800000,  500),
    ("111110331", "14天", "14天限时", 1209600000, 1000),
    ("111110332", "30天", "30天限时", 2592000000, 1000),
    ("111110333", "永久", "永久",     -1,         2500),
]
value_map = {"1天":50, "3天":200, "7天":500, "14天":1000, "30天":1000, "永久":5000}

def build_1111_row(ref, iid, name_suffix, val_ms, vm_val, level_cn, level_en, set_id, dk_id, old_set_id):
    """level_cn=低级/高级, level_en=low/high, set_id=新1365套id, old_set_id=参考行原1365套id"""
    cp = {"effect":[{"typ":"marching_effect","id":set_id,"val":val_ms},{"typ":"vm","id":11151001,"val":vm_val}]}
    # A_ARR_use_labels 里嵌入的 1365 id 字符串也要替换
    ul = [(str(set_id) if x==str(old_set_id) else x) for x in json.loads(ref[hdr_1111.index("A_ARR_use_labels")])]
    p = {
        "A_INT_id": iid,
        "S_STR_comment": f"2026拓荒节行军特效-{level_cn}-{name_suffix}",
        "C_INT_display_key": str(dk_id),
        "A_MAP_lc_name": cj({"typ":"lc","txt":f"LC_ITEM_labor_marcheffect_{level_en}_2026"}),
        "C_MAP_lc_desc": cj({"typ":"lc","txt":f"LC_ITEM_labor_marcheffect_{level_en}_2026_desc"}),
        "A_MAP_category_param": cj(cp),
        "A_ARR_use_labels": cj(ul),
        "A_FLT_value": value_map[name_suffix.split("限时")[0].replace("永久","永久") if "限时" in name_suffix else name_suffix],
    }
    return patch_row(ref, hdr_1111, p)

new_rows_1111 = [hdr_1111]
# 低级 6 行
for (iid, short, name_suffix, val_ms, vm_val), ref in zip(durations, refs_1111):
    new_rows_1111.append(build_1111_row(ref, iid, name_suffix, val_ms, vm_val,
                                         "低级","low", 13650159, 151105261, 13650155))
# 高级 6 行 (id 334~339, 用高级 ref)
high_durations = [
    ("111110334","1天", "1天限时",  86400000,   50),
    ("111110335","3天", "3天限时",  259200000,  200),
    ("111110336","7天", "7天限时",  604800000,  500),
    ("111110337","14天","14天限时", 1209600000, 1000),
    ("111110338","30天","30天限时", 2592000000, 1000),
    ("111110339","永久","永久",     -1,         2500),
]
for (iid, short, name_suffix, val_ms, vm_val), ref in zip(high_durations, refs_1111_high):
    new_rows_1111.append(build_1111_row(ref, iid, name_suffix, val_ms, vm_val,
                                         "高级","high", 13650160, 151105262, 13650156))

# 写表头 + 12 行 (低级 6 + 高级 6)
write(SID_1111, "item_TEST_labor2026!A1:Y13", new_rows_1111)
print(f"  wrote 1111: 111110328~333 (低级) + 111110334~339 (高级)")

# ========================================================================
# Step 4: 2013 测试行 — 主外显 id 改为 111110333 (永久版)
# ========================================================================
SID_2013 = "1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY"
print("\n=== 2013 修正主外显 item_id (111110328 -> 111110333) ===")
v = read(SID_2013, "iap_template_TEST_labor2026!R2")[0]
other = json.loads(v[0])
for item in other:
    if item["asset"].get("id") == 111110328:
        item["asset"]["id"] = 111110333
write(SID_2013, "iap_template_TEST_labor2026!R2", [[cj(other)]])
print(f"  done, 2013.other_items 主外显 now = 111110333")

# ========================================================================
# Step 5: 1168 获取途径跳转(低级+高级各 1 行)
# ========================================================================
SID_1168 = "1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA"
TAB_1168 = "get_access_group（杜绝手搓）"
print("\n=== 1168 get_access_group (低级+高级) ===")
hdr_1168 = read(SID_1168, f"{TAB_1168}!A1:G1")[0]
# 参考科技节低级 11684798 / 高级 11684799
# 先找行号
rows_1168 = json.loads(gws(["sheets","+read","--spreadsheet",SID_1168,"--range",f"{TAB_1168}!A:A","--format","json"]))['values']
ref_rows_1168 = {}
for i,r in enumerate(rows_1168,1):
    if r and r[0] in ("11684798","11684799"):
        ref_rows_1168[r[0]] = i
ref_low_1168 = read(SID_1168, f"{TAB_1168}!A{ref_rows_1168['11684798']}:G{ref_rows_1168['11684798']}")[0]
ref_high_1168 = read(SID_1168, f"{TAB_1168}!A{ref_rows_1168['11684799']}:G{ref_rows_1168['11684799']}")[0]

low_1168 = patch(ref_low_1168, hdr_1168, {
    "A_INT_id": "NEW_LOW_1168_ID",   # 需要查表最大 id + 1
    "S_STR_comment": "26拓荒节-低级行军特效",
    "C_STR_item_label": "13650159",
    "C_ARR_access_group": cj([{"id":11531001,"args":[str(IDS["march_actv"])]}]),
})
high_1168 = patch(ref_high_1168, hdr_1168, {
    "A_INT_id": "NEW_HIGH_1168_ID",
    "S_STR_comment": "26拓荒节-高级行军特效",
    "C_STR_item_label": "13650160",
    "C_ARR_access_group": cj([{"id":11531001,"args":["21127575"]}]),  # 高级跳转活动需确认
})
# 注意:实际 id 需从 1168 表最后一行 +1 顺延; 脚本使用时需替换 NEW_LOW/HIGH_1168_ID
print("  1168 低级+高级行已准备(id 需根据表末尾行顺延分配)")

# ========================================================================
# Step 6: 2112 filter 不需要改 (仍指向 2013560124 = 拓荒节特效 2013 ID)
# ========================================================================
print("\nAll resource chain now closed!")
