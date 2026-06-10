## Context

Mellow 是一个语言学习 AI 伴侣应用，前端采用 React + Vite + TypeScript，后端为 Python FastAPI。目前前端仅作为 Web 应用运行，通过 Vite 开发服务器代理 `/api/v1` 请求到 `http://localhost:8000`。

生产环境中，前端构建后会部署为静态资源，API 请求需要指向实际的后端 URL。将 Web 应用打包为 APK 需要解决：

1. **API 路由问题**：APK 中的 WebView 没有开发代理，需要可配置的 API 基础 URL
2. **原生壳层**：需要 Capacitor 将 Web 资源包装为 Android 原生应用
3. **构建与签名**：需要 Gradle 构建并签名的 APK
4. **发布分发**：需要上传到 GitHub Releases 供用户下载

## Goals / Non-Goals

**Goals:**
- 将 Mellow 前端打包为可在 Android 设备上安装运行的 APK
- 使用 Capacitor 作为 Web-to-Native 桥接层
- 生成 v0.1 签名 APK 文件
- 将 APK 上传到 GitHub Releases（tkship/mellow 仓库）
- 确保 APK 内 Web 视图能正确连接后端 API

**Non-Goals:**
- 不做 App Store/Google Play 上架（仅 GitHub Release 分发）
- 不做 iOS 版本
- 不做推送通知等原生功能集成
- 不做自动 CI/CD 构建流水线（仅手动构建）
- 不修改后端代码

## Decisions

### Decision 1: 使用 Capacitor（而非 TWA 或 PWA Builder）

**选择**：Capacitor

**理由**：
- **TWA（Trusted Web Activity）** 需要应用已有线上部署的 HTTPS URL，且要求 PWA manifest 和 service worker。Mellow 前端目前没有完整 PWA 支持，且 TWA 无法很好地处理登录等交互场景
- **PWA Builder** 本质上也是 TWA 方案，有同样限制
- **Capacitor** 可以直接将本地构建的 Web 资源嵌入 WebView，支持自定义 API 服务器地址配置，且社区成熟、文档完善

**备选方案考虑**：
- Cordova：已过时，Capacitor 是其继任者
- React Native rewrite：成本过高，完全重写不现实

### Decision 2: API 基础 URL 配置方案

**选择**：环境变量 `VITE_API_BASE_URL` + Capacitor 配置 `server.url`

**理由**：
- 构建时通过 `VITE_API_BASE_URL` 环境变量注入完整的后端地址（如 `https://api.mellow.app`）
- Capacitor 的 `server.url` 可在 `capacitor.config.ts` 中配置，用于开发时覆盖
- 生产构建使用绝对 URL，避免 APK WebView 中的相对路径问题

**修改方式**：
- `client.ts` 中的 `API_BASE` 从硬编码 `/api/v1` 改为读取 `import.meta.env.VITE_API_BASE_URL || '/api/v1'`
- 新增 `.env.production` 文件设置生产环境 API 地址

### Decision 3: 构建和签名流程

**选择**：使用 debug 签名 + 生产构建

**理由**：
- v0.1 是首次发布，面向内部测试用户
- debug 签名无需创建 keystore，构建流程简单
- 后续版本可迁入 release 签名和 CI/CD

### Decision 4: GitHub Release 发布方式

**选择**：手动使用 `gh release create` 命令

**理由**：
- v0.1 是一次性发布，不需要自动化 CI
- `gh` CLI 尚未安装在当前环境，需要先安装
- 后续版本可考虑 GitHub Actions 自动化

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Capacitor WebView 在部分 Android 机型上可能有兼容性问题 | v0.1 仅面向测试用户，收集问题后迭代 |
| API 地址硬编码可能导致部署环境变更时需重新构建 | 使用环境变量，构建时注入，一次构建一环境 |
| debug 签名 APK 无法上架 Google Play | 不在 v0.1 scope 内，后续使用 release 签名 |
| Capacitor 生成的 `android/` 目录体积大，增加仓库大小 | 将 `android/` 加入 `.gitignore`，本地构建时生成 |
| `gh` CLI 未安装在构建环境 | 安装 `gh` CLI 或使用 GitHub API 直接上传 |

## Open Questions

1. **后端部署 URL**：v0.1 APK 连接的后端地址是什么？是 `localhost:8000`（仅测试用）还是已有线上部署？
2. **APK 目标 Android API level**：建议 targetSdk 34（Android 14），minSdk 24（Android 7），需要确认
3. **是否需要应用图标和启动画面设计**：v0.1 可暂时使用 Capacitor 默认值