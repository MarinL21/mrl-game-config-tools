# 前端实现详细说明

本文档包含前端自动登录实现的详细说明，包括 React、Vue、Angular 和原生 HTML/JS 的实现。

## Step 3: 前端自动登录实现

**前置条件：** Step 2 必须完全完成

**关键说明：**
- **端口规则：** 前端项目的端口号 = url 中的端口号；后端端口号 = 前端端口号 + 1
- 不需要创建登录按钮，只需要实现自动登录逻辑
- 页面初次进入时自动检查登录状态，未登录时自动跳转到登录页面
- 第一次登录失败时不等待，可立即重试；后续重试可等待10秒再请求，直到登录成功

### 执行步骤

1. **检测前端框架：**

   使用脚本自动检测前端框架：

   ```bash
   python ~/.cursor/skills/login-oauth2/scripts/detect_frontend.py --path <项目路径> --json
   ```

   **注意：**
   - 将 `<项目路径>` 替换为实际的项目根目录路径（如 `.` 表示当前目录）
   - 脚本返回JSON格式，需要解析JSON输出
   - 如果脚本执行失败或未检测到前端框架，默认使用React

   **脚本会自动检测以下前端框架：**
   - **React**: 检测 `package.json` 中的 `react`、`react-dom`，以及 `src/App.jsx`、`src/App.tsx`、`src/index.jsx`、`src/index.tsx` 等文件
   - **Vue**: 检测 `package.json` 中的 `vue`，以及 `src/main.js`、`src/main.ts`、`src/App.vue` 等文件
   - **Angular**: 检测 `package.json` 中的 `@angular/core`，以及 `angular.json`、`src/app/app.component.ts` 等文件
   - **Svelte**: 检测 `package.json` 中的 `svelte`，以及 `svelte.config.js`、`src/App.svelte` 等文件
   - **原生HTML/JS**: 检测 `index.html` 文件，如果没有检测到框架依赖，默认为原生HTML

   **脚本返回格式（成功时）：**
   ```json
   {
     "framework": "react",
     "confidence": 95,
     "evidence": ["Found framework keywords in package.json", "Found file: src/App.tsx"]
   }
   ```

   **脚本返回格式（未检测到时）：**
   ```json
   {
     "framework": null,
     "message": "No frontend framework detected"
   }
   ```

   **处理脚本输出：**
   - 如果 `framework` 不为 `null`，使用检测到的框架生成代码
   - 如果 `framework` 为 `null`，默认使用React生成代码
   - 根据检测到的框架选择对应的实现方式

2. **解析url参数，计算前后端端口：**
   
   **规则：前端端口号 = url 中的端口号；后端端口号 = 前端端口号 + 1**
   
   ```javascript
   // 生成代码前，先解析用户给的url参数
   const urlObj = new URL(userUrl);
   const FRONTEND_HOST = urlObj.hostname;   // 如 "172.20.62.21"
   const FRONTEND_PORT = urlObj.port;       // 如 "3003" —— 前端端口 = url中的端口号
   const BACKEND_PORT  = Number(FRONTEND_PORT) + 1;  // 如 3004 —— 后端端口 = 前端端口+1
   ```
   
   - token的localStorage key固定为 `oauth_token`

