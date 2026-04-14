# 详细工作流程

本文档包含 OAuth2 登录系统接入的详细工作流程说明。

## 第一步强制要求（新接入场景）

**当用户说"接入登录功能"、"接入登录系统"等时：**

1. **立即停止所有操作**（检测、生成代码、调用接口等）
2. **提供参数模板**（JSON格式：systemName、url、redirectUris、employeeId、thirdParty、accessCompanyIds）
3. **等待用户填写并回复参数**
4. **禁止在第一步写任何代码**

**禁止行为：**
- 跳过提供参数模板
- 假设用户会提供参数，直接开始检测或生成代码
- 从其他地方（项目配置、环境变量等）获取参数
- 在没有收到用户参数时，尝试调用接口或生成代码

**触发场景：**

1. **场景1：新接入**
   - 触发词："接入登录功能"、"接入登录系统"等
   - 执行：提供参数模板 → 等待用户回复 → 调用接口获取配置 → 生成代码

2. **场景2：检查和补全**
   - 触发词："完善登录"、"检查登录"、"优化登录"等
   - 执行：检查现有代码 → 如果配置存在则补全，否则执行完整接入流程

**用户视角的两步流程：**

1. **第一步：填写请求参数**
   - 提供参数模板 → 等待用户填写并回复参数

2. **第二步：自动完成所有功能（收到参数后自动执行，无需用户说"继续"）**
   - 收到用户参数后，**先检查是否有前端和后端项目，没有则主动补充完整**，再执行：调用接口获取配置 → 生成/补全后端代码 → 实现前端自动登录 → 检查并补全
   - **关键：收到用户参数后立即开始执行，不需要等待用户说"继续"**

**内部执行步骤（自动完成，无需用户参与）：**

0. **检查并补全前后端项目（收到参数后第一步）**
   - 检测当前项目是否已有前端、是否已有后端
   - 若**没有前端**：主动创建前端项目（如简易 React/Vue/静态页面），再按本 skill 实现前端登录逻辑
   - 若**没有后端**：主动创建后端项目（优先 Node，参考 node_koa_template.md），再按本 skill 实现 OAuth 路由与配置
   - 确保项目同时具备前端与后端后，再执行后续步骤

1. **获取OAuth2配置**
   - 调用接口 → 解析配置 → 写入配置文件 → 验证配置

2. **生成/补全后端代码**
   - 检测后端语言（若无后端则按默认用 Node）→ 生成对应语言的 OAuth2 实现代码

3. **实现前端自动登录**
   - 检测前端框架（若无前端则创建后再实现）→ 实现自动登录逻辑

4. **检查并补全**
   - 全面检查登录流程 → 补全缺失功能

## 流程状态管理

**用户交互：**
- 第一步：提供参数模板，等待用户填写并回复参数
- 第二步：收到用户参数后，自动执行所有功能，完成后发送最终完成提示（包含测试步骤和使用说明）
- **关键：收到用户参数后立即自动执行第二步，不需要用户说"继续"**

**内部执行：**
- 在第二步中，内部按顺序执行：获取配置 → 生成后端代码 → 实现前端自动登录 → 检查并补全
- 如果某个内部步骤失败，记录错误并继续执行后续步骤
- 所有步骤完成后，生成检查报告并发送最终完成提示

## 代码检查流程（场景2：检查和补全）

**触发条件：** 用户说"完善登录"、"检查登录"、"优化登录"等时，先执行代码检查流程。

**执行步骤：**

### 第一步：检查现有代码和配置

**1. 检查后端配置（CLIENT_ID、CLIENT_SECRET、REDIRECT_URI）：**

检查以下位置是否存在OAuth2配置（CLIENT_ID/SECRET/REDIRECT_URI 均为代码常量，不从 .env/application.yml 读取）：
- **Node.js**：`server/config/index.js` 中的常量
- **Python**：`config.py` 或配置模块中的常量（不检查 .env 中这三项）
- **Java**：OAuthConfig 或常量类中的 `static final`（不检查 application.yml 中 client-id/secret/redirect-uri）
- **Go**：配置包中的 `const`（不检查 .env 中这三项）
- **PHP/Ruby/C# 等**：对应语言的配置/常量定义处

**检查的关键字段：**
- `CLIENT_ID` 或 `OAUTH2_CLIENT_ID` 或 `client_id` 或 `ClientId`
- `CLIENT_SECRET` 或 `OAUTH2_CLIENT_SECRET` 或 `client_secret` 或 `ClientSecret`
- `REDIRECT_URI` 或 `OAUTH2_REDIRECT_URI` 或 `redirect_uri` 或 `RedirectUri`
  - 检查 `REDIRECT_URI` 是否与后端实际路由路径匹配（如 `/callback` 对应 `http://xx.xx.xx.xx:PORT/callback`）
  - 授权URL中的 `redirect_uri` 必须与 `REDIRECT_URI` 完全一致

**2. 检查后端路由实现：**

检查以下路由是否已实现：
- `GET /oauth/login` - OAuth登录路由
  - **检查点：** 是否处理了`path`参数（不能为null），是否生成了state，是否构建了正确的授权URL
  - **检查点：** 授权URL中是否只包含必需的参数（client_id、redirect_uri、response_type、state、path），是否错误地添加了scope参数
  - 授权URL中不能包含scope参数（会导致invalid_scope错误）
- `GET /callback` 或 `GET /oauth/callback` - OAuth回调路由
  - **检查点：** 是否验证了state，是否处理了code，是否获取了token和用户信息，是否保存到session
  - **检查点：** 重定向URL是否使用配置的IP地址（不能使用localhost），如果path参数包含localhost是否已替换为配置的IP地址
- `GET /oauth/logout` - 登出路由
  - **检查点：** 是否清除了session/状态
- `GET /oauth/user` - 获取用户信息路由
  - **检查点：** 是否从session中读取用户信息，是否正确返回用户信息和accessToken

**3. 检查后端功能实现：**

