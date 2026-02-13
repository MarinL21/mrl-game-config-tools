# 🚀 详细启动指南 - Mac 系统

## 📋 前置准备

- ✅ 已下载安装 Python 3.9+
- ✅ 有 Google 账号（用于获取 API Key）
- ✅ 项目文件已下载到 `/Users/marinl/游戏运营策划工具`

---

## 🎯 第一步：打开终端

### 方法 1：使用聚焦搜索

1. 按键盘快捷键：`Command + Space`
2. 输入：`Terminal` 或 `终端`
3. 按回车键

### 方法 2：从应用程序打开

1. 打开 Finder
2. 进入 `应用程序` → `实用工具`
3. 双击 `终端.app`

**终端打开后**，您会看到一个黑色或白色的窗口，里面有闪烁的光标。

---

## 🎯 第二步：验证 Python 安装

### 2.1 检查 Python 版本

在终端中输入以下命令（然后按回车）：

```bash
python3 --version
```

**预期输出**：
```
Python 3.9.13
```
或
```
Python 3.10.x
```
或
```
Python 3.11.x
```

只要显示 `Python 3.9` 或更高版本就可以！✅

### 2.2 如果提示"command not found"

说明 Python 未正确安装，请：

1. 访问 https://www.python.org/downloads/
2. 下载 macOS 最新版本
3. 双击安装包 `.pkg` 文件
4. 按照向导完成安装
5. 重新打开终端，再次测试

---

## 🎯 第三步：进入项目目录

### 3.1 输入命令

在终端中复制粘贴以下命令：

```bash
cd "/Users/marinl/游戏运营策划工具"
```

**提示**：
- 可以直接复制粘贴（`Command + C` 复制，`Command + V` 粘贴）
- 路径中的中文字符是正常的
- 必须包含引号（因为路径中有空格和中文）

按回车执行。

### 3.2 验证是否成功

输入命令：

```bash
pwd
```

应该显示：
```
/Users/marinl/游戏运营策划工具
```

### 3.3 查看项目文件

输入命令：

```bash
ls
```

您应该看到以下文件：
```
Gemini API配置指南.md
README.md
index.html
main.py
requirements.txt
翻译工具.html
翻译工具-后端版.html
...（更多文件）
```

如果看到这些文件，说明进入目录成功！✅

---

## 🎯 第四步：安装依赖包

### 4.1 执行安装命令

在终端中输入：

```bash
pip3 install -r requirements.txt
```

按回车执行。

### 4.2 等待安装完成

**安装过程**大约需要 1-3 分钟，您会看到类似这样的输出：

```
Collecting fastapi==0.109.0
  Downloading fastapi-0.109.0-py3-none-any.whl (92 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 92.1/92.1 kB 1.2 MB/s eta 0:00:00
Collecting uvicorn[standard]==0.27.0
  Downloading uvicorn-0.27.0-py3-none-any.whl (60 kB)
...
Installing collected packages: ...
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 google-generativeai-0.3.2 ...
```

**最后一行**应该显示：
```
Successfully installed ...
```

看到 `Successfully installed` 说明安装成功！✅

### 4.3 常见问题

#### 问题：pip3: command not found

**解决方案**：使用 python3 模块方式安装

```bash
python3 -m pip install -r requirements.txt
```

#### 问题：权限错误（Permission denied）

**解决方案**：添加 `--user` 参数

```bash
pip3 install --user -r requirements.txt
```

#### 问题：网络超时

**解决方案**：使用国内镜像源

