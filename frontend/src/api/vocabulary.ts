/**
 * 生词本 API — CRUD
 */

import { api } from './client';

// ===== Types =====

export interface VocabularyCreate {
  word: string;
  phonetic?: string;
  part_of_speech?: string;
  definitions?: string[];
  examples?: string[];
  synonyms?: string[];
  added_at?: string;
}

export interface VocabularyWord {
  id?: number;
  user_id?: string;
  word: string;
  phonetic?: string;
  part_of_speech?: string;
  definitions: string[];
  examples: string[];
  synonyms: string[];
  added_at?: string;
}

export interface VocabularyGroup {
  letter: string;
  words: VocabularyWord[];
  count: number;
}

export interface VocabularyListResponse {
  total: number;
  groups: VocabularyGroup[];
}

export interface VocabularySearchResponse {
  results: VocabularyWord[];
  total: number;
}

// ===== API 函数 =====

export async function listVocabulary(): Promise<VocabularyListResponse> {
  return api.get<VocabularyListResponse>('/api/v1/vocabulary/book');
}

export async function searchVocabulary(q: string, sort: string = 'recent'): Promise<VocabularySearchResponse> {
  return api.get<VocabularySearchResponse>('/api/v1/vocabulary/book/search', {
    params: { q, sort },
  });
}

export async function addVocabulary(data: VocabularyCreate): Promise<{ status: string; word: VocabularyWord }> {
  return api.post('/api/v1/vocabulary/book', data);
}

export async function removeVocabulary(word: string): Promise<{ status: string; word: string }> {
  return api.delete(`/api/v1/vocabulary/book/${encodeURIComponent(word)}`);
}