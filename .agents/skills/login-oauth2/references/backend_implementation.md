# 后端实现详细说明

本文档包含后端 OAuth2 实现的详细说明，包括多语言支持。

## OAuth 固定接口地址（禁止修改，用错会 404）

生成或写入配置时**必须**使用以下固定地址，不得使用 `loginpass-bff-qa.tap4fun.com` 或路径 `/oauth/authorize`、`/oauth/token` 等。

| 用途 | 固定地址 |
|------|----------|
| OAuth 认证接口 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/authorize` |
| OAuth Token 接口 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/token` |
| OAuth 用户信息接口 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/user/info` |
| OAuth 登出 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/logout` |

详见 [oauth_fixed_urls.md](oauth_fixed_urls.md)。

## 关键说明：前后端端口配置

**端口规则：前端项目的端口号 = url 中的端口号；后端端口号 = 前端端口号 + 1。**

```
用户url = "http://172.20.62.21:3003" 时：
  ┌─────────┬─────────────────────────────────────┐
  │  前端   │ PORT = 3003  （= url中的端口号）    │ ← 写入前端配置文件
  │  后端   │ PORT = 3004  （= 前端端口号 + 1）   │ ← 写入后端 .env
  └─────────┴─────────────────────────────────────┘
```

**后端 app.js 只需读 .env（端口已写好，不要运行时计算）：**
```javascript
const port = process.env.PORT || 8099;
```

## Step 2: 检测后端语言并生成对应代码

### 后端语言选择规则

- **若用户写了后端或项目已有后端：** 匹配对应语言生成代码（如 Java → 使用 [Java Spring Boot 模板](java_spring_boot_template.md)，Node → 使用 [Node Koa 模板](node_koa_template.md)）。
- **若用户未写后端或未检测到后端语言：** 优先使用 Node 写后端，使用 [Node Koa 模板](node_koa_template.md)。

生成代码时以各语言独立模板文件为准，保证登录流程稳定、功能完整。

### 执行步骤

1. **检测项目后端语言：**

   使用脚本自动检测后端语言：

   ```bash
   python ~/.cursor/skills/login-oauth2/scripts/detect_backend.py --path <项目路径> --json
   ```

   **注意：**
   - 将 `<项目路径>` 替换为实际的项目根目录路径（如 `.` 表示当前目录）
   - 脚本返回JSON格式，需要解析JSON输出
   - 如果脚本执行失败或未检测到后端语言，默认使用Node.js

   **脚本会自动检测以下后端语言：**
   - **Node.js**: 检测 `package.json`、`server.js`、`app.js`、`index.js` 等文件，以及 `server/`、`backend/`、`api/` 目录
   - **Python**: 检测 `requirements.txt`、`setup.py`、`pyproject.toml`、`*.py` 文件（Flask/Django/FastAPI）
   - **Java**: 检测 `pom.xml`、`build.gradle`、`*.java` 文件
   - **Go**: 检测 `go.mod`、`go.sum`、`*.go` 文件
   - **PHP**: 检测 `composer.json`、`*.php` 文件
   - **Ruby**: 检测 `Gemfile`、`*.rb` 文件
   - **C#/.NET**: 检测 `*.csproj`、`*.sln`、`*.cs` 文件

   **脚本返回格式（成功时）：**
   ```json
   {
     "language": "nodejs",
     "framework": "koa",
     "confidence": 85,
     "evidence": ["Found file: package.json", "Found directory: server"]
   }
   ```

   **脚本返回格式（未检测到时）：**
   ```json
   {
     "language": null,
     "message": "No backend language detected"
   }
   ```

   **处理脚本输出：**
   - 如果 `language` 不为 `null`，使用检测到的语言生成代码（匹配对应模板文件）
   - 如果 `language` 为 `null`，优先使用 Node.js 生成代码（使用 node_koa_template.md）
   - 根据 `framework` 字段选择合适的框架实现方式
   
