# 深海探宝 · 活动开始介绍流程（三联图）

2026-09-08 出稿。对象 = 12 月节「深海探宝」（2112 = **21129575**）活动开局自动弹出的三页玩法教学。

## 交付物

| 文件 | 用途 |
|---|---|
| **intro3.preview.html** | 评审看这个（带缩放条：适应宽度 / 整板 / 100%） |
| **intro3.bundle.html** | 单文件自包含版，双击即开、可直接传人（1.5 MB） |
| intro3_p1/p2/p3.png | 三张单屏 1920×1080，贴案子表 / Jira 用 |
| intro3_board.jpg | 整块三联板 6220×1940，GitHub 上直接能看 |
| intro3.html + intro3.js | 源文件（renderScreen(state) 驱动，改内容改这两个） |
| scripts/prep_assets.py | 从真机截图重建全部切图（源图也在仓库里，可复现） |
| shot.py | 单屏出图：`python3 shot.py 2` → intro3_p2.png |

## 发同事的链接（公开仓库，免登录直接开）

**交互稿**（带缩放条，1.5 MB 单文件，第一次打开等一两秒）：
https://rawcdn.githack.com/MarinL21/mrl-game-config-tools/ec11348/docs/treasure_dive_design/ux/intro3.preview.html

**整板一张图**（不想点的人看这个）：
https://github.com/MarinL21/mrl-game-config-tools/blob/main/docs/treasure_dive_design/ux/intro3_board.jpg

**目录**：https://github.com/MarinL21/mrl-game-config-tools/tree/main/docs/treasure_dive_design/ux

> githack 链接里那段 `ec11348` 是 commit sha，**换稿后要换成新 sha** 才是新版本（sha 版永久缓存、不会串版）。
> `raw.githack.com`（不带 cdn 那个域）会 403，别用。

## 版式（0909 定版）

照竞品 **HOW TO PLAY** 弹窗做：整屏 1920×1080 黑底 + 金色横幅，**每页三联分镜**（盘面示意 → 金色标题 → 说明框，联与联之间橙色弯箭头），底部横贯一条汇总条。三页同一个壳，只换中间三联。

| 页 | 三联 | 底部横条 |
|---|---|---|
| ① 怎么下潜 | 点开格子 → 只能挖通路 → 下潜 +10 米 | 5 类格子各花多少水母 |
| ② 道具怎么用 | 炸弹炸 13 格 → 手电通吃整列 → 只能放空格或海藻 | 金框 / 红框图例 + 道具来源 |
| ③ 海螺换奖 + 深度奖励 | 海螺从哪来 → 拿海螺换奖 → 潜得越深奖越大 | 深度 11 档阶梯（点一档切三态） |

**能点的**：左右翻页圆钮、底部页码点、右上 ✕（关闭 → 「再看一次」叫回来）、③页底部 11 档阶梯（点一档看「已达成 / 下一档 / 未达成」）。三联分镜本身是**静态示意**——实装每联各 K 一小段循环动画，别摆死图。

## 口径来源

机制一律按服务端 `actvdom/treasuredivedom` 通读结论 + 2121 / 2189 实配，不按案子早期粗口径：
6 列 × 8 行 / 10 米一行 / 单次下潜上限 32 行写死在服务端；炸弹 13 格只卷气泡与石块；
手电整列通吃；海藻 3×3 中心格不可破、可点 8 格；宝箱 cost 0、可点 3~5 次。
深度奖励 = 2115 group10003（11 档 300→12000 m，fin_cond cat=10149044，**不要补 arg.ids**）；
兑换商店 = 2116 group58（17 位，金 / 银双币）。

## 素材

真机截图（2026-09-01 徐琮淦发的 treasure_dive 测试包截图）裁出盘面格子 / 工具钮 / 商店入口 /
深度轨 / 场景底；弹窗与按钮走共享素材库母版（高弹窗底板 1542×1027）；
水母图标 = p2-art-gen nano 出图后抠的发光水母。全部落 `assets/`。

## 自检

```bash
python3 check_sizes.py intro3.html          # 每屏 1920×1080 + 有没有元素跑出屏 + 文字有没有被裁
python3 check_sizes.py intro3.bundle.html   # 打包后再跑一次
open "intro3.html?autotest"                 # 自己点一遍：三联数 / 范围格数 / 阶梯三态逐条断言
```

⛔ 布局对错一律读数字，别靠肉眼：深度轨那条竖线曾经只有 3px 高，
根因是 `p2ux19.css` 里的 `.ln{height:3px}` 把 `top/bottom` 撑高吃掉了 —— 是探针量出来的，图上看不出来。