检查以下功能是否已实现：
- State验证（CSRF防护）
  - **检查点：** `/oauth/login`是否生成state并保存到session，`/callback`是否验证state
- Session/状态管理
  - **检查点：** 是否正确配置了session，是否保存了用户信息、token、过期时间
- Token过期处理
  - **检查点：** 是否检查token过期时间，过期后是否清除session要求重新登录
- 错误处理
  - **检查点：** 是否处理了OAuth流程中的各种错误情况
- 授权URL构建
  - **检查点：** `redirect_uri`是否与`REDIRECT_URI`配置一致，`path`参数是否不为null

**4. 检查前端实现：**

检查以下前端功能是否已实现：
- 自动登录逻辑（Hook/Service/Composable）
  - **检查点：** 页面初次进入时是否自动检查登录状态，未登录时是否自动跳转到登录页面
- Token保存逻辑（localStorage的`oauth_token`）
  - **检查点：** 登录成功后是否从`/oauth/user`返回数据中提取`accessToken`并保存到localStorage
- 请求拦截器（自动添加Authorization header）
  - **检查点：** 是否排除了`/oauth/*`接口（不添加Authorization header），是否对业务API添加了Authorization header
- 响应拦截器（处理401错误）
  - **检查点：** 是否处理401错误，是否清除token并重新触发登录流程，是否传递了正确的path参数
- `/oauth/*`接口的credentials设置
  - **检查点：** 调用`/oauth/user`等接口时是否设置了`credentials: 'include'`（fetch）或`withCredentials: true`（axios/Angular）

### 第二步：生成检查报告

**如果发现已存在CLIENT_ID、CLIENT_SECRET、REDIRECT_URI配置：**

1. **提取现有配置值：**
   - 从代码中的常量提取 `CLIENT_ID`、`CLIENT_SECRET`、`REDIRECT_URI`（各语言均为常量存储，不从 .env/yml 读取）
   - 保存这些值，用于后续补全流程

2. **生成检查报告：**
   ```
   📋 代码检查报告
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   
   ✅ 已存在的配置：
   - CLIENT_ID: [已找到/未找到]
   - CLIENT_SECRET: [已找到/未找到]
   - REDIRECT_URI: [已找到/未找到] [如果已找到，检查是否与后端路由路径匹配]
   
   ✅ 已实现的后端功能：
   - [列出已实现的功能，如：/oauth/login路由、/callback路由、State验证、Session管理等]
   
   ❌ 缺失的后端功能：
   - [列出缺失的功能，如：Token过期处理、错误处理、path参数验证等]
   
   ✅ 已实现的前端功能：
   - [列出已实现的功能，如：自动登录逻辑、Token保存、请求拦截器等]
   
   ❌ 缺失的前端功能：
   - [列出缺失的功能，如：响应拦截器、credentials设置等]
   
   ⚠️ 需要修复的问题：
   - [列出发现的问题，如：redirect_uri不匹配、path参数为null、credentials未设置、/oauth/*接口添加了Authorization header等]
   
   📌 下一步操作：
   → 将执行补全流程，补全缺失的功能，修复发现的问题
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

3. **执行补全流程：**
   - **跳过 Step 1**（因为配置已存在）
   - **从 Step 2 开始**，但使用现有的配置值，而不是重新获取
   - 只补全缺失的功能，不覆盖已有代码
   - **⚠️ 重要：补全时，必须检查每个功能是否已存在，如果已存在但实现不完善，可以优化，但不能删除已有代码**
   - **⚠️ 重要：如果路由已存在但功能不完整，只补全缺失的部分，不要重写整个路由**

**如果未发现CLIENT_ID、CLIENT_SECRET、REDIRECT_URI配置：**

1. **生成检查报告：**
   ```
   📋 代码检查报告
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   
   ❌ 未找到OAuth2配置：
   - CLIENT_ID: 未找到
   - CLIENT_SECRET: 未找到
   - REDIRECT_URI: 未找到
   
   📌 下一步操作：
   → 将执行完整接入流程（从Step 1开始）
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

2. **执行完整接入流程：**
   - 从 Step 1 开始，执行完整流程

### 第三步：补全缺失功能

**如果已存在配置，执行补全流程：**

**补全后端功能（如果缺失）：**
- 补全缺失的路由（`/oauth/login`、`/callback`、`/oauth/logout`、`/oauth/user`）
- 补全缺失的功能（State验证、Session管理、Token过期处理）
- 确保所有路由和功能都正确实现
- **⚠️ 检查每个路由的实现：**
  - 如果路由已存在，检查功能是否完整（如`/oauth/login`是否处理了path参数，`/callback`是否验证了state等）
  - 如果功能不完整，只补全缺失的部分，不要重写整个路由
  - 如果路由不存在，创建新路由

**补全前端功能（如果缺失）：**
- 补全自动登录逻辑
- 补全Token保存逻辑（localStorage的`oauth_token`）
- 补全请求拦截器（确保`/oauth/*`接口不添加Authorization header，但设置credentials）
- 补全响应拦截器（处理401错误）
- **⚠️ 检查每个功能的实现：**
  - 如果功能已存在，检查实现是否正确（如请求拦截器是否正确排除了`/oauth/*`接口，是否正确设置了credentials）
  - 如果实现不正确，修复问题，但保留已有代码结构
  - 如果功能不存在，创建新功能

**⚠️ 重要原则：**
- 补全流程中，**绝对不能覆盖已有的代码**
- 只添加缺失的功能，或修复已有功能的问题
- 如果功能已存在但不完善，可以优化，但不能删除已有代码
- 如果代码结构已存在，在现有结构基础上补全，不要重写
- 补全完成后，必须验证所有功能是否正常工作

## Step 1: 获取OAuth2配置信息

**执行顺序：**