```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 🎯 第五步：获取 API Key

### 5.1 打开 Google AI Studio

在浏览器中访问：

```
https://aistudio.google.com/app/apikey
```

### 5.2 登录 Google 账号

- 使用您的 Gmail 账号登录
- 如果没有账号，需要先注册一个

### 5.3 创建 API Key

**首次使用**：

1. 页面会显示 **"Get API key"** 按钮
2. 点击按钮
3. 选择 **"Create API key in new project"**（在新项目中创建）
4. 等待 5-10 秒

**已有项目**：

1. 点击 **"Create API key"** 按钮
2. 选择现有项目或创建新项目
3. 等待 API Key 生成

### 5.4 复制 API Key

创建成功后，会显示您的 API Key：

```
AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567
```

**立即复制**（点击复制按钮或手动选中复制）

⚠️ **重要**：
- API Key 只显示一次
- 请妥善保存
- 不要分享给他人

---

## 🎯 第六步：配置环境变量

### 6.1 创建配置文件

回到终端，输入命令：

```bash
cp .env.example .env
```

按回车执行。

**解释**：这个命令会复制 `.env.example` 文件并命名为 `.env`

### 6.2 打开配置文件

使用文本编辑器打开 `.env` 文件：

```bash
open -a TextEdit .env
```

**TextEdit（文本编辑器）**会自动打开，显示文件内容：

```
# Google Gemini API 配置
# 获取 API Key: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# 示例：GEMINI_API_KEY=AIzaSyABCDEF123456...
```

### 6.3 填入 API Key

将 `your_api_key_here` 替换为您刚才复制的 API Key。

**修改前**：
```
GEMINI_API_KEY=your_api_key_here
```

**修改后**（示例）：
```
GEMINI_API_KEY=AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567
```

⚠️ **注意格式**：
- ✅ 正确：`GEMINI_API_KEY=AIzaSy...`（等号两边无空格）
- ❌ 错误：`GEMINI_API_KEY = AIzaSy...`（有空格）
- ❌ 错误：`GEMINI_API_KEY="AIzaSy..."`（有引号）

### 6.4 保存文件

- 按 `Command + S` 保存
- 关闭 TextEdit 窗口

---

## 🎯 第七步：启动后端服务

### 7.1 执行启动命令

回到终端，输入命令：

```bash
python3 main.py
```

按回车执行。

### 7.2 等待服务启动

**大约 3-5 秒后**，您会看到以下输出：

```
============================================================
✅ 游戏运营策划工具 - 翻译服务
============================================================

📡 服务地址：http://localhost:8000
📖 API 文档：http://localhost:8000/docs
🔍 健康检查：http://localhost:8000/health

============================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**看到这个输出说明服务启动成功！** 🎉

### 7.3 重要提示

⚠️ **不要关闭这个终端窗口！**

- 服务需要持续运行
- 如果关闭终端，服务会停止
- 如果要停止服务，按 `Control + C`

---

## 🎯 第八步：测试服务

### 8.1 打开新的终端窗口

**不要关闭第一个终端！**

打开第二个终端窗口：
- 方法 1：按 `Command + N`（新建窗口）
- 方法 2：按 `Command + T`（新建标签页）
- 方法 3：再次打开终端应用

### 8.2 进入项目目录

在新终端中输入：

```bash
cd "/Users/marinl/游戏运营策划工具"
```

### 8.3 运行测试脚本

输入命令：

```bash
python3 test_api.py
```

### 8.4 查看测试结果

**预期输出**：

```
🧪 ========================================================
     游戏运营策划工具 - 后端 API 测试
============================================================

🔗 测试目标: http://localhost:8000

============================================================
  测试 1: 健康检查
============================================================

状态码: 200
✅ 服务状态: healthy
✅ API 已配置: True
✅ 支持语言数: 17

============================================================
  测试 2: 获取支持的语言
============================================================

✅ 支持 17 种语言
   语言代码: en, fr, de, po, zh...

============================================================
  测试 3: 翻译功能
============================================================

测试文本: ['规则', '如何取得点数']
⏳ 正在翻译...
✅ 成功翻译 2 条文本

📊 翻译结果示例:

原文: 规则
  en: Rules
  fr: Règles
  de: Regeln
  jp: ルール
  kr: 규칙

============================================================
  测试总结
============================================================

✅ 通过  健康检查
✅ 通过  语言列表
✅ 通过  翻译功能

📊 总计: 3/3 通过

🎉 所有测试通过！后端服务运行正常

📖 API 文档: http://localhost:8000/docs
```

**看到 "🎉 所有测试通过！" 说明服务完全正常！** ✅

---

## 🎯 第九步：使用前端页面

### 9.1 打开文件

**方法 1：使用 Finder**

1. 打开 Finder（访达）
2. 按 `Command + Shift + G`（前往文件夹）
3. 输入：`/Users/marinl/游戏运营策划工具`
4. 按回车
5. 找到 `翻译工具-后端版.html` 文件
6. 双击打开（会在浏览器中打开）

