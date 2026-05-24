/**
 * 聊天 API — 同步/流式对话、历史消息、收藏、删除、开场白
 */

import { api, chatStreamSse, type SseCallbacks } from './client';

// ===== Types =====

export interface ChatRequest {
  persona_id: string;
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  reply: string;
  intent: string;
  action: string | null;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  is_favorite?: boolean;
  timestamp: string;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  next_cursor: string | null;
}

export interface QuickPhrasesResponse {
  phrases: string[];
  persona_name: string;
}

// ===== API 函数 =====

export async function sendChatMessage(data: ChatRequest): Promise<ChatResponse> {
  return api.post<ChatResponse>('/api/v1/chat', data);
}

export async function getChatStream(
  personaId: string,
  message: string,
  sessionId: string,
  callbacks: SseCallbacks
): Promise<void> {
  return chatStreamSse(personaId, message, sessionId, callbacks);
}

export async function getChatHistory(
  personaId: string,
  limit: number = 20,
  cursor?: string | null
): Promise<ChatHistoryResponse> {
  return api.get<ChatHistoryResponse>('/api/v1/chat/history', {
    params: { persona_id: personaId, limit, cursor: cursor || undefined },
  });
}

export async function toggleMessageFavorite(
  messageId: string,
  personaId: string
): Promise<ChatMessage> {
  return api.put<ChatMessage>(
    `/api/v1/chat/messages/${encodeURIComponent(messageId)}/favorite`,
    undefined,
    { params: { persona_id: personaId } }
  );
}

export async function deleteMessage(
  messageId: string,
  personaId: string
): Promise<void> {
  return api.delete(`/api/v1/chat/messages/${encodeURIComponent(messageId)}`, {
    params: { persona_id: personaId },
  });
}

export async function getQuickPhrases(personaId: string): Promise<QuickPhrasesResponse> {
  return api.get<QuickPhrasesResponse>('/api/v1/chat/phrases', {
    params: { persona_id: personaId },
  });
}