1. **提供参数模板**：向用户提供JSON参数模板，说明每个参数的含义
2. **等待用户回复**：等待用户填写并回复参数
3. **调用接口**：收到参数后，调用 `PUT https://loginpass-bff-qa.tap4fun.com/application/automation/add`（该接口仅用于申请 client_id/secret/redirect_uri，**不是** OAuth 授权地址）
4. **处理结果**：解析配置、格式化发送给用户、写入配置文件、验证配置

**OAuth 固定接口地址（必读，禁止修改，用错会 404）：**

| 用途 | 固定地址（必须原样使用） |
|------|--------------------------|
| OAuth 认证接口 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/authorize` |
| OAuth Token 接口 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/token` |
| OAuth 用户信息接口 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/user/info` |
| OAuth 登出 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/logout` |

- **申请应用**（仅 Step 1 获取 client_id/secret/redirect_uri）用：`PUT https://loginpass-bff-qa.tap4fun.com/application/automation/add`。该域名**不能**用于上述 OAuth 四个接口。
- **禁止**将 AUTHORIZATION_URI、TOKEN_URI、USER_INFO_URI 设为 `loginpass-bff-qa.tap4fun.com` 或路径 `/oauth/authorize`、`/oauth/token`（会 404），**必须**使用上表固定地址。
- 详细说明见 [oauth_fixed_urls.md](oauth_fixed_urls.md)。生成配置后必须校验：若发现上述 OAuth 地址含 `loginpass-bff` 或路径为 `/oauth/` 开头，必须立即替换为上表固定地址。

### 第一步：提供请求参数模板给用户

向用户展示以下请求参数模板（参考`references/oauth_server_template.md`第14-21行），并说明需要填写的内容：

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
- `url` 可以是IP地址（如 `http://192.168.1.100:3000`）或域名（如 `https://example.com`）
- `redirectUris` 格式为 `{url}/callback`（如 `http://192.168.1.100:3000/callback` 或 `https://example.com/callback`）
- 不要使用 `localhost`，必须使用IP地址或域名
- 前端端口号 = url 中的端口号；后端端口号 = 前端端口号 + 1

**参数说明：**
1. **systemName**：系统名称
2. **url**：前端项目的启动地址，可以是IP地址（如 `http://192.168.1.100:3000`）或域名（如 `https://example.com`），不要使用 `localhost`
3. **redirectUris**：重定向地址，格式为 `{url}/callback`（如 `http://192.168.1.100:3000/callback` 或 `https://example.com/callback`）
4. **employeeId**：员工ID
5. **thirdParty**：可选，未提供时默认 `true`
6. **accessCompanyIds**：可选，未提供时默认 `[1]`

**默认值补充：** 收到用户参数后，若用户未提供 `thirdParty`，则补充为 `true`；若未提供 `accessCompanyIds`，则补充为 `[1]`。再调用接口或脚本时使用补全后的参数。

**参数完整性检查（每次用户提供请求参数后必做两轮）：**

- **第一轮：收到用户参数后（调用接口前）**
  - 必填项：`systemName`、`url`、`redirectUris`、`employeeId` 必须存在且非空。
  - 可选项：缺 `thirdParty` 则补 `true`，缺 `accessCompanyIds` 则补 `[1]`。
  - 若任一项必填项缺失或为空，**不得调用接口**，需提示用户补全后重试。
  - 检查通过后再执行「参数补全」与「调用接口」。

- **第二轮：请求回填后（每次提供参数并调用接口后都要回填，再检查）**
  - 无论接口成功或失败，都要执行「回填数据」；然后做本轮检查。
  - 必须确认以下「请求回填」参数均已写入且非占位符、非空（接口失败时 CLIENT_ID/CLIENT_SECRET 可能缺失，需标注并提示用户重试或手动填写）：
    - `CLIENT_ID`（data.id）
    - `CLIENT_SECRET`（data.secret）
    - `REDIRECT_URI`（data.redirectUris）
    - `BASE_URL` 或用于前端的 url（data.url 或用户 url）
    - 从 url 解析的 host、前端端口、后端端口（用于写入前端/后端配置）
  - 必须确认 OAuth 固定三地址（AUTHORIZATION_URI、TOKEN_URI、USER_INFO_URI）已按 [oauth_fixed_urls.md](oauth_fixed_urls.md) 写入。
  - 若任一项未写入或仍为占位符（如 `[从Step 1获取的...]`），**必须补全或重新写入**，再次检查通过后**才能**进入生成后端/前端等后续步骤。

**前后端端口规则：** 前端项目的端口号 = url 中的端口号；后端端口号 = 前端端口号 + 1。生成时直接写入前端配置与后端 `.env`，不要用默认 3000。

### 第二步：执行接口调用（收到用户参数后自动执行）

**触发条件：** 当用户提供填写好的请求参数（JSON格式，至少包含 systemName、url、redirectUris、employeeId）后，**立即自动执行**接口调用，不需要等待用户说"继续"。若用户未提供 `thirdParty` 或 `accessCompanyIds`，则先默认补充为 `thirdParty: true`、`accessCompanyIds: [1]`，再调用接口。

**重要：用户每次提供参数都要回填数据。** 即：每次收到用户参数并完成（或尝试）接口调用后，**必须执行一次「回填数据」**——将用户提供的参数与接口返回的数据（若调用成功）写入到应写入的配置/文件中。若接口调用失败，也要用已有数据回填（如用用户提供的 url 写 BASE_URL、host、端口，用 redirectUris 写 REDIRECT_URI），并明确标注或提示哪些项因接口未返回而缺失（如 CLIENT_ID、CLIENT_SECRET），建议用户修正参数后重新提供或手动填写，避免只调接口不回填或失败后不写任何内容。

**重要：再次提供参数时，一律以本次为准，保证都是最新。** 若用户第一次提供 url 等信息后接口报错，当用户**再次**提供 url 等信息时，必须保证：① 本次调用接口使用的全是**本次**提供的参数（url、redirectUris、systemName、employeeId 等），不得沿用上次的参数；② 回填到配置文件的数据也全部来自**本次**——用户本次提供的参数 + 本次接口返回的结果（若成功）；不得写入或保留上一次的 url、redirectUris 或旧的接口回填数据。这样 url 等参数与回填数据始终是**最新一次**提交的。

