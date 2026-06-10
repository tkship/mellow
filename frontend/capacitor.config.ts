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
  },
  plugins: {
    // 启用原生 HTTP 层，绕过 WebView CORS 限制
    CapacitorHttp: {
      enabled: true,
    },
  },
};

export default config;