# Java Spring Boot OAuth2 后端模板

当检测到项目使用 Java (Spring Boot) 时，使用此模板生成代码。

**核心架构：前后端分端口，遵循 SKILL.md 的端口规则**
- 前端端口 = url 参数中的端口（如 3000）
- 后端端口（Spring Boot） = 前端端口 + 1（如 3001）
- 前端必须有 `/callback` 转发页面，将 OAuth 回调转发到后端，**否则会 404**
- 前端 API 调用目标为后端端口（port+1），需要 `credentials: 'include'`

**版本与包名：**
- **Spring Boot 2.x**：使用 `javax.servlet.*`（本模板默认）。
- **Spring Boot 3.x**：需将全部 `javax.servlet` 改为 `jakarta.servlet`（见文末「常见问题」）。
- 集成到**已有项目**时：请将 `com.example.oauth` 改为项目包名，或在主类上增加 `@ComponentScan` 包含 OAuth 所在包，否则 Filter/Controller 不会生效。

## 目录结构

```
# ====== 后端（Spring Boot，端口 = url端口 + 1） ======
src/main/java/com/example/oauth/
├── OAuthApplication.java             # 应用入口（含 CORS、RestTemplate）
├── config/
│   └── OAuthConfig.java              # OAuth2配置
├── controller/
│   └── OAuthController.java          # OAuth 路由
├── service/
│   ├── OAuthService.java             # 服务接口
│   └── impl/
│       └── OAuthServiceImpl.java     # 服务实现（包含所有业务逻辑）
├── filter/
│   └── OAuthAuthFilter.java          # 认证过滤器
└── util/
    └── StateStore.java               # 内存存储state（避免跨端口cookie问题）

src/main/resources/
└── application.yml                   # 应用配置（server.port = url端口 + 1）

# ====== 前端（静态文件，端口 = url端口） ======
# 前端文件由 SKILL 根据检测到的前端框架生成到对应位置
# 以下为原生 HTML/JS 时的结构示例：
frontend/                             # 或项目已有的前端目录
├── index.html                        # 前端页面（含自动登录逻辑）
├── app.js                            # 前端脚本（API 调用目标为后端端口）
└── callback/
    └── index.html                    # ★ 关键：OAuth 回调转发页（将 /callback 转发到后端）
```

**重要（避免前端出现 `?error=invalid_scope`）**：构建授权 URL 时**仅允许**参数 `client_id`、`redirect_uri`、`response_type`、`state`、`path`（可选）。**禁止添加 `scope` 或任何其它参数**，否则 OAuth 服务器会返回 invalid_scope，用户会被重定向到前端并看到 `?error=invalid_scope`。

## 1. application.yml

```yaml
server:
  # ⚠️ 后端端口 = url参数中的端口 + 1（生成时写入实际数字）
  # 例如：url=http://172.20.62.13:3000 → port=3001
  port: 3001
  servlet:
    session:
      timeout: 86400  # 24小时（秒）

oauth2:
  # 以下值从Step 1接口返回中获取，生成时写入实际值
  client-id: "[从Step 1获取的data.id]"
  client-secret: "[从Step 1获取的data.secret]"
  redirect-uri: "[从Step 1获取的data.redirectUris]"
  # OAuth2 接口地址（固定值，不要修改域名和路径）
  authorization-uri: https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/authorize
  token-uri: https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/token
  user-info-uri: https://ms-open-gateway-qa.tap4fun.com/loginpass/oauth/user/info
  grant-type: authorization_code
  # 系统基础URL（= 用户填的url参数，前端地址）
  base-url: "[从Step 1获取的url参数]"
  # 用户ID字段名（用于从用户信息中提取用户ID）
  user-name-attribute: id
```

## 2. OAuthConfig.java

```java
package com.example.oauth.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "oauth2")
public class OAuthConfig {
    private String clientId;
    private String clientSecret;
    private String redirectUri;
    private String authorizationUri;
    private String tokenUri;
    private String userInfoUri;
    private String grantType;
    private String baseUrl;
    private String userNameAttribute;

    // Getters and Setters
    public String getClientId() { return clientId; }
    public void setClientId(String clientId) { this.clientId = clientId; }

    public String getClientSecret() { return clientSecret; }
    public void setClientSecret(String clientSecret) { this.clientSecret = clientSecret; }

    public String getRedirectUri() { return redirectUri; }
    public void setRedirectUri(String redirectUri) { this.redirectUri = redirectUri; }

    public String getAuthorizationUri() { return authorizationUri; }
    public void setAuthorizationUri(String authorizationUri) { this.authorizationUri = authorizationUri; }

    public String getTokenUri() { return tokenUri; }
    public void setTokenUri(String tokenUri) { this.tokenUri = tokenUri; }

    public String getUserInfoUri() { return userInfoUri; }
    public void setUserInfoUri(String userInfoUri) { this.userInfoUri = userInfoUri; }

    public String getGrantType() { return grantType; }
    public void setGrantType(String grantType) { this.grantType = grantType; }

    public String getBaseUrl() { return baseUrl; }
    public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }

    public String getUserNameAttribute() {
        return userNameAttribute;
    }
    public void setUserNameAttribute(String userNameAttribute) {
        this.userNameAttribute = userNameAttribute;
    }
}
```

## 3. StateStore.java

```java
package com.example.oauth.util;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 内存存储state（避免跨端口cookie问题，与 Node 模板的 stateStore Map 一致）
 * 使用ConcurrentHashMap保证线程安全
 * state自动过期（10分钟）
 */
public class StateStore {

    private static final Map<String, StateData> store = new ConcurrentHashMap<>();
    private static final long EXPIRE_TIME = 10 * 60 * 1000; // 10分钟

    public static class StateData {
        public final long timestamp;
        public final String path;

        public StateData(String path) {
            this.timestamp = System.currentTimeMillis();
            this.path = path;
        }

        public boolean isExpired() {
            return System.currentTimeMillis() - timestamp > EXPIRE_TIME;
        }
    }

    public static void put(String state, String path) {
        cleanExpired();
        store.put(state, new StateData(path));
    }

    public static StateData get(String state) {
        StateData data = store.get(state);
        if (data != null && data.isExpired()) {
            store.remove(state);
            return null;
        }
        return data;
    }

    public static void remove(String state) {
        store.remove(state);
    }

    public static int size() {
        return store.size();
    }

    private static void cleanExpired() {
        store.entrySet().removeIf(entry -> entry.getValue().isExpired());
    }
}
```

