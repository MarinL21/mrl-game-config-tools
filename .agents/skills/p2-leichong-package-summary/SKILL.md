---
name: p2-leichong-package-summary
description: P2 节日累充礼包归纳填写工具——本地网页可视化源表 1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E 各节日 tab 数据。三块功能：① C 列 2011 IAP id 去重汇总；② A 列礼包按 H 列价格归类；③ 输入累充活动 id 列表 → 生成 K 列 recharge_actv JSON（贴回源表）。 触发：累充礼包归纳、累充网页工具、{节日}礼包归纳、IAP 去重工具、累充 K 列生成。
---

P2 节日累充礼包归纳填写工具。本地 Python http 服务器 + 内嵌 HTML，浏览器可视化操作。

## 用途

源表 `1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E` 每个节日一个 tab（如 `26拓荒节` / `26春节` / `26复活节` 等），每个 tab 有 ~270 条礼包数据。

**额外跨表读 2011 iap_config_QA**（`1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc`）：每个 2013 礼包对应一个 2011 IAP，2011 IAP 的 `A_ARR_iap_status` 字段可能已经有非-recharge_actv 字段（drop / lc / item / task / dig_keys_is_over_level / easter_monopoly_lap_num 等 20+ 种）。**生成 K 列时必须把这些字段保留**，只换 recharge_actv 部分，否则覆盖会破坏掉条件触发逻辑。

每张礼包表 tab 列结构：
- A 列 = 2013 礼包 ID
- B 列 = 礼包类型（random / normal）
- C 列 = 2011 IAP ID
- D 列 = 2014 ID
- E 列 = 礼包名称
- F/G 列 = LC name/desc key
- H 列 = 美元价格（11 档：$1.99 ~ $99.99）
- K 列 = 公式生成的 `recharge_actv` JSON（贴回 2011 IAP 的 iap_status 字段）

填写新节日累充礼包时，PM 需要：
1. 看 C 列哪些 2011 IAP 涉及（去重后）
2. 按价格档位归类礼包（看每档有几个）
3. 输入本节日累充活动的 2112 ID 列表 → 生成 K 列 JSON 贴回源表

工具把这 3 步做成网页。

## 两套部署：本地 server / Apps Script 侧边栏

### A. 本地 Python server（开发/调试用，不需共享时）

```bash
cd /Users/marinl/游戏运营策划工具/.agents/skills/p2-leichong-package-summary
python3 scripts/server.py                 # 默认 26拓荒节
python3 scripts/server.py 26春节           # 切其他 tab
python3 scripts/server.py 26复活节 8800    # 改端口（默认 8765）
```

启动后浏览器自动打开 `http://127.0.0.1:8765/`。依赖 `gws` CLI 已认证。

### B. Apps Script 侧边栏插件（推荐共享给同事用）

**部署到 1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E（已部署）**：
- Script ID: `1XnPa-bAwjcIz-bhAsX4Hg1TM_IC0VtlxAu0dQZahPxbNxPPLuQHtRbrd`
- 部署目录：`/tmp/leichong_deploy/`

**同事使用**：直接打开礼包源表 → 顶部菜单"**累充礼包归纳**" → "打开侧边栏" → 右侧弹出。无需任何安装/配置，只要有源表 + 2011 表权限即可。

**首次运行需授权 OAuth**（每个同事点开后会弹一次授权框），授权后即可读写 2 张表。

**给新源表/迭代代码部署**：

```bash
# 首次给某 spreadsheet 部署
mkdir -p /tmp/leichong_deploy
cd /tmp/leichong_deploy
clasp create-script --title "累充礼包归纳工具" --parentId "<SPREADSHEET_ID>" --rootDir "."

# 复制 3 个文件
SRC=/Users/marinl/游戏运营策划工具/.agents/skills/p2-leichong-package-summary/apps_script
cp "$SRC/Code.gs" "$SRC/Sidebar.html" "$SRC/appsscript.json" .

# 推送
clasp push --force
```

**迭代后重新 push**：编辑 `apps_script/` 下文件 → 复制到 `/tmp/leichong_deploy/` → `clasp push --force`。

## 网页功能

### Section ① 累充活动 id 输入
- textarea 接收 N 个 2112 ID（逗号 / 空格 / 换行任意分隔）
- 校验：每个 id 必须是 8 位数字
- "生成 K 列 JSON" 按钮 → 输出 2 份：
  1. **全局 recharge_actv 数组**：`[{"typ":"recharge_actv","id":21127892,"val":1},...]` —— 适用 2011.iap_status 当前为空的礼包
  2. **按行合并版（推荐）**：每行一个 JSON = 该行 2011 IAP 现有 preserved 字段 + 新 recharge_actv。271 行整列复制粘贴回源表 K 列
