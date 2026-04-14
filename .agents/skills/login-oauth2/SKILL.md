---
name: login-oauth2
description: 自动接入OAuth2登录系统。两步流程：第一步，提供参数模板（systemName、url、redirectUris、employeeId、thirdParty、accessCompanyIds）等待用户填写；第二步，自动完成所有功能（获取配置、生成后端代码、实现前端自动登录、检查并补全）。检查和补全时：用户说"完善登录"等，先检查现有代码，如果配置存在则补全缺失功能，否则执行完整接入流程。支持多语言后端（Node.js、Python、Java、Go等）和多框架前端（React、Vue、Angular等）。
---

# OAuth2 登录系统接入

自动为项目接入第三方登录（OAuth2）系统，**根据项目后端语言自动生成对应语言的代码**。

## 第一步强制要求

**当用户说"接入登录功能"、"接入登录系统"等时：**

1. **立即停止所有操作**（检测、生成代码、调用接口等）
2. **提供参数模板**（JSON格式，包含systemName、url、redirectUris、employeeId、thirdParty、accessCompanyIds）
3. **等待用户填写并回复参数**
4. **禁止在第一步写任何代码**

> **💡 使用提示：** 本技能适合**直接部署项目使用**。生成的代码和配置可以直接用于生产环境部署，包含完整的OAuth2登录流程、Token过期处理、安全验证等功能。适用于需要快速接入OAuth2登录系统的新项目或现有项目。
>
> **🔧 多语言支持：** 若用户写了后端或项目已有后端，则匹配对应语言生成代码（如 Java、Python、Go 等）；若用户未写后端或未检测到后端，则**优先使用 Node** 写后端。Node 后端有独立模板文件，保证登录流程稳定。所有语言版本都实现相同的 OAuth2 功能：登录、回调、登出、获取用户信息、Token 过期处理等。

## 功能特性

- ✅ **自动检测项目技术栈**：自动识别后端语言和前端框架
- ✅ **多语言后端支持**：支持 Node.js、Python、Java、Go、PHP、Ruby、C#/.NET
- ✅ **多框架前端支持**：支持 React、Vue、Angular、Svelte、原生HTML/JS
- ✅ **自动登录逻辑**：页面初次进入时自动检查登录状态，未登录时自动跳转
- ✅ **完整OAuth2流程**：包含登录、回调、登出、获取用户信息等功能
- ✅ **安全防护**：Token过期处理、CSRF防护（State验证）、Session管理
- ✅ **OAuth 固定接口**：认证/Token/用户信息/登出 四个地址固定为 `ms-open-gateway-qa.tap4fun.com/loginpass/oauth/...`，禁止使用 `loginpass-bff` 或 `/oauth/...` 路径（用错会 404）

## 使用流程

当您说"接入登录功能"等时，技能会按以下两步完成配置：

### 第一步：填写请求参数

技能会向您提供请求参数模板，您需要填写以下信息：

```json
{
    "systemName": "你要添加的系统名称",
    "url": "https://your-domain.com 或 http://xx.xx.xx.xx:YOUR_PORT",
    "redirectUris": "https://your-domain.com/callback 或 http://xx.xx.xx.xx:YOUR_PORT/callback",
    "employeeId": 99999999,
    "thirdParty": true,
    "accessCompanyIds": [1]
}
```

**重要提示：** 
- `url` 可以是IP地址（如 `http://172.20.62.21:3003`）或域名（如 `https://example.com`）
- `redirectUris` 格式为 `{url}/callback`
- 不要使用 `localhost`，必须使用IP地址或域名
- **端口规则：** 前端项目的端口号 = url 中的端口号；后端端口号 = 前端端口号 + 1（例如 url 为 `http://172.20.62.21:3003` 则前端 3003，后端 3004）
- `thirdParty`、`accessCompanyIds` 可不填：未提供时默认 `thirdParty: true`，`accessCompanyIds: [1]`
- **登记应用若出现 404：** 向登录系统**注册/登记本应用**用的是独立接口（`PUT .../application/automation/add`），与页面上常见的 OAuth 授权地址（`.../loginpass/oauth/...`）不是一回事；若助手误调接口导致 404，请到本技能目录下查找 **`scripts/get_oauth_config.py`**（例如仓库内 `login-oauth2/scripts/`，或安装路径 `~/.cursor/skills/login-oauth2/scripts/`），用与上表相同的参数在本地执行；也可请助手在项目中搜索该脚本并代你运行，勿自行猜测其它 URL。

### 第二步：自动完成所有功能

**收到您的参数后，技能会自动完成以下所有工作（无需您说"继续"）：**

1. **检查前后端项目**
   - 若项目没有前端或没有后端，会先主动为您补充完整（创建前端或后端），再按本技能实现完整登录功能。