## 4. OAuthController.java

```java
package com.example.oauth.controller;

import com.example.oauth.service.OAuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.util.Map;

@RestController
public class OAuthController {

    @Autowired
    private OAuthService oauthService;

    @GetMapping("/oauth/login")
    public void login(HttpServletRequest request, HttpServletResponse response) throws Exception {
        oauthService.handleLogin(request, response);
    }
    
    @GetMapping("/callback")
    public void callback(@RequestParam(name = "code", required = false) String[] codeArray,
                         @RequestParam(required = false) String state,
                         @RequestParam(required = false) String error,
                         @RequestParam(required = false) String token,
                         @RequestParam(name = "path", required = false) String redirectPath,
                         HttpServletRequest request,
                         HttpServletResponse response,
                         HttpSession session) throws Exception {
        String code = null;
        if (codeArray != null && codeArray.length > 0) {
            for (String c : codeArray) {
                if (c != null && !c.trim().isEmpty() && !"0".equals(c.trim())) {
                    code = c.trim();
                    break;
                }
            }
        }
        oauthService.handleCallback(code, state, error, token, redirectPath, request, response, session);
    }
    
    @GetMapping("/oauth/logout")
    public Map<String, Object> logout(HttpSession session) {
        return oauthService.logout(session);
    }

    @GetMapping("/oauth/user")
    public ResponseEntity<Map<String, Object>> getUser(HttpSession session) {
        Map<String, Object> result = oauthService.getUser(session);
        if (Boolean.TRUE.equals(result.get("success"))) {
            return ResponseEntity.ok(result);
        } else {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(result);
        }
    }

    @GetMapping("/oauth/token")
    public ResponseEntity<Map<String, Object>> getToken(HttpSession session) {
        Map<String, Object> result = oauthService.getToken(session);
        if (Boolean.TRUE.equals(result.get("success"))) {
            return ResponseEntity.ok(result);
        } else {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(result);
        }
    }
}
```

## 5. OAuthService.java

```java
package com.example.oauth.service;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.util.Map;

public interface OAuthService {
    void handleLogin(HttpServletRequest request, HttpServletResponse response) throws Exception;
    void handleCallback(String code, String state, String error, String token, String redirectPath,
                        HttpServletRequest request, HttpServletResponse response, HttpSession session) throws Exception;
    Map<String, Object> getUser(HttpSession session);
    Map<String, Object> getToken(HttpSession session);
    Map<String, Object> logout(HttpSession session);
}
```

## 6. OAuthServiceImpl.java

