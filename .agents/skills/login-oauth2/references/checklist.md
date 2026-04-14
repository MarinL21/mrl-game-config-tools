# 执行检查清单和常见问题

本文档包含完整的执行检查清单和常见问题解答。

## 执行检查清单

完成配置后，检查以下项目：

### 基础配置
- [ ] **参数完整性检查（一）**：收到用户参数后已检查 systemName、url、redirectUris、employeeId 必填项齐全；缺 thirdParty/accessCompanyIds 已按默认补全；缺必填项时未调用接口并已提示用户补全
- [ ] **用户每次提供参数都要回填数据**：本次参数已执行回填（成功时用本次接口返回+本次用户参数，失败时用本次用户参数回填能写的项并标注缺失）；**再次提供时以本次为准**，url 等参数与回填数据均为最新一次，未沿用上次数据
- [ ] **参数完整性检查（二）**：请求回填后已检查 CLIENT_ID、CLIENT_SECRET、REDIRECT_URI、BASE_URL/url、host/端口 等均已写入且无占位符（接口失败时 CLIENT_ID/SECRET 会缺失，已标注并提示用户）；OAuth 固定三地址已写入；未通过时不得进入下一步，已补全或提示后再继续
- [ ] 收到用户参数后，已检查是否有前端与后端项目；若无前端或后端，已主动补充完整后再继续
- [ ] 已调用接口获取OAuth2配置（从data.id、data.secret、data.redirectUris提取）
- [ ] 已检测项目后端语言（若未指定/无后端则优先使用 Node，参考 node_koa_template.md）
- [ ] 后端服务目录/文件已创建（根据检测到的语言）
- [ ] 依赖配置文件已创建并配置（package.json/requirements.txt/pom.xml/go.mod等）
- [ ] OAuth2配置已正确设置（使用Step 1获取的实际值）
- [ ] 环境变量配置文件已创建（.env或对应语言的配置方式）

### 核心功能
- [ ] OAuth登录路由已实现（`/oauth/login`）
- [ ] OAuth回调路由已实现（`/callback`）
- [ ] 登出路由已实现（`/oauth/logout`）
- [ ] 获取用户信息路由已实现（`/oauth/user`）
- [ ] 认证中间件/拦截器已实现（检查登录状态）
- [ ] Token过期时间处理已实现
- [ ] State验证（CSRF防护）已实现
- [ ] Session/状态管理已正确配置

### 前端功能
- [ ] 已检测前端框架类型（React/Vue/Angular/原生HTML等）
- [ ] 已创建自动登录Hook/Service/Composable
- [ ] 已在应用入口或根组件中集成自动登录逻辑
- [ ] 已配置后端服务地址（必须为本项目后端：Step 1 解析的 host+后端端口，不得使用其他域名如 survey-qa.tap4fun.com）
- [ ] 已实现登录状态检查逻辑
- [ ] 已实现登录失败重试机制（第一次不等待，后续重试可等待10秒）
- [ ] 页面初次进入时可以自动检查登录状态并跳转到登录页面

### 功能验证
- [ ] 访问`/oauth/login`可以跳转到OAuth登录页面
- [ ] OAuth回调后可以正常获取用户信息
- [ ] Token过期后可以正确处理（清除session，要求重新登录）
- [ ] 登出功能正常工作
- [ ] 所有路由都能正常响应

## 常见问题

### 1. 如何找到server-test中的OAuth代码？

核心代码位置：
- `server-test/routes/oauth/index.js` - OAuth路由实现
- `server-test/middleware/oauth2Auth.js` - 认证中间件
- `server-test/config/index.js` - OAuth配置
- `server-test/app.js` - 应用入口

### 2. 如何测试OAuth2登录？

1. **启动后端服务：**
   - **Node.js**: `cd server && npm run dev`
   - **Python**: 根据框架启动（如 `python app.py` 或 `flask run`）
   - **Java**: `mvn spring-boot:run` 或运行主类
   - **Go**: `go run main.go` 或 `go build && ./app`
   - 其他语言按对应方式启动

