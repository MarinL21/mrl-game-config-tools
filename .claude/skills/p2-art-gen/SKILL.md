---
name: p2-art-gen
description: P2 活动美术素材批量生成工具，对接 ai-art-api.tap4fun.com（REST API，比老 grfal 快 10×）。三个模块：活动界面 UI（用户贴竞品截图 + P2 锚点）、宝箱图标（固定 P2 宝箱锚点池）、活动道具（固定 P2 道具锚点池）。默认工作流 4 风格 × 2 轮 × 每轮 2 张 nano（Nano Banana 2 = 谷歌）= 16 张/批，8 个并行后台带 PID 后缀防撞秒。自动下载 + 入 gallery.html 分区展示。可选引擎：gpt / seedream / flux / qwen。触发：生图、活动 UI 美术、宝箱图标、道具图标、P2 素材生成。
---

# p2-art-gen

## 一句话

"给我画 16 张 P2 风格的 {春节宝箱 / 复活节礼包 UI / 科技节加速道具}" — Claude 出 4 个差异化风格 + 主题元素，脚本自动挑合规 P2 锚点、并发调 ai-art-api 生成、下载、入 gallery。

## ⚠ 核心原则（Claude 给 AI 只做 3 件事）

1. **找参考图** — 用 `--anchor "a.png,b.png,c.png"` 从合规池显式指定 3 张差异化参考
2. **想主题** — 在 prompt 里写"风格名 + 主题元素 + 配色"，**不要写形态/轮廓/造型/位置等结构限定**（"做成 XX 形状"、"圆柱罐造型"、"椭圆流线型"、"盒盖正中…"、"盒身六面" 都是禁区）
3. **告诉 AI 画风按参考图** — `STYLE_PREFIX` 已固化前置一句："仅借鉴图片的绘画风格，生成道具自选箱。图标上不要有任何文字。"

形态由 AI 按主题自由发挥。Claude 不当美术总监，只当主题策划。

## 工作流（默认 4 风格 × 2 轮 × 每轮 2 张 = 16 张）

1. 用户说"做 X 节日的礼盒" → Claude 主动出 **4 个差异化风格方向**（配色/主体元素/装饰差异明显，**不带"节日·"前缀**，节日由 `--festival` 参数传给 manifest 过滤）
2. 每个风格 **跑 2 轮**，每轮 **2 张 nano**（`--batch 2 --engines gemini`）+ **3 张 ref**（`--ref-count 3` 默认）
3. **每个风格 2 轮的 ref 不能重复** — 合规池若 6 张，每风格 2 轮 = 6 张刚好占满 0 重叠；用 `--anchor "a.png,b.png,c.png"` 显式分配 4×2=8 组组合
4. **prompt 范式（精简）**：
   ```
   "<风格名>风格：主题<元素1>+<元素2>+<元素3>+...；<配色>"
   例：月球哨站对讲机风格：主题航天通讯设备+复古旋钮+按键阵列+伸缩天线+月相示波屏+猩猩印章；浅蓝灰金属配色
   ```
5. **8 次并行后台任务**（ai-art-api 不排队，文件名带 PID 后缀防撞秒覆盖）
6. **重跑机制**：用户不满意 → 换 ref（改 `--anchor`）或改主题描述

## 节日设计灵感（Claude 主出，不要硬套模板）

- 春节 → 红色礼盒+灯笼/红包/祥云元素
- 复活节 → 蛋形/糖果罐+柔色丝带
- 登月节 → 月球纹+舷窗/星轨/紫金描边
- 万圣节 → 南瓜灯/棺材+蛛网+紫黑
- 圣诞节 → 红绿+蝴蝶结+冬青
- 周年庆 → 金光木盒+流苏+蛋糕/小丑/宝石装饰

## 快速使用

### 宝箱图标（最简单）

```bash
cd .claude/skills/p2-art-gen/scripts
python3 generate.py chest --subcategory "节日道具自选箱" --festival 春节 \
    --prompt "金锦祥云风格：主题红绒锦缎+祥云金边+灯笼吊穗+铜钱铆钉；红金配色" \
    --batch 2
```