```java
package com.example.oauth.service.impl;

import com.example.oauth.config.OAuthConfig;
import com.example.oauth.service.OAuthService;
import com.example.oauth.util.StateStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.net.ConnectException;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

@Service
public class OAuthServiceImpl implements OAuthService {

    private static final Logger log = LoggerFactory.getLogger(OAuthServiceImpl.class);

    @Autowired
    private OAuthConfig config;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired(required = false)
    private Environment environment;

    /**
     * 获取当前页面 URL（与 Node 模板 getCurrentPageUrl 一致）
     * 优先级：query path/returnUrl → Referer（经 fixRedirectUrl 修正） → 请求 URL（经 fixRedirectUrl 修正） → BASE_URL 保底
     */
    private String getCurrentPageUrl(HttpServletRequest request) {
        String path = request.getParameter("path");
        if (path != null && !path.isEmpty() && !"null".equals(path)) {
            return path;
        }
        String returnUrl = request.getParameter("returnUrl");
        if (returnUrl != null && !returnUrl.isEmpty() && !"null".equals(returnUrl)) {
            return returnUrl;
        }
        // 与 Node 一致：Referer 经 fixRedirectUrl 修正 localhost
        String referer = request.getHeader("Referer");
        if (referer != null && !referer.isEmpty() && !"null".equals(referer)) {
            return fixRedirectUrl(referer);
        }
        // 与 Node 一致：请求 URL 经 fixRedirectUrl 修正
        String scheme = request.getScheme();
        String host = request.getHeader("Host");
        if (host != null) {
            String uri = request.getRequestURI();
            if (uri != null && uri.startsWith("/oauth/login")) {
                String from = request.getParameter("from");
                uri = (from != null && !from.isEmpty()) ? from : "/";
            }
            String url = scheme + "://" + host + uri;
            if (request.getQueryString() != null && !request.getQueryString().isEmpty()) {
                url += "?" + request.getQueryString();
            }
            if (!url.isEmpty() && !"null".equals(url)) {
                return fixRedirectUrl(url);
            }
        }
        String baseUrl = config.getBaseUrl();
        if (baseUrl != null && !baseUrl.isEmpty() && !"null".equals(baseUrl)) {
            return baseUrl;
        }
        throw new IllegalStateException("无法获取当前页面URL，请确保配置 oauth2.base-url 或从请求中可获取 URL");
    }

    /**
     * 修复重定向 URL（与 Node 模板 fixRedirectUrl 完全一致）
     * - 相对路径（/ 或 /xxx）→ 用 BASE_URL 拼成完整地址
     * - 含 localhost → 用 BASE_URL 的 host 替换，保留路径
     */
    private String fixRedirectUrl(String redirectUrl) {
        if (redirectUrl == null || redirectUrl.isEmpty() || "null".equals(redirectUrl)) {
            return config.getBaseUrl() != null ? config.getBaseUrl() : "/";
        }
        if (redirectUrl.startsWith("/")) {
            String base = config.getBaseUrl();
            if (base != null) {
                base = base.endsWith("/") ? base.substring(0, base.length() - 1) : base;
                return base + ("/".equals(redirectUrl) ? "" : redirectUrl);
            }
            return redirectUrl;
        }
        if (redirectUrl.contains("localhost")) {
            String base = config.getBaseUrl();
            if (base == null) {
                base = config.getRedirectUri();
            }
            if (base != null) {
                try {
                    URL u = new URL(base);
                    String protocol = u.getProtocol();
                    String hostStr = u.getHost();
                    int port = u.getPort();
                    String hostPort = (port > 0 && port != 80 && port != 443) ? hostStr + ":" + port : hostStr;
                    int pathStart = redirectUrl.indexOf('/', 7);
                    String pathStr = (pathStart >= 0) ? redirectUrl.substring(pathStart) : "/";
                    return protocol + "://" + hostPort + pathStr;
                } catch (Exception e) {
                    log.warn("[OAuth2] 解析 BASE_URL 失败，使用原始 URL: {}", redirectUrl);
                }
            }
        }
        return redirectUrl;
    }

    private String generateState() {
        SecureRandom random = new SecureRandom();
        byte[] bytes = new byte[16];
        random.nextBytes(bytes);
        StringBuilder sb = new StringBuilder(32);
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    @Override
    public void handleLogin(HttpServletRequest request, HttpServletResponse response) throws Exception {
        // ★ 与 Node 模板一致：配置校验，防止占位符未被替换
        String clientId = config.getClientId();
        String redirectUri = config.getRedirectUri();
        if (clientId == null || redirectUri == null
                || clientId.isEmpty() || redirectUri.isEmpty()
                || clientId.contains("[从Step") || redirectUri.contains("[从Step")) {
            log.error("[OAuth2] 配置缺失：CLIENT_ID 或 REDIRECT_URI 未设置");
            response.setStatus(500);
            response.setContentType("text/html;charset=utf-8");
            response.getWriter().write("OAuth2 配置缺失：请检查 application.yml 中 oauth2.client-id 和 oauth2.redirect-uri 是否已从 Step 1 接口结果回填");
            return;
        }

        String currentPageUrl;
        try {
            currentPageUrl = getCurrentPageUrl(request);
        } catch (Exception e) {
            log.warn("[OAuth2] 获取当前页面 URL 失败: {}，使用 base-url", e.getMessage());
            currentPageUrl = config.getBaseUrl() != null ? config.getBaseUrl() : "/";
        }
        if (currentPageUrl == null || currentPageUrl.isEmpty() || "null".equals(currentPageUrl)) {
            currentPageUrl = config.getBaseUrl() != null ? config.getBaseUrl() : "/";
        }

        String state = generateState();
        StateStore.put(state, currentPageUrl);

        log.info("[OAuth2] State已保存到内存: {}...", state.substring(0, Math.min(10, state.length())));
        log.info("[OAuth2] 内存中state数量: {}", StateStore.size());

        // ⚠️ 授权 URL 仅允许以下参数，禁止添加 scope
        String authUrl = config.getAuthorizationUri()
                + "?client_id=" + URLEncoder.encode(clientId, StandardCharsets.UTF_8)
                + "&redirect_uri=" + URLEncoder.encode(redirectUri, StandardCharsets.UTF_8)
                + "&response_type=code"
                + "&state=" + URLEncoder.encode(state, StandardCharsets.UTF_8);

        if (currentPageUrl != null && !"/".equals(currentPageUrl) && !"null".equals(currentPageUrl)) {
            authUrl += "&path=" + URLEncoder.encode(currentPageUrl, StandardCharsets.UTF_8);
        }

        log.info("[OAuth2] 重定向到授权服务器: {}", authUrl);
        log.info("[OAuth2] 授权URL中的 redirect_uri: {}", redirectUri);
        response.sendRedirect(authUrl);
    }

    @Override
    public void handleCallback(String code, String state, String error, String token, String redirectPath,
                               HttpServletRequest request, HttpServletResponse response, HttpSession session) throws Exception {
        log.info("[OAuth2] ========== 回调路由被触发 ==========");
        log.info("[OAuth2] 请求路径: {}", request.getRequestURI());
        log.info("[OAuth2] 请求 URL: {}", request.getRequestURL() + (request.getQueryString() != null ? "?" + request.getQueryString() : ""));
        log.info("[OAuth2] 回调参数: code={}, state={}, error={}, token={}, path={}", code, state, error, token != null ? "***" : null, redirectPath);

        if (error != null && !error.isEmpty()) {
            log.error("[OAuth2] 授权失败: {}", error);
            response.setStatus(400);
            response.setContentType("application/json;charset=utf-8");
            response.getWriter().write("{\"success\":false,\"message\":\"授权失败: " + error + "\"}");
            return;
        }

        // ★ 与 Node 模板一致：从内存中获取并验证 state
        StateStore.StateData stateData = state != null ? StateStore.get(state) : null;
        log.info("[OAuth2] 内存中的state: {}", stateData != null ? "存在" : "不存在");

        String activeProfile = (environment != null) ? environment.getProperty("spring.profiles.active", "") : "";
        boolean isProduction = "production".equals(activeProfile);

        if (state == null || state.isEmpty()) {
            log.warn("[OAuth2] 回调 URL 中未包含 state 参数");
            if (isProduction) {
                response.setStatus(400);
                response.setContentType("application/json;charset=utf-8");
                response.getWriter().write("{\"success\":false,\"message\":\"State 参数缺失\"}");
                return;
            }
        } else if (stateData == null) {
            log.error("[OAuth2] State 验证失败 - 内存中未找到state: {}", state);
            log.warn("[OAuth2] 可能的原因：1) state已过期（10分钟） 2) 服务器重启导致内存清空 3) state从未被保存");
            if (isProduction) {
                response.setStatus(400);
                response.setContentType("application/json;charset=utf-8");
                response.getWriter().write("{\"success\":false,\"message\":\"State验证失败\"}");
                return;
            } else {
                log.warn("[OAuth2] 开发环境：State 验证失败但继续处理（仅用于调试）");
            }
        } else {
            // ★ 与 Node 模板一致：显式检查 state 是否过期
            if (stateData.isExpired()) {
                log.error("[OAuth2] State 已过期 - 创建时间: {}, 当前时间: {}", Instant.ofEpochMilli(stateData.timestamp), Instant.now());
                StateStore.remove(state);
                if (isProduction) {
                    response.setStatus(400);
                    response.setContentType("application/json;charset=utf-8");
                    response.getWriter().write("{\"success\":false,\"message\":\"State 已过期，请重新登录\"}");
                    return;
                } else {
                    log.warn("[OAuth2] 开发环境：State 已过期但继续处理（仅用于调试）");
                }
            } else {
                log.info("[OAuth2] State 验证成功: {}...", state.substring(0, Math.min(10, state.length())));
                log.info("[OAuth2] State保存的path: {}", stateData.path);
            }
        }

        String savedPath = stateData != null ? stateData.path : null;
        if (state != null) {
            StateStore.remove(state);
        }

        String accessToken = null;
        String tokenType = "Bearer";
        Long expiresIn = null;
        String refreshToken = null;

        try {
            // 情况1: URL 中直接包含 token（与 Node 一致）
            if (token != null && !token.isEmpty()) {
                log.info("[OAuth2] 检测到 URL 中直接返回的 token");
                accessToken = token;
                expiresIn = 24L * 60 * 60;
                if (token.contains(".")) {
                    try {
                        String payload = new String(java.util.Base64.getUrlDecoder().decode(token.split("\\.")[1]), StandardCharsets.UTF_8);
                        java.util.regex.Pattern p = java.util.regex.Pattern.compile("\"exp\"\\s*:\\s*(\\d+)");
                        java.util.regex.Matcher m = p.matcher(payload);
                        if (m.find()) {
                            long expSec = Long.parseLong(m.group(1));
                            expiresIn = Math.max(0, expSec - System.currentTimeMillis() / 1000);
                        }
                    } catch (Exception e) {
                        log.debug("[OAuth2] 非 JWT 或解析 exp 失败，使用默认过期时间");
                    }
                }
            }
            // 情况2: 使用 code 换取 token（与 Node 模板一致）
            else if (code != null && !code.isEmpty() && !"0".equals(code)) {
                log.info("[OAuth2] ========== 使用 code 换取 access_token ==========");
                log.info("[OAuth2] TOKEN_URI: {}", config.getTokenUri());
                log.info("[OAuth2] 使用的 code: {}...", code.substring(0, Math.min(10, code.length())));
                log.info("[OAuth2] CLIENT_ID: {}", config.getClientId());
                log.info("[OAuth2] REDIRECT_URI: {}", config.getRedirectUri());
                log.info("[OAuth2] ⚠️ 关键：调用TOKEN_URI时使用的 redirect_uri 必须与授权URL中的完全一致");

                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

                MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
                params.add("grant_type", config.getGrantType());
                params.add("code", code);
                params.add("client_id", config.getClientId());
                params.add("client_secret", config.getClientSecret());
                params.add("redirect_uri", config.getRedirectUri());

                HttpEntity<MultiValueMap<String, String>> entity = new HttpEntity<>(params, headers);

                ResponseEntity<Map> tokenResponse;
                try {
                    tokenResponse = restTemplate.postForEntity(config.getTokenUri(), entity, Map.class);
                    log.info("[OAuth2] Token 响应状态: {}", tokenResponse.getStatusCode());
                    log.info("[OAuth2] Token 响应数据: {}", tokenResponse.getBody());
                } catch (HttpClientErrorException e) {
                    // ★ HTTP 4xx 错误（与 Node 模板一致的分类处理）
                    int status = e.getStatusCode().value();
                    String msg = e.getResponseBodyAsString();
                    log.error("[OAuth2] ========== TOKEN_URI调用失败 ==========");
                    log.error("[OAuth2] Token 错误响应状态: {}", status);
                    log.error("[OAuth2] Token 错误响应数据: {}", msg);
                    if (status == 400) {
                        log.error("[OAuth2] ⚠️ 常见原因：1.REDIRECT_URI不匹配 2.CLIENT_ID/SECRET错误 3.Code已过期");
                    }
                    response.setStatus(status);
                    response.setContentType("application/json;charset=utf-8");
                    String hint = (status == 400)
                            ? "请检查REDIRECT_URI、CLIENT_ID、CLIENT_SECRET、Code是否正确"
                            : (status == 401) ? "认证失败" : "获取 token 失败";
                    if (msg == null || msg.isEmpty()) msg = hint;
                    response.getWriter().write("{\"success\":false,\"message\":\"获取token失败: " + msg.replace("\"", "\\\"") + "\"}");
                    return;
                } catch (HttpServerErrorException e) {
                    // ★ HTTP 5xx（Node 模板有，Java 之前缺失）
                    log.error("[OAuth2] TOKEN_URI返回 {} 错误: {}", e.getStatusCode(), e.getResponseBodyAsString());
                    response.setStatus(500);
                    response.setContentType("application/json;charset=utf-8");
                    response.getWriter().write("{\"success\":false,\"message\":\"OAuth服务器内部错误，请稍后重试\"}");
                    return;
                } catch (ResourceAccessException e) {
                    // ★ 网络错误（与 Node 的 ECONNABORTED/ECONNREFUSED/ENOTFOUND 对齐）
                    log.error("[OAuth2] TOKEN_URI网络错误: {}", e.getMessage());
                    Throwable cause = e.getCause();
                    String errorMsg;
                    int errorStatus;
                    if (cause instanceof SocketTimeoutException) {
                        errorMsg = "请求超时，请稍后重试";
                        errorStatus = 504;
                    } else if (cause instanceof ConnectException) {
                        errorMsg = "无法连接OAuth服务器: " + config.getTokenUri();
                        errorStatus = 503;
                    } else {
                        errorMsg = "网络错误，请检查网络连接";
                        errorStatus = 503;
                    }
                    response.setStatus(errorStatus);
                    response.setContentType("application/json;charset=utf-8");
                    response.getWriter().write("{\"success\":false,\"message\":\"" + errorMsg.replace("\"", "\\\"") + "\"}");
                    return;
                } catch (Exception e) {
                    log.error("[OAuth2] TOKEN_URI请求异常: {}", e.getMessage());
                    response.setStatus(503);
                    response.setContentType("application/json;charset=utf-8");
                    response.getWriter().write("{\"success\":false,\"message\":\"无法连接 OAuth 服务器\"}");
                    return;
                }

                Map<String, Object> tokenBody = tokenResponse.getBody();
                if (tokenBody != null) {
                    Map<String, Object> tokenData = tokenBody.containsKey("data")
                            ? (Map<String, Object>) tokenBody.get("data")
                            : tokenBody;
                    accessToken = (String) tokenData.getOrDefault("access_token", tokenData.get("token"));
                    tokenType = (String) tokenData.getOrDefault("token_type", "Bearer");
                    Object exp = tokenData.get("expires_in");
                    if (exp instanceof Number) {
                        expiresIn = ((Number) exp).longValue();
                    }
                    Object refreshTokenObj = tokenData.get("refresh_token");
                    refreshToken = refreshTokenObj != null ? refreshTokenObj.toString() : null;
                }

                if (accessToken == null) {
                    log.error("[OAuth2] 未获取到 access_token，响应数据: {}", tokenBody);
                    throw new RuntimeException("未获取到access_token");
                }
                log.info("[OAuth2] 成功获取access_token");
            } else {
                response.setStatus(400);
                response.setContentType("application/json;charset=utf-8");
                response.getWriter().write("{\"success\":false,\"message\":\"未收到token或code\"}");
                return;
            }

            // 获取用户信息
            log.info("[OAuth2] 获取用户信息: {}", config.getUserInfoUri());
            HttpHeaders userHeaders = new HttpHeaders();
            String capitalizedType = tokenType.substring(0, 1).toUpperCase() + tokenType.substring(1).toLowerCase();
            userHeaders.set("Authorization", capitalizedType + " " + accessToken);

            ResponseEntity<Map> userResponse;
            try {
                userResponse = restTemplate.exchange(
                        config.getUserInfoUri(), HttpMethod.GET,
                        new HttpEntity<>(userHeaders), Map.class);
            } catch (Exception e) {
                if (e instanceof HttpServerErrorException || (e.getCause() != null && e.getCause().toString().contains("500"))) {
                    log.warn("[OAuth2] Header方式失败，尝试query参数方式");
                    userResponse = restTemplate.getForEntity(
                            config.getUserInfoUri() + "?access_token=" + accessToken, Map.class);
                } else {
                    throw e;
                }
            }
            log.info("[OAuth2] 用户信息响应: {}", userResponse.getBody());

            Map<String, Object> userBody = userResponse.getBody();
            Map<String, Object> userInfo = null;
            if (userBody != null) {
                if (userBody.containsKey("data") && userBody.get("data") instanceof Map) {
                    userInfo = (Map<String, Object>) userBody.get("data");
                } else if (userBody.containsKey("id") || userBody.containsKey("userId") || userBody.containsKey("employeeId")) {
                    userInfo = userBody;
                } else {
                    userInfo = userBody;
                }
            }

            if (userInfo == null) {
                throw new RuntimeException("未获取到用户信息");
            }

            String userNameAttr = config.getUserNameAttribute() != null ? config.getUserNameAttribute() : "id";
            Object userId = userInfo.get(userNameAttr);
            if (userId == null) userId = userInfo.get("id");
            if (userId == null) userId = userInfo.get("userId");
            if (userId == null) userId = userInfo.get("employeeId");
            if (userId == null) {
                throw new RuntimeException("用户信息中未找到用户ID");
            }

            Map<String, Object> sessionUser = new HashMap<>(userInfo);
            sessionUser.put("id", userId);
            session.setAttribute("user", sessionUser);
            session.setAttribute("accessToken", accessToken);
            session.setAttribute("refreshToken", refreshToken);
            session.setAttribute("tokenExpiresAt",
                    expiresIn != null ? System.currentTimeMillis() + expiresIn * 1000 : null);

            log.info("[OAuth2] 用户登录成功: {}", userId);

            // ★ 与 Node 模板一致的完整重定向兜底链
            String redirectUrl = (redirectPath != null && !redirectPath.isEmpty()) ? redirectPath : savedPath;
            if (redirectUrl == null || redirectUrl.isEmpty() || "null".equals(redirectUrl)) {
                redirectUrl = "/";
            }
            redirectUrl = fixRedirectUrl(redirectUrl);

            // 二次检查 localhost
            if (redirectUrl != null && redirectUrl.contains("localhost")) {
                String baseUrl = config.getBaseUrl();
                if (baseUrl != null && !baseUrl.isEmpty()) {
                    try {
                        URL u = new URL(baseUrl);
                        int pathStart = redirectUrl.indexOf('/', 7);
                        String pathStr = (pathStart >= 0) ? redirectUrl.substring(pathStart) : "/";
                        redirectUrl = u.getProtocol() + "://" + u.getHost()
                                + (u.getPort() > 0 && u.getPort() != 80 && u.getPort() != 443 ? ":" + u.getPort() : "")
                                + pathStr;
                    } catch (Exception e) {
                        redirectUrl = baseUrl;
                    }
                }
            }

            if (redirectUrl == null || redirectUrl.isEmpty() || "null".equals(redirectUrl)) {
                redirectUrl = config.getBaseUrl() != null ? config.getBaseUrl() : "/";
            }

            // ★ 最终防护：相对路径必须拼 BASE_URL（否则会跳到后端端口而不是前端端口）
            if ("/".equals(redirectUrl) || (redirectUrl.startsWith("/") && !redirectUrl.startsWith("//"))) {
                String baseUrl = config.getBaseUrl();
                if (baseUrl != null && !baseUrl.isEmpty()) {
                    String base = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
                    redirectUrl = base + ("/".equals(redirectUrl) ? "" : redirectUrl);
                }
            }

            log.info("[OAuth2] 重定向到: {}", redirectUrl);
            response.sendRedirect(redirectUrl);

        } catch (Exception e) {
            log.error("[OAuth2] ========== 认证过程出错 ==========");
            log.error("[OAuth2] 错误消息: {}", e.getMessage(), e);
            log.error("[OAuth2] 当前配置: CLIENT_ID={}, REDIRECT_URI={}, TOKEN_URI={}", config.getClientId(), config.getRedirectUri(), config.getTokenUri());
            String queryString = request.getQueryString() != null ? request.getQueryString() : "";
            response.setContentType("text/html;charset=utf-8");
            response.setStatus(500);
            response.getWriter().write(
                    "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>OAuth2 认证失败</title>"
                            + "<style>body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;padding:20px;background:#f5f5f5;}"
                            + ".c{max-width:600px;margin:40px auto;background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1);}"
                            + "h1{color:#ff4d4f;}.d{background:#f9f9f9;padding:15px;margin:15px 0;border-radius:4px;border:1px solid #eee;word-break:break-all;}"
                            + "a{color:#1890ff;}</style></head>"
                            + "<body><div class=\"c\"><h1>OAuth2 认证失败</h1>"
                            + "<p style=\"color:#ff4d4f\">" + escapeHtml(e.getMessage()) + "</p>"
                            + "<div class=\"d\"><p><b>请求路径：</b>" + escapeHtml(request.getRequestURI()) + "</p>"
                            + "<p><b>请求参数：</b>" + escapeHtml(queryString) + "</p></div>"
                            + "<p>请检查服务器日志获取详细信息。</p>"
                            + "<p><a href=\"/oauth/login\">重新登录</a></p></div></body></html>");
        }
    }

    private String escapeHtml(String str) {
        if (str == null) return "";
        return str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;");
    }

    @Override
    public Map<String, Object> getUser(HttpSession session) {
        log.info("[OAuth2] ========== 获取用户信息请求 ==========");
        Map<String, Object> user = (Map<String, Object>) session.getAttribute("user");
        String accessToken = (String) session.getAttribute("accessToken");

        Map<String, Object> result = new HashMap<>();
        if (user != null) {
            log.info("[OAuth2] 返回用户信息: {}", user.get("id"));
            Map<String, Object> data = new HashMap<>(user);
            data.put("accessToken", accessToken);
            result.put("success", true);
            result.put("data", data);
        } else {
            log.warn("[OAuth2] 用户未登录");
            result.put("success", false);
            result.put("message", "未登录");
        }
        return result;
    }

    @Override
    public Map<String, Object> getToken(HttpSession session) {
        String accessToken = (String) session.getAttribute("accessToken");
        String refreshToken = (String) session.getAttribute("refreshToken");
        Long tokenExpiresAt = (Long) session.getAttribute("tokenExpiresAt");

        Map<String, Object> result = new HashMap<>();
        if (accessToken != null) {
            Map<String, Object> data = new HashMap<>();
            data.put("accessToken", accessToken);
            data.put("refreshToken", refreshToken);
            data.put("expiresAt", tokenExpiresAt);
            result.put("success", true);
            result.put("data", data);
        } else {
            result.put("success", false);
            result.put("message", "未登录");
        }
        return result;
    }

    @Override
    public Map<String, Object> logout(HttpSession session) {
        session.invalidate();
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "登出成功");
        return result;
    }
}
```