2. **访问登录路由：**
   - 浏览器访问：`http://xx.xx.xx.xx:YOUR_PORT/oauth/login`（将 `xx.xx.xx.xx` 替换为您的本地IP地址，将 `YOUR_PORT` 替换为实际端口号）
   - 应该自动跳转到OAuth授权页面

3. **完成授权后：**
   - 应该回调到`/callback`
   - 自动获取用户信息并保存到session/状态
   - 重定向到首页

### 3. Token过期如何处理？

- 在认证中间件中检查`tokenExpiresAt`
- 如果过期，清除session，要求重新登录
- 如果有refresh_token，可以在过期前刷新token

### 4. 如何配置不同环境的OAuth地址？

在对应语言配置中：**所有语言**的 CLIENT_ID/SECRET/REDIRECT_URI 均为常量（Node 在 `server/config/index.js`，Python 在 `config.py`，Java 在 OAuthConfig/常量类，Go 在配置包），不从 .env/application.yml 读取；OAuth 地址等可在 .env 或 config 中。
- 开发环境：使用QA环境的OAuth地址
- QA环境：使用QA环境的OAuth地址
- 生产环境：使用生产环境的OAuth地址

### 5. 前端如何调用后端服务？

- **自动登录：** 页面初次进入时自动检查登录状态，未登录时自动跳转到`http://xx.xx.xx.xx:YOUR_PORT/oauth/login`（将 `xx.xx.xx.xx` 替换为您的本地IP地址，将 `YOUR_PORT` 替换为实际端口号）
- **登录重试：** 第一次登录失败不等待；后续重试可等待10秒后再次请求登录接口
- **获取用户信息：** 调用`http://xx.xx.xx.xx:YOUR_PORT/oauth/user`（需要携带cookie/session，将 `xx.xx.xx.xx` 替换为您的本地IP地址）
- **登出：** 调用`http://xx.xx.xx.xx:YOUR_PORT/oauth/logout`（将 `xx.xx.xx.xx` 替换为您的本地IP地址）
  - **⚠️ 提示：** 如果保留登出按钮，就需要自行创建未登录的停留页面（在当前页面不进行自动登录）。也可以选择直接去掉登出按钮

**注意：** 
- 不同语言的后端服务调用方式相同，都是通过HTTP请求访问上述端点
- 前端自动登录逻辑已自动创建，页面初次进入时会自动检查登录状态
- 后端服务地址已自动配置，无需手动修改

### 6. 如何为其他语言生成代码？

如果检测到项目使用其他后端语言（Python、Java、Go等），请：

1. **参考Node.js版本的实现逻辑**（`references/oauth_server_template.md`）
2. **使用对应语言的框架和库**实现相同的功能：
   - HTTP请求库（调用OAuth服务器接口）
   - Session/状态管理（存储用户信息和token）
   - 路由系统（定义OAuth相关端点）
   - 中间件/拦截器（认证检查）
3. **确保实现所有必需功能**（登录、回调、登出、获取用户信息、Token过期处理）
4. **使用Step 1获取的实际配置值**，不要使用占位符
5. **遵循各语言的最佳实践**和代码规范

## 注意事项

### OAuth2配置注意事项

