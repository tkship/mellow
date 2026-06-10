import React from 'react';
import { updateProfile } from '../api/profile';
import { getApiKeys, updateApiKeys, type ApiKeyConfigResponse } from '../api/settings';

interface SettingsViewProps {
  user: { username: string; level: string };
  darkMode: boolean;
  language: string;
  notifications: boolean;
  onUpdateDarkMode: (v: boolean) => void;
  onUpdateLanguage: (v: string) => void;
  onUpdateNotifications: (v: boolean) => void;
  onGoBack: () => void;
  onLogout: () => void;
}

interface ToastMessage {
  text: string;
  type: 'success' | 'error';
}

const AVATAR_COLORS = [
  'bg-blue-500', 'bg-emerald-500', 'bg-violet-500', 'bg-amber-500',
  'bg-rose-500', 'bg-cyan-500', 'bg-fuchsia-500', 'bg-lime-500',
];

function getAvatarColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

export default function SettingsView({
  user,
  darkMode,
  language,
  notifications,
  onUpdateDarkMode,
  onUpdateLanguage,
  onUpdateNotifications,
  onGoBack,
  onLogout,
}: SettingsViewProps) {
  const [showGoalDropdown, setShowGoalDropdown] = React.useState(false);
  const [showLangDropdown, setShowLangDropdown] = React.useState(false);
  const [showKeyConfig, setShowKeyConfig] = React.useState(false);
  const [toast, setToast] = React.useState<ToastMessage | null>(null);

  // API Key 配置状态
  const [keyLoading, setKeyLoading] = React.useState(false);
  const [keySaving, setKeySaving] = React.useState(false);
  const [keyStatus, setKeyStatus] = React.useState<ApiKeyConfigResponse | null>(null);
  const [keyForm, setKeyForm] = React.useState({
    llm_api_key: '',
    llm_base_url: '',
    llm_model: '',
    llm_fast_model: '',
    embed_api_key: '',
    embed_model: '',
  });

  // 展开 API Key 配置时加载当前配置
  React.useEffect(() => {
    if (showKeyConfig && !keyStatus && !keyLoading) {
      setKeyLoading(true);
      getApiKeys()
        .then((data) => {
          setKeyStatus(data);
        })
        .catch(() => {
          showToast('加载配置失败', 'error');
        })
        .finally(() => setKeyLoading(false));
    }
  }, [showKeyConfig]);

  const handleSaveKeys = async () => {
    setKeySaving(true);
    try {
      // 只发送有值的字段（空字符串表示清除）
      const updates: Record<string, string | number> = {};
      if (keyForm.llm_api_key) updates.llm_api_key = keyForm.llm_api_key;
      if (keyForm.llm_base_url) updates.llm_base_url = keyForm.llm_base_url;
      if (keyForm.llm_model) updates.llm_model = keyForm.llm_model;
      if (keyForm.llm_fast_model) updates.llm_fast_model = keyForm.llm_fast_model;
      if (keyForm.embed_api_key) updates.embed_api_key = keyForm.embed_api_key;
      if (keyForm.embed_model) updates.embed_model = keyForm.embed_model;

      const result = await updateApiKeys(updates);
      setKeyStatus(result);
      setKeyForm({ llm_api_key: '', llm_base_url: '', llm_model: '', llm_fast_model: '', embed_api_key: '', embed_model: '' });
      showToast('配置已保存并生效');
    } catch {
      showToast('保存配置失败，请重试', 'error');
    } finally {
      setKeySaving(false);
    }
  };

  const showToast = (text: string, type: 'success' | 'error' = 'success') => {
    setToast({ text, type });
    setTimeout(() => setToast(null), 3000);
  };

  const goalLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
  const languages = ['简体中文', 'English', 'Español', '日本語'];

  const initial = user.username?.charAt(0)?.toUpperCase() || '?';
  const avatarColor = getAvatarColor(user.username);

  const handleCefrChange = async (level: string) => {
    setShowGoalDropdown(false);
    try {
      await updateProfile({ cefr_level: level });
      showToast('目标已更新');
    } catch {
      showToast('更新失败，请重试', 'error');
    }
  };

  return (
    <div className="bg-background text-on-background h-screen max-h-screen flex flex-col items-center overflow-hidden">
      {/* Toast Notification Banner */}
      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 animate-fade-in flex items-center gap-2 px-4 py-2.5 rounded-full shadow-lg border text-xs font-semibold backdrop-blur-md transition-all whitespace-nowrap bg-surface-container-lowest border-primary/10">
          <span className={`w-2 h-2 rounded-full ${toast.type === 'success' ? 'bg-primary animate-ping' : 'bg-error animate-ping'}`}></span>
          <span className={`${toast.type === 'success' ? 'text-primary' : 'text-error'}`}>{toast.text}</span>
        </div>
      )}

      {/* Header and Back navigation */}
      <header className="w-full bg-white border-b border-primary/5 px-6 h-16 flex items-center justify-between shrink-0">
        <button
          onClick={onGoBack}
          className="w-10 h-10 flex items-center justify-center text-on-surface hover:bg-primary-container/10 rounded-full transition-colors cursor-pointer"
        >
          <span className="material-symbols-outlined font-bold">arrow_back</span>
        </button>
        <h1 className="font-display font-medium text-headline-sm text-center">Settings & Preferences</h1>
        <div className="w-10"></div>
      </header>

      {/* Main Content */}
      <main className="w-full max-w-3xl px-4 py-8 md:px-8 space-y-6 flex-grow overflow-y-auto pb-12">
        {/* Profile Section Header */}
        <div className="flex items-center gap-4 bg-white p-5 rounded-2xl shadow-sm border border-primary/5 hover:shadow-md transition-shadow duration-300">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-sm ${avatarColor}`}>
            {initial}
          </div>
          <div>
            <h2 className="font-display font-bold text-headline-sm text-on-surface">{user.username}</h2>
            <p className="text-xs text-on-surface-variant font-sans">
              Manage your Mellow AI account preferences & levels.
            </p>
          </div>
        </div>

        {/* Settings List */}
        <div className="flex flex-col gap-1.5 bg-white rounded-2xl p-4 shadow-sm border border-outline-variant/10">
          {/* Item: Notifications */}
          <div className="w-full flex items-center justify-between py-2.5">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-primary">
                <span className="material-symbols-outlined text-[20px]">notifications</span>
              </div>
              <span className="text-[15px] font-sans text-on-surface font-medium">消息通知 (Notifications)</span>
            </div>
            {/* Toggle Switch */}
            <button
              onClick={() => {
                onUpdateNotifications(!notifications);
                showToast(notifications ? '通知已关闭' : '通知已开启');
              }}
              className={`w-12 h-6 rounded-full relative flex items-center px-1 cursor-pointer transition-colors duration-300 focus:outline-none ${
                notifications ? 'bg-primary-container' : 'bg-outline-variant'
              }`}
            >
              <div
                className={`w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform duration-300 ${
                  notifications ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* Divider */}
          <div className="h-px w-full bg-primary/5 ml-14"></div>

          {/* Item: Learning Goals dropdown */}
          <div className="py-2.5">
            <div className="w-full flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[20px]">flag</span>
                </div>
                <span className="text-[15px] font-sans text-on-surface font-medium">学习目标 (Target Goal)</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowGoalDropdown(!showGoalDropdown)}
                  className="px-3 py-1 bg-surface-container hover:bg-primary-container/20 transition-colors text-xs font-bold font-sans text-on-surface-variant rounded-md flex items-center gap-1 cursor-pointer"
                >
                  <span>{user.level}</span>
                  <span className="material-symbols-outlined text-[14px]">expand_more</span>
                </button>
              </div>
            </div>

            {/* Dropdown overlay panel */}
            {showGoalDropdown && (
              <div className="ml-14 mt-3 grid grid-cols-6 gap-2 bg-surface-container-low p-2 rounded-xl border border-primary/5 max-w-sm animate-fade-in">
                {goalLevels.map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => handleCefrChange(lvl)}
                    className={`p-2 rounded-lg text-xs font-bold font-sans hover:bg-primary hover:text-white transition-colors cursor-pointer ${
                      user.level === lvl ? 'bg-primary text-white' : 'bg-white text-on-surface-variant/80'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="h-px w-full bg-primary/5 ml-14"></div>

          {/* Item: Language Preferences dropdown */}
          <div className="py-2.5">
            <div className="w-full flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[20px]">language</span>
                </div>
                <span className="text-[15px] font-sans text-on-surface font-medium">语言偏好 (Interface Language)</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowLangDropdown(!showLangDropdown)}
                  className="px-3 py-1 bg-surface-container hover:bg-primary-container/20 transition-colors text-xs font-sans text-on-surface-variant rounded-md flex items-center gap-1 cursor-pointer"
                >
                  <span>{language}</span>
                  <span className="material-symbols-outlined text-[14px]">expand_more</span>
                </button>
              </div>
            </div>

            {/* Dropdown lang selector panel */}
            {showLangDropdown && (
              <div className="ml-14 mt-3 flex gap-2 flex-wrap bg-surface-container-low p-2 rounded-xl border border-primary/5 max-w-sm animate-fade-in">
                {languages.map((lang) => (
                  <button
                    key={lang}
                    onClick={() => {
                      onUpdateLanguage(lang);
                      setShowLangDropdown(false);
                      showToast(`已切换界面语言为：${lang}`);
                    }}
                    className={`px-3 py-1.5 rounded-lg text-xs hover:bg-primary hover:text-white transition-colors cursor-pointer ${
                      language === lang ? 'bg-primary text-white' : 'bg-white text-on-surface-variant'
                    }`}
                  >
                    {lang}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="h-px w-full bg-primary/5 ml-14"></div>

          {/* Item: Theme (Dark Mode) */}
          <div className="w-full flex items-center justify-between py-2.5">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-primary">
                <span className="material-symbols-outlined text-[20px]">dark_mode</span>
              </div>
              <span className="text-[15px] font-sans text-on-surface font-medium">眼保主题 (Dark Calm Mode)</span>
            </div>
            {/* Toggle Switch */}
            <button
              onClick={() => {
                onUpdateDarkMode(!darkMode);
                showToast(darkMode ? '已切换至亮色模式' : '已切换至深色夜间模式');
              }}
              className={`w-12 h-6 rounded-full relative flex items-center px-1 cursor-pointer transition-colors duration-300 focus:outline-none ${
                darkMode ? 'bg-primary-container' : 'bg-outline-variant'
              }`}
            >
              <div
                className={`w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform duration-300 ${
                  darkMode ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* Divider */}
          <div className="h-px w-full bg-primary/5 ml-14"></div>

          {/* Item: Account Security */}
          <button
            onClick={() => alert('安全检查通过')}
            className="w-full flex items-center justify-between py-2.5 group cursor-pointer text-left"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-primary group-hover:bg-primary-container/20 transition-colors">
                <span className="material-symbols-outlined text-[20px]">security</span>
              </div>
              <span className="text-[15px] font-sans text-on-surface font-medium">账号安全 (Account Security)</span>
            </div>
            <span className="material-symbols-outlined text-on-surface-variant/50 group-hover:text-primary transition-colors text-[20px]">
              chevron_right
            </span>
          </button>

          {/* Divider */}
          <div className="h-px w-full bg-primary/5 ml-14"></div>

          {/* Item: About */}
          <button
            onClick={() => alert('Mellow AI v2.0.0 • 极简口语向导\n致力于打造让心灵和外语沟通瞬间沉浸的极简 AI 向导。')}
            className="w-full flex items-center justify-between py-2.5 group cursor-pointer text-left"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-primary group-hover:bg-primary-container/20 transition-colors">
                <span className="material-symbols-outlined text-[20px]">info</span>
              </div>
              <span className="text-[15px] font-sans text-on-surface font-medium">关于 Mellow (About Mellow)</span>
            </div>
            <span className="material-symbols-outlined text-on-surface-variant/50 group-hover:text-primary transition-colors text-[20px]">
              chevron_right
            </span>
          </button>

          {/* Divider */}
          <div className="h-px w-full bg-primary/5 ml-14"></div>

          {/* Item: API Key Configuration */}
          <button
            onClick={() => setShowKeyConfig(!showKeyConfig)}
            className="w-full flex items-center justify-between py-2.5 group cursor-pointer text-left"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-primary group-hover:bg-primary-container/20 transition-colors">
                <span className="material-symbols-outlined text-[20px]">key</span>
              </div>
              <span className="text-[15px] font-sans text-on-surface font-medium">API 密钥配置 (API Keys)</span>
            </div>
            <span className={`material-symbols-outlined text-on-surface-variant/50 group-hover:text-primary transition-all text-[20px] ${showKeyConfig ? 'rotate-90' : ''}`}>
              chevron_right
            </span>
          </button>

          {/* API Key Config Panel */}
          {showKeyConfig && (
            <div className="ml-14 mt-2 mb-2 space-y-3 animate-fade-in">
              {keyLoading ? (
                <div className="flex items-center gap-2 text-xs text-on-surface-variant py-2">
                  <span className="material-symbols-outlined text-[16px] animate-spin">progress_activity</span>
                  加载中...
                </div>
              ) : (
                <>
                  <div>
                    <label className="block text-xs text-on-surface-variant font-sans mb-1">LLM API Key</label>
                    <input
                      type="password"
                      value={keyForm.llm_api_key}
                      onChange={(e) => setKeyForm({ ...keyForm, llm_api_key: e.target.value })}
                      placeholder={keyStatus?.llm_api_key || '未配置'}
                      className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline-variant/20 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary font-sans"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-on-surface-variant font-sans mb-1">LLM Base URL</label>
                    <input
                      type="text"
                      value={keyForm.llm_base_url}
                      onChange={(e) => setKeyForm({ ...keyForm, llm_base_url: e.target.value })}
                      placeholder={keyStatus?.llm_base_url || 'https://api.openai.com/v1'}
                      className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline-variant/20 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary font-sans"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-on-surface-variant font-sans mb-1">LLM Model</label>
                    <input
                      type="text"
                      value={keyForm.llm_model}
                      onChange={(e) => setKeyForm({ ...keyForm, llm_model: e.target.value })}
                      placeholder={keyStatus?.llm_model || 'gpt-4o'}
                      className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline-variant/20 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary font-sans"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-on-surface-variant font-sans mb-1">Embedding API Key</label>
                    <input
                      type="password"
                      value={keyForm.embed_api_key}
                      onChange={(e) => setKeyForm({ ...keyForm, embed_api_key: e.target.value })}
                      placeholder={keyStatus?.embed_api_key || '未配置'}
                      className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline-variant/20 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary font-sans"
                    />
                  </div>
                  <button
                    onClick={handleSaveKeys}
                    disabled={keySaving}
                    className="w-full py-2 bg-primary text-white rounded-lg text-sm font-sans font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 cursor-pointer"
                  >
                    {keySaving ? '保存中...' : '保存配置'}
                  </button>
                  <p className="text-[10px] text-on-surface-variant/60 font-sans">
                    密钥仅保存在本机，不会上传至第三方。留空表示使用服务端默认值。
                  </p>
                </>
              )}
            </div>
          )}

          {/* Divider */}
          <div className="h-px w-full bg-primary/5 ml-14"></div>

          {/* Exit Logout item in list directly */}
          <button
            onClick={onLogout}
            className="w-full flex items-center justify-between py-2.5 group cursor-pointer text-left"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-error/10 flex items-center justify-center text-error group-hover:bg-error/20 transition-colors">
                <span className="material-symbols-outlined text-[20px]">logout</span>
              </div>
              <span className="text-[15px] font-sans text-error font-medium">退出登录 (Log Out)</span>
            </div>
            <span className="material-symbols-outlined text-on-surface-variant/50 group-hover:text-error transition-colors text-[20px]">
              chevron_right
            </span>
          </button>
        </div>
      </main>
    </div>
  );
}
