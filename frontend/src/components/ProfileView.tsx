import React, { useState } from 'react';
import { UserState } from '../types';

interface ProfileViewProps {
  user: UserState;
  onUpdateUser: (updatedFields: Partial<UserState>) => void;
  onLogout: () => void;
  currentSection: ProfileSection;
  onSectionChange: (section: ProfileSection) => void;
}

type ProfileSection = 'main' | 'security';

interface ToastMessage {
  text: string;
  type: 'success' | 'error';
}

export default function ProfileView({
  user,
  onUpdateUser,
  onLogout,
  currentSection,
  onSectionChange,
}: ProfileViewProps) {
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [tempUsername, setTempUsername] = useState(user.username);
  const [tempBio, setTempBio] = useState(user.bio);
  
  // Toast notifications state
  const [toast, setToast] = useState<ToastMessage | null>(null);

  // Dropdown UI Language
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
  const languages = ['简体中文', 'English', 'Español', '日本語'];

  // Security forms state
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [isEditingPhone, setIsEditingPhone] = useState(false);
  const [isEditingEmail, setIsEditingEmail] = useState(false);

  // Security inputs
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [phoneNumber, setPhoneNumber] = useState('138 0000 8888');
  const [tempPhone, setTempPhone] = useState(phoneNumber);
  
  const [emailAddress, setEmailAddress] = useState(user.email);
  const [tempEmail, setTempEmail] = useState(emailAddress);

  // Trigger beautifully styled Toast
  const showToast = (text: string, type: 'success' | 'error' = 'success') => {
    setToast({ text, type });
    setTimeout(() => {
      setToast(null);
    }, 3000);
  };

  const handleSaveProfile = () => {
    if (!tempUsername.trim()) {
      showToast('用户名不能为空', 'error');
      return;
    }
    onUpdateUser({
      username: tempUsername,
      bio: tempBio,
    });
    setIsEditingProfile(false);
    showToast('个人资料已成功保存！');
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!oldPassword) {
      showToast('请输入原密码', 'error');
      return;
    }
    if (newPassword.length < 6) {
      showToast('新密码长度不能少于 6 位', 'error');
      return;
    }
    if (newPassword !== confirmPassword) {
      showToast('两次新密码输入不一致', 'error');
      return;
    }
    showToast('密码修改成功！已启用强加密保护。');
    setIsChangingPassword(false);
    setOldPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  const handlePhoneSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const phonePattern = /^1[3-9]\d{9}$/;
    const rawPhone = tempPhone.replace(/\s+/g, '');
    if (!phonePattern.test(rawPhone)) {
      showToast('请输入有效的 11 位手机号码', 'error');
      return;
    }
    setPhoneNumber(tempPhone);
    setIsEditingPhone(false);
    showToast('手机号码已绑定并验证成功！');
  };

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(tempEmail)) {
      showToast('请输入有效的电子邮箱地址', 'error');
      return;
    }
    setEmailAddress(tempEmail);
    onUpdateUser({ email: tempEmail });
    setIsEditingEmail(false);
    showToast('邮箱绑定已成功更新！');
  };

  return (
    <div className="bg-surface text-on-background font-sans antialiased h-full overflow-y-auto pb-6 selection:bg-primary-container/30">
      
      {/* Toast Notification Banner Floating */}
      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 animate-fade-in flex items-center gap-2 px-4 py-2.5 rounded-full shadow-lg border text-xs font-semibold backdrop-blur-md transition-all whitespace-nowrap bg-surface-container-lowest border-primary/10">
          <span className={`w-2 h-2 rounded-full ${toast.type === 'success' ? 'bg-primary animate-ping' : 'bg-error animate-ping'}`}></span>
          <span className={`${toast.type === 'success' ? 'text-primary' : 'text-error'}`}>{toast.text}</span>
        </div>
      )}

      <main className="max-w-xl mx-auto px-4 py-6">
        {currentSection === 'main' ? (
          <div className="space-y-6">

            {/* Unified Interactive Settings Options */}
            <section className="space-y-4">
              <div className="bg-surface-container-lowest rounded-3xl shadow-[0_2px_12px_rgba(0,0,0,0.015),0_1px_3px_rgba(0,0,0,0.03)] overflow-hidden border border-primary/5 p-2">
                
                {/* Setting Item: Notifications */}
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
                    onClick={() => onUpdateUser({ notifications: !user.notifications })}
                    className={`w-11 h-5.5 rounded-full relative flex items-center px-0.5 cursor-pointer transition-colors duration-300 focus:outline-none ${
                      user.notifications ? 'bg-primary' : 'bg-outline-variant'
                    }`}
                  >
                    <div
                      className={`w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform duration-300 ${
                        user.notifications ? 'translate-x-6' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>

                {/* Separator */}
                <div className="h-px bg-primary/5 mx-3.5"></div>

                {/* Setting Item: UI Language Preference */}
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
                      <span>{user.language}</span>
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
                                onUpdateUser({ language: lang });
                                setShowLanguageDropdown(false);
                                showToast(`已切换界面语言为：${lang}`);
                              }}
                              className={`w-full text-left px-4 py-2 text-xs hover:bg-primary/5 transition-colors cursor-pointer block ${
                                user.language === lang ? 'text-primary font-bold bg-primary/5' : 'text-on-surface'
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

                {/* Separator */}
                <div className="h-px bg-primary/5 mx-3.5"></div>

                {/* Setting Item: Dark Mode Toggle */}
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
                      const newMode = !user.darkMode;
                      onUpdateUser({ darkMode: newMode });
                      showToast(newMode ? '已切换至深色夜间模式' : '已切换至亮色模式');
                    }}
                    className={`w-11 h-5.5 rounded-full relative flex items-center px-0.5 cursor-pointer transition-colors duration-300 focus:outline-none ${
                      user.darkMode ? 'bg-primary' : 'bg-outline-variant'
                    }`}
                  >
                    <div
                      className={`w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform duration-300 ${
                        user.darkMode ? 'translate-x-6' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>

                {/* Separator */}
                <div className="h-px bg-primary/5 mx-3.5"></div>

                {/* Setting Item: Account & Encryption Security PAGE TRANSITION */}
                <button
                  onClick={() => {
                    onSectionChange('security');
                    setIsChangingPassword(false);
                    setIsEditingPhone(false);
                    setIsEditingEmail(false);
                  }}
                  className="w-full flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors text-left cursor-pointer"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                      <span className="material-symbols-outlined text-[19px]">security</span>
                    </div>
                    <div>
                      <div className="text-sm text-on-background font-semibold">账号与安全 (Security)</div>
                      <div className="text-[10px] text-outline mt-0.5 font-sans">修改登录密码等敏感设置</div>
                    </div>
                  </div>
                  <span className="material-symbols-outlined text-outline text-[18px]">chevron_right</span>
                </button>

                {/* Separator */}
                <div className="h-px bg-primary/5 mx-3.5"></div>

                {/* Setting Item: About Mellow */}
                <button
                  onClick={() => alert(`Mellow AI English v8.2.0\n\n以极简自然美学为灵感，搭载多款拟人情境口语向导，带给您没有时间压迫、毫无焦虑的无门槛随行口语教学体验。`)}
                  className="w-full flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-colors text-left cursor-pointer"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                      <span className="material-symbols-outlined text-[19px]">info</span>
                    </div>
                    <div>
                      <div className="text-sm text-on-background font-semibold">关于 Mellow (About)</div>
                      <div className="text-[10px] text-outline mt-0.5 font-sans">版本 v8.2.0 • 软件版权与隐私条款</div>
                    </div>
                  </div>
                  <span className="material-symbols-outlined text-outline text-[18px]">chevron_right</span>
                </button>
                
              </div>

              {/* Log Out CTA */}
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
        ) : (
          /* =========================================
             ACCOUNT & SECURITY SUBPAGE VIEW
             ========================================= */
          <div className="space-y-6 animate-fade-in">
            {/* Header / Subpage Back Button */}
            <div className="flex items-center justify-between pb-2 border-b border-primary/5">
              <button
                onClick={() => onSectionChange('main')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-surface-container/75 transition-all text-sm text-primary font-semibold cursor-pointer"
              >
                <span className="material-symbols-outlined text-[18px]">arrow_back</span>
                <span>返回资料</span>
              </button>
              <h2 className="text-base font-bold text-on-background font-display pr-4">账号与安全 (Security)</h2>
              <div className="w-8"></div> {/* dummy to align */}
            </div>

            {/* Information Card */}
            <div className="p-4 bg-primary/5 border border-primary/10 rounded-2xl">
              <div className="flex gap-3">
                <span className="material-symbols-outlined text-primary text-[20px] shrink-0 mt-0.5">verified_user</span>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  您的数据传输已启用 256 位 SSL 强加密通道保护。在此安全中心中，您可以修改您的登录保护密码。
                </p>
              </div>
            </div>

            {/* Interactive Forms & Operations lists */}
            <div className="bg-surface-container-lowest rounded-3xl border border-primary/5 p-2 shadow-sm space-y-1">
              
              {/* Op Row 1: Change Password */}
              <div className="p-1">
                <div 
                  onClick={() => {
                    setIsChangingPassword(!isChangingPassword);
                  }}
                  className="flex items-center justify-between p-3.5 hover:bg-surface-container/30 rounded-2xl transition-all cursor-pointer"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                      <span className="material-symbols-outlined text-[19px]">lock</span>
                    </div>
                    <div>
                      <div className="text-sm text-on-background font-semibold">修改密码</div>
                      <div className="text-[10px] text-outline mt-0.5">定期更换密码确保个人学习数据高强度安全</div>
                    </div>
                  </div>
                  <span className="material-symbols-outlined text-outline text-[18px] transition-transform duration-300" style={{ transform: isChangingPassword ? 'rotate(95deg)' : 'none' }}>
                    chevron_right
                  </span>
                </div>

                {/* Change Password Expansion Block */}
                {isChangingPassword && (
                  <form onSubmit={handlePasswordSubmit} className="mx-3.5 mb-3.5 p-4 bg-surface rounded-2xl border border-primary/5 space-y-3.5 animate-fade-in">
                    <div>
                      <label className="text-[11px] font-bold text-outline block mb-1">当前旧密码</label>
                      <input
                        type="password"
                        placeholder="请输入当前的原密码"
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                        className="w-full bg-surface-container border border-primary/10 rounded-xl px-3 py-2 text-sm text-on-surface focus:outline-none focus:border-primary/40 focus:ring-1 focus:ring-primary/25 bg-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-bold text-outline block mb-1">新密码</label>
                      <input
                        type="password"
                        placeholder="请输入新密码 (不少于6位)"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="w-full bg-surface-container border border-primary/10 rounded-xl px-3 py-2 text-sm text-on-surface focus:outline-none focus:border-primary/40 focus:ring-1 focus:ring-primary/25 bg-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-bold text-outline block mb-1">确认新密码</label>
                      <input
                        type="password"
                        placeholder="请再次键入您的新密码"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full bg-surface-container border border-primary/10 rounded-xl px-3 py-2 text-sm text-on-surface focus:outline-none focus:border-primary/40 focus:ring-1 focus:ring-primary/25 bg-transparent"
                      />
                    </div>
                    <div className="flex gap-2 justify-end pt-1">
                      <button
                        type="button"
                        onClick={() => setIsChangingPassword(false)}
                        className="px-3.5 py-1.5 text-xs font-semibold text-outline hover:bg-surface-container rounded-lg"
                      >
                        取消
                      </button>
                      <button
                        type="submit"
                        className="px-4 py-1.5 text-xs font-bold bg-primary text-white hover:bg-primary/95 rounded-lg shadow-sm"
                      >
                        保存并更新密码
                      </button>
                    </div>
                  </form>
                )}
              </div>

            </div>

            {/* Quick Actions Panel */}
            <div className="pt-2">
              <button
                onClick={onLogout}
                className="w-full py-3.5 border border-error/15 bg-error/5 hover:bg-error/10 text-error font-semibold rounded-2xl text-sm active:scale-[0.98] transition-all text-center flex items-center justify-center gap-1.5 cursor-pointer shadow-sm"
              >
                <span className="material-symbols-outlined text-[16px]">logout</span>
                <span>退出登录 (Log Out)</span>
              </button>
            </div>

          </div>
        )}
      </main>
    </div>
  );
}