2. **根据检测结果生成代码：**
   - **若用户写了后端或检测到已有后端语言：** 按该语言生成，使用对应模板（Java → java_spring_boot_template.md，Node → node_koa_template.md 等）
   - **若用户未写后端或未检测到后端：** 优先使用 Node 写后端，使用 [Node Koa 模板](node_koa_template.md)
   - **如果检测到多种语言：** 询问用户选择使用哪种语言，或使用项目主要使用的语言

3. **生成代码要求：**
   - 所有语言版本必须实现相同的OAuth2功能：
     - 登录路由（重定向到OAuth授权页面）
     - 回调处理（接收code/token，换取access_token，获取用户信息）
     - 登出路由
     - 获取用户信息路由
     - Token过期处理
     - Session管理（或对应的状态管理方式）
     - CSRF防护（State验证）
   - 使用Step 1中获取的配置值（CLIENT_ID、CLIENT_SECRET、REDIRECT_URI）
   - 代码必须可以直接部署使用，包含必要的依赖配置

## Node.js 实现（默认 / 优先）

若用户未写后端或未检测到后端语言，优先使用 Node 写后端；若项目已是 Node 后端，则按 Node 生成。**完整代码以 [Node Koa 模板](node_koa_template.md) 为准，保证登录流程稳定。**

### 关键文件

1. **创建server目录：** 在项目根目录创建`server`目录（注意：正式项目中使用`/server`，不是`/server-test`）
2. **参考模板：** 使用 [references/node_koa_template.md](node_koa_template.md) 中的模板代码（基于 tokenrank-fe，功能完整、流程稳定）
3. **关键文件：**
   - `server/app.js` - 应用入口
   - `server/config/index.js` - OAuth配置
   - `server/routes/oauth/index.js` - OAuth路由（核心代码，基于tokenrank-fe项目）
   - `server/middleware/oauth2Auth.js` - 认证中间件
   - `server/package.json` - 依赖配置

### OAuth2 接口地址（必须使用固定地址，见 [oauth_fixed_urls.md](oauth_fixed_urls.md)）

- `AUTHORIZATION_URI`: **必须** `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/authorize`
- `TOKEN_URI`: **必须** `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/token`
- `USER_INFO_URI`: **必须** `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/user/info`
- OAuth 登出（如需跳转至 OAuth 登出页）: **必须** `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/logout`

**禁止**使用 `loginpass-bff-qa.tap4fun.com` 或路径 `/oauth/authorize`、`/oauth/token`（会 404）。

**CLIENT_ID、CLIENT_SECRET、REDIRECT_URI 统一存成常量：** 所有语言（Node、Python、Java、Go 等）均将这三项在代码中定义为常量，回填时直接写入常量值，**不从 .env / application.yml / 环境变量读取**。防止 client_id=undefined 等导致 500；/oauth/login 重定向前必须校验常量已回填且非占位符。

### 操作步骤

1. **创建目录结构：**
```bash
mkdir -p server/config server/routes/oauth server/middleware
```

2. **创建package.json：**
```bash
cd server
npm init -y
npm install koa koa-router koa-session koa-body koa-static koa-views axios dotenv cross-env
```

3. **创建配置文件：**
   - 复制 [node_koa_template.md](node_koa_template.md) 中的`config/index.js`代码
   - **OAUTH2_CLIENT_ID、OAUTH2_CLIENT_SECRET、OAUTH2_REDIRECT_URI 存成常量**，在 `config/index.js` 顶部定义，从 Step 1 回填时直接写入常量值，**不从 .env 读取**。
   - 其他配置：`BASE_URL` 可从 .env；`AUTHORIZATION_URI`、`TOKEN_URI`、`USER_INFO_URI` 为固定地址（见 oauth_fixed_urls.md）。
   **重要：** 在创建/更新 `server/config/index.js` 时，**将 Step 1 接口返回的 data.id、data.secret、data.redirectUris 直接写入上述三个常量**，不要使用占位符。