1. **OAuth 固定接口（用错会 404）：** 必须使用 [oauth_fixed_urls.md](oauth_fixed_urls.md) 中的固定地址，不得使用 `loginpass-bff-qa.tap4fun.com` 或路径 `/oauth/authorize`、`/oauth/token`：
   - 认证: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/authorize`
   - Token: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/token`
   - 用户信息: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/user/info`
   - 登出: `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/logout`
   - 生成后必须校验：若发现含 `loginpass-bff` 或 `/oauth/` 路径，立即替换为上述地址。

2. **CLIENT_ID、CLIENT_SECRET、REDIRECT_URI（所有语言）：** 存成常量并从常量读取，不从 .env/application.yml 读取。Node 在 `server/config/index.js`，Python 在 `config.py`，Java 在 OAuthConfig 或常量类，Go 在配置包。必须使用接口返回的值（data.id、data.secret、data.redirectUris）回填到对应常量，不能手动占位。

3. **REDIRECT_URI：** 从接口返回的`data.redirectUris`提取，必须与请求参数中的`redirectUris`一致
   - **⚠️ 关键：`REDIRECT_URI` 必须与后端实际实现的路由路径完全匹配**
   - **⚠️ 关键：如果后端路由是 `/callback`，则 `redirectUris` 应该是 `http://xx.xx.xx.xx:PORT/callback`**
   - **⚠️ 关键：如果后端路由是 `/api/oauth/callback`，则 `redirectUris` 应该是 `http://xx.xx.xx.xx:PORT/api/oauth/callback`**
   - **⚠️ 关键：授权URL中的 `redirect_uri` 必须与 `REDIRECT_URI` 完全一致，否则OAuth服务器会返回500错误**

4. **数据提取：** 接口返回的数据在`data`对象中，需要从`response.data.data`中提取`id`、`secret`、`redirectUris`

5. **Session/状态管理配置：** 确保后端服务的session/状态管理机制正确配置（不同语言使用不同的方式）

6. **CORS配置：** 如果前端和后端不在同一域名，需要配置CORS（根据使用的框架配置）

7. **HTTPS：** 生产环境建议使用HTTPS，并设置相应的安全cookie配置

8. **State验证：** 确保OAuth回调中的state验证逻辑正确，防止CSRF攻击（所有语言都必须实现）

9. **OAuth2授权URL参数：** 构建授权URL时，包含以下参数：
    - `client_id`: OAuth2客户端ID
    - `redirect_uri`: 重定向URI（OAuth回调地址）
    - `response_type`: 固定为 `'code'`
    - `state`: 用于CSRF防护的随机字符串
    - `path`: **当前页面的完整URL**（用于登录成功后跳转回原页面，不能为 `null`）
      - 必须从请求中获取当前页面的完整URL（包括协议、域名、端口、路径）
      - 例如：如果用户访问 `http://192.168.1.100:3000/dashboard`，则 `path` 应该为 `http://192.168.1.100:3000/dashboard`
      - 如果无法获取当前页面URL，可以使用系统的基础URL（从Step 1获取的 `url` 参数）
    - **禁止添加的参数：**
      - 不要添加 `scope` 参数（会导致 `invalid_scope` 错误）
      - 不要添加任何其他未明确要求的参数
    - **⚠️ 重要：`path` 参数不能为 `null`，必须传递有效的URL**

10. **Cookie/Session设置：** 前端调用后端API时，需要正确设置以携带cookie/session（根据后端语言和框架）

11. **Token过期处理（重要）：**
    - OAuth2的token有过期时间，必须在代码中处理token过期的情况
    - 在认证中间件/拦截器中检查token是否过期
    - Token过期后，清除session/状态，要求用户重新登录
    - 如果有refresh_token，可以实现token刷新机制（在token即将过期时提前刷新）

12. **多语言支持：**
    - 若用户写了后端或项目已有后端，匹配对应语言生成代码（Java → java_spring_boot_template.md，Node → node_koa_template.md）
    - 若用户未写后端或未检测到后端，优先使用 Node（参考 node_koa_template.md，保证登录流程稳定）
    - 生成的代码必须可以直接部署使用，包含必要的依赖配置
    - 所有语言版本实现的功能必须一致

13. **前端自动登录（重要）：**
    - 后端接口实现完成后，必须自动检测前端框架并实现自动登录逻辑
    - 支持React、Vue、Angular、原生HTML/JS等主流前端框架
    - 页面初次进入时自动检查登录状态，未登录时自动跳转到后端登录路由
    - 第一次登录失败不等待；后续重试可等待10秒后重试，直到登录成功
    - 后端服务地址自动从Step 1解析的系统URL获取，无需手动配置
    - 如果前端和后端不在同一域名，确保后端配置了CORS