3. **写入配置文件（必须执行，必须写入实际数字，禁止写变量或占位符）：**
   
   **以 url = `http://172.20.62.21:3003` 为例，生成代码时必须写入的内容：**
   
   **a. 前端配置文件 — 写入 HOST 和 PORT（等于url中的值）：**
   
   | 框架 | 要修改的文件 | 写入内容 |
   |------|-------------|---------|
   | React (CRA) | `.env` | `HOST=172.20.62.21`<br>`PORT=3003` |
   | Vite | `vite.config.js` 的 `server` 字段 | `host: '172.20.62.21', port: 3003` |
   | Angular | `angular.json` 的 `serve.options` | `"host": "172.20.62.21", "port": 3003` |
   | Webpack | `webpack.config.js` 的 `devServer` | `host: '172.20.62.21', port: 3003` |
   
   **b. 后端配置文件 — 写入 PORT（等于前端端口+1）：**
   
   | 文件 | 写入内容 |
   |------|---------|
   | 后端 `.env` | `PORT=3004` |
   
   **c. 前端请求后端的地址（BACKEND_URL / REACT_APP_BACKEND_URL）：** 必须为「本项目后端」地址，即从 url 解析的 host + 后端端口，例如 `http://172.20.62.21:3004`。**禁止**使用其他域名（如 survey-qa.tap4fun.com）或未从 Step 1 解析的地址，否则 /oauth/user 会 401 或请求到错误服务。
   
   **d. 验证（生成后必须检查）：**
   - ✅ 前端 `.env` 或配置文件中 PORT = **3003**（等于url中的端口）
   - ✅ 后端 `.env` 中 PORT = **3004**（等于前端端口+1）
   - ❌ 如果前端 PORT=3000 → **错误**，必须修正
   - ❌ 如果前后端 PORT 相同 → **错误**，必须修正

   **d. 开发环境：前端必须监听所有网卡（避免 OAuth 回调 ERR_CONNECTION_REFUSED）：**
   - **现象**：redirect_uri 使用 IP（如 `http://172.20.62.23:3002/callback`），授权后浏览器跳转到该地址时报「连接被拒绝」或 `ERR_CONNECTION_REFUSED`；Referer 可能是 `http://localhost:3002/`。
   - **原因**：前端开发服务器默认只监听 `127.0.0.1`，不监听 `172.20.62.23`，用 IP 访问时无法连上。
   - **解决**：让前端开发服务器监听**所有网卡**（`0.0.0.0`），这样既可用 localhost 也可用 IP 访问，OAuth 回调到 IP 才能成功。

   | 框架 | 要修改的文件 | 修改方式（监听 0.0.0.0） |
   |------|-------------|--------------------------|
   | Vite | `vite.config.js` 的 `server` | 增加 `host: true`（等价于 `host: '0.0.0.0'`），例如：<br>`server: { host: true, port: 3002 }` |
   | Webpack | `webpack.config.js` 的 `devServer` | `host: '0.0.0.0'` 或 `host: true`（视版本而定） |
   | Angular | `angular.json` 的 `serve.options` | `"host": "0.0.0.0"` |
   | React (CRA) | `.env` | `HOST=0.0.0.0`（或 `DANGEROUSLY_DISABLE_HOST_CHECK=true` 等，视 CRA 版本而定） |

   **Vite 示例（vite.config.js）：**
   ```javascript
   export default defineConfig({
     server: {
       host: true,  // 监听 0.0.0.0，使 172.20.62.23:PORT 可访问（OAuth 回调需要）
       port: 3002,
       open: true,
     },
   });
   ```

3. **根据检测到的框架实现自动登录逻辑：**

   **自动登录逻辑要求：**
   - 页面初次进入时，立即检查登录状态（不等待，直接执行）
   - 如果已登录，显示应用内容，不再请求
   - 如果未登录，立即跳转到登录页面（不等待，第一次检查时直接跳转）
   - 第一次登录失败时不等待，可立即重试；从第二次重试起可等待10秒后再请求登录接口
   - 重复上述逻辑，直到登录成功

