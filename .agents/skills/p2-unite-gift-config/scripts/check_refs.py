#!/usr/bin/env python3
"""深度校验资源链路：从 2013/2121 引用开始，递归跟进到 1111/1365/1180/1511/1512，主/测试页签都查。

原则：
- 列出所有从顶层到叶子的引用关系 (id→id)
- 每个 id 都要能在对应表(主/测试页签任一)找到行
- 若缺失 → 标红 ❌；若找到 → ✓ 并列出行号
"""
import json, subprocess

def gws(args):
    r = subprocess.run(["gws"]+args, capture_output=True, text=True).stdout
    if r.startswith("Using"): r = r.split("\n",1)[1]
    return r

def a_col(sid, tab):
    try:
        d = json.loads(gws(["sheets","+read","--spreadsheet",sid,"--range",f"{tab}!A:A","--format","json"]))
        return {r[0]:i+1 for i,r in enumerate(d.get("values",[])) if r}
    except Exception:
        return {}

# 索引所有资源表(主页签 + 测试页签)
SHEETS = {
  "1111": ("1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws","item","item_TEST_labor2026"),
  "1365": ("1mD_NfAS14odzRnCLGBhB5LDGMk1DH_aHB4BFX7VmS3U","master","master_TEST_labor2026"),
  "1180": ("1SloOHvSFrEJz7HaU8yur9Qt8dOzsmqa69DUBERkkBmw","qa",None),
  "1511": ("1Oks7yHCxYnWxo1QiNdO5EYNET68l_aCzZU-58zATlLY","display_key","display_key_TEST_labor2026"),
  "1168": ("1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA","get_access_group（杜绝手搓）",None),
  "1512": ("11TpByDhx3FzMRZYNEimZroz0hO6_NEioXiF8NHbOI6s","effect_list","effect_list_TEST_labor2026"),
}
INDEXES = {}
for k,(sid,main,test) in SHEETS.items():
    INDEXES[k] = [a_col(sid, main)]
    if test: INDEXES[k].append(a_col(sid, test))

def find(table, iid):
    iid = str(iid)
    for i, idx in enumerate(INDEXES[table]):
        if iid in idx:
            tag = "主页签" if i==0 else "测试页签"
            return f"✓ {table} {tag} row {idx[iid]}"
    return f"❌ {table} 缺失"

missing = 0

def check_line(label, status):
    global missing
    if "❌" in status: missing += 1
    print(f"  {label} → {status}")

# ====== 2013 other_items → 1111 ======
print("=== 2013 测试行 other_items ===")
v = json.loads(gws(["sheets","+read","--spreadsheet","1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY","--range","iap_template_TEST_labor2026!R2","--format","json"]))['values'][0][0]
for x in json.loads(v):
    a = x['asset']
    if a['typ']=='xp':
        print(f"  id={a['id']:<12} xp   → skip")
    else:
        check_line(f"id={a['id']:<12} item", find('1111', a['id']))

# ====== 2121 reward → 1111 ======
print("\n=== 2121 联动 reward ===")
v = json.loads(gws(["sheets","+read","--spreadsheet","1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc","--range","activity_special_TEST_labor2026!D2","--format","json"]))['values'][0][0]
for x in json.loads(v):
    a = x['asset']
    check_line(f"id={a['id']:<12} item", find('1111', a['id']))

# ====== 1111 测试页签每行 → 1365 / 1511 / use_labels 里嵌入的 1365 ======
print("\n=== 1111 测试行 - 全量 ===")
HDR_1111 = json.loads(gws(["sheets","+read","--spreadsheet","1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws","--range","item!A1:Y1","--format","json"]))['values'][0]
all_1111 = json.loads(gws(["sheets","+read","--spreadsheet","1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws","--range","item_TEST_labor2026!A2:Y100","--format","json"])).get('values',[])
for r in all_1111:
    while len(r) < len(HDR_1111): r.append("")
    iid = r[0]
    if not iid: continue
    dk = r[HDR_1111.index("C_INT_display_key")]
    cp = json.loads(r[HDR_1111.index("A_MAP_category_param")] or "{}")
    ul = json.loads(r[HDR_1111.index("A_ARR_use_labels")] or "[]")
    for eff in cp.get("effect",[]):
        if eff['typ']=='marching_effect':
            check_line(f"{iid} category_param → 1365 id={eff['id']}", find('1365', eff['id']))
        elif eff['typ']=='map_emoji':
            check_line(f"{iid} category_param → 1180 id={eff['id']}", find('1180', eff['id']))
    # use_labels 里含 1365 套 id 字符串 (非 "bag" 开头的数字)
    for lab in ul:
        if lab.isdigit() and lab.startswith("1365"):
            check_line(f"{iid} use_labels → 1365 id={lab}", find('1365', lab))
    check_line(f"{iid} display_key → 1511 id={dk}", find('1511', dk))

# ====== 1365 测试页签每行 → 1111 (items双向) / 1511 / 1512 ======
print("\n=== 1365 测试行 - 全量 ===")
HDR_1365 = json.loads(gws(["sheets","+read","--spreadsheet","1mD_NfAS14odzRnCLGBhB5LDGMk1DH_aHB4BFX7VmS3U","--range","master!A1:V1","--format","json"]))['values'][0]
all_1365 = json.loads(gws(["sheets","+read","--spreadsheet","1mD_NfAS14odzRnCLGBhB5LDGMk1DH_aHB4BFX7VmS3U","--range","master_TEST_labor2026!A2:V100","--format","json"])).get('values',[])
for r in all_1365:
    while len(r) < len(HDR_1365): r.append("")
    iid = r[0]
    if not iid: continue
    dk = r[HDR_1365.index("C_INT_display_key")]
    ek = r[HDR_1365.index("C_INT_effect_key")]
    items = json.loads(r[HDR_1365.index("A_ARR_items")] or "[]")
    print(f"\n  套 {iid}:")
    check_line(f"    display_key → 1511 id={dk}", find('1511', dk))
    check_line(f"    effect_key  → 1512 id={ek}", find('1512', ek))
    for it in items:
        check_line(f"    A_ARR_items → 1111 id={it}", find('1111', it))

# ====== 1168 获取途径: item_label 指向 1365 套 id ======
print("\n=== 1168 获取途径 → 1365 ===")
SID_1168 = "1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA"
TAB_1168 = "get_access_group（杜绝手搓）"
HDR_1168 = json.loads(gws(["sheets","+read","--spreadsheet",SID_1168,"--range",f"{TAB_1168}!A1:G1","--format","json"]))['values'][0]
# 搜索 1168 里 item_label 指向拓荒节 1365 套 id 的行
all_1168 = json.loads(gws(["sheets","+read","--spreadsheet",SID_1168,"--range",f"{TAB_1168}!A:D","--format","json"]))['values']
labor_1365_ids = {"13650159","13650160"}
for i,r in enumerate(all_1168, 1):
    if len(r) >= 4 and r[3] in labor_1365_ids:
        check_line(f"1168 id={r[0]} item_label={r[3]} → 1365", find('1365', r[3]))

# 反向: 检查每个拓荒节 1365 套 id 是否在 1168 有对应行
print("\n=== 1365 套 → 1168 (反向校验) ===")
found_labels = {r[3] for r in all_1168 if len(r)>=4}
for sid in labor_1365_ids:
    if sid in found_labels:
        print(f"  1365 套 {sid} → ✓ 1168 有对应行")
    else:
        missing += 1
        print(f"  1365 套 {sid} → ❌ 1168 缺失!")

print(f"\n==> 缺失总数: {missing}")
