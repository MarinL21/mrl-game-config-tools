---
name: p2-gdconfig-push
description: >-
  P2 配置表从 Google Sheet 导到 gdconfig git 仓库的端到端 skill。
  读指定页签 → 按 id 精准 patch 对应 tsv 行 → 处理 schema 漂移 → diff 预览 → commit → push 到用户指定分支。
  覆盖 cn/fo 双路径，知道 Gen/ 是 CI 产出不能碰，自动装 git-lfs。
  触发：传表、导表、传 {id} 去 {branch}、push {表} 到 {分支}、同步 xxx 到 hotfix/qa/dev/bugfix、配表上线。
  Scope：只做"sheet → tsv → git"这一段；表本身的配置/翻译/校验归前置 skill（p2-unite-gift-config 等）。
---

# P2 gdconfig 导表 Skill

## Scope

**做**：已在 sheet 里配好的 id → 对应 gdconfig tsv → commit → push 指定分支。
**不做**：配置表内容本身（字段写什么、奖励怎么配、翻译、美术）。那些事上游 skill 已经处理完，本 skill 只负责"搬运+提交"。

---

## Step 0：默认值 + 必问的事

### 默认（不再问用户，已用户确认沉淀）
- **server = fo**：所有表默认只动 `fo/`，cn 必须用户明确说才同步
- **commit message** = `[配置更新]{表号}-{file}-{branch}`（仓库习惯，不带 Claude co-author）

### 仍要问的（按场景区分）

**场景 A：用户明确给了 id 列表**（"传 2013101095 到 hotfix"）→ patch 模式
- 走 `patch_tsv.py` 或 `merge_rows.py`（精准防洗）
- 仍要问：源页签（QA 主页签 / TEST 暂存 / 活动专属）

**场景 B：用户只说"传 X 表到 Y 分支"，没给 id**（如"传1511到bugfix"）→ 整表覆盖模式
- 走 `dump_table.py`（对齐老 GSheetDownloader 的语义）
- **默认页签**：`{file}_QA` → `{file}_qa` → `{file}（QA）` → `{file}` 顺序回退（第一个存在的就用）
- **不需要问 id**（整表覆盖，sheet 是权威）
- 但 push 前必须做 sanity check（见下方 dump 流程的 Phase 3）

**场景 C：1011 i18n** → 见下文「1011 i18n 表特殊流程」

---

## 仓库常量（别重复查）

- Repo 路径：`/Users/marinl/gdconfig`
- Remote：`git@git.tap4fun.com:p2/gdconfig.git`
- 三路径分工：
  | 路径 | 用途 | 手改 |
  |---|---|---|
  | `cn/config/*.tsv` | 国服（列少行少） | ✅ |
  | `fo/config/*.tsv` | 国际服（完整，节日主战场） | ✅ |
  | `Gen/tsv/*.tsv` | CI `p2-config-build-cache` Jenkins 产出 | ❌ 永远别碰 |
- 主索引 sheet：`1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c` 的 `fw_gsheet_config` 页签
  - 每行：`分类, 标题, 文件名, SheetID, (空), mode`
  - mode: 0=cn+fo, 1=仅 fo, 2=仅 cn

## 常用表 → 文件/SheetID 速查