## 7. OAuthAuthFilter.java

```java
package com.example.oauth.filter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

/**
 * OAuth 认证过滤器（与 Node 模板 oauth2Auth 一致）
 */
@Component
public class OAuthAuthFilter implements Filter {

    private static final Logger log = LoggerFactory.getLogger(OAuthAuthFilter.class);

    private static final List<String> PUBLIC_PATHS = Arrays.asList(
            "/oauth/", "/callback", "/favicon.ico", "/health", "/healthz"
    );

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;
        String path = request.getRequestURI();

        boolean isPublic = PUBLIC_PATHS.stream().anyMatch(path::startsWith);
        if (isPublic) {
            chain.doFilter(req, res);
            return;
        }

        HttpSession session = request.getSession(false);
        if (session != null) {
            Map<String, Object> user = (Map<String, Object>) session.getAttribute("user");
            Object expObj = session.getAttribute("tokenExpiresAt");
            Long tokenExpiresAt = (expObj instanceof Number) ? ((Number) expObj).longValue() : null;

            if (user != null) {
                if (tokenExpiresAt != null && tokenExpiresAt < System.currentTimeMillis()) {
                    log.warn("[OAuth2] Token已过期，清除session");
                    session.invalidate();
                } else {
                    request.setAttribute("user", user);
                    chain.doFilter(req, res);
                    return;
                }
            }
        }

        request.setAttribute("requireAuth", true);
        chain.doFilter(req, res);
    }
}
```