4. **Token管理和请求拦截器：**
   
   **关键要求：**
   - 登录成功后，从 `/oauth/user` 接口返回的数据中提取 `accessToken`
   - 将token保存到localStorage，key固定为：`oauth_token`
   - 必须为所有前端请求添加请求拦截器，在header中自动添加 `Authorization: Bearer ${token}`
   - 如果token不存在或已过期，需要清除localStorage中的token并重新登录
   
   **Token保存逻辑：**
   - 在获取用户信息成功后（`/oauth/user` 接口返回成功），提取 `data.data.accessToken`
   - 保存到localStorage：`localStorage.setItem('oauth_token', accessToken)`
   
   **请求拦截器实现要求（必须创建文件并集成）：**
   - **React**: 
     - 必须创建拦截器文件（如 `src/utils/request.ts` 或 `src/api/interceptor.ts`）
     - 如果使用axios，必须配置axios拦截器
     - 如果使用fetch，必须创建封装的fetch函数（如 `src/utils/apiFetch.ts`）
     - **⚠️ 关键：必须在应用入口文件（如 `src/index.tsx`、`src/main.tsx`）中引入拦截器，确保所有请求都经过拦截器**
   - **Vue**: 
     - 必须创建拦截器文件（如 `src/utils/request.ts` 或 `src/api/interceptor.ts`）
     - 如果使用axios，必须配置axios拦截器
     - 如果使用fetch，必须创建封装的fetch函数（如 `src/utils/apiFetch.ts`）
     - **⚠️ 关键：必须在应用入口文件（如 `src/main.ts`、`src/main.js`）中引入拦截器，确保所有请求都经过拦截器**
   - **Angular**: 
     - 必须创建HTTP拦截器类（如 `src/app/interceptors/auth.interceptor.ts`）
     - **⚠️ 关键：必须在 `app.config.ts` 或 `app.module.ts` 中注册拦截器**，确保所有HTTP请求都经过拦截器
   - **原生HTML/JS**: 
     - 必须创建封装的fetch函数文件（如 `js/apiFetch.js`）
     - **⚠️ 关键：必须在所有使用fetch的地方替换为封装的apiFetch函数**，或者在主JS文件中引入并覆盖全局fetch
   
   **请求拦截器逻辑（Authorization值来自localStorage）：**
   ```javascript
   // ⚠️ 关键：从localStorage获取token，key固定为：oauth_token
   // ⚠️ 重要：/oauth/* 接口不需要Authorization header，它们依赖session（cookie）认证
   const token = localStorage.getItem('oauth_token');
   // 排除 /oauth/* 接口，这些接口使用session认证，不需要token
   if (token && !url.includes('/oauth/')) {
     // 在请求header中添加Authorization，值为：Bearer ${token}
     headers['Authorization'] = `Bearer ${token}`;
   }
   ```
   
   **⚠️ 重要说明：**
   - Authorization header的值必须从localStorage的`oauth_token`中获取
   - **⚠️ 关键：`/oauth/*` 接口（如 `/oauth/user`、`/oauth/login`、`/oauth/logout`）不需要Authorization header**，它们依赖session（cookie）认证
   - **⚠️ 关键：`/oauth/*` 接口必须设置 `credentials: 'include'`（fetch）或 `withCredentials: true`（axios/Angular）来携带cookie**，否则后端无法读取session，会返回401
   - 只有业务API接口需要Authorization header
   - 如果localStorage中没有token，则不添加Authorization header（请求正常发送，后端会返回401）
   - 拦截器必须在应用启动时就被注册/引入，确保所有后续的API请求都自动添加Authorization header
   
   **响应拦截器逻辑（处理401错误，必须实现）：**
   ```javascript
   // 响应拦截器：处理401未授权错误
   if (response.status === 401) {
     // 1. 清除localStorage中的token
     localStorage.removeItem('oauth_token');
     
     // 2. 获取当前页面的完整URL（包括协议、域名、端口、路径）
     const currentUrl = window.location.href;
     
     // 3. 重新触发登录流程，确保传递正确的path参数（不能为null）
     const loginUrl = `${BACKEND_URL}/oauth/login?path=${encodeURIComponent(currentUrl)}`;
     window.location.href = loginUrl;
     
     // 4. 返回rejected promise，阻止后续处理
     return Promise.reject(new Error('Unauthorized'));
   }
   ```
   
   **⚠️ 重要：**
   - 所有通过前端发起的API请求，都必须自动添加Authorization header
   - 如果token不存在，请求应该正常发送（不添加Authorization），后端会返回401，前端再处理登录逻辑
   - **如果收到401错误，必须执行以下步骤：**
     1. 清除localStorage中的token：`localStorage.removeItem('oauth_token')`
     2. 获取当前页面的完整URL：`window.location.href`（确保不为null）
     3. 重新触发登录流程，跳转到：`${BACKEND_URL}/oauth/login?path=${encodeURIComponent(currentUrl)}`
     4. **⚠️ 关键：path参数必须是当前页面的完整URL（不能为null），使用`encodeURIComponent`进行URL编码**

## React 实现（最常见）

详细代码示例请参考完整实现文档。主要步骤：

1. **创建配置文件（必须，避免重复声明）**：创建 `src/config/index.ts`，统一定义 `BACKEND_URL`
2. 创建自动登录Hook (`useAutoLogin.ts`)
3. 在应用入口或根组件中使用
4. **实现Token保存逻辑**：登录成功后，从 `/oauth/user` 返回数据中提取 `accessToken`，保存到 `localStorage.setItem('oauth_token', accessToken)`
5. **创建请求拦截器文件**：
   - 如果使用axios：创建 `src/utils/request.ts`，配置axios拦截器
   - 如果使用fetch：创建 `src/utils/apiFetch.ts`，封装fetch函数
6. **在应用入口文件中引入拦截器**（必须）：
   - 在 `src/index.tsx` 或 `src/main.tsx` 的最顶部添加：`import './utils/request'` 或 `import './utils/apiFetch'`
   - **⚠️ 关键：必须在其他导入之前引入，确保拦截器在应用启动时就被注册**
7. **实现响应拦截器**：处理401错误，清除token并重新触发登录流程（确保传递正确的path参数，不能为null）

**⚠️ 关键：避免重复声明 BACKEND_URL**

**⚠️ 关键：/oauth/user 必须请求「本项目后端」，不得请求其他域名**
- 获取当前用户信息必须请求**本 skill 生成的本项目后端**的 `/oauth/user`（或 `/api/oauth/user`，以实际后端路由为准），即 BACKEND_URL 或相对路径指向的**本项目后端**。
- **禁止**将「获取用户信息」请求发到其他域名（如 `survey-qa.tap4fun.com`、其他业务线域名）。否则会 401 或拿到错误数据。
- BACKEND_URL 生成时必须使用 Step 1 解析出的**本项目**后端地址（url 的 host + 后端端口），不能使用其他项目的 API 地址或环境变量中的其他域名。

**重要：前后端端口可以不一致，需要正确配置后端地址**

**推荐方案1：使用相对路径（如果前后端在同一域名和端口）**
- 如果前后端在同一域名和端口，使用相对路径更简单
- 不需要定义 `BACKEND_URL`，直接使用 `/oauth/user`、`/oauth/login` 等
- **⚠️ 注意：如果前后端端口不同，不能使用相对路径，必须使用完整URL**