**方法 2：使用终端命令**

在终端中输入：

```bash
open "翻译工具-后端版.html"
```

### 9.2 检查 API 配置

页面打开后，在顶部找到 **"🔗 后端 API 配置"** 区域。

确认地址为：
```
http://localhost:8000
```

如果不是，手动修改为 `http://localhost:8000`

### 9.3 开始翻译

**步骤 1：输入文本**

在 "输入中文文本" 框中输入：

```
规则
如何取得点数
注意事项
进行中
```

**步骤 2：点击翻译**

点击 **"🤖 开始翻译"** 按钮

**步骤 3：等待完成**

您会看到进度提示：
```
🤖 正在翻译第 1/4 行
规则
```

大约 5-10 秒后翻译完成。

**步骤 4：复制结果**

点击 **"📋 复制表格到剪贴板"** 按钮

系统会提示：
```
✅ 表格已复制到剪贴板！
可以直接粘贴到 Excel 或 Google Sheets
```

**步骤 5：粘贴到 Excel**

1. 打开 Excel 或 Google Sheets
2. 选中一个单元格
3. 按 `Command + V` 粘贴
4. 完成！

---

## 🎉 完成！

恭喜！您已经成功：

✅ 安装了 Python 依赖  
✅ 配置了 Gemini API Key  
✅ 启动了后端服务  
✅ 测试了 API 功能  
✅ 使用了翻译工具  

---

## 📝 每次使用流程

**第一次之后**，每次使用只需要两步：

### 1. 启动后端服务

打开终端，输入：

```bash
cd "/Users/marinl/游戏运营策划工具"
python3 main.py
```

### 2. 打开前端页面

双击 `翻译工具-后端版.html` 文件

就这么简单！

---

## 🛑 如何停止服务

当您不需要使用时，可以停止后端服务：

1. 切换到运行 `python3 main.py` 的终端窗口
2. 按 `Control + C`
3. 服务会停止

输出会显示：
```
INFO:     Shutting down
INFO:     Finished server process [12345]
```

---

## 🔧 快速启动脚本

为了更方便，您可以使用启动脚本：

```bash
# 给脚本添加执行权限（只需执行一次）
chmod +x start.sh

# 以后每次启动，只需运行：
./start.sh
```

启动脚本会自动：
- 检查 Python 环境
- 安装依赖（如果需要）
- 检查配置文件
- 启动服务

---

## ❓ 常见问题

### Q1：如何重新配置 API Key？

**A1**：编辑 `.env` 文件

```bash
cd "/Users/marinl/游戏运营策划工具"
open -a TextEdit .env
```

修改后保存，然后重启服务。

### Q2：如何查看 API 使用情况？

**A2**：访问 Google AI Studio

https://aistudio.google.com/

查看 API 使用统计。

### Q3：服务启动失败怎么办？

**A3**：检查以下几点

1. 检查 Python 版本：`python3 --version`
2. 检查依赖是否安装：`pip3 list`
3. 检查 `.env` 文件是否存在：`ls -la .env`
4. 检查 API Key 是否正确：`cat .env`
5. 查看详细错误信息

### Q4：端口 8000 被占用？

**A4**：查找并终止占用端口的进程

```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 终止进程（替换 12345 为实际的 PID）
kill -9 12345
```

或者修改端口：

在 `main.py` 文件中，将 `port=8000` 改为其他端口，如 `port=8080`。

### Q5：前端连接失败？

**A5**：检查清单

- [ ] 后端服务是否在运行？
- [ ] API 地址是否正确？（`http://localhost:8000`）
- [ ] 浏览器访问 http://localhost:8000/health 是否正常？
- [ ] 是否有防火墙拦截？

---

## 📚 更多资源

- [后端部署指南](后端部署指南.md) - 部署到云端
- [Gemini API配置指南](Gemini%20API配置指南.md) - API Key 详细说明
- [项目说明](项目说明.md) - 完整项目文档

---

## 📞 需要帮助？

如果遇到问题：

1. 查看本文档的"常见问题"部分
2. 查看终端的错误信息
3. 查看浏览器控制台（按 `Option + Command + J`）
4. 提交 GitHub Issue

---

**祝您使用愉快！** 🚀

最后更新：2026-02-05