**关键要求：收到用户参数后，按顺序执行以下操作：**
1. **先检查前后端项目**：若无前端则创建前端，若无后端则创建后端，按本 skill 补充完整后再继续
2. 参数补全 → 调用接口获取 OAuth2 配置
3. **回填数据**：每次提供参数后都要执行，成功时回填接口返回 + 用户参数；失败时回填用户参数并标注缺失项
4. 生成/补全后端代码
5. 实现前端自动登录
6. 检查并补全登录流程

**执行操作：**

1. **检查并补全前后端（必做，最先执行）：**
   - 检测项目是否已有前端（如存在前端目录、package.json 含 react/vue、或明显前端入口）。
   - 检测项目是否已有后端（如存在 server/、backend/、或后端语言特征文件）。
   - **若无前端**：在项目下创建前端（如 `frontend/` 或根目录简易前端），使用本 skill 规定的前端端口（url 中的端口）、后端地址（url 端口+1），并实现自动登录、拦截器、Token 存储等（见 frontend_implementation.md）。
   - **若无后端**：在项目下创建后端（如 `server/`），优先 Node（node_koa_template.md），配置端口为 url 端口+1，实现 OAuth 登录/回调/登出/用户信息等（见 backend_implementation.md）。
   - 补全前后端后，再执行下面的参数补全与接口调用。

2. **参数完整性检查（一）：收到用户参数后** 检查必填项 systemName、url、redirectUris、employeeId 是否均有值；缺则提示用户补全，不调用接口。缺 thirdParty/accessCompanyIds 则按默认补全。**用户再次提供参数时，只认本次提交**：不沿用历史参数，本次即最新。
3. **参数补全（调用接口前必做）：** 若用户提供的参数中缺少 `thirdParty`，则补充为 `true`；缺少 `accessCompanyIds`，则补充为 `[1]`。**调用接口时只使用本次补全后的参数**，回填时只使用本次参数与本次接口返回，保证 url 等与回填数据均为最新。
4. **方式一：使用脚本调用接口（推荐）**

使用脚本调用接口获取OAuth2配置：

```bash
python ~/.cursor/skills/login-oauth2/scripts/get_oauth_config.py \
    --system-name "用户提供的systemName" \
    --url "用户提供的url" \
    --redirect-uris "用户提供的redirectUris" \
    --employee-id 用户提供的employeeId \
    --json
```

**脚本返回的JSON格式：**
```json
{
  "success": true,
  "client_id": 210,
  "client_secret": "4ca2022e537c44448666fffe62379e2c",
  "redirect_uri": "http://xx.xx.xx.xx:YOUR_PORT/callback",
  "url": "http://xx.xx.xx.xx:YOUR_PORT",
  "system_name": "系统名称",
  "parsed_url": {
    "host": "xx.xx.xx.xx",
    "port": "YOUR_PORT",
    "scheme": "http",
    "path": "/"
  },
  "parsed_redirect": {
    "host": "xx.xx.xx.xx",
    "port": "YOUR_PORT",
    "scheme": "http",
    "path": "/callback"
  }
}
```

**如果脚本执行失败，返回格式：**
```json
{
  "success": false,
  "error": "错误信息"
}
```

**注册接口若出现 HTTP 404（助手误调或路径/方法错误）：**

- **不要**把 OAuth 授权/Token 用的网关地址（`ms-open-gateway-qa.tap4fun.com/loginpass/oauth/...`）当作「注册登录系统」的接口；那是登录流程用的，不是登记应用。
- **正确登记应用**与本仓库 **`scripts/get_oauth_config.py`** 一致：`PUT` + `https://loginpass-bff-qa.tap4fun.com/application/automation/add` + JSON 体（systemName、url、redirectUris、employeeId、thirdParty、accessCompanyIds）。
- **对用户说明：** 若遇 404，请在本技能仓库或安装目录下查找 **`get_oauth_config.py`**（路径示例：`login-oauth2/scripts/` 或 `~/.cursor/skills/login-oauth2/scripts/`），本地用与用户参数一致的命令行执行；或由助手在 workspace 与 skill 目录中 **glob/搜索 `get_oauth_config.py`** 并代为执行，**禁止**在未核对脚本的情况下臆造其它注册 URL。

**方式二：使用curl（备用方式）**

如果脚本执行失败，可以使用curl作为备用方式：

```bash
curl --location --request PUT 'https://loginpass-bff-qa.tap4fun.com/application/automation/add' \
--header 'Content-Type: application/json' \
--data '{
    ... 用户提供的请求参数
}'
```

**curl返回的原始数据结构：**
```json
{
    "success": true,
    "code": null,
    "message": null,
    "data": {
        "id": 210,
        "doSystemId": 210,
        "systemName": "系统名称",
        "url": "http://xx.xx.xx.xx:YOUR_PORT",
        "status": 1,
        "canRemove": true,
        "thirdParty": true,
        "secret": "4ca2022e537c44448666fffe62379e2c",
        "redirectUris": "http://xx.xx.xx.xx:YOUR_PORT/callback"
    }
}
```

**注意：** 
- 优先使用脚本方式，脚本会自动解析和格式化返回结果，并解析URL信息
- 必须等待接口调用完成并获取返回结果后，才能继续执行第三步
- 如果脚本执行失败，可以使用curl作为备用方式，但需要手动解析返回结果
- **用户每次提供参数都要回填数据**：无论接口成功还是失败，都要执行「回填」——成功时把接口返回 + 用户参数写入配置；失败时用用户参数回填能写的项（url→BASE_URL、host/端口、redirectUris→REDIRECT_URI 等），并明确提示 CLIENT_ID/CLIENT_SECRET 等因接口未返回而缺失，建议用户修正参数后重新提供或手动填写。

