/// API 配置 —— 后端地址。
class ApiConfig {
  // 开发环境默认地址
  static const String baseUrl = 'http://localhost:9000'; // 本地后端
  // static const String baseUrl = 'http://10.0.2.2:8000'; // Android 模拟器
  // static const String baseUrl = 'http://localhost:8000'; // iOS 模拟器

  static const String apiPrefix = '/api/v1';

  static String get authUrl => '$baseUrl$apiPrefix/auth';
  static String get chatUrl => '$baseUrl$apiPrefix/chat';
  static String get personasUrl => '$baseUrl$apiPrefix/personas';
  static String get knowledgeUrl => '$baseUrl$apiPrefix/knowledge';
  static String get profileUrl => '$baseUrl$apiPrefix/profile';
  static String get memoryUrl => '$baseUrl$apiPrefix/memory';
  static String get wsUrl => 'ws://10.0.2.2:8000$apiPrefix/voice/stream';
}
