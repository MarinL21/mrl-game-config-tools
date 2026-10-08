# 绿洲农园 · 可玩 demo

按「节日农场·作物图鉴」策划案 v3 口径做的可玩示意，用来体感核心循环，不是数值验证。

## 直接玩（浏览器打开即可）

**发同事就发这一个**（合集页：顶部两页签 = 玩法 demo ＋ 图文规则说明，单文件 9 MB，首开等几秒）：

- https://htmlpreview.github.io/?https://github.com/MarinL21/mrl-game-config-tools/blob/492aff4/docs/farm_codex_design/demo/oasis_farm_all.html

单独页（同一内容拆开）：

- 可玩 demo：https://htmlpreview.github.io/?https://github.com/MarinL21/mrl-game-config-tools/blob/492aff4/docs/farm_codex_design/demo/oasis_farm.html
- 图文规则说明（17 屏真实截图 + 编号标注 + 数值全集）：https://htmlpreview.github.io/?https://github.com/MarinL21/mrl-game-config-tools/blob/492aff4/docs/farm_codex_design/demo/oasis_farm_intro.html

备用入口：

- githack（透传 `?参数`；同一 IP 短时间开太多次会 429，过一会儿就好；首次有「One more step」点一下）：https://rawcdn.githack.com/MarinL21/mrl-game-config-tools/492aff4/docs/farm_codex_design/demo/oasis_farm_all.html
- GitHub Pages（仓库已开，构建完成后可用，跟 main 最新）：https://marinl21.github.io/mrl-game-config-tools/docs/farm_codex_design/demo/oasis_farm_all.html
- 本地：双击 `farm_all.html` 或 `绿洲农园_玩法示意_单文件.html`
- 直达参数拼在合集页链接后对 demo 页签生效，例如 `https://rawcdn.githack.com/MarinL21/mrl-game-config-tools/492aff4/docs/farm_codex_design/demo/oasis_farm_all.html?state=mid`；`?tab=intro` 直接开图文页签（htmlpreview 入口不透传参数）

打开先弹「玩法示意」，点「开始种菜」进新手指引（8 步）。左下 ❗ 随时回看带图规则（9 页 + 第 10 页「程序规格」给开发 / QA 对照用）。

## 演示口径（与案子不同的只此三条）

1. 1 游戏小时 = 3 秒；1 演示日 = 120 秒，每 3 天一次丰收周末（售价 ×2）
2. 偷菜 60 次 / 祝福 10 次 / 每日种子袋 / 集市每日限购 按演示日重置
3. 等级经验曲线按 demo 压缩

## 评审直达参数（加在 URL 后）

| 参数 | 看什么 |
|---|---|
| `?state=mid` | 进行中的盘面：成熟 / 生长 / 被偷 / 良田 / 可开垦 |
| `?state=npc` | 串门态 |
| `?rule=0` ~ `?rule=9` | 直接打开规则第 N 页；`?rule=9` = **程序规格**（口径与数值全集，可一键复制为 Markdown） |
| `?pop=guard` / `?pop=barn` / `?pop=seed` / `?pop=mile` | 巨猿形态 / 谷仓 / 种子袋 / 勋绩 |
| `?shop=0` / `?shop=1` | 集市两页签 |
| `?ctab=0` / `?ctab=1` | 植物志 / 异变图录 |
| `?rank=0` / `?rank=1` | 丰收榜 / 排名奖励 |
| `?bag` | 直接开一次每日种子袋 |
| `?ring` | 在第一块空地上打开环形选种 |
| `?end` | 活动结束结算 |
| `?noguide` | 关掉新手指引 |
| `?test` | 67 项自检 |

## 目录

- `farm_demo.html` 源（引 `assets/`）
- `oasis_farm_all.html` = `farm_all.html` 合集页（`build_all.py` 把下面两个单文件塞进 <template>，iframe srcdoc 装载）
- `oasis_farm_intro.html` = `farm_intro.html` 图文规则说明（`build_intro.py` 从 demo 真实截图 + `?measure=` 量坐标生成）
- `oasis_farm.html` = `绿洲农园_玩法示意_单文件.html` 单文件交付版（`art/bundle.py` 打出；ASCII 文件名只是为了分享链接干净，中文名在 githack 上也能开）
- `assets/p2/` P2 真实切图 chrome；`assets/art/` 生成的作物 / 场景 / 巨猿形态 / 道具图标
- `art/gen_*.py` 生图脚本（走 p2-art-gen 的 AiArtClient）；原始出图不入库