脚本自动：
1. 按 `manifest.json` 过滤当前节日合规锚点，随机挑 3 张差异化 ref（`--ref-count 3` 默认）
2. 上传 ref 到 ai-art-api
3. 并发调 nanobanana（gemini）出 2 张
4. 下载到 `output/grfal/images/chest/`，文件名带 PID 后缀防撞秒
5. 追加到 `output/grfal/gallery.html` 宝箱分区顶部

### 活动道具

```bash
python3 generate.py item --prompt "加速卡道具，钟表造型" --theme "科技节"
```

### 活动界面 UI（必须传竞品截图）

```bash
python3 generate.py ui --prompt "替换主题为 P2 春节活动" --competitor ~/Downloads/competitor.png
```

`ui` 模块会上传两张 ref：你的竞品截图 + 一张 P2 活动面板锚点，让 ai-art-api 同时学构图和画风。
如只要"完全按竞品画"不加 P2 修饰，用 `--no-p2-anchor`。

### 引擎配置

**默认单引擎**：`--engines gemini`（= 谷歌 Nano Banana 2）。`gpt` 在节日宝箱/道具场景效果差已弃。
ai-art-api 键 `gemini` 对应的产品是**谷歌 Nano Banana 2**（不要叫它 Gemini）。

```bash
# 默认（推荐）
python3 generate.py chest --prompt "..." --engines gemini --batch 2

# 调风格切其它引擎（少用）
python3 generate.py chest --prompt "..." --engines seedream   # 即梦豆包，国风/红金质感强
python3 generate.py chest --prompt "..." --engines flux       # Flux Kontext，写实质感
python3 generate.py chest --prompt "..." --engines qwen       # 阿里千问编辑
```

可用引擎键（ai-art-api 已上线）：
`gemini`（谷歌 Nano Banana 2，**默认**）· `gpt`（OpenAI GPT Image，已弃）· `seedream`（即梦豆包）· `flux`（Flux Kontext）· `qwen`（阿里千问编辑）。

### 指定锚点

```bash
# 只用"银宝箱"做锚点
python3 generate.py chest --prompt "..." --anchor 银宝箱.png
```

### 节日语义过滤（强制）

带 `manifest.json` 的子分类（如 `chest/节日道具自选箱/`）**必须传 `--festival`**，否则脚本拒绝执行。manifest 给每张锚点打了"适用节日"标签，过滤逻辑会只挑当前节日的合规图，避免被其他节日专属图污染（典型案例：春节马头 `151104264.png` 错配到登月节）。

```bash
# 登月节自选箱：只挑深紫蓝/银白航天感的合规锚点
python3 generate.py chest --subcategory "节日道具自选箱" \
    --festival 登月节 --prompt "登月节·银河月光风格..."
```

合法节日：12 主节日（春节/情人节/科技节/复活节/拓荒节/深海节/登月节/周年庆/音乐节/万圣节/感恩节/圣诞节）。

`*` = 通用锚点（任何节日可借用作中性形态参考）。

**新加锚点的归档流程**：把图复制进 `anchors/chest/节日道具自选箱/` 后，必须同步在该目录的 `manifest.json` 里加一条：
```json
"<新文件名>": { "festivals": ["<节日1>", "<节日2>"], "tag": "<视觉关键词>" }
```
没加 manifest 条目的图会被当作"未标记"放过过滤（向后兼容），但会绕过节日校验——所以遇到节日子分类务必同步 manifest。

## 凭据管理

`~/.ai-art-auth.json`（建议 `chmod 600`）：

```json
{
  "api_host": "https://ai-art-api.tap4fun.com/v2",
  "token": "<JWT 持久 token>"
}
```

**Token 来源**：浏览器登录 ai-art portal → 右上角头像 → "生成令牌"。是持久 JWT，不像老 grfal cookie 一周一换。

**报 `AiArtAuthError` / 401**：去 portal 重生成 token，覆写文件 `token` 字段。

> macOS + Python 3.14 可能报 `CERTIFICATE_VERIFY_FAILED`。客户端 import 时已自动 `os.environ.setdefault("SSL_CERT_FILE", certifi.where())`，正常无需手动设；仍报错则 `pip install --upgrade certifi`。

## 锚点库扩充（**唯一来源：AssetsSVN**）

**新参考图必须从 `~/AssetsSVN/P2_UI_CUT/` 拉**，不要让用户每次重新上传——附件无文件路径，无法 cp 入库。

