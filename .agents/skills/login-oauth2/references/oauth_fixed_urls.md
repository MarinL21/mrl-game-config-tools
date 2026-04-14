# OAuth 固定接口地址（禁止修改）

**以下四个地址为固定值，生成或写入配置时必须原样使用。用错会导致 404 或认证失败。**

| 用途 | 固定地址 |
|------|----------|
| OAuth 认证（授权） | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/authorize` |
| OAuth Token | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/token` |
| OAuth 用户信息 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/user/info` |
| OAuth 登出 | `https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/logout` |

**禁止使用的错误地址（会导致 404）：**
- 域名 `loginpass-bff-qa.tap4fun.com`（申请应用用该域名，**不是** OAuth 接口）
- 路径 `/oauth/authorize`、`/oauth/token` 等（正确路径为 **`/loginpass/oauth/authorize`** 等）

**正确规则：** 域名必须为 `ms-open-gateway-qa.tap4fun.com`，路径必须为 `/loginpass/oauth/...`。

**生成后校验：** 写入配置或代码后，必须检查 AUTHORIZATION_URI、TOKEN_URI、USER_INFO_URI 是否为上表地址；若发现含 `loginpass-bff` 或路径为 `/oauth/` 开头，必须立即替换为上述固定地址。