- 显示统计："X / 271 行有保留字段" + 字段类型分布表 + 详细行清单（默认折叠）
- "复制全列（按行序）" → textarea 复制全部 271 行

#### ⚡ 一键写回 2011 表 iap_status

按钮直接调 `gws sheets spreadsheets values batchUpdate` 把 unique 2011 IAP 的 `A_ARR_iap_status` 列（col L）写为 `[preserved..., new_recharge_actv...]`。
- 写前弹 confirm dialog，列出: 写入行数 / 累充 id / 合并规则
- 后端 `POST /api/write` body: `{tab, actv_ids[]}` —— 校验 8 位数字 → fetch 源表 unique 2011 → 跨表 batchUpdate
- 返回: `{updated: N, ranges: M, skipped: [...]}` 或 `{error: ...}`
- 跳过条件: 2011 id 在 iap_config_QA 中找不到（理论上不应发生）
- 同一 2011 IAP 被多个 2013 礼包共用时只写一次（按 unique 2011 去重）

### Section ② 数据概览
- N 条礼包 / N 个唯一 IAP / N 档价格

### Section ③ C 列 2011 IAP id 去重
- 网格展示所有唯一 ID（226 个左右）
- "复制全部 id（逗号分隔）" 一键拷

### Section ④ A 列礼包按 H 列价格归类
- 11 档价格折叠面板（$1.99 / $2.99 / ... / $99.99）
- 每档展开看：2013 ID / 类型 badge / 2011 IAP / 礼包名 / K 列现有内容预览
- 点开看每档具体哪些礼包

## 顶部控制
- 节日 tab 下拉切换（17 个常用节日预填）
- "🔄 刷新数据" 按钮重新拉 sheet
- 显示最后更新时间

## 输出去向

两种模式（用户选）：
1. **手动复制粘贴**：textarea 显示 271 行合并 K JSON，用户选中粘贴回源表 K 列；或单独复制全局 recharge_actv 数组
2. **一键写回 2011 表 iap_status**（直接修改活表）：跳过源表 K 列中转，直接通过 `gws sheets spreadsheets values batchUpdate` 把每个 unique 2011 IAP 的 `iap_config_QA!L<row>` 写为合并后的 JSON。带 confirm dialog 确认

## 数据流

```
浏览器 ──GET /api/data?tab=...──> Python http server
                                     │
                                     ├─> subprocess: gws read 礼包源表 tab!A:K
                                     ├─> subprocess: gws read 2011 iap_config_QA!A:L
                                     │     └─> 缓存 {2011_id: [non-recharge_actv 字段]}
                                     │
                                     ├─> 解析 271 条礼包数据行
                                     ├─> 去重 C 列 → unique_2011[]
                                     ├─> 按 H 列分组 → by_price[]
                                     └─> 每行附 preserved[]（来自 2011.iap_status 反查）
                                                                              │
浏览器 <──JSON 渲染──────────────────────────────────────────────────────────────┘
```

## 已知节日 tab 清单

预填在下拉里的常用 tab：26拓荒节 / 26复活节 / 26科技节 / 26情人节 / 26春节 / 25圣诞节 / 25.11星球套装 / 25万圣节 / 25音乐节 / 25周年庆 / 25登月节 / 深海节 / 拓荒节 / 复活节 / 科技节 / 情人节 / 春节。
源表底部还有些老节日（沙滩节 / 沙滩节付费 / 周年庆礼包内容 等），需要时手动改 KNOWN_TABS。

## 不做的事

- 不直接写回源表（礼包 sheet）K 列（K 是公式列，PM 维护；写回目标是 **2011 iap_config_QA**）
- 不验证 2112 id 是否真存在于 2112 表（前端只校验 8 位数字格式）
- 不生成跨 tab 汇总（一次操作一个节日）
- 不集成翻译/价格转换/汇率（只做归纳展示）
- 写回前不做 backup（用户应该自己 git 或 gws 备份；写回后 sheet 有 revision history 可回滚）

## 与其他 skill 的关系

- 输入数据来源：源表本身由 PM 维护（属"礼包内容池"，我不写源表）
- 生成的 K 列 JSON 贴回 2011 IAP 的 iap_status 字段：用户后续会用 `iap-leichong-sync` 类 skill 把 K 列数据 push 到 2011 表（不在本 skill 范围）
- 跟 `p2-festival-cityeffect-recharge` / `p2-festival-mecha-recharge` 配合：累充 三件套和机甲累充的 2112 ID 是这里输入的累充活动 id 来源
