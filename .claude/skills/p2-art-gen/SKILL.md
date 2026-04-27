---
name: p2-art-gen
description: P2 活动美术素材批量生成工具，对接 grfal.tap4fun.com。三个模块：活动界面 UI（用户贴竞品截图 + P2 锚点）、宝箱图标（固定 P2 宝箱锚点池）、活动道具（固定 P2 道具锚点池）。每次 8 张并发 = GPT × 4 + Nano Banana 2（谷歌） × 4 双引擎，自动下载 + 入 gallery.html 分区展示，图片徽章显示引擎来源。支持 13 个引擎（gpt/gemini/seedream/flux/vidu/wan/runway/qwen/ideogram/hunyuan/grok/zimage/firered）。触发：生图、活动 UI 美术、宝箱图标、道具图标、P2 素材生成、grfal。
---

# p2-art-gen

## 一句话

"给我画 8 张 P2 风格的 {春节宝箱 / 复活节礼包 UI / 科技节加速道具}" — 脚本自动挑 P2 锚点图、并发调 grfal 生成、下载、入 gallery。

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
python3 generate.py chest --prompt "火焰节宝箱，熔岩纹理橙红配色" --batch 8
```

脚本自动：
1. 随机挑一张 P2 宝箱锚点（`anchors/chest/` 下 4 张）
2. 上传到 grfal
3. 并发跑 2 轮 × 4 张 = 8 张
4. 下载到 `output/grfal/images/chest/`
5. 追加到 `output/grfal/gallery.html` 宝箱分区顶部

### 活动道具

```bash
python3 generate.py item --prompt "加速卡道具，钟表造型" --theme "科技节"
```

### 活动界面 UI（必须传竞品截图）

```bash
python3 generate.py ui --prompt "替换主题为 P2 春节活动" --competitor ~/Downloads/competitor.png
```

`ui` 模块会上传两张 ref：你的竞品截图 + 一张 P2 活动面板锚点，让 grfal 同时学构图和画风。
如只要"完全按竞品画"不加 P2 修饰，用 `--no-p2-anchor`。

### 引擎配置（默认双引擎）

**默认**：`--engines gpt,gemini` → GPT × 4 + Nano Banana 2 × 4 并发。
grfal API 键 `gemini` 对应的产品实际是**谷歌 Nano Banana 2**（不要叫它 Gemini）。

```bash
# 单引擎
python3 generate.py chest --prompt "..." --engines gpt
python3 generate.py chest --prompt "..." --engines seedream   # 即梦豆包
python3 generate.py chest --prompt "..." --engines gemini     # Nano Banana 2

# 自定义组合（总 batch 会均分）
python3 generate.py chest --prompt "..." --engines gpt,seedream,flux --batch 9  # 3×3
```

可用引擎键（grfal API 名 / 产品名）：
`gpt`（OpenAI GPT Image 2）· `gemini`（谷歌 Nano Banana 2）· `seedream`（即梦豆包）·
`flux`（Flux Max）· `vidu` · `wan`（阿里万象）· `runway` · `qwen`（阿里千问）·
`ideogram` · `hunyuan`（混元）· `grok` · `zimage` · `firered`（FireRed Edit）

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

`~/.grfal-auth.json`：

```json
{
  "session_cookie": "<grfal_session 的 value>",
  "base_url": "https://grfal.tap4fun.com"
}
```

**过期刷新流程**：session cookie 大约一周一换。当脚本报 401/未认证：
1. 浏览器登录 `https://grfal.tap4fun.com/v2/`
2. F12 → Application → Cookies → `grfal.tap4fun.com`
3. 找 `grfal_session` 那行，复制 value
4. 覆盖 `~/.grfal-auth.json` 里的 `session_cookie` 字段

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
│   ├── grfal_client.py      # 客户端（upload + generate + SSE）
│   ├── gallery.py            # HTML 画廊模板 + 增量写入
│   └── generate.py           # 三模块入口 CLI
└── anchors/
    ├── chest/      # 4 张 P2 宝箱
    ├── item/       # 13 张 P2 道具
    └── ui_panel/   # 4 张 P2 活动面板效果图
```

输出：

```
output/grfal/
├── gallery.html          # 单一持久画廊，三分区累积
└── images/
    ├── ui/
    ├── chest/
    └── item/
```

## 成本

- GPT 引擎 8 张约 3-5 元、3 分钟
- 即梦/Flux 单价更便宜

## 故障排查

| 症状 | 原因 / 处理 |
|---|---|
| `GrfalAuthError` | session 过期，按上面流程刷新 |
| `生成标记失败` | 提示词可能触发安全过滤，改中性词重试 |
| 长时间无响应 | grfal 队列排队，正常；SSE 会持续心跳 |
| 部分批次失败 | 脚本继续收集已成功批次，最终打印失败数 |

## 已知约束

- `ui` 模块强制需要 `--competitor`
- `ideogram` 引擎只支持 1 张参考图、`zimage` 纯文生图不支持参考
- gradio 单次请求 batch ≤ 4；脚本内部已拆分并发
