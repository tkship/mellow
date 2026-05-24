import React, { useState, useEffect, useCallback } from 'react';
import { getMistakes, type MistakeEntry } from '../api/profile';

interface MistakesViewProps {
  onGoBack: () => void;
}

export default function MistakesView({ onGoBack }: MistakesViewProps) {
  const [mistakes, setMistakes] = useState<MistakeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadMistakes = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await getMistakes();
      setMistakes(res.mistakes);
    } catch (err: any) {
      setError(err.message || '加载失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMistakes();
  }, [loadMistakes]);

  const errorTypeLabels: Record<string, string> = {
    grammar: '语法错误',
    spelling: '拼写错误',
    vocabulary: '词汇错误',
    pronunciation: '发音问题',
    word_choice: '用词不当',
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
        <h1 className="font-display font-medium text-headline-sm">错题本</h1>
        <button
          onClick={loadMistakes}
          className="w-10 h-10 flex items-center justify-center text-primary hover:bg-primary-container/10 rounded-full transition-colors cursor-pointer"
          title="刷新"
        >
          <span className={`material-symbols-outlined text-[20px] ${loading ? 'animate-spin' : ''}`}>
            refresh
          </span>
        </button>
      </header>

      {/* Content */}
      <main className="flex-grow overflow-y-auto px-4 py-4">
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse bg-white rounded-2xl p-5 shadow-sm">
                <div className="h-4 bg-surface-container-high rounded w-20 mb-3" />
                <div className="h-6 bg-surface-container-high rounded w-3/4 mb-2" />
                <div className="h-4 bg-surface-container-high rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-16 text-on-surface-variant">
            <span className="material-symbols-outlined text-5xl mb-3">error_outline</span>
            <p>{error}</p>
          </div>
        ) : mistakes.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-on-surface-variant">
            <span className="material-symbols-outlined text-6xl mb-4 text-primary/30">check_circle</span>
            <p className="text-lg font-display font-semibold mb-1">暂无错题</p>
            <p className="text-sm">继续保持，你的学习表现很好！</p>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-xs text-on-surface-variant px-1">
              最近 {mistakes.length} 条错误记录
            </p>
            {mistakes.map((mistake, i) => (
              <div key={i} className="bg-white rounded-2xl p-5 shadow-sm border border-primary/5 animate-fade-in">
                {/* 错误类型标签 */}
                <div className="flex items-center gap-2 mb-3">
                  <span className="px-3 py-1 bg-error/10 text-error text-xs font-bold rounded-full">
                    {errorTypeLabels[mistake.error_type] || mistake.error_type}
                  </span>
                  {mistake.timestamp && (
                    <span className="text-xs text-on-surface-variant/60">
                      {new Date(mistake.timestamp).toLocaleDateString()}
                    </span>
                  )}
                </div>

                {/* 错误词汇 */}
                <div className="mb-3">
                  <p className="text-xs text-on-surface-variant/60 mb-1">错误词汇</p>
                  <p className="text-lg font-display font-bold text-error line-through decoration-error/30">
                    {mistake.word}
                  </p>
                </div>

                {/* 正确形式 */}
                {mistake.correction && (
                  <div className="mb-3">
                    <p className="text-xs text-on-surface-variant/60 mb-1">正确形式</p>
                    <p className="text-lg font-display font-bold text-primary">
                      {mistake.correction}
                    </p>
                  </div>
                )}

                {/* 上下文 */}
                {mistake.context && (
                  <div>
                    <p className="text-xs text-on-surface-variant/60 mb-1">上下文</p>
                    <div className="bg-surface-container-low p-3 rounded-xl">
                      <p className="text-sm text-on-surface italic">{mistake.context}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}