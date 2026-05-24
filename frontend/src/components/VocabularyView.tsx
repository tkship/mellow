import React, { useState, useEffect, useCallback } from 'react';
import {
  listVocabulary,
  searchVocabulary,
  addVocabulary,
  removeVocabulary,
  type VocabularyWord,
  type VocabularyGroup,
} from '../api/vocabulary';
import { lookupWord, type WordEntry } from '../api/knowledge';
import { ApiError } from '../api/client';

interface VocabularyViewProps {
  onGoBack: () => void;
}

export default function VocabularyView({ onGoBack }: VocabularyViewProps) {
  const [groups, setGroups] = useState<VocabularyGroup[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<VocabularyWord[] | null>(null);
  const [searching, setSearching] = useState(false);
  const [selectedWord, setSelectedWord] = useState<VocabularyWord | null>(null);
  const [wordDetail, setWordDetail] = useState<WordEntry | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // 加载生词本
  const loadVocabulary = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listVocabulary();
      setGroups(res.groups);
      setTotal(res.total);
    } catch (err) {
      console.error('加载生词本失败:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadVocabulary();
  }, [loadVocabulary]);

  // 搜索（去抖 300ms）
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }
    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const res = await searchVocabulary(searchQuery);
        setSearchResults(res.results);
      } catch (err) {
        console.error('搜索失败:', err);
      } finally {
        setSearching(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // 查看单词详情
  const handleViewDetail = async (word: VocabularyWord) => {
    setSelectedWord(word);
    setDetailLoading(true);
    setWordDetail(null);
    try {
      const entry = await lookupWord(word.word);
      setWordDetail(entry);
    } catch {
      // 查词失败，显示基本信息
      setWordDetail(null);
    } finally {
      setDetailLoading(false);
    }
  };

  // 删除单词
  const handleDelete = async (word: string) => {
    try {
      await removeVocabulary(word);
      setGroups((prev) =>
        prev
          .map((g) => ({
            ...g,
            words: g.words.filter((w) => w.word !== word),
            count: g.words.filter((w) => w.word !== word).length,
          }))
          .filter((g) => g.count > 0)
      );
      setTotal((prev) => prev - 1);
      if (selectedWord?.word === word) setSelectedWord(null);
    } catch (err) {
      console.error('删除失败:', err);
    }
  };

  // 显示列表
  const displayList = searchResults || groups.flatMap((g) => g.words);

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
        <h1 className="font-display font-medium text-headline-sm">生词本</h1>
        <div className="w-10 text-right text-xs text-primary font-bold">{total} 词</div>
      </header>

      {/* Search */}
      <div className="px-4 py-3 shrink-0">
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline-variant text-[20px]">
            search
          </span>
          <input
            type="text"
            placeholder="搜索生词..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface-container-lowest border border-outline-variant rounded-xl py-2.5 pl-10 pr-4 text-sm text-on-surface placeholder:text-outline-variant focus:border-primary focus:ring-1 focus:ring-primary/25 focus:outline-none transition-all"
          />
          {searching && (
            <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-primary animate-spin text-[18px]">
              progress_activity
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <main className="flex-grow overflow-y-auto">
        {loading ? (
          <div className="p-6 space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="animate-pulse flex items-center gap-3 p-3">
                <div className="w-10 h-10 rounded-full bg-surface-container-high" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-surface-container-high rounded w-24" />
                  <div className="h-3 bg-surface-container-high rounded w-48" />
                </div>
              </div>
            ))}
          </div>
        ) : searchQuery && searchResults?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-on-surface-variant">
            <span className="material-symbols-outlined text-5xl mb-3">search_off</span>
            <p>未找到 "{searchQuery}"</p>
          </div>
        ) : searchResults ? (
          // 搜索结果
          <div className="px-4 py-2 space-y-1">
            {searchResults.map((word) => (
              <button
                key={word.word}
                onClick={() => handleViewDetail(word)}
                className="w-full flex items-center gap-3 p-3 hover:bg-surface-container-low rounded-xl transition-colors text-left cursor-pointer"
              >
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-display font-bold text-sm">
                  {word.word[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-on-surface">{word.word}</p>
                  <p className="text-xs text-on-surface-variant truncate">
                    {word.definitions?.[0] || word.part_of_speech || ''}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(word.word);
                  }}
                  className="text-error/50 hover:text-error p-1 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">delete</span>
                </button>
              </button>
            ))}
          </div>
        ) : (
          // 分组列表
          <div className="px-4 py-2">
            {groups.map((group) => (
              <div key={group.letter} className="mb-4">
                <h3 className="text-xs font-bold text-primary uppercase tracking-wider px-3 py-1 sticky top-0 bg-background/90 backdrop-blur-sm z-10">
                  {group.letter}
                </h3>
                <div className="space-y-1">
                  {group.words.map((word) => (
                    <button
                      key={word.word}
                      onClick={() => handleViewDetail(word)}
                      className="w-full flex items-center gap-3 p-3 hover:bg-surface-container-low rounded-xl transition-colors text-left cursor-pointer"
                    >
                      <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-primary font-display font-bold text-xs">
                        {word.word[0].toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-on-surface">{word.word}</p>
                        <p className="text-xs text-on-surface-variant truncate">
                          {word.definitions?.[0] || word.part_of_speech || ''}
                        </p>
                      </div>
                      <span className="material-symbols-outlined text-outline-variant text-[18px]">chevron_right</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Word Detail BottomSheet */}
      {selectedWord && (
        <div className="fixed inset-0 z-50 flex items-end justify-center" onClick={() => setSelectedWord(null)}>
          <div className="absolute inset-0 bg-black/30" />
          <div
            className="relative bg-white w-full max-w-lg rounded-t-2xl p-6 max-h-[70vh] overflow-y-auto animate-slide-up shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-10 h-1 bg-outline-variant/30 rounded-full mx-auto mb-4" />
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-primary/15 flex items-center justify-center text-primary font-display font-bold text-lg">
                {selectedWord.word[0].toUpperCase()}
              </div>
              <div>
                <h2 className="font-display font-bold text-xl text-on-surface">{selectedWord.word}</h2>
                {wordDetail?.phonetic && (
                  <p className="text-sm text-on-surface-variant">{wordDetail.phonetic}</p>
                )}
              </div>
            </div>

            {detailLoading ? (
              <div className="animate-pulse space-y-3 py-4">
                <div className="h-4 bg-surface-container-high rounded w-3/4" />
                <div className="h-3 bg-surface-container-high rounded w-1/2" />
                <div className="h-3 bg-surface-container-high rounded w-2/3" />
              </div>
            ) : wordDetail ? (
              <div className="space-y-4">
                {wordDetail.part_of_speech && (
                  <div>
                    <span className="text-xs font-bold text-primary uppercase tracking-wider">词性</span>
                    <p className="text-sm text-on-surface mt-1">{wordDetail.part_of_speech}</p>
                  </div>
                )}
                {wordDetail.definitions.length > 0 && (
                  <div>
                    <span className="text-xs font-bold text-primary uppercase tracking-wider">释义</span>
                    <ul className="mt-2 space-y-1.5">
                      {wordDetail.definitions.map((d, i) => (
                        <li key={i} className="text-sm text-on-surface flex gap-2">
                          <span className="text-primary font-bold">{i + 1}.</span>
                          <span>{d}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {wordDetail.examples.length > 0 && (
                  <div>
                    <span className="text-xs font-bold text-primary uppercase tracking-wider">例句</span>
                    <ul className="mt-2 space-y-2">
                      {wordDetail.examples.map((ex, i) => (
                        <li key={i} className="text-sm text-on-surface-variant italic bg-surface-container-low p-2 rounded-lg">
                          {ex}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {wordDetail.synonyms.length > 0 && (
                  <div>
                    <span className="text-xs font-bold text-primary uppercase tracking-wider">近义词</span>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {wordDetail.synonyms.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {selectedWord.definitions && selectedWord.definitions.length > 0 && (
                  <div>
                    <span className="text-xs font-bold text-primary uppercase tracking-wider">释义</span>
                    <ul className="mt-2 space-y-1">
                      {selectedWord.definitions.map((d, i) => (
                        <li key={i} className="text-sm text-on-surface">{i + 1}. {d}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <button
              onClick={() => handleDelete(selectedWord.word)}
              className="mt-6 w-full py-3 border border-error/15 bg-error/5 text-error font-semibold rounded-xl text-sm hover:bg-error/10 active:scale-[0.98] transition-all cursor-pointer"
            >
              从生词本删除
            </button>
          </div>
        </div>
      )}
    </div>
  );
}