**推荐方案2：统一配置文件（推荐，适用于前后端端口不同的情况）**
- 创建 `src/config/index.ts`，只在这里定义一次 `BACKEND_URL`
- **必须使用完整的后端地址，包括正确的端口号**（如 `http://192.168.1.100:8099`）
- 其他文件从配置文件导入，避免重复声明
- **示例：如果前端在3000端口，后端在8099端口，BACKEND_URL应该是 `http://192.168.1.100:8099`**

**配置文件示例：`src/config/index.ts`**
```typescript
// ⚠️ 重要：前后端端口可以不一致，必须使用完整的后端地址（包括端口号）
// 例如：前端在 http://192.168.1.100:3000，后端在 http://192.168.1.100:8099
// 那么 BACKEND_URL 应该是 'http://192.168.1.100:8099'
export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://192.168.1.100:8099';
```

**Token保存示例（在useAutoLogin.ts中，使用相对路径）：**
```typescript
// 推荐：使用相对路径，不需要 BACKEND_URL
const userInfo = await fetch('/oauth/user', {
  credentials: 'include'
}).then(res => res.json());

if (userInfo.success && userInfo.data?.accessToken) {
  // 保存token到localStorage
  localStorage.setItem('oauth_token', userInfo.data.accessToken);
}
```

**或者使用配置文件（如果前后端不在同一域名）：**
```typescript
import { BACKEND_URL } from '@/config';

const userInfo = await fetch(`${BACKEND_URL}/oauth/user`, {
  credentials: 'include'
}).then(res => res.json());

if (userInfo.success && userInfo.data?.accessToken) {
  localStorage.setItem('oauth_token', userInfo.data.accessToken);
}
```

**请求拦截器和响应拦截器示例（使用axios）：**

**文件：`src/utils/request.ts`**
```typescript
import axios from 'axios';
// ⚠️ 关键：从配置文件导入，避免重复声明
// 如果使用相对路径，可以注释掉这行，直接使用 '/oauth/login'
import { BACKEND_URL } from '@/config';

// 请求拦截器：自动添加Authorization header
// ⚠️ 关键：Authorization的值来自localStorage的`oauth_token`
// ⚠️ 重要：/oauth/* 接口不需要Authorization header，它们依赖session（cookie）认证
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('oauth_token'); // 从localStorage获取token
  // 排除 /oauth/* 接口，这些接口使用session认证，不需要token
  if (token && !config.url?.includes('/oauth/')) {
    config.headers.Authorization = `Bearer ${token}`; // 添加Authorization header
  }
  // ⚠️ 关键：/oauth/* 接口必须设置 withCredentials: true 来携带cookie
  if (config.url?.includes('/oauth/')) {
    config.withCredentials = true;
  }
  return config;
});

// 响应拦截器：处理401错误
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 1. 清除token
      localStorage.removeItem('oauth_token');
      // 2. 获取当前页面的完整URL（确保不为null）
      const currentUrl = window.location.href;
      // 3. 重新触发登录流程，确保传递正确的path参数（不能为null）
      window.location.href = `${BACKEND_URL}/oauth/login?path=${encodeURIComponent(currentUrl)}`;
    }
    return Promise.reject(error);
  }
);

export default axios;
```

**⚠️ 关键：在 `src/main.ts` 或 `src/main.js` 的最顶部引入（必须在其他导入之前）：**
```typescript
// src/main.ts
import './utils/request'; // 必须在最顶部，确保拦截器先注册
import { createApp } from 'vue';
// ... 其他导入
```

**请求拦截器和响应拦截器示例（使用fetch封装）：**

**文件：`src/utils/apiFetch.ts`**
```typescript
// ⚠️ 关键：从配置文件导入，避免重复声明
// 如果使用相对路径，可以注释掉这行，直接使用 '/oauth/login'
import { BACKEND_URL } from '@/config';

export const apiFetch = async (url: string, options: RequestInit = {}) => {
  // ⚠️ 关键：Authorization的值来自localStorage的`oauth_token`
  // ⚠️ 重要：/oauth/* 接口不需要Authorization header，它们依赖session（cookie）认证
  const token = localStorage.getItem('oauth_token'); // 从localStorage获取token
  const headers = new Headers(options.headers);
  // 排除 /oauth/* 接口，这些接口使用session认证，不需要token
  if (token && !url.includes('/oauth/')) {
    headers.set('Authorization', `Bearer ${token}`); // 添加Authorization header
  }
  
  // ⚠️ 关键：/oauth/* 接口必须设置 credentials: 'include' 来携带cookie
  const fetchOptions: RequestInit = {
    ...options,
    headers,
    // 对于 /oauth/* 接口，必须设置 credentials: 'include' 来携带cookie
    credentials: url.includes('/oauth/') ? 'include' : (options.credentials || 'same-origin'),
  };
  
  const response = await fetch(url, fetchOptions);
  
  // 处理401错误
  if (response.status === 401) {
    // 1. 清除token
    localStorage.removeItem('oauth_token');
    // 2. 获取当前页面的完整URL（确保不为null）
    const currentUrl = window.location.href;
    // 3. 重新触发登录流程，确保传递正确的path参数（不能为null）
    // 推荐：使用相对路径 '/oauth/login'（如果前后端在同一域名）
    // 或者：使用 `${BACKEND_URL}/oauth/login`（如果前后端不在同一域名）
    window.location.href = `/oauth/login?path=${encodeURIComponent(currentUrl)}`;
    // 如果前后端不在同一域名，使用：`${BACKEND_URL}/oauth/login?path=${encodeURIComponent(currentUrl)}`;
    // 4. 返回rejected promise，阻止后续处理
    return Promise.reject(new Error('Unauthorized'));
  }
  
  return response;
};
```