2. **获取OAuth2配置与回填数据**
   - **用户每次提供参数都要回填数据**：调用接口后（无论成功或失败）都会将用户参数与接口返回的数据写入配置；接口失败时也会用用户参数回填能写的项，并提示缺失项建议重试或手动填写。
   - **再次提供参数时一律以本次为准**：例如第一次提供 url 后接口报错，用户再次提供 url 等信息时，接口请求与回填都只使用**本次**提交的参数和**本次**接口返回结果，保证 url 等参数与回填数据都是最新的，不沿用上次的数据。
   - 收到参数后先做参数完整性检查（一），必填项齐全再调用接口；接口返回后执行回填，再做参数完整性检查（二），通过后再继续。
   - **注册登录系统（申请 OAuth 应用）若返回 404：** 常见原因是误调了接口（例如 HTTP 方法错误、路径错误，或把 OAuth 网关地址 `ms-open-gateway-qa.../loginpass/oauth/...` 当成注册接口）。**正确做法**与本仓库脚本一致：`PUT https://loginpass-bff-qa.tap4fun.com/application/automation/add`，请求体字段见参数模板。此时**必须**向用户说明：请到本技能目录查找并执行 Python 脚本 **`scripts/get_oauth_config.py`**（常见路径：`login-oauth2/scripts/get_oauth_config.py` 或 `~/.cursor/skills/login-oauth2/scripts/get_oauth_config.py`）；或由助手在用户的 workspace 与本技能安装路径下**搜索 `get_oauth_config.py`**，找到后**替用户执行**该脚本（传入与用户一致的参数），不要继续猜测其它 URL。

3. **生成后端代码**
   - 检测项目使用的后端语言（Node.js、Python、Java、Go、PHP、Ruby、C#/.NET）
   - 生成对应语言的OAuth2实现代码
   - 实现完整的OAuth2功能：登录路由、回调处理、登出、获取用户信息、Token过期处理等

4. **实现前端自动登录**
   - 检测项目使用的前端框架（React、Vue、Angular、Svelte、原生HTML/JS）
   - 实现自动登录逻辑：页面初次进入时自动检查登录状态，未登录时自动跳转，第一次登录失败不等待、后续可等待10秒重试

5. **检查并补全登录流程**
   - 全面检查登录流程是否完善（后端配置、路由实现、功能实现、前端实现）
   - 自动补全缺失的功能，修复发现的问题
   - 确保所有登录功能都完整且正确实现

**最终结果：**
- ✅ 完整的OAuth2登录系统已接入
- ✅ 后端和前端代码已生成并配置完成
- ✅ 所有功能已检查并补全

## 环境要求

**本地开发环境：**
- 必须使用配置的系统地址访问（如 `http://xx.xx.xx.xx:YOUR_PORT`）
- 不要使用 `localhost`，OAuth2回调需要匹配配置的 `redirectUris`

## 生成的功能

### 后端功能

所有后端语言都会生成以下功能：

- **登录路由** (`GET /oauth/login`) - 重定向到OAuth授权页面
- **回调处理** (`GET /callback`) - 处理OAuth回调，获取用户信息
- **登出路由** (`GET /oauth/logout`) - 清除登录状态
- **获取用户信息** (`GET /oauth/user`) - 获取当前登录用户信息
- **Token过期处理** - 自动检测并处理token过期
- **CSRF防护** - State验证防止跨站请求伪造
- **Session管理** - 安全的会话状态管理

### 前端功能

所有前端框架都会实现：

- **自动登录检查** - 页面加载时自动检查登录状态
- **自动跳转登录** - 未登录时自动跳转到登录页面
- **自动重试机制** - 第一次登录失败不等待；后续重试可等待10秒后再试
- **用户信息管理** - 自动获取和保存用户信息

## 注意事项

1. **OAuth2配置**：必须使用从接口获取的实际配置值，不要手动填写。CLIENT_ID、CLIENT_SECRET、REDIRECT_URI 在所有语言中均存成代码常量，不从 .env/application.yml 读取。
2. **IP地址要求**：必须使用IP地址访问，不能使用 `localhost`
3. **Token过期**：系统会自动处理token过期，过期后需要重新登录
4. **跨域配置**：如果前端和后端不在同一域名，需要确保后端配置了CORS
5. **登出功能**：如果保留登出按钮，需要自行创建未登录的停留页面，或选择去掉登出按钮
6. **注册接口 404：** 勿与「OAuth 固定接口」（`ms-open-gateway-qa.../loginpass/oauth/...`）混淆；向登录系统**登记应用**须用 `PUT .../application/automation/add`（与 `scripts/get_oauth_config.py` 一致）。若出现 404，按第二步「获取OAuth2配置」中的说明：提示用户查找该 Python 脚本本地执行，或由助手搜索并执行 `get_oauth_config.py`。
