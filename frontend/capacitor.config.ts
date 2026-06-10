import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.mellow.app',
  appName: 'Mellow AI',
  webDir: 'dist',
  // Android 必须使用 https scheme，否则本地存储和 CORS 会出问题
  server: {
    androidScheme: 'https',
    // 允许 HTTP 明文请求（后端 API 不支持 HTTPS）
    cleartext: true,
    // ─── 单进程部署模式 ───
    // APK 启动后，Capacitor WebView 直接加载后端服务的前端页面。
    // 取消下面的注释并填入你的服务器地址即可：
    // url: 'http://your-server-ip:8000',
    //
    // 本地开发时注释掉 url，使用本地 dist 文件 + Vite proxy。
  },
  plugins: {
    // 启用原生 HTTP 层，绕过 WebView CORS 限制
    CapacitorHttp: {
      enabled: true,
    },
  },
};

export default config;