**⚠️ 关键：在 `src/index.tsx` 或 `src/main.tsx` 中引入，并在所有API调用中使用 `apiFetch` 替代 `fetch`：**
```typescript
// src/index.tsx
import { apiFetch } from './utils/apiFetch'; // 引入封装的fetch
// ... 其他导入

// 在所有API调用中使用 apiFetch 替代 fetch
// 例如：apiFetch('/api/users').then(res => res.json())
```

## Vue 实现

详细代码示例请参考完整实现文档。主要步骤：

1. 创建自动登录Composable (`useAutoLogin.ts`)
2. 在应用入口或根组件中使用
3. **实现Token保存逻辑**：登录成功后，从 `/oauth/user` 返回数据中提取 `accessToken`，保存到 `localStorage.setItem('oauth_token', accessToken)`
4. **创建请求拦截器文件**：
   - 如果使用axios：创建 `src/utils/request.ts`，配置axios拦截器
   - 如果使用fetch：创建 `src/utils/apiFetch.ts`，封装fetch函数
5. **在应用入口文件中引入拦截器**（必须）：
   - 在 `src/main.ts` 或 `src/main.js` 的最顶部添加：`import './utils/request'` 或 `import './utils/apiFetch'`
   - **⚠️ 关键：必须在其他导入之前引入，确保拦截器在应用启动时就被注册**
6. **实现响应拦截器**：处理401错误，清除token并重新触发登录流程（确保传递正确的path参数，不能为null）

**Token保存示例（在useAutoLogin.ts中，使用相对路径）：**
```typescript
// 推荐：使用相对路径，不需要 BACKEND_URL
const userInfo = await fetch('/oauth/user', {
  credentials: 'include'
}).then(res => res.json());

if (userInfo.success && userInfo.data?.accessToken) {
  // 保存token到localStorage
  localStorage.setItem('oauth_token', userInfo.data.accessToken);
}
```

**请求拦截器和响应拦截器示例（使用axios）：**

**文件：`src/utils/request.ts`**
```typescript
import axios from 'axios';
// ⚠️ 关键：从配置文件导入，避免重复声明
// 如果使用相对路径，可以注释掉这行，直接使用 '/oauth/login'
import { BACKEND_URL } from '@/config';

// 请求拦截器：自动添加Authorization header
// ⚠️ 关键：Authorization的值来自localStorage的`oauth_token`
// ⚠️ 重要：/oauth/* 接口不需要Authorization header，它们依赖session（cookie）认证
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('oauth_token'); // 从localStorage获取token
  // 排除 /oauth/* 接口，这些接口使用session认证，不需要token
  if (token && !config.url?.includes('/oauth/')) {
    config.headers.Authorization = `Bearer ${token}`; // 添加Authorization header
  }
  // ⚠️ 关键：/oauth/* 接口必须设置 withCredentials: true 来携带cookie
  if (config.url?.includes('/oauth/')) {
    config.withCredentials = true;
  }
  return config;
});

// 响应拦截器：处理401错误
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 1. 清除token
      localStorage.removeItem('oauth_token');
      // 2. 获取当前页面的完整URL（确保不为null）
      const currentUrl = window.location.href;
      // 3. 重新触发登录流程，确保传递正确的path参数（不能为null）
      window.location.href = `${BACKEND_URL}/oauth/login?path=${encodeURIComponent(currentUrl)}`;
    }
    return Promise.reject(error);
  }
);

export default axios;
```

**⚠️ 关键：在 `src/main.ts` 或 `src/main.js` 的最顶部引入（必须在其他导入之前）：**
```typescript
// src/main.ts
import './utils/request'; // 必须在最顶部，确保拦截器先注册
import { createApp } from 'vue';
// ... 其他导入
```

## Angular 实现

详细代码示例请参考完整实现文档。主要步骤：

