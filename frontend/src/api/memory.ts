/**
 * 记忆系统 API — 情绪、事实、摘要、主动消息
 */

import { api } from './client';

// ===== Types =====

export interface MoodEvent {
  date: string;
  mood: string;
  reason: string;
  intensity: number;
}

export interface ProactiveMessage {
  id: string;
  persona_id: string;
  content: string;
  created_at: string;
  delivered: boolean;
}

// ===== API 函数 =====

export async function getEmotions(personaId: string): Promise<{ emotions: MoodEvent[] }> {
  return api.get<{ emotions: MoodEvent[] }>('/api/v1/memory/emotions', {
    params: { persona_id: personaId },
  });
}

export async function getFacts(personaId: string): Promise<{ facts: string[] }> {
  return api.get<{ facts: string[] }>('/api/v1/memory/facts', {
    params: { persona_id: personaId },
  });
}

export async function getSummary(personaId: string): Promise<{ summary: string }> {
  return api.get<{ summary: string }>('/api/v1/memory/summary', {
    params: { persona_id: personaId },
  });
}

export async function getProactiveMessages(
  personaId: string
): Promise<{ messages: ProactiveMessage[]; count: number }> {
  return api.get('/api/v1/memory/proactive', {
    params: { persona_id: personaId },
  });
}