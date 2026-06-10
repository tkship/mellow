## Why

Mellow 目前是一个 React + Vite + TypeScript 的 Web 应用，用户只能通过浏览器访问。为了提供更好的移动端体验和分发渠道，需要将前端打包为 Android APK 并发布到 GitHub Releases，让用户可以直接在手机上安装使用 v0.1 版本。

## What Changes

- **集成 Capacitor**：将 Capacitor 添加到前端项目，将 Vite 构建的 Web 资源包装为 Android 原生应用
- **配置 Android 平台**：初始化 Capacitor Android 项目，配置应用包名、版本号（v0.1）、应用名称、图标和启动画面
- **适配移动端 API 地址**：将前端 API 请求从开发环境代理模式改为可配置的生产环境地址，确保 APK 内的 Web 视图能正确连接后端
- **构建 APK**：配置 Gradle 签名和构建流程，生成 debug 或 release 签名的 APK 文件
- **发布到 GitHub Releases**：使用 GitHub API 将 v0.1 APK 上传到 `tkship/mellow` 仓库的 Release 页面

## Capabilities

### New Capabilities
- `apk-build`: 将 Web 前端打包为 Android APK 的完整流程，包括 Capacitor 集成、Android 项目配置、构建和签名
- `github-release`: 自动化发布流程，将构建产物上传到 GitHub Releases

### Modified Capabilities

（无现有能力需要修改）

## Impact

- **frontend/package.json**: 新增 Capacitor 相关依赖（@capacitor/core, @capacitor/cli, @capacitor/android）
- **frontend/capacitor.config.ts**: 新增 Capacitor 配置文件
- **frontend/android/**: 新增 Capacitor 生成的 Android 项目目录
- **frontend/src/api/**: API 基础 URL 可能需要适配（从代理模式变为直接请求）
- **frontend/vite.config.ts**: 可能需要调整构建配置以适配 Capacitor
- **.github/**: 可能新增 CI/CD 工作流（可选）
- **GitHub Releases**: 新增 v0.1 release 及 APK 产物