1. 创建自动登录服务 (`auto-login.service.ts`)
2. 在应用根组件中使用
3. 配置HTTP客户端（在app.module.ts或app.config.ts中）
4. **实现Token保存逻辑**：登录成功后，从 `/oauth/user` 返回数据中提取 `accessToken`，保存到 `localStorage.setItem('oauth_token', accessToken)`
5. **创建HTTP拦截器文件**：创建 `src/app/interceptors/auth.interceptor.ts`，实现HttpInterceptor
6. **在app.config.ts或app.module.ts中注册拦截器**（必须）：
   - 在 `app.config.ts` 或 `app.module.ts` 中添加拦截器到 `HTTP_INTERCEPTORS` 提供者
   - **⚠️ 关键：必须注册拦截器，确保所有HTTP请求都经过拦截器**
7. **实现401错误处理**：在HTTP拦截器中处理401错误，清除token并重新触发登录流程（确保传递正确的path参数，不能为null）

**Token保存示例（在auto-login.service.ts中，使用相对路径）：**
```typescript
// 推荐：使用相对路径，不需要 BACKEND_URL
this.http.get('/oauth/user', { withCredentials: true })
  .subscribe((userInfo: any) => {
    if (userInfo.success && userInfo.data?.accessToken) {
      // 保存token到localStorage
      localStorage.setItem('oauth_token', userInfo.data.accessToken);
    }
  });
```

**HTTP拦截器示例（包含401错误处理）：**

**文件：`src/app/interceptors/auth.interceptor.ts`**
```typescript
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpErrorResponse } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
// ⚠️ 关键：从配置文件导入，避免重复声明
// 如果使用相对路径，可以注释掉这行，直接使用 '/oauth/login'
import { BACKEND_URL } from '@/config';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler) {
    // ⚠️ 关键：Authorization的值来自localStorage的`oauth_token`
    // ⚠️ 重要：/oauth/* 接口不需要Authorization header，它们依赖session（cookie）认证
    const token = localStorage.getItem('oauth_token'); // 从localStorage获取token
    let cloned = req;
    
    // 排除 /oauth/* 接口，这些接口使用session认证，不需要token
    if (token && !req.url.includes('/oauth/')) {
      cloned = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`) // 添加Authorization header
      });
    }
    
    // ⚠️ 关键：/oauth/* 接口必须设置 withCredentials: true 来携带cookie
    if (req.url.includes('/oauth/')) {
      cloned = cloned.clone({
        setHeaders: {},
        withCredentials: true
      });
    }
    
    return next.handle(cloned).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // 1. 清除token
          localStorage.removeItem('oauth_token');
          // 2. 获取当前页面的完整URL（确保不为null）
          const currentUrl = window.location.href;
          // 3. 重新触发登录流程，确保传递正确的path参数（不能为null）
          // 推荐：使用相对路径 '/oauth/login'（如果前后端在同一域名）
          // 或者：使用 `${BACKEND_URL}/oauth/login`（如果前后端不在同一域名）
          window.location.href = `/oauth/login?path=${encodeURIComponent(currentUrl)}`;
          // 如果前后端不在同一域名，使用：`${BACKEND_URL}/oauth/login?path=${encodeURIComponent(currentUrl)}`;
        }
        return throwError(() => error);
      })
    );
  }
}
```

**⚠️ 关键：在 `app.config.ts` 或 `app.module.ts` 中注册拦截器：**
```typescript
// app.config.ts (Angular 15+)
import { provideHttpClient, withInterceptorsFromDi, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptor } from './interceptors/auth.interceptor';

export const appConfig = {
  providers: [
    provideHttpClient(withInterceptorsFromDi()),
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ]
};

// 或 app.module.ts (Angular < 15)
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptor } from './interceptors/auth.interceptor';

@NgModule({
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ]
})
export class AppModule { }
```

## 原生 HTML/JS 实现

详细代码示例请参考完整实现文档。主要步骤：

1. 实现自动登录逻辑
2. **实现Token保存逻辑**：登录成功后，从 `/oauth/user` 返回数据中提取 `accessToken`，保存到 `localStorage.setItem('oauth_token', accessToken)`
3. **创建封装的fetch函数文件**：创建 `js/apiFetch.js`，封装fetch函数
4. **在主HTML文件中引入**（必须）：
   - 在 `index.html` 中引入封装的fetch函数：`<script src="js/apiFetch.js"></script>`
   - **⚠️ 关键：必须在所有使用fetch的地方替换为封装的apiFetch函数**，或者在主JS文件中覆盖全局fetch
5. **实现401错误处理**：在fetch封装函数中处理401错误，清除token并重新触发登录流程（确保传递正确的path参数，不能为null）

**Token保存示例：**
```javascript
// 获取用户信息成功后
fetch(`${BACKEND_URL}/oauth/user`, {
  credentials: 'include'
})
.then(res => res.json())
.then(userInfo => {
  if (userInfo.success && userInfo.data?.accessToken) {
    // 保存token到localStorage
    localStorage.setItem(tokenKey, userInfo.data.accessToken);
  }
});
```

**封装fetch函数示例（包含401错误处理）：**

**文件：`js/apiFetch.js`**
```javascript
const BACKEND_URL = 'http://your-backend-url'; // 从Step 1获取

