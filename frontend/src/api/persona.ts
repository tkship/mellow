/**
 * 角色 (Persona) API
 */

import { api } from './client';

// ===== Types =====

export interface LanguageStyle {
  tone: string;
  traits: string[];
}

export interface TeachingStyle {
  approach: string;
  strictness: number;
  correction_frequency: string;
}

export interface Persona {
  id: string;
  name: string;
  role: string;
  language_style: LanguageStyle;
  teaching_style: TeachingStyle;
  intimacy_level: string;
  interaction_rhythm: [number, number];
  emotional_sensitivity: number;
  system_prompt_template: string;
  is_preset: boolean;
  created_by: string | null;
  voice_id: string | null;
}

// ===== API 函数 =====

export async function listPersonas(): Promise<{ personas: Persona[] }> {
  return api.get<{ personas: Persona[] }>('/api/v1/personas');
}

export async function listCustomPersonas(): Promise<{ personas: Persona[] }> {
  return api.get<{ personas: Persona[] }>('/api/v1/personas/custom');
}

export async function getPersona(personaId: string): Promise<Persona> {
  return api.get<Persona>(`/api/v1/personas/${encodeURIComponent(personaId)}`);
}

export function getPersonaVoiceUrl(personaId: string): string {
  return `/api/v1/personas/${encodeURIComponent(personaId)}/voice`;
}