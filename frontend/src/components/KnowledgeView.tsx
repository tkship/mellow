import React, { useState, useCallback } from 'react';
import { lookupWord, searchKnowledge, type WordEntry, type SearchResultItem } from '../api/knowledge';

interface KnowledgeViewProps {
  onGoBack: () => void;
}

export default function KnowledgeView({ onGoBack }: KnowledgeViewProps) {
  const [query, setQuery] = useState('');
  const [wordResult, setWordResult] = useState<WordEntry | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState<'lookup' | 'search'>('lookup');

  const handleLookup = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    setSearchResults([]);
    try {
      const res = await lookupWord(query.trim());
      setWordResult(res);
    } catch (err: any) {
      setWordResult(null);
      setError(err.message || '未找到该单词');
    } finally {
      setLoading(false);
    }
  }, [query]);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    setWordResult(null);
    try {
      const res = await searchKnowledge(query.trim(), 10);
      setSearchResults(res.results);
      if (res.results.length === 0) {
        setError('未找到相关结果');
      }
    } catch (err: any) {
      setSearchResults([]);
      setError(err.message || '搜索失败');
    } finally {
      setLoading(false);
    }
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      mode === 'lookup' ? handleLookup() : handleSearch();
    }
  };

  return (
    <div className="bg-background text-on-background h-screen max-h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <header className="w-full bg-white border-b border-primary/5 px-6 h-16 flex items-center justify-between shrink-0">
        <button
          onClick={onGoBack}
          className="w-10 h-10 flex items-center justify-center text-on-surface hover:bg-primary-container/10 rounded-full transition-colors cursor-pointer"
        >
          <span className="material-symbols-outlined">arrow_back</span>
        </button>
        <h1 className="font-display font-medium text-headline-sm">知识库</h1>
        <div className="w-10"></div>
      </header>

      {/* Search Bar */}
      <div className="px-4 py-4 shrink-0 space-y-3">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline-variant text-[20px]">
              search
            </span>
            <input
              type="text"
              placeholder={mode === 'lookup' ? '输入单词精确查询...' : '语义搜索...'}
              value={query}
              onChange={(e) => { setQuery(e.target.value); setError(''); }}
              onKeyDown={handleKeyDown}
              className="w-full bg-surface-container-lowest border border-outline-variant rounded-xl py-2.5 pl-10 pr-4 text-sm text-on-surface placeholder:text-outline-variant focus:border-primary focus:ring-1 focus:ring-primary/25 focus:outline-none transition-all"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { setMode('lookup'); handleLookup(); }}
            className={`flex-1 py-2 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
              mode === 'lookup'
                ? 'bg-primary text-white shadow-sm'
                : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
            }`}
          >
            精确查词
          </button>
          <button
            onClick={() => { setMode('search'); handleSearch(); }}
            className={`flex-1 py-2 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
              mode === 'search'
                ? 'bg-primary text-white shadow-sm'
                : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
            }`}
          >
            语义搜索
          </button>
        </div>
      </div>

      {/* Results */}
      <main className="flex-grow overflow-y-auto px-4 pb-6">
        {loading ? (
          <div className="animate-pulse space-y-4 py-8">
            <div className="h-6 bg-surface-container-high rounded w-1/3" />
            <div className="h-4 bg-surface-container-high rounded w-2/3" />
            <div className="h-4 bg-surface-container-high rounded w-1/2" />
            <div className="h-4 bg-surface-container-high rounded w-3/4" />
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-16 text-on-surface-variant">
            <span className="material-symbols-outlined text-5xl mb-3">search_off</span>
            <p>{error}</p>
          </div>
        ) : wordResult ? (
          // 精确查词结果
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-primary/5 space-y-4 animate-fade-in">
            <div className="flex items-center gap-3">
              <div className="w-14 h-14 rounded-full bg-primary/15 flex items-center justify-center text-primary font-display font-bold text-xl">
                {wordResult.word[0].toUpperCase()}
              </div>
              <div>
                <h2 className="font-display font-bold text-2xl text-on-surface">{wordResult.word}</h2>
                {wordResult.phonetic && (
                  <p className="text-sm text-on-surface-variant font-mono">{wordResult.phonetic}</p>
                )}
              </div>
            </div>

            {wordResult.part_of_speech && (
              <div className="flex gap-2">
                <span className="px-3 py-1 bg-primary/10 text-primary text-xs font-semibold rounded-full">
                  {wordResult.part_of_speech}
                </span>
                <span className="px-3 py-1 bg-surface-container-low text-on-surface-variant text-xs rounded-full">
                  来源: {wordResult.source}
                </span>
              </div>
            )}

            {wordResult.definitions.length > 0 && (
              <div>
                <h3 className="text-xs font-bold text-primary uppercase tracking-wider mb-2">释义</h3>
                <ol className="space-y-2">
                  {wordResult.definitions.map((d, i) => (
                    <li key={i} className="text-sm text-on-surface flex gap-2 pl-1">
                      <span className="text-primary/60 font-bold min-w-[20px]">{i + 1}.</span>
                      <span>{d}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {wordResult.examples.length > 0 && (
              <div>
                <h3 className="text-xs font-bold text-primary uppercase tracking-wider mb-2">例句</h3>
                <div className="space-y-2">
                  {wordResult.examples.map((ex, i) => (
                    <div key={i} className="bg-surface-container-low p-3 rounded-xl">
                      <p className="text-sm text-on-surface italic">{ex}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {wordResult.synonyms.length > 0 && (
              <div>
                <h3 className="text-xs font-bold text-primary uppercase tracking-wider mb-2">近义词</h3>
                <div className="flex flex-wrap gap-2">
                  {wordResult.synonyms.map((s, i) => (
                    <span key={i} className="px-3 py-1 bg-secondary-container/20 text-on-secondary-container text-xs rounded-full">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : searchResults.length > 0 ? (
          // 语义搜索结果
          <div className="space-y-3 animate-fade-in">
            <p className="text-xs text-on-surface-variant px-1">
              找到 {searchResults.length} 个相关结果
            </p>
            {searchResults.map((item, i) => (
              <div key={i} className="bg-white rounded-2xl p-4 shadow-sm border border-primary/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-primary">
                    相关度: {(item.score * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-sm text-on-surface leading-relaxed">{item.content}</p>
                {item.metadata && Object.keys(item.metadata).length > 0 && (
                  <div className="flex gap-2 mt-3 flex-wrap">
                    {Object.entries(item.metadata).map(([k, v]) => (
                      <span key={k} className="px-2 py-0.5 bg-surface-container-low text-on-surface-variant text-xs rounded-full">
                        {k}: {String(v)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : null}

        {!query && !loading && !wordResult && searchResults.length === 0 && !error && (
          <div className="flex flex-col items-center justify-center py-20 text-on-surface-variant">
            <span className="material-symbols-outlined text-6xl mb-4 text-primary/30">menu_book</span>
            <p className="text-lg font-display font-semibold mb-1">Mellow 知识库</p>
            <p className="text-sm">输入单词精确查询或进行语义搜索</p>
          </div>
        )}
      </main>
    </div>
  );
}