### 第三步：处理接口返回结果并回填数据

**回填原则：用户每次提供参数后都要回填，且一律使用本次数据。** 接口成功时，用**本次**接口返回的数据 + **本次**用户参数写入配置；接口失败时，用**本次**用户提供的参数回填能确定的项（见下方「接口失败时的回填」），并提示缺失项。**用户再次提供参数时，必须用本次的请求与本次的返回做回填，不得沿用或混入上次的 url、redirectUris 或旧接口结果，保证配置里是最新一次提交的数据。**

**如果使用脚本方式（推荐）且接口成功：**

脚本已经处理了返回结果，直接使用脚本返回的JSON数据：

1. **提取OAuth2配置值并写入（回填）：**
   - 从 `response.client_id` 提取 → `CLIENT_ID`
   - 从 `response.client_secret` 提取 → `CLIENT_SECRET`
   - 从 `response.redirect_uri` 提取 → `REDIRECT_URI`

2. **解析系统URL信息：**
   - 从 `response.parsed_url.host` 提取 → IP地址/域名
   - 从 `response.parsed_url.port` 提取 → 端口号
   - 从 `response.parsed_redirect.path` 提取 → 重定向路径

**如果使用curl方式（备用）：**

需要手动解析返回结果：

1. **提取OAuth2配置值：**
   - 从 `response.data.data.id` 提取 → `CLIENT_ID`
   - 从 `response.data.data.secret` 提取 → `CLIENT_SECRET`
   - 从 `response.data.data.redirectUris` 提取 → `REDIRECT_URI`

2. **解析系统URL信息（如果包含IP地址）：**
   - 从 `response.data.data.url` 解析URL
   - 使用URL解析工具（如JavaScript的`new URL()`或正则表达式）解析：
     - 如果URL是IP地址格式（如 `http://192.168.1.100:3000`），提取IP地址和端口号
     - 如果URL是域名格式（如 `https://example.com` 或 `https://example.com:8080`），提取域名和端口号（默认端口：http: 80, https: 443）
     - 代码会自动识别URL格式，支持IP地址和域名两种格式

3. **解析重定向地址路径：**
   - 从 `response.data.data.redirectUris` 解析完整URL
   - 使用URL解析工具提取路径部分（如 `/callback`）
   - 例如：`http://xx.xx.xx.xx:YOUR_PORT/callback` → 路径为 `/callback`
   - 例如：`http://xx.xx.xx.xx:YOUR_PORT/oauth/callback` → 路径为 `/oauth/callback`

**接口失败时的回填（用户每次提供参数都要回填，失败时也要执行；再次提供时只用本次数据）：**
- 仍用**用户本次提供的参数**回填能确定的项并写入配置（不得使用上次提交的 url、redirectUris 等）：
  - 用用户提供的 `url` 解析并写入：BASE_URL、host、前端端口、后端端口（前端/后端配置文件）。
  - 用用户提供的 `redirectUris` 写入 REDIRECT_URI（后端配置）。
  - OAuth 固定三地址（AUTHORIZATION_URI、TOKEN_URI、USER_INFO_URI）按 [oauth_fixed_urls.md](oauth_fixed_urls.md) 写入。
- CLIENT_ID、CLIENT_SECRET 因接口未返回，写入占位或留空，并在配置旁或向用户明确说明：「接口调用未成功，CLIENT_ID/CLIENT_SECRET 未获取，请修正参数后重新提供或手动填写」。
- 将请求的报错信息返回给用户，提示检查参数、网络，或尝试 curl 备用方式。
- 执行「参数完整性检查（二）」时，会因 CLIENT_ID/CLIENT_SECRET 缺失而不通过，不得进入生成后端/前端步骤，直到用户重新提供参数并接口成功或用户手动补全后再继续。

### 第四步：格式化并发送给用户保存

**必须向用户发送以下格式化的信息，提醒用户保存：**

```
✅ OAuth2配置获取成功！

请保存以下配置信息，后续配置需要使用：

📋 OAuth2配置信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLIENT_ID: [从接口返回的data.id获取]
CLIENT_SECRET: [从接口返回的data.secret获取]
REDIRECT_URI: [从接口返回的data.redirectUris获取]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 系统信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
系统URL: [从接口返回的data.url获取]
IP地址: [从系统URL中解析]
端口号: [从系统URL中解析]
重定向路径: [从redirectUris中解析]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 重要提示：
1. 请妥善保存上述配置信息，后续配置Node服务时需要用到
2. 如果丢失，需要重新调用接口获取
3. CLIENT_ID 对应配置中的 CLIENT_ID
4. CLIENT_SECRET 对应配置中的 CLIENT_SECRET
5. REDIRECT_URI 对应配置中的 REDIRECT_URI
```

### 第五步：立即写入前端和后端配置文件（回填数据）

**关键要求：用户每次提供参数后都要回填，且全部使用本次数据。** 接口成功时，用**本次**接口返回 + **本次**用户参数写入；接口失败时，用**本次**用户参数写入能写的项（url→host/端口/BASE_URL、redirectUris→REDIRECT_URI、OAuth 固定三地址等），CLIENT_ID/CLIENT_SECRET 标注缺失并提示用户重试或手动填写。**用户再次提供参数时，接口请求与回填都必须基于本次提交，保证 url 等参数与回填数据都是最新的。**

**端口分配规则：前端项目的端口号 = url 中的端口号；后端端口号 = 前端端口号 + 1。**

```
用户url = "http://172.20.62.21:3003" 时：
  ┌─────────┬─────────────────────────────────────┐
  │  前端   │ PORT = 3003  （= url中的端口号）    │ ← 修改前端配置文件
  │  后端   │ PORT = 3004  （= 前端端口号 + 1）   │ ← 写入后端 .env
  └─────────┴─────────────────────────────────────┘
```

**执行步骤：**

