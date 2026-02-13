# 🔑 Google Gemini API 配置指南

## 🎯 超简单版（3 分钟完成）

**不用担心"启用 API"，系统会自动帮您完成！**

### 只需 3 步：

#### 1️⃣ 获取密钥（1 分钟）
- 访问：https://aistudio.google.com/app/apikey
- 登录 Google 账号
- 点击"Create API key"
- 复制显示的密钥（像这样：`AIzaSy...`）

#### 2️⃣ 配置工具（30 秒）
- 打开翻译工具
- 粘贴密钥到输入框
- 点击"测试连接"
- 看到"连接成功"✅

#### 3️⃣ 开始翻译（马上）
- 输入中文
- 点击"AI 翻译"
- 完成！🎉

**就这么简单！无需其他任何设置！**

---

## 📝 快速开始

### 第一步：获取免费 API Key（详细步骤）

#### 1. 访问 Google AI Studio

打开浏览器，访问：**[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**

#### 2. 登录 Google 账号

- 使用您的 Google 账号登录（Gmail 账号）
- 如果没有账号，需要先注册一个

#### 3. 创建 API Key

**情况 A：如果是第一次使用**

1. 页面会显示 **"Get API key"** 按钮
2. 点击后，系统会提示选择或创建项目
3. 选择 **"Create API key in new project"**（在新项目中创建）
4. 等待几秒，API Key 就创建好了

**情况 B：如果已有项目**

1. 点击 **"Create API key"** 按钮
2. 选择现有项目或创建新项目
3. 系统会自动生成 API Key

#### 4. 复制 API Key

- API Key 格式类似：`AIzaSyABCDEF123456...`（约 39 个字符）
- 点击复制按钮，或手动选择全部文本复制
- **重要**：API Key 只显示一次，请立即保存

#### 5. 保存 API Key（推荐）

建议将 API Key 保存到：
- 密码管理器（如 1Password、LastPass）
- 或单独的文本文件（妥善保管）
- 不要分享给他人或上传到 GitHub

⚠️ **注意**：如果丢失 API Key，需要重新生成新的

---

## 🔧 启用 API 访问（首次使用需要）

### Google AI Studio 自动启用

好消息！**Google AI Studio 会自动启用 Gemini API 访问**，您无需手动配置。

当您创建 API Key 时：
- ✅ Gemini API 自动激活
- ✅ 免费配额自动分配
- ✅ 无需额外设置

### 验证 API 是否已启用

在我们的翻译工具中：
1. 粘贴 API Key
2. 点击 **"🔌 测试连接"** 按钮
3. 如果显示 **"连接成功 ✓"**，说明 API 已启用

### 如果测试失败怎么办？

**可能原因 1：API Key 刚创建，还未生效**
- 等待 1-2 分钟
- 重新测试连接

**可能原因 2：网络问题**
- 确认可以访问 Google 服务
- 尝试关闭 VPN 或代理

**可能原因 3：API Key 复制不完整**
- 重新复制完整的 API Key（约 39 个字符）
- 确保没有多余的空格

**可能原因 4：Google 账号限制**
- 某些地区可能有访问限制
- 尝试使用其他 Google 账号

---

## 📸 图文说明

### Google AI Studio 界面说明

访问 https://aistudio.google.com/app/apikey 后，您会看到：

**首次访问：**
```
┌─────────────────────────────────────┐
│   Google AI Studio                  │
│                                     │
│   API keys                          │
│                                     │
│   [Get API key] 按钮                │
│                                     │
│   点击后选择：                       │
│   • Create API key in new project  │
│   • Select existing project        │
└─────────────────────────────────────┘
```

**已有 API Key：**
```
┌─────────────────────────────────────┐
│   Your API keys                     │
│                                     │
│   My API Key                        │
│   AIzaSy*******************         │
│   [Copy] [Delete]                   │
│                                     │
│   [+ Create API key]                │
└─────────────────────────────────────┘
```

### 完整流程示意图

```
1. 访问网站
   ↓
2. 登录 Google 账号
   ↓
3. 创建 API Key
   ↓
4. 复制 API Key
   ↓
5. 粘贴到翻译工具
   ↓
6. 测试连接
   ↓
7. 开始翻译 ✅
```

---

## 🎯 配置翻译工具

### 第二步：在工具中配置 API Key

1. 打开翻译工具页面
2. 找到顶部的 **"🔑 Google Gemini API 配置"** 区域
3. 将 API Key 粘贴到输入框中
4. 点击 **"🔌 测试连接"** 按钮
5. 看到 **"连接成功 ✓"** 即可开始使用

✅ **自动保存**：API Key 会自动保存在浏览器中，下次访问无需重新输入

---

## ✨ 开始翻译

配置完成后：

1. 在输入框中输入中文文本（每行一条）
2. 点击 **"🤖 AI 翻译"** 按钮
3. 等待自动翻译完成（每行约1-2秒）
4. 点击 **"📋 复制表格"** 复制到 Excel

---

## 📊 API 配额说明

### 免费额度（完全够用）

- **每分钟**：60 次请求
- **每天**：1,500 次请求
- **价格**：完全免费

### 翻译速度

- **单行文本**：约 1-2 秒
- **10 行文本**：约 10-20 秒
- **100 行文本**：约 2-3 分钟

💡 **提示**：如果翻译很多行，工具会自动控制速度，避免超过限额

---

## 🔒 安全说明

### API Key 存储

- ✅ 存储在**浏览器本地**（localStorage）
- ✅ 不会发送到任何第三方服务器
- ✅ 仅用于调用 Google Gemini API

### 如何保护您的 API Key

1. **设置使用限额**：
   - 访问 [Google Cloud Console](https://console.cloud.google.com/)
   - 找到您的项目 → API & Services → Quotas
   - 设置每日使用限额（例如：每天 1,000 次）

2. **限制 API Key 使用来源**：
   - 在 API Key 设置中
   - 添加应用程序限制（HTTP 引用来源）
   - 仅允许您的网站域名

3. **定期更新 API Key**：
   - 如果怀疑 API Key 泄露
   - 立即在 Google AI Studio 删除旧 Key
   - 创建新的 API Key

---

## ❓ 常见问题

### Q: 如何在 Google AI Studio 启用 API？

**A:** 好消息！**无需手动启用**，完全自动化：

**步骤 1：访问 Google AI Studio**
- 打开 https://aistudio.google.com/app/apikey
- 用 Google 账号登录

**步骤 2：创建 API Key**
- 点击 **"Get API key"** 或 **"Create API key"**
- 选择项目（或创建新项目）
- **系统会自动启用 Gemini API**

**步骤 3：验证是否启用**
- 在翻译工具中粘贴 API Key
- 点击"测试连接"
- 看到"连接成功"即表示 API 已启用

**💡 重点**：
- ✅ API 在创建 Key 时**自动启用**
- ✅ 无需进入 Google Cloud Console
- ✅ 无需手动开启任何开关
- ✅ 免费配额自动分配

**可视化流程：**
```
Google AI Studio
       ↓
点击 "Create API key"
       ↓
选择/创建项目
       ↓
系统自动启用：
✓ Generative Language API
✓ Gemini API
✓ 免费配额
       ↓
获得 API Key
       ↓
可以使用了！✅
```

**如果测试连接失败**：
1. 等待 1-2 分钟（新 Key 需要生效时间）
2. 检查 API Key 是否完整复制
3. 确认网络可以访问 Google 服务
4. 尝试重新生成 API Key

### Q: API Key 会被其他人看到吗？

**A:** 由于这是前端集成，技术上其他人可以在浏览器开发者工具中看到。建议：
- 设置 API 使用限额
- 仅在个人电脑上使用
- 如果是团队共享，建议搭建后端服务

### Q: 翻译质量如何？

**A:** 
- 使用 Gemini-1.5-Flash 模型
- 翻译质量非常高，理解上下文
- 远超普通机器翻译 API
- 适合游戏文本、界面翻译等场景

### Q: 为什么选择 Gemini 而不是其他翻译 API？

**A:** 
1. **完全免费**：Google 提供慷慨的免费额度
2. **质量最高**：AI 模型理解上下文，翻译自然
3. **速度快**：Gemini-1.5-Flash 专为速度优化
4. **支持广泛**：17 种语言同时翻译

### Q: 如果超出免费额度怎么办？

**A:** 
- 每分钟 60 次请求已经很多（约能翻译 60 行文本）
- 如果超出，等待 1 分钟后自动恢复
- 或者等到第二天重置每日限额

### Q: 可以升级到付费版吗？

**A:** 
可以！如果需要更高配额：
1. 在 Google Cloud Console 启用计费
2. Gemini API 按使用量付费（非常便宜）
3. 价格参考：[Gemini API Pricing](https://ai.google.dev/pricing)

---

## 🛠️ 故障排除

### "API 未启用" 或 "API not enabled" 错误

**这个错误很少见，但如果出现，请按以下步骤解决：**

#### 方案 1：等待生效（最常见）
- API Key 刚创建后需要 **1-2 分钟**生效
- 等待后重新测试
- 90% 的情况这样就能解决

#### 方案 2：重新生成 API Key
1. 返回 https://aistudio.google.com/app/apikey
2. 删除旧的 API Key
3. 创建新的 API Key
4. 重新测试

#### 方案 3：检查 Google Cloud 项目
1. 访问 https://console.cloud.google.com/
2. 选择您的项目
3. 进入 **API & Services** → **Library**
4. 搜索 **"Generative Language API"**
5. 确认状态为 **"API enabled"**
6. 如果未启用，点击 **"Enable"** 按钮

#### 方案 4：使用新的 Google 账号
- 某些旧账号可能有限制
- 尝试使用新注册的 Google 账号
- 或使用其他 Gmail 账号

**💡 提示**：99% 的用户只需要在 Google AI Studio 创建 API Key，系统会自动启用所有必要的 API。

### 测试连接失败

**可能原因**：
1. API Key 输入错误
2. 网络连接问题
3. API 尚未激活

**解决方案**：
1. 检查 API Key 是否完整复制
2. 确认网络可以访问 Google 服务
3. 在 Google AI Studio 确认 API Key 已创建

### 翻译时报错

**可能原因**：
1. 超出每分钟配额（60 次）
2. API Key 已失效
3. 输入文本过长

**解决方案**：
1. 等待 1 分钟后重试
2. 重新生成 API Key
3. 分批翻译（每次不超过 50 行）

---

## 📚 更多资源

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API 文档](https://ai.google.dev/docs)
- [API 使用限制](https://ai.google.dev/pricing)
- [Google Cloud Console](https://console.cloud.google.com/)

---

**准备好了吗？** 🚀

[点击这里开始翻译 →](翻译工具.html)
