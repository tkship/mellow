import React, { useState } from 'react';
import { login, register } from '../api/auth';
import { ApiError } from '../api/client';

interface LoginViewProps {
  onLoginSuccess: () => void;
}

export default function LoginView({ onLoginSuccess }: LoginViewProps) {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    if (username.trim().length < 3) {
      setErrorMsg('用户名至少需要 3 个字符');
      return;
    }
    if (password.length < 6) {
      setErrorMsg('密码至少需要 6 个字符');
      return;
    }

    setIsLoading(true);
    setErrorMsg('');

    try {
      if (isRegisterMode) {
        await register({ username: username.trim(), password });
      } else {
        await login({ username: username.trim(), password });
      }
      onLoginSuccess();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setErrorMsg(err.message || err.code || '请求失败，请稍后重试');
      } else if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('未知错误，请稍后重试');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen max-h-screen flex items-center justify-center p-4 md:p-12 relative overflow-hidden bg-background">
      {/* Decorative Background Elements */}
      <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-primary-container opacity-10 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] left-[-10%] w-[400px] h-[400px] bg-secondary-container opacity-10 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="w-full max-w-md bg-surface rounded-[2rem] shadow-[0_20px_40px_-10px_rgba(0,106,101,0.05),0_4px_6px_-2px_rgba(0,106,101,0.02)] flex flex-col overflow-hidden relative">
        <div className="absolute inset-0 rounded-[2rem] border border-primary/10 pointer-events-none"></div>

        {/* User Form */}
        <div className="w-full flex flex-col justify-center px-6 py-12 md:px-10 relative z-10 bg-white/40 backdrop-blur-md">
          {/* Brand Header */}
          <div className="mb-8 flex items-center gap-3">
            <span
              className="material-symbols-outlined text-primary-container text-[36px] font-bold"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              cloud
            </span>
            <h1 className="font-display font-bold text-headline-md text-primary tracking-tight">Mellow AI</h1>
          </div>

          <div className="mb-8">
            <h2 className="font-display text-[32px] font-bold text-on-surface leading-tight mb-2">
              {isRegisterMode ? '创建账号' : '欢迎回来'}
            </h2>
            <p className="text-body-lg text-on-surface-variant font-sans">
              {isRegisterMode ? '加入 Mellow，开启您的智能英语学习之旅。' : '请登录以继续您的宁静之旅。'}
            </p>
          </div>

          {errorMsg && (
            <div className="mb-4 p-3 bg-error-container text-on-error-container text-sm rounded-xl">
              {errorMsg}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-label-sm text-on-surface-variant mb-1" htmlFor="username">
                用户名 / 账号
              </label>
              <div className="relative flex items-center">
                <span className="material-symbols-outlined absolute left-3 text-outline-variant pointer-events-none">
                  person
                </span>
                <input
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded-xl py-2.5 pl-11 pr-4 font-body-md text-on-surface placeholder:text-outline-variant focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 focus:outline-none transition-all"
                  id="username"
                  name="username"
                  placeholder="请输入用户名"
                  required
                  type="text"
                  value={username}
                  onChange={(e) => { setUsername(e.target.value); setErrorMsg(''); }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-label-sm text-on-surface-variant" htmlFor="password">
                  密码
                </label>
                {!isRegisterMode && (
                  <button
                    type="button"
                    onClick={() => setErrorMsg('DEMO 模版中密码可任意输入，点击登录即可！')}
                    className="text-label-sm text-primary hover:text-primary-container transition-colors"
                  >
                    忘记密码
                  </button>
                )}
              </div>
              <div className="relative flex items-center">
                <span className="material-symbols-outlined absolute left-3 text-outline-variant pointer-events-none">
                  lock
                </span>
                <input
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded-xl py-2.5 pl-11 pr-11 font-body-md text-on-surface placeholder:text-outline-variant focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 focus:outline-none transition-all"
                  id="password"
                  name="password"
                  placeholder="请输入您的密码"
                  required
                  type="password"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setErrorMsg(''); }}
                />
              </div>
            </div>

            <div className="pt-2">
              <button
                className="w-full bg-primary-container text-on-primary-container font-label-lg py-3 rounded-full shadow-[0_4px_14px_rgba(78,205,196,0.3)] hover:shadow-[0_6px_20px_rgba(78,205,196,0.4)] hover:scale-[1.01] active:scale-[0.99] transition-all duration-300 flex items-center justify-center gap-1 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-[0_4px_14px_rgba(78,205,196,0.3)]"
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <span>处理中...</span>
                    <span className="material-symbols-outlined text-[18px] animate-spin">progress_activity</span>
                  </>
                ) : (
                  <>
                    <span>{isRegisterMode ? '立即注册' : '登录'}</span>
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </>
                )}
              </button>
            </div>
          </form>

          <div className="mt-8 text-center">
            <p className="text-body-sm text-on-surface-variant">
              {isRegisterMode ? '已有账号？' : '还没有账号？'}
              <button
                onClick={() => {
                  setIsRegisterMode(!isRegisterMode);
                  setErrorMsg('');
                }}
                className="text-label-sm text-primary font-bold hover:text-primary-container transition-colors ml-1"
              >
                {isRegisterMode ? '立即登录' : '新用户注册'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
