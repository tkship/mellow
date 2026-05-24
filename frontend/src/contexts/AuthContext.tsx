/**
 * 认证上下文 — 全局 JWT 状态管理
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import {
  login as apiLogin,
  register as apiRegister,
  getMe,
  logout as apiLogout,
  type LoginRequest,
  type RegisterRequest,
  type UserResponse,
} from '../api/auth';
import { getAccessToken, setTokens, clearTokens } from '../api/client';

// ===== Types =====

interface AuthContextValue {
  user: UserResponse | null;
  isLoggedIn: boolean;
  isLoading: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

// ===== Context =====

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 启动时自动检测 token 并恢复用户信息
  useEffect(() => {
    const restoreSession = async () => {
      const token = getAccessToken();
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const userInfo = await getMe();
        setUser(userInfo);
      } catch {
        clearTokens();
      } finally {
        setIsLoading(false);
      }
    };
    restoreSession();
  }, []);

  // 监听来自 api/client 的 auth:logout 事件
  useEffect(() => {
    const handleForceLogout = () => {
      setUser(null);
      setError('登录已过期，请重新登录');
    };
    window.addEventListener('auth:logout', handleForceLogout);
    return () => window.removeEventListener('auth:logout', handleForceLogout);
  }, []);

  const login = useCallback(async (data: LoginRequest) => {
    setError(null);
    try {
      await apiLogin(data);
      const userInfo = await getMe();
      setUser(userInfo);
    } catch (err: any) {
      clearTokens();
      setError(err.message || '登录失败');
      throw err;
    }
  }, []);

  const register = useCallback(async (data: RegisterRequest) => {
    setError(null);
    try {
      await apiRegister(data);
      const userInfo = await getMe();
      setUser(userInfo);
    } catch (err: any) {
      clearTokens();
      setError(err.message || '注册失败');
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setUser(null);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoggedIn: !!user,
        isLoading,
        error,
        login,
        register,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}