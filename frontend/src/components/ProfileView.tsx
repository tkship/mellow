import React, { useState } from 'react';
import { UserResponse } from '../api/auth';
import { UserProfile, PersonaDisplay, CEFRLevel } from '../types';

// ===== Props =====

interface ProfileViewProps {
  user: UserResponse | null;
  profile: UserProfile | null;
  personas: PersonaDisplay[];
  currentPersonaId: string;
  onSelectPersona: (id: string) => void;
  onOpenVocabulary: () => void;
  onOpenKnowledge: () => void;
  onOpenMistakes: () => void;
  onOpenMemory: () => void;
  onOpenSettings: () => void;
  onLogout: () => void;
  darkMode: boolean;
  onUpdateDarkMode: (v: boolean) => void;
  language: string;
  onUpdateLanguage: (v: string) => void;
  notifications: boolean;
  onUpdateNotifications: (v: boolean) => void;
}

// ===== Helpers =====

const AVATAR_COLORS = [
  '#4F46E5', '#7C3AED', '#2563EB', '#0891B2',
  '#0D9488', '#059669', '#65A30D', '#CA8A04',
  '#D97706', '#DC2626', '#DB2777', '#9333EA',
];

function getAvatarColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

function getInitial(name: string): string {
  return name.charAt(0).toUpperCase();
}

const CEFR_LABELS: Record<CEFRLevel, string> = {
  'A0': 'A0 入门',
  'A1': 'A1 基础',
  'A2': 'A2 初级',
  'B1': 'B1 中级',
  'B2': 'B2 中高级',
  'C1': 'C1 高级',
  'C2': 'C2 精通',
};

// ===== Toast =====

interface ToastMessage {
  text: string;
  type: 'success' | 'error';
}

// ===== Component =====

