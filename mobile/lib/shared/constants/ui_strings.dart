/// Mellow UI string constants - centralized Chinese text management.
class MellowStrings {
  // Auth
  static const appSubtitle = '你的 AI 英语老师';
  static const login = '登录';
  static const register = '注册';
  static const username = '用户名';
  static const password = '密码';
  static const usernameHint = '请输入用户名';
  static const passwordHint = '请输入密码';
  static const confirmPassword = '确认密码';
  static const confirmPasswordHint = '再次输入密码';
  static const noAccount = '还没有账号？';
  static const hasAccount = '已有账号？';
  static const registerNow = '立即注册';
  static const loginNow = '立即登录';
  static const createAccount = '创建账号';
  static const joinMellow = '加入 Mellow，AI 陪你学英语';
  static const appName = 'Mellow';

  // Persona
  static const chooseTeacher = '选择你的 AI 老师';
  static const skip = '跳过';
  static const noPersonas = '暂无可用角色';
  static const personaDetail = '角色详情';
  static const personaUnavailable = '角色信息不可用';
  static const languageStyle = '语言风格';
  static const teachingStyle = '教学风格';
  static const tone = '语气';
  static const traits = '特征';
  static const approach = '方法';
  static const strictness = '严格度';
  static const correctionFreq = '纠错频率';
  static const tryVoice = '试听语音';
  static const playing = '播放中...';
  static const startChat = '开始聊天';

  // Chat
  static const copyText = '复制文本';
  static const favorite = '收藏';
  static const unfavorite = '取消收藏';
  static const delete = '删除';
  static const selectPersona = '选择一个角色开始对话吧~';
  static const selectPersonaBtn = '选择角色';
  static const switchPersona = '切换角色';
  static const close = '关闭';
  static const inputHint = '输入消息...';
  static String chatWith(String name) => '和 $name 说点什么吧~';

  // Learn
  static const learn = '学习';
  static const progress = '进度';
  static const vocabBook = '生词本';
  static const mistakes = '错题';
  static const cefrLevel = 'CEFR 等级';
  static const vocabCount = '词汇量';
  static const learningDays = '学习天数';
  static const weakAreas = '薄弱项';
  static const completeToday = '完成今日任务';
  static const week = '周';
  static const month = '月';
  static const halfYear = '半年';
  static const searchWord = '搜索单词...';
  static const noVocabHint = '在对话中长按单词即可加入生词本';
  static const noMistakesHint = '继续对话，AI 会自动记录你的常见错误';
  static const retry = '重试';
  static const recent = '最近';
  static const alpha = '字母';
  static const noDefinition = '暂无释义';
  static const definitions = '释义';
  static const examples = '例句';
  static const synonyms = '近义词';
  static String wordCount(int count) => '$count 个单词';

  // Profile
  static const myProfile = '我的';
  static const defaultUser = 'Mellow 用户';
  static String learnerLevel(String level) => '$level 英语学习者';
  static const messageCount = '消息数';
  static const checkinCount = '打卡次数';
  static const switchRole = '切换角色';
  static const voiceSettings = '语音设置';
  static const learningGoal = '学习目标 (CEFR)';
  static String currentLevel(String level) => '当前: $level';
  static const darkMode = '深色模式';
  static const logout = '退出登录';
  static const logoutAction = '退出';
  static const about = '关于 Mellow · v0.1.0';
  static const logoutTitle = '退出登录';
  static const logoutConfirm = '确定要退出登录吗？';
  static const cancel = '取消';
  static const selectGoal = '选择学习目标';
  static const underDevelopment = '开发中';

  // Splash
  static const start = '开始';

  // TODO placeholders
  static const todoCefrChart = 'TODO: spending_tracker CEFR 图表';
  static const todoLearnPlan = 'TODO: drink_rewards_list 学习计划';
}