// 封装fetch，自动添加Authorization header，并处理401错误
// ⚠️ 关键：Authorization的值来自localStorage的`oauth_token`
// ⚠️ 重要：/oauth/* 接口不需要Authorization header，它们依赖session（cookie）认证
async function apiFetch(url, options = {}) {
  const token = localStorage.getItem('oauth_token'); // 从localStorage获取token
  const headers = new Headers(options.headers || {});
  // 排除 /oauth/* 接口，这些接口使用session认证，不需要token
  if (token && !url.includes('/oauth/')) {
    headers.set('Authorization', `Bearer ${token}`); // 添加Authorization header
  }
  
  // ⚠️ 关键：/oauth/* 接口必须设置 credentials: 'include' 来携带cookie
  const fetchOptions = {
    ...options,
    headers,
    // 对于 /oauth/* 接口，必须设置 credentials: 'include' 来携带cookie
    credentials: url.includes('/oauth/') ? 'include' : (options.credentials || 'same-origin'),
  };
  
  const response = await fetch(url, fetchOptions);
  
  // 处理401错误
  if (response.status === 401) {
    // 1. 清除token
    localStorage.removeItem('oauth_token');
    // 2. 获取当前页面的完整URL（确保不为null）
    const currentUrl = window.location.href;
    // 3. 重新触发登录流程，确保传递正确的path参数（不能为null）
    // 推荐：使用相对路径 '/oauth/login'（如果前后端在同一域名）
    // 或者：使用 `${BACKEND_URL}/oauth/login`（如果前后端不在同一域名）
    window.location.href = `/oauth/login?path=${encodeURIComponent(currentUrl)}`;
    // 如果前后端不在同一域名，使用：`${BACKEND_URL}/oauth/login?path=${encodeURIComponent(currentUrl)}`;
    // 4. 返回rejected promise，阻止后续处理
    return Promise.reject(new Error('Unauthorized'));
  }
  
  return response;
}
```

**⚠️ 关键：在 `index.html` 中引入，并在所有使用fetch的地方替换为 `apiFetch`：**
```html
<!-- index.html -->
<script src="js/apiFetch.js"></script>
<script>
  // 方式1：在所有API调用中使用 apiFetch 替代 fetch
  // 例如：apiFetch('/api/users').then(res => res.json())
  
  // 方式2：或者覆盖全局fetch（可选）
  // window.fetch = apiFetch;
