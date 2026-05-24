import React from 'react';
import { UserState, CEFRGoal } from '../types';

interface SettingsViewProps {
  user: UserState;
  onUpdateUser: (updatedFields: Partial<UserState>) => void;
  onGoBack: () => void;
  onLogout: () => void;
}

export default function SettingsView({
  user,
  onUpdateUser,
  onGoBack,
  onLogout,
}: SettingsViewProps) {
  const [showGoalDropdown, setShowGoalDropdown] = React.useState(false);
  const [showLangDropdown, setShowLangDropdown] = React.useState(false);

  const goalLevels: CEFRGoal[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
  const languages = ['简体中文', 'English', 'Español', '日本語'];

  return (
    <div className="bg-background text-on-background h-screen max-h-screen flex flex-col items-center overflow-hidden">
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
          <img
            alt="User Avatar"
            className="w-16 h-16 rounded-full object-cover shadow-sm"
            src={user.avatar}
            referrerPolicy="no-referrer"
          />
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
              onClick={() => onUpdateUser({ notifications: !user.notifications })}
              className={`w-12 h-6 rounded-full relative flex items-center px-1 cursor-pointer transition-colors duration-300 focus:outline-none ${
                user.notifications ? 'bg-primary-container' : 'bg-outline-variant'
              }`}
            >
              <div
                className={`w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform duration-300 ${
                  user.notifications ? 'translate-x-6' : 'translate-x-0'
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
                    onClick={() => {
                      onUpdateUser({ level: lvl });
                      setShowGoalDropdown(false);
                    }}
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
                  <span>{user.language}</span>
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
                      onUpdateUser({ language: lang });
                      setShowLangDropdown(false);
                    }}
                    className={`px-3 py-1.5 rounded-lg text-xs hover:bg-primary hover:text-white transition-colors cursor-pointer ${
                      user.language === lang ? 'bg-primary text-white' : 'bg-white text-on-surface-variant'
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

          {/* Item: Theme (Simulated) */}
          <div className="w-full flex items-center justify-between py-2.5">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-primary">
                <span className="material-symbols-outlined text-[20px]">dark_mode</span>
              </div>
              <span className="text-[15px] font-sans text-on-surface font-medium">眼保主题 (Dark Calm Mode)</span>
            </div>
            {/* Toggle Switch */}
            <button
              onClick={() => alert('已自动为您配置专属 Mint Lake 绿色眼保调色系统，静雅绝伦。')}
              className="w-12 h-6 bg-primary-container rounded-full relative flex items-center px-1 cursor-pointer focus:outline-none"
            >
              <div className="w-4 h-4 bg-white rounded-full shadow-sm transform translate-x-6"></div>
            </button>
          </div>

          {/* Divider */}
          <div className="h-px w-full bg-primary/5 ml-14"></div>

          {/* Item: Account Security */}
          <button
            onClick={() => alert(`您当前登录用户名: ${user.username}\n密码状态: 已进行SSL高强度双向宁静加密，绝不丢失。`)}
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
            onClick={() => alert('Mellow AI v8.2.0 • 聆天核儳\n致力于打造能让心灵和外语沟通瞬间静止的极简 AI 向导。')}
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