| 表 | 文件名（cn/fo/config/*.tsv） | Sheet ID | 默认页签 |
|---|---|---|---|
| 2011 | `iap_config.tsv` | `1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc` | `iap_config_QA` |
| 2013 | `iap_template.tsv` | `1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY` | `iap_template_QA` |
| 2111 | `activity_calendar.tsv` | `1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g` | `activity_calendar_QA` |
| 2112 | `activity_config.tsv` | `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E` | `activity_config_qa` |
| 2115 | `activity_task.tsv` | `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY` | `activity_task_QA` |
| 2116 | `activity_item_exchange.tsv` | `14IDttHNuHx1U2I1kHinkMLIA6Q4cKmZ8MLoMkgdTGfY` | `activity_item_exchange` |
| 2121 | `activity_special.tsv` | `1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc` | `activity_special_QA` |
| 2122 | `activity_rank_rule.tsv` | `1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M` | `activity_rank_rule（QA）` |
| 2124 | `activity_drop.tsv` | `1V7xDriTe0hGW3SF7ZPtk71-sFGyzpbbO47V6gLoBqVA` | `activity_drop` |
| 2135 | `activity_event_package.tsv` | `1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc` | `activity_event_pkg` |
| 2137 | `activity_asset_retake.tsv` | `1ctEGsAU053iaCCTJeIU1qnp9zfyuURt7k8EzHkKzv2Y` | `activity_asset_retake` |
| 1111 | `item.tsv` | `1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws` | `item` |
| 1011 | `{server}/i18n/{lang}.tsv` 全量 | fo=`11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY` cn=`1x7E76B9U2CWzOgbuk60F6oEDo_4Lkz1MnRJYSA9m_CM` | 23 个 tab 全量重建（特例） |

默认页签仅作后备；用户没明说时必须回到 Step 0 问。

**1011 是特例** — 不走单 tsv patch，走全量重建，见下文「1011 i18n 表特殊流程」。

---

## 整表覆盖流程（场景 B，dump_table.py）

老 GSheetDownloader 的核心语义。脚本 `scripts/dump_table.py` 已实现：

### 规则（来自 `gsheet_down.py` + `gsheet_utility.py`）
1. **整页签下载**（不是 patch）；sheet 是权威，整文件覆盖目标 tsv
2. **mode=0 表的 country_use_type 切分**：sheet 里若有 `A_INT_country_use_type` 列，按值切行（0=公共两服都要；1=仅 fo；2=仅 cn），切完**剥掉这列**
3. **剥非 S 开头的 `_STR_comment` 列**：`A_STR_comment` / `C_STR_comment` 剥掉，`S_STR_comment`（server-only）保留
4. **保留目标文件原有 trailing newline 状态**：仓库 tsv 末尾多数无 newline，无脑加会触发"末尾行假 diff"（已在 `write_tsv` 里实现）

### 默认页签解析
按经验顺序找权威页签：`{file}_QA` → `{file}_qa` → `{file}（QA）` → `{file}(QA)` → `{file}`。第一个存在的用。
显式指定走 `--tab "..."`。

### 命令
```bash
SSL_CERT_FILE=$(python3 -m certifi) python3 \
  /Users/marinl/游戏运营策划工具/.claude/skills/p2-gdconfig-push/scripts/dump_table.py \
  --table 1511     # 自动从 fw_gsheet_config 解 SheetID + file_name + mode
```
表号未登记或想覆盖：`--sheet-id ... --file-name ...`。

### Phase 3：sanity check（push 前必跑）
```bash
F=fo/config/{file}.tsv
diff_cnt=$(comm -23 <(awk -F'\t' 'NR>1 {print $1}' $F | sort -u) \
                    <(git show HEAD:$F | awk -F'\t' 'NR>1 {print $1}' | sort -u) | wc -l)
del_cnt=$(comm -13 <(awk -F'\t' 'NR>1 {print $1}' $F | sort -u) \
                   <(git show HEAD:$F | awk -F'\t' 'NR>1 {print $1}' | sort -u) | wc -l)
echo "new_ids=$diff_cnt deleted_ids=$del_cnt"
```
- 期望 `deleted_ids=0`（纯增量）；非 0 停下来给用户看具体哪些 id 被删（可能是 sheet 端清理过期内容、也可能是页签选错了）
- `new_ids` 不限上限，但 git diff --stat 远超历史峰值（display_key 历史 commit 单次几十~几百行）就要主动确认

### 与精准 patch 模式（场景 A）的区别
| 场景 | 工具 | 适用 | 风险 |
|---|---|---|---|
| 整表覆盖 | `dump_table.py` | "传 X 表" 无 id 列表 | sheet 端有未传给我的孤立改动会被同步 |
| 精准 patch | `merge_rows.py` / `patch_tsv.py` | 用户明指 id | 只动指定 id，其他行不变 |

---

## 标准流程（精准 patch，场景 A）

### merge_rows.py 已知坑：trailing newline 假 diff
公司 `scripts/merge_rows.py` 写出时无脑加最后一个 `\n`，但仓库 HEAD 末尾多数无 newline。后果：merge_rows 后末行会出"假 diff"（git 把"无 LF → 有 LF"算作行变更，会把无关的最后一个 id 显示为修改）。

**必跑兜底**：merge_rows 之后 strip 最后一个 newline：
```bash
python3 -c "
p='fo/config/X.tsv'
data=open(p,'rb').read()
if data.endswith(b'\n'):
    open(p,'wb').write(data[:-1])
"
```
然后 `git diff -U0 X.tsv | grep -oE '^[+-]<id_prefix>' | sort -u` 验证只有目标 id 变化。

### Phase 1：准备

1. `cd /Users/marinl/gdconfig && git status` 确认工作区干净
2. `git branch --show-current` 确认当前分支；若和用户说的目标分支不符，`git checkout <target>` 并 `git pull --ff-only`
3. `which git-lfs` 验证；没有就跑 `scripts/install_git_lfs.sh`（从 GitHub releases 拉 darwin-arm64 v3.5.1 到 `~/.local/bin/`）

### Phase 2：读 sheet + 定位

```bash
gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"<SHEET_ID>","range":"<TAB_NAME>!A:AZ"}' \
  --format json 2>/dev/null > /tmp/sheet.json
```

**注意**：`2>/dev/null` 是故意的，吞掉 `Using keyring backend: keyring` stderr。不要写 `2>/tmp/sheet.json` 那样只会捕获 stderr。

### Phase 3：精准 patch

调 `scripts/patch_tsv.py`（见脚本区），传参：
- `--sheet-json /tmp/sheet.json`
- `--tsv /Users/marinl/gdconfig/fo/config/<file>.tsv`
- `--ids 2013101095,2013101096,...`
- `--mode update|insert`

脚本会：
1. 对齐 sheet header 与 tsv header，**自动丢弃** sheet 多出来的列（schema 漂移）
2. update 模式：按 id 定位原行，整行覆盖（保留其他行顺序）
3. insert 模式：按 id 数值排序插到合适前驱行之后
4. 验证列数一致，验证 id 不重复
5. 打印每行哪些列真的变了

### Phase 4：diff review + commit + push

```bash
cd /Users/marinl/gdconfig
git diff --stat <file>
git diff <file> | head -200   # 给用户看
```

用户确认后：
```bash
git add <file>
git commit -m "$(cat <<'EOF'
<type>: <一句话描述 + id 区间>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push origin <branch>
```

**push 是不可逆的**，commit 前必须让用户看过 diff。

---

## Schema 漂移常见坑

sheet 经常会先加新列但 fo/ 还没跟上（CI 没重建、或者临时字段），例：
- 2013 的 `A_INT_country_use_type`（值 `0`）在 sheet 里第 30 列，fo 没有这列
- 脚本默认丢弃 sheet 多出的列

但如果 sheet **少**列（用户手工删了），脚本报错停下来，问用户怎么办（不要默默补默认值）。

---

## cn vs fo 决策

默认只动 `fo/`。决策树：
- id 在 cn tsv 里存在？ → 也同步 cn/
- id 不在 cn？ → 只动 fo/，不要强行往 cn 里插

典型节日付费 id（`201310xxxx` / `201350xxxx` / `201351xxxx`）多数 cn 没有。

验证命令：`grep -c "^<id>	" /Users/marinl/gdconfig/cn/config/<file>.tsv`

---

## 失败恢复

- `git push` 因 git-lfs 缺失失败：commit 已经在本地了，别 reset；先装 git-lfs 再 `git push` 重试
- `git push` 因远端 non-fast-forward 失败：`git pull --rebase origin <branch>` 再 push；**不要 force push**
- patch 脚本报列数不匹配：停下来读 sheet header 与 tsv header 对照，问用户

## 沉淀到 memory 的情况

跑完一次后如果发现：
- 某张表的默认页签不是 QA 主页签（有特殊约定）→ 记到 `reference_gdconfig_repo.md` 的速查表里
- 某个节日的 id 段规则（比如 `2013101xxx` 段专属某节日）→ 加 project memory

---

## 1011 i18n 表特殊流程（不要再问用户）

### 为什么不走标准 patch
i18n 表跟普通 2xxx 配置表完全不同：
- 源 sheet **42 个 tab**（不是索引表登记的 23 个 — 那个列表是过时快照）。脚本动态发现所有 tab 后按 header 形态过滤业务 tab：必须 `header[0] == "ID_int"` 且 `header[1] == "ID"`，不符合的（说明文档/检查脚本/AI翻译暂存/Operation Mail 等）自动 skip
- 输出落到 **18 个语言文件**（fo: ar/cn/cns/de/en/fr/id/it/jp/kr/pl/po/ru/sp/th/tr/vi/zh），cn 仓库只保留 cn.tsv
- key = `{tab_name}_{ID}`（字符串、跨页签），无 id-int 主键可 patch
- 老 GSheetDownloader 的处理就是「全量下载所有 tab → 按语言切分 → 整体覆盖」，**没有 patch 模式**

### 默认决策（不再问用户）
- **只做 fo，不做 cn**（cn sheet 长期未同步，全量替换会引入 9k+ 新增 + 100+ 删除，业务影响不可控；除非用户明确说"也传 cn"）
- **全量重建模式**：直接覆盖 `fo/i18n/*.tsv` 18 个文件
- 不需要"指定哪些 LC_Key" — 1011 全量同步
- commit message 模板：`[配置更新]1011-i18n-{branch}`（参照仓库历史风格，不带 Claude co-author 行——节日运营提交习惯不带）

### 四个曾经踩过的坑（已在脚本里修了，提及防回归）
1. **写死的 tab 列表过时** → 改动态发现 + header 形态判断
2. **Py3 insertion-order 跟仓库 key 字母序不一致** → 写出前 `sorted(rows, key=lambda r: r[0])`
3. **value 里有人误按 Enter 的真换行符切碎 tsv** → `escape_value()` 把 `\r\n` `\n` `\r` `\t` 转字面双字符；**不要** escape 反斜杠（sheet 里已经是字面 `\n` 双字符，再转就 `\\n` 错位）
4. **gws 读单 tab 偶发网络抖动失败导致整脚本退出** → `read_tab` 加 3 次 retry（2/4/6s backoff）。曾经踩过：脚本中途挂了但没改 working tree，外部看 `git status` 干净 → 误判"sheet 无变化"。**rebuild_i18n 跑完必须看 exit code 0 + "18 file(s) written" 字样**，光看 git diff 容易漏

### 源 sheet 结构（每页签）
```
col0  ID_int     col1 ID         col2 cn    col3 en    col4 fr   ...   colN <语言>
1011140001       add_CD_desc    使用后...   {0} CDs   {0} CD    ...
```
- ID_int 是数字主键，ID 是 LC_Key 短名
- col2 起按 sheet 列顺序对应 lang code（fo sheet 包含 18 lang，cn sheet 只有 cn 列有效）

### 输出 tsv 结构
```
id\tvalue\tindex_int     <- header
{tab_name}_{ID}\t{lang翻译}\t{ID_int}    <- 每行
```
例：`ITEM_add_CD_desc\t{0} shiny CDs!\t1011140001`

### 执行步骤

**Phase 1**：仓库准备（同标准流程的 Phase 1）

**Phase 2**：调全量重建脚本（只做 fo，cn 默认不动）
```bash
SSL_CERT_FILE=$(python3 -m certifi) python3 \
  /Users/marinl/游戏运营策划工具/.claude/skills/p2-gdconfig-push/scripts/rebuild_i18n.py \
  --server fo
```
脚本会：动态拉所有 tab → header 形态判断业务 tab → 按 lang 聚合 → escape 真换行 → key 字母序排序 → 写 `fo/i18n/{lang}.tsv` 18 份 → 重复 key 检测（同 lang 同 key 不同 index_int 报错停下来）

**Phase 3**：sanity check + diff review
首先验证**没有 key 被删除**（fo 应该是纯增量；如果有 key 删除，停下来问用户）：
```bash
comm -13 \
  <(awk -F'\t' 'NR>1 {print $1}' fo/i18n/en.tsv | sort -u) \
  <(git show HEAD:fo/i18n/en.tsv | awk -F'\t' 'NR>1 {print $1}' | sort -u) \
  | wc -l
# 期望 0；如果非 0，是 sheet 端删了 key，要跟用户确认是否真要下线
```
然后 `git diff --stat fo/i18n/` 看新增/修改行数（典型 1k~3k 行级，纯增量）。**不要 `git diff` 逐行展开**，会爆屏幕。

**Phase 4**：commit + push
- commit message：`[配置更新]1011-i18n-{branch}`（仓库习惯，不带 Claude co-author）
- 多分支推送（用户说"传 bugfix 和 hotfix"）：**每个分支独立** checkout → pull → rebuild → diff sanity → commit → push 循环。不能复用同一份 working tree 的 commit，不同分支 base 不同 diff 不同（实测 hotfix 比 bugfix 多 4k 行积压，因为基线落后）

### 兜底：用户明确要传 cn
若用户说"也传 cn"，在 fo 流程之后追加：
```bash
SSL_CERT_FILE=$(python3 -m certifi) python3 .../rebuild_i18n.py --server cn
```
然后**必须**对 cn.tsv 跑同样的 only-in-HEAD 检查（找会被删除的 key），把列表给用户看，他点头才能 push。cn 容易出现"积压同步"导致大量新增 + 少量已下线 key 的删除——后者风险高。

### 注意事项
- 23 tab 全量读 ≈ 30~60 秒，期间不要中断
- 老脚本里 `cns` 之前曾被注释掉（"cns只用于国服屏蔽词编辑，不导出"），但 fo sheet 现在确实有 cns 列且仓库有 cns.tsv，所以保持导出
- 重复 key 错误：通常是 sheet 里同一个 LC 短名出现在两个页签 + index_int 不一致，去 sheet 里改完再重跑（不要在 tsv 里硬补）
- 这个流程不依赖 `merge_rows.py` / `patch_tsv.py`
