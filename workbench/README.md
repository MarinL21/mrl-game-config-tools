# 运营策划工作台 · workbench

一个站装下 SLG 运营 + 商业化的全部工具。外壳 + 模块结构，模块一个个往里加。

| | |
|---|---|
| 启动 | `cd workbench && ./run.sh -d` → http://127.0.0.1:8790 |
| 停 | `./run.sh stop` |
| 换端口 | `WB_PORT=8791 ./run.sh -d` |
| 依赖 | Python 3.14 + fastapi / uvicorn / pillow / python-multipart（已装） |
| 视频封面 | macOS 自带 `qlmanage`，不需要 ffmpeg |

## 模块

| 模块 | 状态 | 说明 |
|---|---|---|
| **竞品外观库** | ✅ 已上线 | 竞品外显素材（图 + 视频）按 游戏 × 类别 汇总 |
| 节日运营驾驶舱 | 待并入 | 现在还在 `festival_ops/`（8781），后续搬进来 |
| 数值工作台 | 规划中 | 礼包定价 / ROI / 蒙卡 |
| 商业化看板 | 规划中 | 营收回归 / 付费分层 |

---

## 竞品外观库怎么用

### 1. 投喂（三条路，可混用）

| 路子 | 做法 | 适合 |
|---|---|---|
| **收件箱**（主路） | 把图 / 录屏拖进 `workbench/inbox/`，网页点「扫描收件箱」 | 一次收一批、视频 |
| 网页拖拽 | 直接把文件拖到网页上 | 临时补一两张 |
| 会话贴给我 | 在对话里粘贴截图，我存进 `inbox/` 再扫 | 顺手一张 |

支持 `png jpg jpeg webp gif heic` / `mp4 mov m4v webm`。
**按内容指纹去重** —— 同一张图重复丢进来只会有一份，收件箱扫完自动清空。

### 2. 打标（游戏 / 类别 / 名称 / 标签 / 备注 / 评分）

- **网页手改**：点开任意一件 → 右侧面板改，改完自动存。游戏和类别都能直接输入新词，不用先建。
- **批量**：点「多选」（或按住 ⌘ 点卡片）→ 底部条统一设游戏 / 类别 / 加标签 / 删除。
- **AI 预标**：跟我说一句「新进来的打个标」，我走下面这条管线，你只需在网页上纠正。

```bash
python3 tools/wb.py scan          # 收件箱入库
python3 tools/wb.py sheet         # 待标注拼成一张带编号大图（我看一张顶 20 张，省 token）
python3 tools/wb.py tag tags.json # [{n:1, game:"...", category:"...", title:"...", tags:"..."}] 写回
python3 tools/wb.py stat          # 看进度
```

### 3. 看

左栏按 游戏 / 类别 / 待标注 / 图片 / 视频 筛，顶栏搜名称·标签·备注·文件名。
点开大图或播视频，`← →` 切换、`Esc` 关。地址栏的 `#g/12` 是这一件的固定链接，可以存下来或发人。

> 分类池初值在 `taxonomy.json`（22 个竞品 + 19 个外观类别），只在建库时播种一次；
> 之后以库里为准，网页上加的删的都不会被它覆盖。

---

## 加一个新模块（三步）

1. `modules/<key>/api.py` —— 写一个 `router = APIRouter(prefix="/api/<key>")`，在 `server.py` 里 include。
2. `static/mod_<key>.js` —— 导出 `mount(root, ctx)`，可选 `unmount()` / `onSearch(q)`。
3. `server.py` 的 `MODULES` 加一行（`ready: true` 才可点）。

数据表统一放 `core/db.py` 的 `SCHEMA`，表名带模块前缀（`gallery_*`），一个库装所有模块。

## 数据在哪

```
workbench/
├── inbox/            收件箱（扫完即空）
├── data/             ⚠ 全部身家，不进 git，要备份就备份这个目录
│   ├── workbench.db  SQLite：素材记录 + 分类池
│   ├── media/        原图 / 原视频（按内容指纹分目录）
│   ├── thumbs/       600px 缩略图（网格只加载它，所以不卡）
│   └── sheets/       AI 预标用的拼图，可随时删
├── core/             db.py 数据层 · media.py 入库与缩略图
├── modules/gallery/  竞品外观库后端
├── static/           app.js 外壳 · mod_gallery.js 模块 · app.css
└── tools/wb.py       命令行入口
```