主要来源：
- `T_图标/D道具图标/` — 793+ 张 P2 道具/宝箱图标（chest 和 item 模块都从这取）
- `H_活动/*/效果图.png` — 活动面板效果图（ui 模块）
- `H_活动/*礼包*/` — 礼包类界面

**新增锚点工作流**：
1. 用户指出"用某个节日/品类的新参考"时，先 `ls ~/AssetsSVN/P2_UI_CUT/T_图标/D道具图标/ | grep <关键词>` 找候选
2. 视觉无法精确匹配（图太多）时直接问用户文件名
3. `cp` 进 `anchors/<module>/<subcategory>/`，文件名保持 SVN 原名（数字 ID 或英文名）
4. 同步在该子目录的 `manifest.json` 加条目（`festivals` + `tag`）
5. 弃用某锚点：把 `festivals` 改为 `[]` 并在 `tag` 前缀 `[已弃用·原因]`，物理保留作档案

挑中好看的生成图后，也可归档：

```bash
cp output/grfal/images/chest/20260424_120000_03.png .claude/skills/p2-art-gen/anchors/chest/
```

## 引擎选择经验

| 场景 | 推荐 |
|---|---|
| 语义忠实度最重要（改主题保结构） | `gpt`（默认） |
| 中文场景/国风/节日 | `seedream` 即梦豆包 |
| 细节质感 / 真实光影 | `flux` Flux Max |
| 自然编辑感 / 多图参考 | `gemini` Google Nano Banana |
| 影视风格 / 大场景 | `wan` 阿里万象 |
| 写实 LoRA 仅文生图 | `zimage` |

## 文件布局

```
.claude/skills/p2-art-gen/
├── SKILL.md
├── scripts/
│   ├── ai_art_client.py     # 主客户端（REST：upload_image + generate + download，内置 ThreadPoolExecutor）
│   ├── grfal_client.py      # 老客户端，留作 fallback（ai-art 挂时改一行 import 即可回切）
│   ├── gallery.py            # HTML 画廊模板 + 增量写入（兼容 PID 后缀文件名）
│   └── generate.py           # 三模块入口 CLI（STYLE_PREFIX 前置 + --ref-count 3 默认 + ts 加 PID 后缀）
└── anchors/
    ├── chest/
    │   └── 节日道具自选箱/  # 13+ 张 P2 自选箱图 + manifest.json（按节日打标签）
    ├── item/                # 13+ 张 P2 道具
    └── ui_panel/            # 4 张 P2 活动面板效果图
```

输出（目录名 `grfal/` 是历史遗留——已迁 ai-art-api 但保留以兼容旧 gallery 链接，不要改）：

```
output/grfal/
├── gallery.html          # 单一持久画廊，三分区累积，最新批次置顶
└── images/
    ├── ui/
    ├── chest/
    └── item/             # 文件名：YYYYMMDD_HHMMSS_<PID>_<engine>_<idx>.png
```

## 成本

- GPT 引擎 8 张约 3-5 元、3 分钟
- 即梦/Flux 单价更便宜

## 故障排查

| 症状 | 原因 / 处理 |
|---|---|
| `AiArtAuthError` / 401 | token 过期或没设，去 ai-art portal 重生成覆写 `~/.ai-art-auth.json` 的 `token` 字段 |
| `AiArtAPIError: 生成失败: ...` | 提示词触发安全过滤，改中性词重试；或 ref 文件路径不对 |
| `CERTIFICATE_VERIFY_FAILED` | macOS Python 3.14 SSL 链，客户端已自动 `SSL_CERT_FILE=certifi.where()`，仍报错则 `pip install --upgrade certifi` |
| 部分批次失败 | 脚本继续收集已成功批次，最终打印失败数 |
| 出图全跑偏主题 | ref 选错（manifest 节日筛漏？查 `--festival` 是否传对），或 prompt 含形态/位置/造型限定（违反核心原则） |

## 已知约束

- `ui` 模块强制需要 `--competitor`
- ai-art-api 的 nanobanana 单次响应 1 张图，client 内置 `ThreadPoolExecutor(max_workers=4)` 自动 fan-out 到 batch 张
- 节日子分类（带 `manifest.json`）必须传 `--festival`，否则脚本拒绝执行
- prompt 不带「节日·」前缀（节日由 `--festival` 过滤 manifest）；不写形态/位置/造型限定（违反核心原则）