4. **创建OAuth路由：**
   - **核心代码参考：** tokenrank-fe 项目的 `server/routes/oauth/index.js`
   - 复制 [node_koa_template.md](node_koa_template.md) 中的 `routes/oauth/index.js` 代码
   - 包含登录、回调、登出、获取用户信息等路由
   - 代码中会调用`AUTHORIZATION_URI`、`TOKEN_URI`、`USER_INFO_URI`三个接口
   - **⚠️ 关键：** 代码已实现path参数处理和localhost替换逻辑

5. **创建认证中间件：**
   - 复制 [node_koa_template.md](node_koa_template.md) 中的 `middleware/oauth2Auth.js` 代码
   - **⚠️ 关键：** 代码已实现token过期检查

6. **创建应用入口：**
   - 复制 [node_koa_template.md](node_koa_template.md) 中的 `app.js` 代码
   - 配置session、中间件、路由等
   - 后端端口必须和前端不同，生成代码时在后端 `.env` 中设置 `PORT=前端端口+1`
   - **✅ 正确示例：**
     ```javascript
     // ✅ 正确：端口从 .env 读取（生成代码时已写入正确的值）
     const port = process.env.PORT || 8099;
     app.listen(port, function() {
         console.log(`OAuth2 server listening on port: ${port}`);
     });
     ```
   - ❌ 错误示例：`const port = FRONTEND_PORT;`（禁止，不能用前端端口）
   - ❌ 错误示例：`const port = new URL(BASE_URL).port;`（禁止，不能从url解析端口）
   - ❌ 错误示例：`const port = process.env.PORT || (Number(FRONTEND_PORT) + 1);`（禁止运行时计算）

7. **配置：CLIENT_ID、CLIENT_SECRET、REDIRECT_URI 一律为常量**
   - **Node：** 在 `server/config/index.js` 中常量定义，不从 .env 读取；.env 只配置 PORT、BASE_URL、APP_KEYS 等。
   - **Python：** 在 config.py 或配置模块中常量定义，不从 .env 读取。
   - **Java：** 在 OAuthConfig 或常量类中 `static final` 定义，不从 application.yml 读取；yml 不写 client-id、client-secret、redirect-uri。
   - **Go：** 在配置包中 `const` 定义，不从 .env 读取。
   - 所有语言均不从环境变量/配置文件读取上述三项，只从代码中的常量读取。

8. **实现Token过期时间处理（重要）：**
   
   OAuth2的token有过期时间，需要在代码中处理token过期的情况：
   
   **a. 存储token过期时间：**
   - 在回调处理中，代码已经存储了`tokenExpiresAt`到session
   - `ctx.session.tokenExpiresAt = expires_in ? Date.now() + (expires_in * 1000) : null;`
   
   **b. 检查token是否过期：**
   
   在认证中间件或需要验证token的地方，添加过期检查：
   
   ```javascript
   // middleware/oauth2Auth.js 或相关中间件
   module.exports = () => async (ctx, next) => {
       // 检查session中是否有用户信息
       if (ctx.session && ctx.session.user) {
           // 检查token是否过期
           if (ctx.session.tokenExpiresAt && ctx.session.tokenExpiresAt < Date.now()) {
               // Token已过期，清除session，要求重新登录
               ctx.logger.warn('[OAuth2] Token已过期，清除session');
               ctx.session = null;
               ctx.requireAuth = true;
               return next();
           }
           // Token有效，继续处理
           ctx.user = ctx.session.user;
           return next();
       }
       
       // 未登录
       ctx.requireAuth = true;
       return next();
   };
   ```
   
   **c. 可选：实现token刷新（如果有refresh_token）：**
   
   如果OAuth服务器提供了refresh_token，可以实现token刷新（参考完整代码模板）。
   
   **重要说明：**
   - Token过期后，用户需要重新登录
   - 建议在token过期前（如提前5-10分钟）检查并刷新token
   - 如果没有refresh_token，token过期后只能重新登录