1. **解析url参数中的端口号：**
   ```javascript
   const urlObj = new URL(userUrl); // 如 "http://172.20.62.21:3003"
   const FRONTEND_HOST = urlObj.hostname; // "172.20.62.21"
   const FRONTEND_PORT = urlObj.port;     // "3003" ← 这是前端端口！
   const BACKEND_PORT = Number(FRONTEND_PORT) + 1; // 3004 ← 后端端口
   ```

2. **立即修改前端项目的启动端口（url中的端口是前端的！）：**
   
   根据前端框架找到对应配置文件，写入从url解析出的端口号：
   - **React (CRA)**: 创建或更新项目根目录 `.env` → `HOST=172.20.62.21` 和 `PORT=3003`
   - **Vite**: 更新 `vite.config.js` → `server: { host: '172.20.62.21', port: 3003 }`
   - **Angular**: 更新 `angular.json` → `serve.options: { host: '172.20.62.21', port: 3003 }`
   - **Webpack**: 更新 `webpack.config.js` → `devServer: { host: '172.20.62.21', port: 3003 }`
   - **package.json scripts**: 如有 `--port` 参数，改为 `--port 3003`
   
   **⚠️ 以上 3003 是示例，实际值从url参数解析。前端端口 = url中的端口！**

3. **写入后端配置文件（后端端口 = 前端端口 + 1）：**
   
   **OAuth 固定接口（必须使用 [oauth_fixed_urls.md](oauth_fixed_urls.md)，不可用接口返回或其它域名替换）：**
   - 认证: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/authorize`
   - Token: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/token`
   - 用户信息: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/user/info`
   - 登出: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/logout`
   - 使用 `loginpass-bff-qa.tap4fun.com` 或路径 `/oauth/authorize`、`/oauth/token` 会 **404**，禁止使用。
   
   **Node.js示例 — 回填到常量与 .env：**
   - **OAUTH2_CLIENT_ID、OAUTH2_CLIENT_SECRET、OAUTH2_REDIRECT_URI** 存成常量，写入 `server/config/index.js`（不从 .env 读取）：
     ```javascript
     const OAUTH2_CLIENT_ID = '[接口返回的data.id的实际值]';
     const OAUTH2_CLIENT_SECRET = '[接口返回的data.secret的实际值]';
     const OAUTH2_REDIRECT_URI = '[接口返回的data.redirectUris的实际值]';
     exports.OAUTH2_CONFIG = {
       CLIENT_ID: OAUTH2_CLIENT_ID,
       CLIENT_SECRET: OAUTH2_CLIENT_SECRET,
       REDIRECT_URI: OAUTH2_REDIRECT_URI,
       // AUTHORIZATION_URI、TOKEN_URI、USER_INFO_URI 固定地址；BASE_URL 等可从 .env
       ...
     };
     ```
   - 创建或更新 `server/.env`（仅 PORT、BASE_URL、APP_KEYS 等，不含上述三个）：
     ```
     PORT=3004
     BASE_URL=[接口返回的url或用户url]
     OAUTH2_AUTHORIZATION_URI=https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/authorize
     OAUTH2_TOKEN_URI=https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/token
     OAUTH2_USER_INFO_URI=https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/user/info
     ```
   **⚠️ PORT=3004 为 url 端口+1。CLIENT_ID/SECRET/REDIRECT_URI 只写在 config 常量中，不从 .env 读取。** 若已有 `server/config/index.js`，回填时只更新上述三处常量的值即可。
   
   **Python示例（常量存储，不从 .env 读取）：**
   - 在 `config.py` 或 OAuth 配置模块中**以常量定义**，回填时直接写入实际值：
     ```python
     OAUTH2_CLIENT_ID = '[接口返回的data.id的实际值]'
     OAUTH2_CLIENT_SECRET = '[接口返回的data.secret的实际值]'
     OAUTH2_REDIRECT_URI = '[接口返回的data.redirectUris的实际值]'
     ```
   - `.env` 中不配置上述三项。
   
   **Java示例（常量存储，不从 application.yml 读取）：**
   - 在配置类或常量类中**以常量定义**；`application.yml` 中不写 client-id、client-secret、redirect-uri：
     ```java
     public static final String CLIENT_ID = "[接口返回的data.id的实际值]";
     public static final String CLIENT_SECRET = "[接口返回的data.secret的实际值]";
     public static final String REDIRECT_URI = "[接口返回的data.redirectUris的实际值]";
     ```
   
   **Go示例（常量存储，不从 .env 读取）：**
   - 在配置包中**以常量定义**：
     ```go
     const (
         OAuth2ClientID     = "[接口返回的data.id的实际值]"
         OAuth2ClientSecret = "[接口返回的data.secret的实际值]"
         OAuth2RedirectURI  = "[接口返回的data.redirectUris的实际值]"
     )
     ```
   - `.env` 中不配置上述三项。
   
   **所有语言统一规则：** CLIENT_ID、CLIENT_SECRET、REDIRECT_URI 均存成常量并直接从常量读取，不从 .env / application.yml / 环境变量读取。

4. **参数完整性检查（二）：请求回填后** 在写入配置后必须做一次完整检查，确认以下均已完成且无占位符、无空值：
   - **用户参数与默认补全**：systemName、url、redirectUris、employeeId、thirdParty、accessCompanyIds 已齐备（缺的已按默认补全）。
   - **请求回填参数**：CLIENT_ID、CLIENT_SECRET、REDIRECT_URI、BASE_URL（或等价 url）已从接口结果写入后端/前端所用配置（**所有语言**均将 CLIENT_ID/SECRET/REDIRECT_URI 存成常量并从常量读取，不从 .env / application.yml / 环境变量读取）；从 url 解析的 host、前端端口、后端端口已写入对应配置文件。
   - **OAuth 固定地址**：AUTHORIZATION_URI、TOKEN_URI、USER_INFO_URI 已按 [oauth_fixed_urls.md](oauth_fixed_urls.md) 写入；若发现含 `loginpass-bff` 或路径 `/oauth/authorize`、`/oauth/token`，必须替换为固定地址。
   - 任一项未通过则**不得进入下一步**：立即补全或重新写入，再次检查通过后再继续生成后端/前端等。