## 8. OAuthApplication.java

```java
package com.example.oauth;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@SpringBootApplication
public class OAuthApplication {

    public static void main(String[] args) {
        SpringApplication.run(OAuthApplication.class, args);
    }

    @Bean
    public RestTemplate restTemplate() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(10000);
        factory.setReadTimeout(30000);
        return new RestTemplate(factory);
    }

    /**
     * ★ CORS 配置（port+1 架构下前后端跨端口，必须配置）
     * 允许前端端口的跨域请求携带 cookie（session），否则 /oauth/user 无法识别登录状态
     */
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                        .allowedOriginPatterns("*")
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                        .allowedHeaders("*")
                        .allowCredentials(true)
                        .maxAge(3600);
            }
        };
    }
}
```

## 9. 前端：callback/index.html（★ 回调转发页，解决 404）

**这是解决回调 404 的关键文件。** 放在前端项目的 `callback/` 目录下（如 `frontend/callback/index.html`）。

OAuth 回调会打到前端端口（redirect_uri = `http://host:3000/callback`），此页面自动将请求转发到后端端口（port+1），由后端完成 code→token→用户信息 的处理。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>登录中...</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f0f2f5; }
        .loading { text-align: center; color: #666; }
        .spinner { width: 40px; height: 40px; border: 3px solid #e0e0e0; border-top-color: #1890ff; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="loading">
        <div class="spinner"></div>
        <p>正在处理登录，请稍候...</p>
    </div>
    <script>
        // ★ 将 OAuth 回调从前端端口转发到后端端口（前端端口 + 1）
        // 前端收到: http://host:3000/callback?code=xxx&state=yyy
        // 转发到:   http://host:3001/callback?code=xxx&state=yyy
        (function () {
            var port = parseInt(window.location.port) || (window.location.protocol === 'https:' ? 443 : 80);
            var backendPort = port + 1;
            var backendBase = window.location.protocol + '//' + window.location.hostname + ':' + backendPort;
            var search = window.location.search || '';
            window.location.href = backendBase + '/callback' + search;
        })();
    </script>
</body>
</html>
```

**⚠️ 不同前端框架的处理方式：**

| 前端类型 | 处理方式 |
|---------|---------|
| **原生 HTML/JS** | 放文件 `callback/index.html`（如上） |
| **React** | 添加 `/callback` 路由组件，`useEffect` 中执行相同的转发逻辑 |
| **Vue** | 添加 `/callback` 路由组件，`created` 或 `mounted` 中执行转发 |
| **Angular** | 添加 `/callback` 路由组件，`ngOnInit` 中执行转发 |

转发逻辑都一样：`window.location.href = 后端地址 + '/callback' + window.location.search`

## 10. 前端：index.html（主页面，含自动登录）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>系统</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .container { background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,.08); padding: 40px; max-width: 480px; width: 90%; text-align: center; }
        h1 { font-size: 24px; color: #333; margin-bottom: 20px; }
        .status { color: #999; font-size: 14px; margin-bottom: 16px; }
        .user-info { text-align: left; margin: 20px 0; }
        .user-info .row { padding: 10px 0; border-bottom: 1px solid #f0f0f0; display: flex; }
        .user-info .label { color: #999; width: 80px; flex-shrink: 0; }
        .user-info .value { color: #333; word-break: break-all; }
        .btn { display: inline-block; padding: 10px 28px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn:hover { opacity: .85; }
        .btn-primary { background: #1890ff; color: #fff; }
        .btn-danger { background: #ff4d4f; color: #fff; margin-top: 20px; }
        #login-section, #user-section { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1 id="title">系统</h1>
        <div id="loading" class="status">正在检查登录状态...</div>
        <div id="login-section">
            <p class="status">您尚未登录，正在跳转到登录页面...</p>
            <button class="btn btn-primary" onclick="doLogin()">手动登录</button>
        </div>
        <div id="user-section">
            <div class="user-info" id="user-info"></div>
            <button class="btn btn-danger" onclick="doLogout()">登出</button>
        </div>
    </div>
    <script src="app.js"></script>
</body>
</html>
```

## 11. 前端：app.js（自动登录脚本）

```javascript
(function () {
    // ★ port+1 架构：后端在当前端口 + 1
    var frontendPort = parseInt(window.location.port) || (window.location.protocol === 'https:' ? 443 : 80);
    var BACKEND_BASE = window.location.protocol + '//' + window.location.hostname + ':' + (frontendPort + 1);

    function checkLogin() {
        // ★ credentials: 'include' 确保跨端口请求携带 cookie（session）
        fetch(BACKEND_BASE + '/oauth/user', { credentials: 'include' })
            .then(function (res) {
                document.getElementById('loading').style.display = 'none';
                if (res.status === 401) {
                    document.getElementById('login-section').style.display = 'block';
                    // 自动跳转到后端的 /oauth/login（后端会重定向到 OAuth 授权页）
                    window.location.href = BACKEND_BASE + '/oauth/login?path=' + encodeURIComponent(window.location.href);
                    return null;
                }
                return res.json();
            })
            .then(function (data) {
                if (data && data.success && data.data) {
                    showUser(data.data);
                }
            })
            .catch(function (err) {
                console.error('[OAuth2] 检查登录状态失败:', err);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('login-section').style.display = 'block';
            });
    }

    function showUser(user) {
        document.getElementById('user-section').style.display = 'block';
        var info = document.getElementById('user-info');
        var html = '';
        html += '<div class="row"><span class="label">用户ID</span><span class="value">' + (user.id || '-') + '</span></div>';
        var name = user.name || user.username || user.employeeName;
        if (name) {
            html += '<div class="row"><span class="label">用户名</span><span class="value">' + name + '</span></div>';
        }
        if (user.email) {
            html += '<div class="row"><span class="label">邮箱</span><span class="value">' + user.email + '</span></div>';
        }
        info.innerHTML = html;
    }

    window.doLogin = function () {
        window.location.href = BACKEND_BASE + '/oauth/login?path=' + encodeURIComponent(window.location.href);
    };

    window.doLogout = function () {
        fetch(BACKEND_BASE + '/oauth/logout', { credentials: 'include' })
            .then(function () { window.location.reload(); });
    };

    checkLogin();
})();
```

## 12. pom.xml 依赖

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-configuration-processor</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

## 端口配置说明

```
遵循 SKILL.md 端口规则：前端 = url端口，后端 = url端口 + 1

用户url = "http://172.20.62.13:3000" 时：
  ┌─────────┬────────────────────────────────────────────────────┐
  │  前端   │ PORT = 3000  （= url中的端口号）                   │
  │         │ ├── index.html, app.js                             │
  │         │ └── callback/index.html  ★ 转发到后端 /callback    │
  ├─────────┼────────────────────────────────────────────────────┤
  │  后端   │ PORT = 3001  （= url中的端口号 + 1）               │
  │         │ ├── /callback      → OAuthController 处理          │
  │         │ ├── /oauth/login   → 重定向到 OAuth 授权服务器     │
  │         │ ├── /oauth/user    → 返回当前用户信息              │
  │         │ └── /oauth/logout  → 清除登录状态                  │
  └─────────┴────────────────────────────────────────────────────┘

★ OAuth 回调流程（解决 404）：
  1. OAuth 授权后重定向到 → http://host:3000/callback?code=xxx
  2. 前端 callback/index.html 自动转发 → http://host:3001/callback?code=xxx
  3. 后端处理 code 换 token、获取用户信息、存 session
  4. 后端重定向回前端 → http://host:3000/
  5. 前端 app.js 调用后端 /oauth/user → 已登录，显示用户信息
```

生成代码时在 `application.yml` 中将 `server.port` 设为 url端口+1 的实际数字。

## 常见问题与启动说明

1. **Spring Boot 3.x 使用 Jakarta 命名空间**  
   若项目为 Spring Boot 3，需将以下 import 全部替换：
    - `javax.servlet.*` → `jakarta.servlet.*`
    - `javax.servlet.http.*` → `jakarta.servlet.http.*`  
      涉及文件：`OAuthController.java`、`OAuthService.java`、`OAuthServiceImpl.java`、`OAuthAuthFilter.java`。

2. **集成到已有项目、Filter/Controller 不生效**  
   若 OAuth 代码放在独立包（如 `com.example.oauth`），而主应用在 `com.t4f.xxx`，需在主类上增加扫描，例如：
   `@ComponentScan(basePackages = {"com.t4f.xxx", "com.example.oauth"})`  
   或将 OAuth 相关类移到主应用同包/子包下。

3. **回调 404（⚠️ 最常见问题）**
    - **原因**：redirect_uri 指向前端端口（如 3000），但前端没有 `/callback` 处理器
    - **解决**：在前端项目中添加 `callback/index.html` 转发页（见第 9 节），将请求转发到后端端口（port+1）
    - **验证**：浏览器访问 `http://host:前端端口/callback` 应能看到"正在处理登录"页面并自动跳转
    - **React/Vue/Angular**：在前端路由中添加 `/callback` 路由，组件中执行 `window.location.href = 后端地址 + '/callback' + window.location.search`

4. **CORS 与 allowCredentials（port+1 必需）**  
   前后端跨端口时 CORS 必须配置。`allowedOriginPatterns("*")` 需 Spring Boot 2.4+；若版本较低请改为 `.allowedOrigins("http://前端地址:端口")`，并保留 `.allowCredentials(true)`。  
   前端调用后端 API 时必须设置 `credentials: 'include'`（fetch）或 `withCredentials: true`（axios），否则 session cookie 不会发送。

5. **Session 中 tokenExpiresAt 类型**  
   部分容器反序列化后为 `Integer`，Filter 中已改为通过 `Number` 安全取 `Long`，避免 `ClassCastException`。

6. **State 校验与开发/生产环境**  
   开发环境放宽 state 校验（继续处理），生产环境请设置 `spring.profiles.active=production`，state 校验失败会返回 400。

7. **前端静态文件如何启动**  
   前端文件需要一个静态文件服务器在 url 端口上运行，可选方案：
    - `npx serve frontend/ -l 3000`
    - `python3 -m http.server 3000 --directory frontend/`
    - 项目已有的前端 dev server（webpack-dev-server、vite 等）
    - Nginx 等反向代理

8. **若配置了 server.servlet.context-path**  
   Filter 中 `request.getRequestURI()` 会带 context-path，需在 `PUBLIC_PATHS` 中使用带前缀的路径。

## 关键要点（与 SKILL.md、Node 模板对齐）

1. **端口规则**：遵循 SKILL.md，前端端口 = url 端口，后端端口 = 前端端口 + 1。
2. **回调转发**：前端必须有 `callback/index.html`（或对应框架的 /callback 路由），将 OAuth 回调转发到后端端口。这是解决 404 的关键。
3. **禁止在授权 URL 中添加 scope 参数**：授权 URL 仅允许 `client_id`、`redirect_uri`、`response_type`、`state`、`path`（可选）。
4. **配置校验**：登录前校验 CLIENT_ID、REDIRECT_URI 是否仍为占位符（与 Node 一致）。
5. **state 使用内存存储**：避免跨端口 cookie 问题（与 Node 的 stateStore Map 一致）。
6. **redirect_uri**：必须与 Step 1 获取的 REDIRECT_URI 完全一致。
7. **getCurrentPageUrl**：从 path/returnUrl、Referer（经 fixRedirectUrl 修正）、请求 URL（经 fixRedirectUrl 修正）、base-url 依次获取（与 Node 一致）。
8. **fixRedirectUrl**：相对路径用 base-url 拼接；含 localhost 时替换为配置的 host；回调后二次检查 localhost 和相对路径。
9. **Token 交换错误处理**：区分 4xx、5xx、超时、连接拒绝等不同错误类型（与 Node 对齐）。
10. **RestTemplate 超时**：10秒连接 + 30秒读取，避免请求挂起。
11. **CORS 必需**：跨端口架构下 CORS + `credentials: 'include'` 缺一不可。
12. **前端 API 调用**：`BACKEND_BASE = protocol + hostname + ':' + (frontendPort + 1)`，所有 API 调用目标为后端端口。
13. **登录成功后重定向到前端**：`fixRedirectUrl` 和最终防护确保重定向到 BASE_URL（前端地址），而不是后端端口。
14. **OAuth2 接口地址固定**：
    - 正确：`ms-open-gateway-qa.tap4fun.com`，路径 `/loginpass/oauth/...`
    - 禁止：`loginpass-bff` 或 路径 `/oauth/...`（用错会 404）
    - user-info-uri 路径为 `/user/info`，不是 `/userinfo`
