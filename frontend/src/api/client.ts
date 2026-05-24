/**
 * Mellow API Client — 基于 fetch 的轻量级 HTTP 客户端
 *
 * 特性：
 * - 自动携带 JWT Bearer Token
 * - 401 响应自动尝试 refresh token
 * - 统一错误处理
 * - SSE 流式请求支持
 */

const API_BASE = '/api/v1';

// ===== Token 管理 =====

const TOKEN_KEY = 'mellow_access_token';
const REFRESH_KEY = 'mellow_refresh_token';

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function isLoggedIn(): boolean {
  return !!getAccessToken();
}

// ===== 统一错误类型 =====

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    public message: string,
    public detail?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// ===== Refresh Token 锁，防止并发刷新 =====

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

async function tryRefreshToken(): Promise<boolean> {
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) return false;

      const data = await res.json();
      setTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      return false;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

// ===== 核心 Request 函数 =====

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, ...fetchOptions } = options;

  // 构建 URL（含 query params）
  const url = new URL(endpoint, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    });
  }

  // 添加 Authorization header
  const token = getAccessToken();
  const headers = new Headers(fetchOptions.headers);
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!headers.has('Content-Type') && fetchOptions.body) {
    headers.set('Content-Type', 'application/json');
  }

  const res = await fetch(url.toString(), {
    ...fetchOptions,
    headers,
  });

  // 401 → 尝试 refresh token
  if (res.status === 401) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      // 重试原请求
      const newToken = getAccessToken();
      headers.set('Authorization', `Bearer ${newToken}`);
      const retryRes = await fetch(url.toString(), {
        ...fetchOptions,
        headers,
      });
      if (retryRes.ok) {
        if (retryRes.status === 204) return undefined as T;
        return retryRes.json();
      }
      const errData = await retryRes.json().catch(() => ({}));
      throw new ApiError(
        retryRes.status,
        errData.error || 'RefreshRetryFailed',
        errData.message || '认证已过期，请重新登录',
        errData.detail
      );
    }
    // Refresh 也失败 → 清除 token
    clearTokens();
    window.dispatchEvent(new CustomEvent('auth:logout'));
    throw new ApiError(401, 'Unauthorized', '登录已过期，请重新登录');
  }

  // 其他错误
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new ApiError(
      res.status,
      errData.error || `HTTP${res.status}`,
      errData.message || `请求失败 (${res.status})`,
      errData.detail
    );
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json();
}

// ===== 便捷方法 =====

export const api = {
  get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, { ...options, method: 'GET' });
  },

  post<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, { ...options, method: 'DELETE' });
  },
};

// ===== SSE 流式请求 =====

export interface SseCallbacks {
  onToken: (token: string) => void;
  onDone: () => void;
  onError: (error: Error) => void;
}

export async function chatStreamSse(
  personaId: string,
  message: string,
  sessionId: string,
  callbacks: SseCallbacks
): Promise<void> {
  const token = getAccessToken();
  const url = new URL(`${API_BASE}/chat/stream`, window.location.origin);
  url.searchParams.set('persona_id', personaId);
  url.searchParams.set('message', message);
  if (sessionId) {
    url.searchParams.set('session_id', sessionId);
  }
  // SSE 通过 query param 传递 token（EventSource 不支持自定义 header）
  if (token) {
    url.searchParams.set('token', token);
  }

  try {
    const res = await fetch(url.toString(), {
      method: 'GET',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new ApiError(res.status, errData.error || 'SSEError', errData.message || '流式对话失败');
    }

    const reader = res.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;
          try {
            const data = JSON.parse(jsonStr);
            if (data.done) {
              callbacks.onDone();
              return;
            }
            if (data.token) {
              callbacks.onToken(data.token);
            }
            if (data.error) {
              callbacks.onError(new Error(data.error));
            }
          } catch {
            // 忽略非 JSON 行
          }
        }
      }
    }

    callbacks.onDone();
  } catch (err) {
    if (err instanceof ApiError) {
      callbacks.onError(err);
    } else {
      callbacks.onError(err instanceof Error ? err : new Error('SSE 连接失败'));
    }
  }
}