5. **验证配置已正确写入（与上一步合并执行）：**
   - 验证 CLIENT_ID、CLIENT_SECRET、REDIRECT_URI 已正确写入且非占位符（各语言均为代码中的常量，不从 .env/yml 读取）。
   - 校验 CLIENT_ID、REDIRECT_URI 缺失会导致 `client_id=undefined`、500；缺失时返回 500 并提示「OAuth2 配置缺失」。
   - 配置为空或未写入时立即重新写入；验证失败时向用户报告错误，不继续后续步骤。

**字段映射关系：**

**如果使用脚本方式：**
- `response.client_id` → `CLIENT_ID`
- `response.client_secret` → `CLIENT_SECRET`
- `response.redirect_uri` → `REDIRECT_URI`
- `response.system_name` → `SYSTEM_NAME`（可选保存，token key固定为 `oauth_token`，不再需要systemName）
- `response.parsed_url.host` → IP地址/域名
- `response.parsed_url.port` → 端口号
- `response.parsed_redirect.path` → 重定向路径

**如果使用curl方式：**
- `response.data.data.id` → `CLIENT_ID`
- `response.data.data.secret` → `CLIENT_SECRET`
- `response.data.data.redirectUris` → `REDIRECT_URI`
- `response.data.data.systemName` → `SYSTEM_NAME`（可选保存，token key固定为 `oauth_token`，不再需要systemName）
- 需要手动解析URL获取IP地址、端口号和重定向路径

**重要说明：**
- **优先使用脚本方式**，脚本已经处理了数据解析和格式化
- 如果使用curl方式，返回的数据在 `data` 对象中，需要从 `response.data.data` 中提取
- **必须先向用户发送格式化的配置信息，提醒用户保存**
- 然后才继续后续的配置文件创建步骤

### 第六步：验证配置已正确写入

**验证步骤：**
1. 验证代码中常量 CLIENT_ID、CLIENT_SECRET、REDIRECT_URI 是否已回填且非空（各语言均为常量，不从 .env/yml 读取）
2. 如果验证失败，重新写入或向用户报告错误，不能继续执行后续步骤
3. 验证成功后，继续执行Step 1完成提示

**✅ 收到用户参数后的处理：**

**关键要求：收到用户参数后，立即自动执行第二步，不需要等待用户说"继续"**

在用户填写并回复参数后，立即开始执行第二步，并向用户发送提示：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 第一步：参数已收到

📋 已收到您的参数，现在自动开始完成所有功能：
→ 获取OAuth2配置
→ 生成后端代码
→ 实现前端自动登录
→ 检查并补全登录流程

⏳ 正在自动完成，请稍候...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**执行顺序：**
1. 收到用户参数后，立即调用接口获取OAuth2配置
2. 配置获取成功后，立即开始生成后端代码
3. 后端代码生成完成后，立即开始实现前端自动登录
4. 前端实现完成后，立即开始检查并补全登录流程
5. 所有步骤完成后，发送最终完成提示

**环境要求：**
- 本地项目启动后，必须使用配置的系统地址访问（如 `http://xx.xx.xx.xx:YOUR_PORT`），不要使用 `localhost`
- OAuth2登录回调需要匹配配置的 `redirectUris`，因此必须使用IP地址

## Step 2: 检测后端语言并生成对应代码

**前置条件：** Step 1 必须完全完成

**后端语言选择：** 若用户写了后端或项目已有后端，则按该语言生成（匹配对应模板）；若用户未写后端或未检测到后端，则**优先使用 Node** 写后端（使用 node_koa_template.md）。Node 模板单独维护，保证登录流程稳定。

详细说明请参考 [后端实现文档](backend_implementation.md)。

## Step 3: 前端自动登录实现

**前置条件：** Step 2 必须完全完成

**关键步骤：把url参数中的端口号写入前后端配置文件**

```
例：用户给的 url = "http://172.20.62.21:3003"

必须写入的配置：
  前端 .env (或vite.config.js等) → HOST=172.20.62.21  PORT=3003  ← 前端端口=url中的端口号
  后端 .env                      → PORT=3004                      ← 后端端口=前端端口+1
```

**生成代码时必须做到：**
1. 从url参数解析出 host 和 port（如 `172.20.62.21` 和 `3003`）
2. 把 host 和 port **直接写入**前端配置文件（写实际数字，不写变量）
3. 把 port+1 **直接写入**后端 `.env` 的 PORT 字段（写实际数字，不写变量）
4. 检查：前端端口号=url中的端口号 ✅，后端端口号=前端端口号+1 ✅，前后端不同 ✅

详细说明请参考 [前端实现文档](frontend_implementation.md)。

## Step 4: 检查并补全登录流程

**前置条件：** Step 3 必须完全完成

**执行步骤：**

### 第一步：全面检查登录流程

**1. 检查后端配置：**
- 检查 `CLIENT_ID`、`CLIENT_SECRET`、`REDIRECT_URI` 是否正确配置
- 检查 `REDIRECT_URI` 是否与后端实际路由路径匹配
- 检查环境变量配置文件是否正确创建

**2. 检查后端路由实现：**
- `GET /oauth/login` - 检查是否处理了`path`参数（不能为null），是否生成了state，是否构建了正确的授权URL
- `GET /callback` 或 `GET /oauth/callback` - 检查是否验证了state，是否处理了code，是否获取了token和用户信息，是否保存到session
- `GET /oauth/logout` - 检查是否清除了session/状态
- `GET /oauth/user` - 检查是否从session中读取用户信息，是否正确返回用户信息和accessToken