9. **前端调用：**
```javascript
// 登录：跳转到Node服务的登录路由
window.location.href = 'http://xx.xx.xx.xx:YOUR_PORT/oauth/login';

// 获取用户信息：调用Node服务的用户信息接口
fetch('http://xx.xx.xx.xx:YOUR_PORT/oauth/user', {
    credentials: 'include'  // 重要：携带cookie
})
.then(res => res.json())
.then(data => {
    if (data.success) {
        // 保存用户信息和token
        tokenStorage.set(data.data.accessToken);
        // 更新用户信息
    }
});

// 登出：调用Node服务的登出接口
fetch('http://xx.xx.xx.xx:YOUR_PORT/oauth/logout', {
    credentials: 'include'
});
```

**详细代码模板：** 参考 [Node Koa 模板](node_koa_template.md)

**✅ Step 2 完成提示：**

在完成 Step 2 的所有操作后（后端代码生成完成），必须向用户发送以下提示：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Step 2: 后端接口实现 - 已完成

📋 已完成的操作：
✓ 已检测项目后端语言：[检测到的语言]
✓ 已创建后端服务目录和文件
✓ 已实现OAuth2登录路由（/oauth/login）
✓ 已实现OAuth2回调路由（/callback）
✓ 已实现登出路由（/oauth/logout）
✓ 已实现获取用户信息路由（/oauth/user）
✓ 已实现Token过期处理
✓ 已实现State验证（CSRF防护）
✓ 已配置Session/状态管理
✓ 已创建环境变量配置文件

📌 下一步操作：
→ 即将开始 Step 3: 前端自动登录实现
→ 请确保后端服务可以正常启动（可先测试：cd server && npm run dev）

⚠️ 重要提醒：
- 后端服务地址：[从Step 1解析的系统URL]
- 如果后端服务未启动，前端自动登录将无法正常工作
- 建议先启动后端服务进行测试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**⚠️ 如果 Step 2 未完成，需要提示用户：**

如果在执行 Step 2 过程中遇到错误或未完成，必须向用户发送未完成提示，说明问题并给出建议。

## 其他语言实现说明

**如果检测到项目使用其他后端语言，请根据以下要求生成对应语言的代码：**

### 功能要求（所有语言必须实现）