export default function ProfileView({
  user,
  profile,
  personas,
  currentPersonaId,
  onSelectPersona,
  onOpenVocabulary,
  onOpenKnowledge,
  onOpenMistakes,
  onOpenMemory,
  onOpenSettings,
  onLogout,
  darkMode,
  onUpdateDarkMode,
  language,
  onUpdateLanguage,
  notifications,
  onUpdateNotifications,
}: ProfileViewProps) {
  const [toast, setToast] = useState<ToastMessage | null>(null);
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
  const languages = ['简体中文', 'English', 'Español', '日本語'];

  const currentPersona = personas.find((p) => p.id === currentPersonaId);

  const showToast = (text: string, type: 'success' | 'error' = 'success') => {
    setToast({ text, type });
    setTimeout(() => {
      setToast(null);
    }, 3000);
  };

  // ===== Skeleton while profile loads =====
  if (profile === null) {
    return (
      <div className="bg-surface text-on-background font-sans antialiased h-full overflow-y-auto pb-6 selection:bg-primary-container/30">
        <main className="max-w-xl mx-auto px-4 py-6">
          <div className="space-y-6 animate-pulse">
            {/* Avatar skeleton */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-surface-container" />
              <div className="space-y-2">
                <div className="h-5 w-28 bg-surface-container rounded-lg" />
                <div className="h-3 w-20 bg-surface-container rounded-md" />
              </div>
            </div>
            {/* Stats skeleton */}
            <div className="grid grid-cols-3 gap-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-surface-container-lowest rounded-2xl p-4 border border-primary/5">
                  <div className="h-6 w-10 bg-surface-container rounded-md mx-auto mb-2" />
                  <div className="h-3 w-12 bg-surface-container rounded-md mx-auto" />
                </div>
              ))}
            </div>
            {/* Menu items skeleton */}
            <div className="bg-surface-container-lowest rounded-3xl border border-primary/5 p-2 space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center gap-3.5 p-3.5">
                  <div className="w-9 h-9 rounded-xl bg-surface-container shrink-0" />
                  <div className="flex-1 space-y-1.5">
                    <div className="h-4 w-24 bg-surface-container rounded-md" />
                    <div className="h-2.5 w-36 bg-surface-container rounded-md" />
                  </div>
                </div>
              ))}
            </div>
            <div className="text-center text-xs text-outline py-6 font-sans">加载中...</div>
          </div>
        </main>
      </div>
    );
  }

  // ===== Full profile view =====
  return (
    <div className="bg-surface text-on-background font-sans antialiased h-full overflow-y-auto pb-6 selection:bg-primary-container/30">
      {/* Toast Notification Banner */}
      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 animate-fade-in flex items-center gap-2 px-4 py-2.5 rounded-full shadow-lg border text-xs font-semibold backdrop-blur-md transition-all whitespace-nowrap bg-surface-container-lowest border-primary/10">
          <span
            className={`w-2 h-2 rounded-full ${
              toast.type === 'success' ? 'bg-primary animate-ping' : 'bg-error animate-ping'
            }`}
          />
          <span className={toast.type === 'success' ? 'text-primary' : 'text-error'}>
            {toast.text}
          </span>
        </div>
      )}

      <main className="max-w-xl mx-auto px-4 py-6">
        <div className="space-y-6">
          {/* ========== Top: User Avatar + Info ========== */}
          <section className="flex items-center gap-4">
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center text-white text-xl font-bold shadow-md shrink-0"
              style={{ backgroundColor: user ? getAvatarColor(user.username) : '#6B7280' }}
            >
              {user ? getInitial(user.username) : '?'}
            </div>
            <div>
              <h1 className="text-lg font-bold text-on-background font-display">
                {user?.username ?? '未知用户'}
              </h1>
              <p className="text-xs text-outline mt-0.5 font-sans">语言学习者</p>
            </div>
          </section>

          {/* ========== Stats Row ========== */}
          <section className="grid grid-cols-3 gap-3">
            {/* Vocab Count */}
            <div className="bg-surface-container-lowest rounded-2xl border border-primary/5 p-4 text-center">
              <span className="material-symbols-outlined text-primary text-[22px] block mb-1">
                menu_book
              </span>
              <div className="text-lg font-bold text-on-background">
                {profile.vocabularySize.toLocaleString()}
              </div>
              <div className="text-[10px] text-outline mt-0.5 font-sans">词汇量</div>
            </div>

            {/* Streak */}
            <div className="bg-surface-container-lowest rounded-2xl border border-primary/5 p-4 text-center">
              <span className="material-symbols-outlined text-primary text-[22px] block mb-1">
                local_fire_department
              </span>
              <div className="text-lg font-bold text-on-background">{profile.streak}</div>
              <div className="text-[10px] text-outline mt-0.5 font-sans">连续天</div>
            </div>

            {/* CEFR Level */}
            <div className="bg-surface-container-lowest rounded-2xl border border-primary/5 p-4 text-center">
              <span className="material-symbols-outlined text-primary text-[22px] block mb-1">
                trending_up
              </span>
              <div className="text-lg font-bold text-on-background">{profile.cefrLevel}</div>
              <div className="text-[10px] text-outline mt-0.5 font-sans">
                {CEFR_LABELS[profile.cefrLevel] ?? profile.cefrLevel}
              </div>
            </div>
          </section>

          {/* ========== Persona Card ========== */}
          <section className="bg-surface-container-lowest rounded-3xl border border-primary/5 p-4 shadow-[0_2px_12px_rgba(0,0,0,0.015),0_1px_3px_rgba(0,0,0,0.03)]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                  <span className="material-symbols-outlined text-[19px]">person</span>
                </div>
                <div>
                  <div className="text-sm text-on-background font-semibold">
                    {currentPersona?.name ?? '未选择角色'}
                  </div>
                  <div className="text-[10px] text-outline mt-0.5 font-sans">
                    {currentPersona?.tagline ?? '点击切换学习伙伴'}
                  </div>
                </div>
              </div>
              <button
                onClick={() => {
                  if (personas.length > 0) {
                    const currentIdx = personas.findIndex((p) => p.id === currentPersonaId);
                    const nextIdx = (currentIdx + 1) % personas.length;
                    onSelectPersona(personas[nextIdx].id);
                    showToast(`已切换至：${personas[nextIdx].name}`);
                  }
                }}
                className="bg-surface-container hover:bg-primary-container/20 transition-colors text-xs font-sans text-primary font-bold rounded-lg px-3 py-1.5 flex items-center gap-1 cursor-pointer outline-none border-none shrink-0"
              >
                <span>切换角色</span>
                <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
              </button>
            </div>
          </section>

          {/* ========== Menu Items ========== */}
          <section className="space-y-4">
            <div className="bg-surface-container-lowest rounded-3xl shadow-[0_2px_12px_rgba(0,0,0,0.015),0_1px_3px_rgba(0,0,0,0.03)] overflow-hidden border border-primary/5 p-2">
              {/* 生词本 */}
              <button
                onClick={onOpenVocabulary}
                className="w-full flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors text-left cursor-pointer"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-[19px]">menu_book</span>
                  </div>
                  <div>
                    <div className="text-sm text-on-background font-semibold">生词本</div>
                    <div className="text-[10px] text-outline mt-0.5 font-sans">
                      管理收藏的生词与短语
                    </div>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline text-[18px]">chevron_right</span>
              </button>

              <div className="h-px bg-primary/5 mx-3.5" />

              {/* 知识库查词 */}
              <button
                onClick={onOpenKnowledge}
                className="w-full flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors text-left cursor-pointer"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-[19px]">search</span>
                  </div>
                  <div>
                    <div className="text-sm text-on-background font-semibold">知识库查词</div>
                    <div className="text-[10px] text-outline mt-0.5 font-sans">
                      查询单词释义、例句与用法
                    </div>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline text-[18px]">chevron_right</span>
              </button>

              <div className="h-px bg-primary/5 mx-3.5" />

              {/* 错题本 */}
              <button
                onClick={onOpenMistakes}
                className="w-full flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors text-left cursor-pointer"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-[19px]">assignment</span>
                  </div>
                  <div>
                    <div className="text-sm text-on-background font-semibold">错题本</div>
                    <div className="text-[10px] text-outline mt-0.5 font-sans">
                      回顾练习中的常见错误
                    </div>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline text-[18px]">chevron_right</span>
              </button>

              <div className="h-px bg-primary/5 mx-3.5" />

              {/* 角色记忆 */}
              <button
                onClick={onOpenMemory}
                className="w-full flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors text-left cursor-pointer"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-[19px]">psychology</span>
                  </div>
                  <div>
                    <div className="text-sm text-on-background font-semibold">角色记忆</div>
                    <div className="text-[10px] text-outline mt-0.5 font-sans">
                      查看角色对你的了解与互动历史
                    </div>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline text-[18px]">chevron_right</span>
              </button>

              <div className="h-px bg-primary/5 mx-3.5" />

              {/* 设置 */}
              <button
                onClick={onOpenSettings}
                className="w-full flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors text-left cursor-pointer"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-[19px]">settings</span>
                  </div>
                  <div>
                    <div className="text-sm text-on-background font-semibold">设置</div>
                    <div className="text-[10px] text-outline mt-0.5 font-sans">
                      账号安全与应用偏好设置
                    </div>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline text-[18px]">chevron_right</span>
              </button>

              <div className="h-px bg-primary/5 mx-3.5" />

              {/* 通知 Toggle */}
              <div className="flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors">
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-[19px]">notifications</span>
                  </div>
                  <div>
                    <div className="text-sm text-on-background font-semibold">消息通知 (Notifications)</div>
                    <div className="text-[10px] text-outline mt-0.5 font-sans">开启每日口语及复习提醒</div>
                  </div>
                </div>
                <button
                  onClick={() => onUpdateNotifications(!notifications)}
                  className={`w-11 h-5.5 rounded-full relative flex items-center px-0.5 cursor-pointer transition-colors duration-300 focus:outline-none ${
                    notifications ? 'bg-primary' : 'bg-outline-variant'
                  }`}
                >
                  <div
                    className={`w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform duration-300 ${
                      notifications ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>

              <div className="h-px bg-primary/5 mx-3.5" />

              {/* 界面语言 */}
              <div className="flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors relative">
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-[19px]">language</span>
                  </div>
                  <div>
                    <div className="text-sm text-on-background font-semibold">界面语言 (UI Language)</div>
                    <div className="text-[10px] text-outline mt-0.5 font-sans">设置系统的操作指导语言</div>
                  </div>
                </div>
                <div className="relative">
                  <button
                    onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
                    className="bg-surface-container hover:bg-primary-container/20 transition-colors text-xs font-sans text-primary font-bold rounded-lg px-3 py-1.5 flex items-center gap-1 cursor-pointer outline-none border-none"
                  >
                    <span>{language}</span>
                    <span className="material-symbols-outlined text-[14px]">
                      {showLanguageDropdown ? 'expand_less' : 'expand_more'}
                    </span>
                  </button>

                  {showLanguageDropdown && (
                    <>
                      <div
                        className="fixed inset-0 z-40 bg-transparent"
                        onClick={() => setShowLanguageDropdown(false)}
                      />
                      <div className="absolute right-0 mt-1.5 w-32 bg-surface-container-lowest border border-primary/10 shadow-xl rounded-2xl py-1.5 z-50 animate-fade-in">
                        {languages.map((lang) => (
                          <button
                            key={lang}
                            onClick={() => {
                              onUpdateLanguage(lang);
                              setShowLanguageDropdown(false);
                              showToast(`已切换界面语言为：${lang}`);
                            }}
                            className={`w-full text-left px-4 py-2 text-xs hover:bg-primary/5 transition-colors cursor-pointer block ${
                              language === lang ? 'text-primary font-bold bg-primary/5' : 'text-on-surface'
                            }`}
                          >
                            {lang}
                          </button>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div className="h-px bg-primary/5 mx-3.5" />

              {/* 夜间模式 Toggle */}
              <div className="flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors">
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-[19px]">dark_mode</span>
                  </div>
                  <div>
                    <div className="text-sm text-on-background font-semibold">夜间模式 (Night Mode)</div>
                    <div className="text-[10px] text-outline mt-0.5 font-sans">开启舒适深色界面，缓解眼部疲劳</div>
                  </div>
                </div>
                <button
                  onClick={() => {
                    const newMode = !darkMode;
                    onUpdateDarkMode(newMode);
                    showToast(newMode ? '已切换至深色夜间模式' : '已切换至亮色模式');
                  }}
                  className={`w-11 h-5.5 rounded-full relative flex items-center px-0.5 cursor-pointer transition-colors duration-300 focus:outline-none ${
                    darkMode ? 'bg-primary' : 'bg-outline-variant'
                  }`}
                >
                  <div
                    className={`w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform duration-300 ${
                      darkMode ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>

              <div className="h-px bg-primary/5 mx-3.5" />

              {/* 关于 Mellow */}
              <button
                onClick={() =>
                  alert(
                    `Mellow AI v2.0\n\n以极简自然美学为灵感，搭载多款拟人情境口语向导，带给您没有时间压迫、毫无焦虑的无门槛随行口语教学体验。`
                  )
                }
                className="w-full flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors text-left cursor-pointer"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-[19px]">info</span>
                  </div>
                  <div>
                    <div className="text-sm text-on-background font-semibold">关于 Mellow (About)</div>
                    <div className="text-[10px] text-outline mt-0.5 font-sans">版本 v2.0 • 软件版权与隐私条款</div>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline text-[18px]">chevron_right</span>
              </button>
            </div>

            {/* ========== Logout ========== */}
            <div className="pt-2 px-1">
              <button
                onClick={onLogout}
                className="w-full py-3.5 border border-error/15 bg-error/5 hover:bg-error/10 text-error font-semibold rounded-2xl text-sm active:scale-[0.98] transition-all text-center flex items-center justify-center gap-1.5 cursor-pointer shadow-sm"
              >
                <span className="material-symbols-outlined text-[16px]">logout</span>
                <span>退出登录 (Log Out)</span>
              </button>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