**3. 检查后端功能实现：**
- State验证（CSRF防护）：检查是否生成state并保存到session，是否验证state
- Session/状态管理：检查是否正确配置了session，是否保存了用户信息、token、过期时间
- Token过期处理：检查是否检查token过期时间，过期后是否清除session
- 授权URL构建：检查`redirect_uri`是否与`REDIRECT_URI`配置一致，`path`参数是否不为null
- 错误处理：检查是否处理了OAuth流程中的各种错误情况

**4. 检查前端实现：**
- 前端项目启动配置：检查前端端口是否等于url参数中的端口号（如url是3002则前端必须是3002），后端端口是否和前端不同
- 自动登录逻辑：检查页面初次进入时是否自动检查登录状态，未登录时是否自动跳转到登录页面
- Token保存逻辑：检查登录成功后是否从`/oauth/user`返回数据中提取`accessToken`并保存到localStorage（key为`oauth_token`）
- 请求拦截器：检查是否排除了`/oauth/*`接口（不添加Authorization header），是否对业务API添加了Authorization header
- 响应拦截器：检查是否处理401错误，是否清除token并重新触发登录流程，是否传递了正确的path参数
- credentials设置：检查调用`/oauth/user`等接口时是否设置了`credentials: 'include'`（fetch）或`withCredentials: true`（axios/Angular）

### 第二步：生成检查报告

生成详细的检查报告，列出：
- ✅ 已实现的功能
- ❌ 缺失的功能
- ⚠️ 需要修复的问题

**检查报告格式：**
```
📋 登录流程检查报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 已实现的后端功能：
- [列出已实现的功能，如：/oauth/login路由、/callback路由、State验证、Session管理等]

❌ 缺失的后端功能：
- [列出缺失的功能，如：Token过期处理、错误处理、path参数验证等]

✅ 已实现的前端功能：
- [列出已实现的功能，如：自动登录逻辑、Token保存、请求拦截器等]

❌ 缺失的前端功能：
- [列出缺失的功能，如：响应拦截器、credentials设置等]

⚠️ 需要修复的问题：
- [列出发现的问题，如：redirect_uri不匹配、path参数为null、credentials未设置、/oauth/*接口添加了Authorization header等]

📌 下一步操作：
→ 将自动补全缺失的功能，修复发现的问题
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 第三步：自动补全缺失功能

**如果发现缺失的后端功能：**
- 补全缺失的路由（`/oauth/login`、`/callback`、`/oauth/logout`、`/oauth/user`）
- 补全缺失的功能（State验证、Session管理、Token过期处理、错误处理）
- 修复发现的问题（如`path`参数为null、`redirect_uri`不匹配等）
- **⚠️ 检查每个路由的实现：**
  - 如果路由已存在，检查功能是否完整（如`/oauth/login`是否处理了path参数，`/callback`是否验证了state等）
  - 如果功能不完整，只补全缺失的部分，不要重写整个路由
  - 如果路由不存在，创建新路由

**如果发现缺失的前端功能：**
- 补全自动登录逻辑
- 补全Token保存逻辑（localStorage的`oauth_token`）
- 补全请求拦截器（确保`/oauth/*`接口不添加Authorization header，但设置credentials）
- 补全响应拦截器（处理401错误）
- 修复发现的问题（如credentials未设置、`/oauth/*`接口添加了Authorization header等）
- **⚠️ 检查每个功能的实现：**
  - 如果功能已存在，检查实现是否正确（如请求拦截器是否正确排除了`/oauth/*`接口，是否正确设置了credentials）
  - 如果实现不正确，修复问题，但保留已有代码结构
  - 如果功能不存在，创建新功能

**⚠️ 重要原则：**
- 补全流程中，**绝对不能覆盖已有的代码**
- 只添加缺失的功能，或修复已有功能的问题
- 如果功能已存在但不完善，可以优化，但不能删除已有代码
- 如果代码结构已存在，在现有结构基础上补全，不要重写
- 补全完成后，必须验证所有功能是否正常工作

### 第四步：发送完成提示

**第二步完成后，发送最终完成提示：**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 第二步：所有功能已完成

🎉 OAuth2登录系统已成功接入并完善！

📋 已完成的工作：
✓ 获取OAuth2配置（CLIENT_ID、CLIENT_SECRET、REDIRECT_URI）
✓ 生成后端代码（检测语言并生成对应实现）
✓ 实现前端自动登录（检测框架并实现自动登录逻辑）
✓ 检查并补全登录流程（全面检查并补全缺失功能）

📊 检查结果：
[显示检查报告内容]

✅ 已补全的功能：
[列出已补全的功能]

⚠️ 测试步骤：
1. 启动后端服务（确保环境变量已配置）
2. 启动前端应用
3. 访问前端应用，应该自动跳转到登录页面
4. 登录成功后，应该自动返回原页面
5. 测试登出功能（如果已实现）
6. 测试Token过期处理（等待token过期或手动清除token）
7. 测试401错误处理（模拟401错误，应该自动重新登录）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**关键要求：**
- 第二步完成后，整个流程结束
- 必须明确说明所有功能都已完成
- 必须提供详细的检查报告和补全结果
- 必须提供测试步骤和使用说明

## 流程中断提示

如果在执行过程中，用户中断了流程或去做其他操作，需要提示用户：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 登录系统接入流程未完成

📊 当前进度：
- 第一步：填写请求参数 - [状态：已完成/未完成]
- 第二步：自动完成所有功能 - [状态：进行中/未开始]

⚠️ 重要提醒：
- 登录系统接入流程尚未完成，部分功能可能无法正常使用
- 建议完成所有步骤后再进行其他操作
- 如果中断流程，可能需要重新获取配置或重新生成代码

📌 继续操作：
- 如果第一步未完成，请填写并回复参数（回复参数后会自动执行第二步）
- 如果第一步已完成但第二步被中断，回复"继续"可以继续完成剩余步骤

💡 提示：
- 正常情况下，填写参数后会自动执行第二步，无需说"继续"
- 只有在流程被中断的情况下，才需要回复"继续"来继续完成剩余步骤
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
