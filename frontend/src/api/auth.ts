/**
 * 认证 API — 注册、登录、刷新 Token、获取当前用户
 */

import { api, setTokens, clearTokens } from './client';

// ===== Types =====

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  username: string;
  is_active: boolean;
}

// ===== API 函数 =====

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>('/api/v1/auth/register', data);
  setTokens(res.access_token, res.refresh_token);
  return res;
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>('/api/v1/auth/login', data);
  setTokens(res.access_token, res.refresh_token);
  return res;
}

export async function refreshToken(refresh_token: string): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>('/api/v1/auth/refresh', { refresh_token });
  setTokens(res.access_token, res.refresh_token);
  return res;
}

export async function getMe(): Promise<UserResponse> {
  return api.get<UserResponse>('/api/v1/auth/me');
}

export function logout(): void {
  clearTokens();
}