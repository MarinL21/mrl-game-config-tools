# 🎮 游戏运营策划工具

快速配置游戏奖励与掉落的Web工具集

## ⚡ 快速开始

### 方式 1：前端工具（零配置）

直接在浏览器中打开 `index.html`，即可使用：
- 礼包配置工具
- 掉落配置工具  
- 翻译工具（前端版）

### 方式 2：后端版翻译工具（推荐）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 Gemini API Key

# 3. 启动服务
./start.sh  # Linux/Mac
# 或
start.bat   # Windows
# 或
python main.py

# 4. 打开 翻译工具-后端版.html
```

📖 **详细文档**：[后端使用说明.md](后端使用说明.md) | [部署指南](后端部署指南.md) | [项目说明.md](项目说明.md)

---

## 📦 功能模块

### 1. 奖励配置工具
- ✅ 快速配置礼包奖励JSON
- ✅ 支持自定义物品和数量
- ✅ 自动计算XP和帮派宝箱
- ✅ 可选固定配置
- ✅ 拖拽排序
- ✅ 一键复制压缩格式

### 2. 掉落配置工具
- ✅ 配置随机掉落奖励
- ✅ 设置权重和抽取次数
- ✅ 实时显示掉落概率
- ✅ 拖拽排序
- ✅ JSON格式输出

### 3. 多语言翻译工具
- ✅ **安全**：API Key 存储在服务器端，不会暴露
- ✅ **AI 翻译**：使用 Google Gemini 2.5 Flash 最新模型
- ✅ **高质量**：AI 理解上下文，翻译准确自然
- ✅ **统一管理**：可添加访问控制、日志、缓存等功能
- ✅ **免费部署**：支持 Vercel、Railway 等平台
- ✅ 批量翻译中文到17种语言
- ✅ 一键复制到Excel/Google Sheets

**技术栈**：FastAPI (Python) + Google Gemini API

**使用流程**：
1. 启动后端服务（本地或云端）
2. 打开翻译工具页面
3. 输入中文 → 点击翻译 → 复制到 Excel

📖 [快速开始](后端使用说明.md) | [部署指南](后端部署指南.md) | [API Key 获取](Gemini%20API配置指南.md)

## 🚀 使用方法

1. 打开 `index.html` 进入主页
2. 选择需要的配置工具
3. 添加物品和参数
4. 复制生成的JSON配置

## 🌐 在线访问

[点击访问在线版本](https://你的用户名.github.io/仓库名/)

## 📝 技术栈

### 前端工具
- HTML5 + CSS3 + JavaScript (ES6+)
- 无需后端服务器
- 可直接部署到 GitHub Pages

### 后端服务（翻译工具）
- **框架**：FastAPI (Python 3.9+)
- **AI 模型**：Google Gemini-1.5-Flash
- **部署**：Vercel / Railway / Heroku
- **特性**：异步处理、CORS 支持、环境变量管理

## 📂 项目文件

```
├── 前端文件
│   ├── index.html                    # 主页
│   ├── 礼包配置工具.html
│   ├── 掉落配置工具.html
│   ├── 翻译工具.html                # 前端版
│   └── 翻译工具-后端版.html          # 后端版
│
├── 后端文件
│   ├── main.py                       # FastAPI 服务
│   ├── requirements.txt              # Python 依赖
│   ├── .env.example                  # 配置模板
│   ├── test_api.py                   # 测试脚本
│   └── start.sh / start.bat          # 启动脚本
│
└── 文档
    ├── README.md                     # 本文件
    ├── 项目说明.md                   # 完整说明
    ├── 后端使用说明.md               # 快速入门
    └── 后端部署指南.md               # 部署文档
```

## 📄 License

MIT License

---

© 2026 游戏运营策划工具
