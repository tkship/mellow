class MellowErrors {
  // Auth
  static const wrongCredentials = '用户名或密码错误';
  static const registerFailed = '注册失败，请稍后重试';
  // Chat
  static const connectionLost = '连接中断，请重试';
  static const sendFailed = '发送失败，请重试';
  // Learn
  static const loadFailed = '加载失败';
  static const loadVocabFailed = '加载生词本失败，请重试';
  static const loadMistakesFailed = '加载错题失败，请重试';
  static const deleteVocabFailed = '删除失败，请重试';
  // Persona
  static const loadPersonasFailed = '加载角色列表失败';
  static const loadPersonaDetailFailed = '加载角色详情失败';
  static const voicePlayFailed = '语音播放失败';
  // Network (from api_client.dart)
  static const networkTimeout = '网络连接超时，请检查网络后重试';
  static const serverUnreachable = '无法连接到服务器，请检查网络';
  static const requestFailed = '请求失败，请稍后重试';
  // Profile
  static const updateProfileFailed = '更新失败，请重试';
  // Chat actions
  static const favoriteFailed = '收藏失败，请重试';
  static const deleteFailed = '删除失败，请重试';
}
