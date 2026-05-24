/**
 * 知识库 API — 查词、语义搜索
 */

import { api } from './client';

// ===== Types =====

export interface WordEntry {
  word: string;
  phonetic: string | null;
  part_of_speech: string | null;
  definitions: string[];
  examples: string[];
  synonyms: string[];
  source: string;
}

export interface SearchResultItem {
  content: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
}

// ===== API 函数 =====

export async function lookupWord(word: string): Promise<WordEntry> {
  return api.get<WordEntry>('/api/v1/knowledge/lookup', {
    params: { word },
  });
}

export async function searchKnowledge(q: string, topK: number = 5): Promise<SearchResponse> {
  return api.get<SearchResponse>('/api/v1/knowledge/search', {
    params: { q, top_k: topK },
  });
}