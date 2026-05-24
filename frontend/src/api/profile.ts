/**
 * 用户画像 API — 学习档案、统计、错题、学习计划
 */

import { api } from './client';

// ===== Types =====

export interface LearningProfile {
  cefr_level: string;
  vocabulary_size: number;
  weak_areas: string[];
  known_words_count: number;
  completed_lessons: string[];
  current_plan: WeeklyPlan | null;
  summary: string;
}

export interface WeeklyPlan {
  week: number;
  theme: string;
  days: DailyPlan[];
  completed: boolean;
}

export interface DailyPlan {
  day: number;
  topic: string;
  vocabulary: string[];
  grammar_point: string;
  practice: string;
}

export interface ProfileUpdateRequest {
  cefr_level?: string;
  vocabulary_size?: number;
  learning_goal?: string;
}

export interface ProfileStats {
  total_messages: number;
  learning_days: number;
  check_in_count: number;
  cefr_level: string;
  vocabulary_size: number;
  weak_areas: string[];
  cefr_progress: CefrProgressItem[];
  range: string;
}

export interface CefrProgressItem {
  date: string;
  level: string;
  score: number;
}

export interface MistakeEntry {
  word_or_rule: string;
  mistake_type: string;
  correction: string;
  context: string;
  timestamp: string;
}

// ===== API 函数 =====

export async function getProfile(): Promise<LearningProfile> {
  return api.get<LearningProfile>('/api/v1/profile');
}

export async function updateProfile(data: ProfileUpdateRequest): Promise<LearningProfile> {
  return api.put<LearningProfile>('/api/v1/profile', data);
}

export async function getProfileStats(range: string = 'month'): Promise<ProfileStats> {
  return api.get<ProfileStats>('/api/v1/profile/stats', { params: { range } });
}

export async function getMistakes(): Promise<{ mistakes: MistakeEntry[] }> {
  return api.get<{ mistakes: MistakeEntry[] }>('/api/v1/profile/mistakes');
}

export async function getPlan(): Promise<{ plan: WeeklyPlan | null; completed?: boolean; message?: string }> {
  return api.get('/api/v1/profile/plan');
}

export async function setPlan(data: WeeklyPlan): Promise<{ plan: WeeklyPlan | null; message: string }> {
  return api.put('/api/v1/profile/plan', data);
}

export async function completePlan(): Promise<{ message: string; completed_lessons: string[] }> {
  return api.post('/api/v1/profile/plan/complete');
}