</script>
```

## 自动集成到项目中

**⚠️ 关键要求：生成代码时，必须自动创建并集成以下内容：**

### 1. 自动登录逻辑集成
- **如果检测到已有应用入口文件：** 在应用入口文件中添加自动登录逻辑
- **如果没有应用入口文件：** 在根组件或主页面中添加自动登录逻辑
- **如果使用路由系统：** 在路由守卫或应用初始化时添加自动登录逻辑

### 2. 请求拦截器集成（必须自动完成）
- **React/Vue (axios)**：
  - 创建拦截器配置文件（如 `src/utils/request.ts`）
  - **⚠️ 关键：必须在应用入口文件（`src/index.tsx`、`src/main.ts`）的最顶部引入拦截器**，确保在应用启动时就注册拦截器
  - 示例：在 `src/index.tsx` 中添加 `import './utils/request'`（必须在其他导入之前）
  
- **React/Vue (fetch封装)**：
  - 创建封装的fetch函数文件（如 `src/utils/apiFetch.ts`）
  - **⚠️ 关键：必须在应用入口文件中引入并导出**，确保所有API调用都使用封装的函数
  - 或者创建全局替换，将原生的 `fetch` 替换为封装的 `apiFetch`
  
- **Angular**：
  - 创建HTTP拦截器类（如 `src/app/interceptors/auth.interceptor.ts`）
  - **⚠️ 关键：必须在 `app.config.ts` 或 `app.module.ts` 中注册拦截器**，添加到 `HTTP_INTERCEPTORS` 提供者中
  - 示例：`{ provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }`
  
- **原生HTML/JS**：
  - 创建封装的fetch函数文件（如 `js/apiFetch.js`）
  - **⚠️ 关键：必须在主HTML文件（`index.html`）中引入**，并在所有使用fetch的地方替换为 `apiFetch`
  - 或者创建全局替换：`window.fetch = apiFetch`

**⚠️ 重要：拦截器必须在应用启动时就被注册/引入，确保所有后续的API请求都自动添加Authorization header（值来自localStorage的`oauth_token`）**

## 配置后端服务地址

- 创建环境变量配置文件（`.env`、`.env.local`、`config.js` 等）
- 将后端服务地址写入配置文件
- 在代码中通过环境变量读取后端服务地址

## 重要提示

- **后端服务地址：** 必须使用从Step 1解析的系统URL（`response.data.data.url`），不要使用占位符
- **跨域问题：** 如果前端和后端不在同一域名，需要确保后端配置了CORS
- **Cookie设置：** 前端调用后端API时，必须设置 `credentials: 'include'` 以携带cookie
- **自动登录逻辑：** 页面初次进入时自动检查登录状态，未登录时自动跳转到登录页面
- **重试机制：** 第一次登录失败不等待；后续重试可等待10秒再自动重试，直到登录成功
- **登出功能：** logout 函数已提供，如果需要可以自己调用
  - **⚠️ 提示：** 如果保留登出按钮，就需要自行创建未登录的停留页面（在当前页面不进行自动登录）。也可以选择直接去掉登出按钮

## 执行检查

- [ ] 已检测前端框架类型
- [ ] 已创建自动登录Hook/Service/Composable
- [ ] 已在应用入口或根组件中集成自动登录逻辑
- [ ] 已配置后端服务地址（环境变量或配置文件）
- [ ] 已实现登录状态检查逻辑
- [ ] 已实现登录失败重试机制（第一次不等待，后续重试可等待10秒）
- [ ] 页面初次进入时可以自动检查登录状态并跳转到登录页面
- [ ] **已实现Token保存逻辑**：登录成功后，从 `/oauth/user` 返回数据中提取 `accessToken`，保存到 `localStorage.setItem('oauth_token', accessToken)`
- [ ] **已创建请求拦截器文件**：
  - React/Vue (axios)：已创建 `src/utils/request.ts` 文件
  - React/Vue (fetch)：已创建 `src/utils/apiFetch.ts` 文件
  - Angular：已创建 `src/app/interceptors/auth.interceptor.ts` 文件
  - 原生HTML/JS：已创建 `js/apiFetch.js` 文件
- [ ] **已在应用入口文件中引入/注册拦截器**（必须）：
  - React/Vue：已在 `src/index.tsx` 或 `src/main.ts` 最顶部引入拦截器
  - Angular：已在 `app.config.ts` 或 `app.module.ts` 中注册拦截器
  - 原生HTML/JS：已在 `index.html` 中引入封装的fetch函数
- [ ] **已实现请求拦截器**：所有前端请求自动在header中添加 `Authorization: Bearer ${token}`（值来自localStorage的`oauth_token`）
- [ ] **已实现响应拦截器**：处理401错误，清除token并重新触发登录流程（确保传递正确的path参数，不能为null）

## 完成提示

**✅ Step 3 完成提示：**

在完成 Step 3 的所有操作后（包括：前端框架检测、自动登录逻辑实现、集成到应用中），必须向用户发送以下提示：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Step 3: 前端自动登录实现 - 已完成

📋 已完成的操作：
✓ 已检测前端框架类型：[检测到的框架]
✓ 已配置前端启动端口：前端端口 = url参数中的端口号，后端端口 = 前端端口+1
✓ 已创建自动登录Hook/Service/Composable
✓ 已在应用入口或根组件中集成自动登录逻辑
✓ 已配置后端服务地址
✓ 已实现登录状态检查逻辑
✓ 已实现登录失败重试机制（第一次不等待，后续重试可等待10秒）
✓ 页面初次进入时可以自动检查登录状态并跳转到登录页面
✓ 已实现Token保存逻辑：登录成功后，token已保存到localStorage（key: `oauth_token`）
✓ 已创建请求拦截器文件：已创建拦截器文件（`src/utils/request.ts`、`src/utils/apiFetch.ts` 或 `src/app/interceptors/auth.interceptor.ts`）
✓ 已在应用入口文件中引入/注册拦截器：拦截器已在应用启动时注册，确保所有请求都经过拦截器
✓ 已实现请求拦截器：所有前端请求自动在header中添加 `Authorization: Bearer ${token}`（值来自localStorage的`oauth_token`）
✓ 已实现响应拦截器：处理401错误，清除token并重新触发登录流程（确保传递正确的path参数，不能为null）

📌 流程完成：
→ ✅ Step 1: OAuth2配置获取 - 已完成
→ ✅ Step 2: 后端接口实现 - 已完成
→ ✅ Step 3: 前端自动登录实现 - 已完成

⚠️ 注意：Step 3 完成后，将自动执行 Step 4（检查并补全登录流程）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**⚠️ 关键要求：**
- Step 3 完成后，必须继续执行 Step 4（检查并补全登录流程）
- 必须明确说明 Step 3 已完成，将执行 Step 4

**⚠️ 如果 Step 3 未完成，需要提示用户：**

如果在执行 Step 3 过程中遇到错误或未完成，必须向用户发送未完成提示，说明问题并给出建议。**绝对不能在前一步未完成时继续执行下一步。**
