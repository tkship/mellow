/**
 * Mellow Settings API — 用户配置管理（API Key 等）
 */

import { api } from './client';

/** API Key 配置查询响应（脱敏显示） */
export interface ApiKeyConfigResponse {
  llm_api_key: string;
  llm_base_url: string;
  llm_model: string;
  llm_fast_model: string;
  embed_api_key: string;
  embed_model: string;
  embed_dimension: number;
  asr_app_id: string;
  asr_token: string;
  tts_app_id: string;
  tts_token: string;
}

/** API Key 配置更新请求（只传需要修改的字段） */
export interface ApiKeyConfigUpdate {
  llm_api_key?: string;
  llm_base_url?: string;
  llm_model?: string;
  llm_fast_model?: string;
  embed_api_key?: string;
  embed_model?: string;
  embed_dimension?: number;
  asr_app_id?: string;
  asr_token?: string;
  tts_app_id?: string;
  tts_token?: string;
}

/** 获取当前 API Key 配置（脱敏显示） */
export function getApiKeys(): Promise<ApiKeyConfigResponse> {
  return api.get<ApiKeyConfigResponse>('/api/v1/settings/keys');
}

/** 更新 API Key 配置（热更新，无需重启服务） */
export function updateApiKeys(config: ApiKeyConfigUpdate): Promise<ApiKeyConfigResponse> {
  return api.put<ApiKeyConfigResponse>('/api/v1/settings/keys', config);
}