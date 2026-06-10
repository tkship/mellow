## 1. 环境准备

- [ ] 1.1 安装 Capacitor 依赖：在 `frontend/` 目录下安装 `@capacitor/core`、`@capacitor/cli`、`@capacitor/android`
- [ ] 1.2 初始化 Capacitor 配置：创建 `frontend/capacitor.config.ts`，配置 `appId: 'com.mellow.app'`、`appName: 'Mellow'`、`webDir: 'dist'`、`server.androidScheme: 'https'`
- [ ] 1.3 添加 Android 平台：在 `frontend/` 下运行 `npx cap add android`

## 2. API 地址适配

- [ ] 2.1 修改 `frontend/src/api/client.ts`：将 `API_BASE` 从硬编码 `'/api/v1'` 改为 `import.meta.env.VITE_API_BASE_URL || '/api/v1'`
- [ ] 2.2 创建 `frontend/.env.production`，设置 `VITE_API_BASE_URL` 为生产环境后端地址
- [ ] 2.3 确认 SSE 流式请求（`chatStreamSse` 函数）中的 URL 构建逻辑同样使用可配置的 base URL

## 3. Android 项目配置

- [ ] 3.1 配置 Android 版本信息：设置 `versionCode: 1`、`versionName: "0.1.0"`
- [ ] 3.2 确认 Android SDK 版本：`minSdkVersion: 24`、`targetSdkVersion: 34`
- [ ] 3.3 配置 Android 应用名称为 "Mellow"
- [ ] 3.4 将 `frontend/android/` 目录添加到 `.gitignore`

## 4. 构建流程

- [ ] 4.1 执行前端构建：`npm run build`（确保 `VITE_API_BASE_URL` 环境变量已设置）
- [ ] 4.2 同步 Web 资源到 Android 项目：`npx cap sync android`
- [ ] 4.3 构建 debug APK：使用 Gradle 在 `frontend/android/` 下运行 `./gradlew assembleDebug`
- [ ] 4.4 验证 APK 生成：确认 `frontend/android/app/build/outputs/apk/debug/app-debug.apk` 存在且文件大小合理（<50MB）

## 5. GitHub Release 发布

- [ ] 5.1 安装 GitHub CLI（`gh`）或确认 API 可访问性
- [ ] 5.2 创建 `v0.1` git tag 并推送到远程仓库
- [ ] 5.3 使用 `gh release create v0.1` 创建 GitHub Release，标题为 "v0.1 - First Android APK"
- [ ] 5.4 上传 APK 文件到 Release 作为可下载资产
- [ ] 5.5 编写 Release Notes，说明这是首个 Android 测试版本，需要开启"未知来源安装"权限