1. **OAuth2配置管理**
   - 从环境变量或配置文件中读取：
     - `CLIENT_ID`（从Step 1获取的`data.id`）
     - `CLIENT_SECRET`（从Step 1获取的`data.secret`）
     - `REDIRECT_URI`（从Step 1获取的`data.redirectUris`）
     - `AUTHORIZATION_URI`: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/authorize`
     - `TOKEN_URI`: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/token`
     - `USER_INFO_URI`: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/user/info`
       - 注意：路径是 `/user/info` 不是 `/userinfo`
       - 禁止使用错误域名：`loginpass-bff-qa.tap4fun.com` 或错误路径：`/oauth/...`

2. **必需的路由/端点：**
   - `GET /oauth/login` - 初始化OAuth登录，生成state，重定向到授权服务器
     - 必须从请求中获取当前页面的完整URL（通过查询参数 `path` 或 `returnUrl`，或从 `Referer` 头获取）
     - 如果无法获取当前页面URL，使用系统的基础URL
     - 构建授权URL时，`path` 参数必须传递有效的URL，不能为 `null`
   - `GET /callback` - OAuth回调处理，接收code/token，换取access_token，获取用户信息
     - 处理完OAuth回调后，必须从OAuth服务器返回的`path`参数获取重定向URL
     - 如果`path`参数包含`localhost`，必须替换为配置的IP地址
     - 重定向URL必须使用配置的IP地址，不能使用localhost
     - 如果无法从`path`参数获取有效URL，使用系统的基础URL
   - `GET /oauth/logout` - 登出，清除session/状态
   - `GET /oauth/user` - 获取当前登录用户信息
   - `GET /oauth/token` - 获取当前用户的token信息（可选）

3. **核心功能实现：**
   - **State生成和验证**：防止CSRF攻击
   - **Session/状态管理**：存储用户信息、token、过期时间
   - **Token过期处理**：检查token是否过期，过期则清除状态要求重新登录
   - **HTTP请求**：调用OAuth服务器的三个接口（authorize、token、user/info）
   - **错误处理**：处理OAuth流程中的各种错误情况
   - **OAuth2授权URL构建**：构建授权URL时，包含以下参数：
     - `client_id`: OAuth2客户端ID
     - `redirect_uri`: 重定向URI（OAuth回调地址）
       - 必须与Step 1获取的 `REDIRECT_URI` 完全一致
       - 必须与后端实际路由路径和OAuth服务器注册值完全匹配，否则会返回500错误
       - 使用 `OAUTH2_CONFIG.REDIRECT_URI`，不要手动修改
     - `response_type`: 固定为 `'code'`
     - `state`: 用于CSRF防护的随机字符串
     - `path`: **当前页面的完整URL**（用于登录成功后跳转回原页面，不能为 `null`）
       - 必须从请求中获取当前页面的完整URL（包括协议、域名、端口、路径）
       - 获取方式（按优先级）：
         1. 从查询参数获取：`req.query.path` 或 `req.query.returnUrl`
         2. 从请求头获取：`req.headers.referer` 或 `req.headers['referer']`
         3. 从请求URL构建：使用 `req.protocol`、`req.hostname`、`req.originalUrl` 等构建完整URL
         4. 如果以上都无法获取，使用系统的基础URL（从Step 1获取的 `url` 参数）
       - 例如：如果用户访问 `http://192.168.1.100:3000/dashboard`，则 `path` 应该为 `http://192.168.1.100:3000/dashboard`
       - `path` 参数不能为 `null`，必须传递有效的URL
     - **禁止添加的参数：**
       - 不要添加 `scope` 参数（会导致 `invalid_scope` 错误）
       - 不要添加任何其他未明确要求的参数
     
   **授权URL构建示例（Node.js/Koa）：**
   ```javascript
   // 获取当前页面URL（必须返回有效URL，不能为null）
   const getCurrentPageUrl = (ctx) => {
     // 方式1: 从查询参数获取
     if (ctx.query.path && ctx.query.path !== 'null' && ctx.query.path !== '') {
       return ctx.query.path;
     }
     if (ctx.query.returnUrl && ctx.query.returnUrl !== 'null' && ctx.query.returnUrl !== '') {
       return ctx.query.returnUrl;
     }
     
     // 方式2: 从Referer头获取
     const referer = ctx.headers.referer || ctx.headers['referer'];
     if (referer && referer !== 'null' && referer !== '') {
       return referer;
     }
     
     // 方式3: 从请求URL构建
     const protocol = ctx.protocol || 'http';
     const host = ctx.host || ctx.headers.host;
     if (host) {
       // 移除 /oauth/login 路径，获取原始请求路径
       let originalUrl = ctx.originalUrl || ctx.url;
       if (originalUrl.startsWith('/oauth/login')) {
         // 如果是从 /oauth/login 访问，尝试从查询参数获取原始路径
         originalUrl = ctx.query.from || '/';
       }
       const currentUrl = `${protocol}://${host}${originalUrl}`;
       if (currentUrl && currentUrl !== 'null') {
         return currentUrl;
       }
     }
     
     // 方式4: 使用系统基础URL（从配置中获取，这是最后的保底方案）
     const baseUrl = OAUTH2_CONFIG.BASE_URL || process.env.BASE_URL;
     if (baseUrl && baseUrl !== 'null' && baseUrl !== '') {
       return baseUrl;
     }
     
     // ⚠️ 如果所有方式都失败，抛出错误或使用默认值（不应该发生）
     throw new Error('无法获取当前页面URL，请确保配置了BASE_URL或从请求中获取URL');
   };
   
   // 构建授权URL
   try {
     const currentPageUrl = getCurrentPageUrl(ctx);
     
     // ⚠️ 验证：确保 path 不为 null 或空字符串
     if (!currentPageUrl || currentPageUrl === 'null' || currentPageUrl === '') {
       ctx.throw(400, '无法获取当前页面URL，请检查请求参数或配置');
       return;
     }
     
     const state = generateState(); // 生成随机state
     // ⚠️ 关键：redirect_uri 必须使用 Step 1 获取的 REDIRECT_URI，不能修改
     // ⚠️ 关键：redirect_uri 必须与后端实际路由路径匹配，必须与OAuth服务器注册值一致
     // ⚠️ 关键：如果 redirect_uri 不匹配，OAuth服务器会返回500错误
     const authUrl = `${OAUTH2_CONFIG.AUTHORIZATION_URI}?` +
       `client_id=${OAUTH2_CONFIG.CLIENT_ID}&` +
       `redirect_uri=${encodeURIComponent(OAUTH2_CONFIG.REDIRECT_URI)}&` +
       `response_type=code&` +
       `state=${state}&` +
       `path=${encodeURIComponent(currentPageUrl)}`; // ⚠️ 已验证：path不为null
     
     // 保存state到session
     ctx.session.oauthState = state;
     
     // 重定向到授权服务器
     ctx.redirect(authUrl);
   } catch (error) {
     ctx.logger.error('[OAuth2] 构建授权URL失败:', error);
     ctx.throw(500, '登录初始化失败，请稍后重试');
   }
   ```
   
   **⚠️ 关键要求：**
   - 必须在构建授权URL前验证 `path` 参数不为 `null`、空字符串或字符串 `'null'`
   - 如果无法获取有效的 `path`，应该抛出错误或使用系统基础URL（从Step 1获取的 `url` 参数）
   - 所有语言实现都必须包含这个验证逻辑

5. **回调处理中的重定向URL构建（重要）：**
   
   **关键问题：登录成功后跳转到localhost而不是配置的地址**
   
   在OAuth回调处理（`/callback`路由）中，处理完OAuth回调后，需要重定向回原页面。必须确保重定向URL使用配置的地址（IP地址或域名），不能使用localhost。
   
   **支持格式：**
   - IP地址格式：`http://192.168.1.100:3000`
   - 域名格式：`https://example.com` 或 `https://example.com:8080`
   - 代码会自动识别URL格式，如果是域名则直接使用，如果是localhost则替换为配置的地址
   
   **回调处理重定向URL构建示例（Node.js/Koa）：**
   ```javascript
   // 在 /callback 路由中，处理完OAuth回调后
   router.get('/callback', async (ctx) => {
     // ... 验证state、换取token、获取用户信息、保存到session ...
     
     // 获取重定向URL（从OAuth服务器返回的path参数）
     const redirectPath = ctx.query.path || ctx.query.returnUrl;
     
     // 如果path包含localhost，必须替换为配置的地址（IP地址或域名）
     let redirectUrl = redirectPath;
     if (redirectUrl && redirectUrl.includes('localhost')) {
       // 从配置中获取系统URL（从Step 1获取的url参数，可以是IP地址或域名）
       const baseUrl = OAUTH2_CONFIG.BASE_URL || process.env.BASE_URL;
       if (baseUrl) {
         // 解析baseUrl获取协议、地址（IP地址或域名）、端口
         const urlObj = new URL(baseUrl);
         const protocol = urlObj.protocol;
         const host = urlObj.host; // 包含IP地址/域名和端口，如 192.168.1.100:3000 或 example.com:8080
         
         // 从redirectPath中提取路径部分
         const pathMatch = redirectPath.match(/\/.*$/);
         const path = pathMatch ? pathMatch[0] : '/';
         
         // 构建新的重定向URL，使用配置的IP地址和端口
         redirectUrl = `${protocol}//${host}${path}`;
       } else {
         // 如果没有配置BASE_URL，尝试从REDIRECT_URI中提取IP地址和端口
         const redirectUri = OAUTH2_CONFIG.REDIRECT_URI;
         if (redirectUri) {
           const redirectUriObj = new URL(redirectUri);
           const protocol = redirectUriObj.protocol;
           const host = redirectUriObj.host; // 包含IP地址和端口
           
           const pathMatch = redirectPath.match(/\/.*$/);
           const path = pathMatch ? pathMatch[0] : '/';
           
           redirectUrl = `${protocol}//${host}${path}`;
         }
       }
     }
     
     // 如果无法获取重定向URL，使用系统基础URL
     if (!redirectUrl || redirectUrl === 'null' || redirectUrl === '') {
       redirectUrl = OAUTH2_CONFIG.BASE_URL || process.env.BASE_URL || '/';
     }
     
     // 重定向回原页面（使用配置的IP地址）
     ctx.redirect(redirectUrl);
   });
   ```
   
   **⚠️ 关键要求：**
   - 在回调处理中，从`path`参数获取重定向URL后，**必须检查是否包含`localhost`**
   - 如果包含`localhost`，**必须替换为配置的IP地址**（从Step 1获取的`url`参数或`REDIRECT_URI`中提取）
   - 重定向URL必须使用配置的IP地址和端口，不能使用localhost
   - 如果无法从`path`参数获取有效URL，使用系统的基础URL（从Step 1获取的`url`参数）
   - 所有语言实现都必须包含这个逻辑

4. **代码结构建议：**
   - 配置文件（读取OAuth2配置）
   - 路由/控制器（处理OAuth相关请求）
   - 中间件/拦截器（认证检查、token过期检查）
   - 工具函数（生成state、解析token、HTTP请求等）

### 各语言实现要点

**Python (Flask/FastAPI/Django):**
- 使用 `requests` 库进行HTTP请求
- 使用框架的session机制存储状态
- 使用框架的路由系统定义端点
- 示例依赖：`requests`, `flask`/`fastapi`/`django`

**Java (Spring Boot):**
- **完整模板：参考 [Java Spring Boot 模板](java_spring_boot_template.md)**
- 使用 `RestTemplate` 进行HTTP请求
- 使用 `HttpSession` 存储状态，内存 `ConcurrentHashMap` 存储state
- 使用 `@RestController` 和 `@GetMapping` 定义端点
- 示例依赖：`spring-boot-starter-web`, `spring-boot-starter-session`

**Go:**
- 使用 `net/http` 或 `gin`/`echo` 等框架
- 使用cookie或session存储状态
- 使用 `http.Client` 进行HTTP请求
- 示例依赖：`github.com/gin-gonic/gin` 或标准库

**PHP:**
- 使用 `$_SESSION` 存储状态
- 使用 `curl` 或 `Guzzle` 进行HTTP请求
- 使用框架的路由系统（如Laravel、Symfony）

**Ruby (Rails/Sinatra):**
- 使用 `session` 存储状态
- 使用 `Net::HTTP` 或 `Faraday` 进行HTTP请求
- 使用框架的路由系统

**C#/.NET:**
- 使用 `HttpClient` 进行HTTP请求
- 使用 `ISession` 存储状态
- 使用 `[ApiController]` 和 `[Route]` 定义端点

**生成代码时请注意：**
- 使用Step 1中获取的实际配置值，不要使用占位符
- 代码必须可以直接运行，包含必要的依赖配置
- 遵循各语言的最佳实践和代码规范
- 实现完整的错误处理和日志记录
- 确保安全性（CSRF防护、输入验证等）
- **⚠️ 必须实现 `path` 参数验证**：
  - 在构建授权URL前，必须验证 `path` 参数不为 `null`、空字符串或字符串 `'null'`
  - 必须实现多种获取当前页面URL的方式（查询参数、Referer头、请求URL构建、系统基础URL）
  - 如果无法获取有效的 `path`，必须使用系统基础URL（从Step 1获取的 `url` 参数）作为保底方案
  - 绝对不允许 `path` 参数为 `null` 的情况发生
- **⚠️ 必须实现回调处理中的重定向URL修复**：
  - 在回调处理中，从`path`参数获取重定向URL后，必须检查是否包含`localhost`
  - 如果包含`localhost`，必须替换为配置的IP地址（从Step 1获取的`url`参数或`REDIRECT_URI`中提取）
  - 重定向URL必须使用配置的IP地址和端口，不能使用localhost
  - 所有语言实现都必须包含这个逻辑