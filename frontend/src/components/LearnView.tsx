import React, { useState, useMemo } from 'react';
import type { UserProfile } from '../types';
import type { ProfileStats, CefrProgressItem, WeeklyPlan } from '../api/profile';

// ===== Props =====

interface LearnViewProps {
  profile: UserProfile | null;
  stats: ProfileStats | null;
  isLoading: boolean;
  onRefresh: () => void;
  plan: WeeklyPlan | null;
  onCompletePlan: () => Promise<void>;
  onSetPlan: (data: WeeklyPlan) => Promise<void>;
}

// ===== Chart Types =====

interface ChartDataPoint {
  day: string;
  label: string;
  score: number;
  coordX: number;
  coordY: number;
}

// ===== Constants =====

const LEVEL_DESC: Record<string, string> = {
  A0: 'Pre-beginner. Just starting your language journey.',
  A1: 'Beginner. Laying down strong linguistic foundations.',
  A2: 'Elementary. Building practical conversational phrases.',
  B1: 'Intermediate. Navigating daily expressions standardly.',
  B2: 'Upper Intermediate. You are flowing beautifully.',
  C1: 'Advanced. Expressing abstract thoughts with precision.',
  C2: 'Proficient. Perfect integration and near-native structure.',
};

const DAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const DAY_NAMES = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

// ===== Chart Data Mapper =====

function mapCefrToChart(progress: CefrProgressItem[]): ChartDataPoint[] {
  const last7 = progress.length > 7 ? progress.slice(-7) : progress;

  return last7.map((item, index) => {
    const date = new Date(item.date);
    const dayLabel = isNaN(date.getTime()) ? `D${index + 1}` : DAY_LABELS[date.getDay()];

    const coordX = index * 15 + 5;
    const score = Math.max(0, Math.min(6, item.score ?? 0));
    const coordY = 50 - (score / 6) * 42;

    return {
      day: item.date,
      label: dayLabel,
      score,
      coordX,
      coordY,
    };
  });
}

// ===== Component =====

export default function LearnView({ profile, stats, isLoading, onRefresh, plan, onCompletePlan, onSetPlan }: LearnViewProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  // Plan form state
  const [showPlanForm, setShowPlanForm] = useState(false);
  const [planWeek, setPlanWeek] = useState(1);
  const [planTheme, setPlanTheme] = useState('');
  const [planSubmitting, setPlanSubmitting] = useState(false);
  const [completingDay, setCompletingDay] = useState<number | null>(null);

  const chartPoints = useMemo<ChartDataPoint[]>(() => {
    if (!stats?.cefr_progress || stats.cefr_progress.length === 0) return [];
    return mapCefrToChart(stats.cefr_progress);
  }, [stats?.cefr_progress]);

  const curvePath = useMemo(() => {
    if (chartPoints.length === 0) return '';
    return (
      'M 5, ' +
      chartPoints[0].coordY +
      ' ' +
      chartPoints
        .map((p, i) => {
          if (i === 0) return '';
          const prev = chartPoints[i - 1];
          const cpX1 = prev.coordX + (p.coordX - prev.coordX) / 2;
          const cpY1 = prev.coordY;
          const cpX2 = prev.coordX + (p.coordX - prev.coordX) / 2;
          const cpY2 = p.coordY;
          return `C ${cpX1},${cpY1} ${cpX2},${cpY2} ${p.coordX},${p.coordY}`;
        })
        .join(' ')
    );
  }, [chartPoints]);

  const fillPath = useMemo(() => {
    if (chartPoints.length === 0) return '';
    return `${curvePath} L 95,50 L 5,50 Z`;
  }, [curvePath]);

  const handleCreatePlan = async () => {
    if (!planTheme.trim()) return;
    setPlanSubmitting(true);
    try {
      await onSetPlan({
        week: planWeek,
        theme: planTheme.trim(),
        days: Array.from({ length: 7 }, (_, i) => ({
          day: i + 1,
          topic: `Day ${i + 1} - ${planTheme.trim()}`,
          vocabulary: [],
          grammar_point: '',
          practice: '',
        })),
        completed: false,
      });
      setShowPlanForm(false);
      setPlanTheme('');
      setPlanWeek(1);
    } finally {
      setPlanSubmitting(false);
    }
  };

  const handleCompleteDay = async (dayIndex: number) => {
    setCompletingDay(dayIndex);
    try {
      await onCompletePlan();
    } finally {
      setCompletingDay(null);
    }
  };

  // ===== Loading State (Shimmer Skeleton) =====

  if (isLoading) {
    return (
      <div className="bg-background text-on-background h-full overflow-y-auto pb-6">
        <main className="max-w-7xl mx-auto px-4 py-8 md:px-8">
          <section className="mb-8 mt-2">
            <div className="h-8 w-48 bg-surface-container rounded-lg animate-pulse mb-2" />
            <div className="h-4 w-80 bg-surface-container rounded animate-pulse" />
          </section>

          <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="bg-surface-container-lowest rounded-3xl p-6 flex flex-col justify-between aspect-square md:aspect-auto shadow-sm border border-outline-variant/10"
              >
                <div className="flex justify-between items-start mb-6">
                  <div className="h-3 w-16 bg-surface-container rounded animate-pulse" />
                  <div className="w-10 h-10 rounded-full bg-surface-container animate-pulse" />
                </div>
                <div>
                  <div className="h-12 w-24 bg-surface-container rounded-lg animate-pulse mb-2" />
                  <div className="h-4 w-40 bg-surface-container rounded animate-pulse" />
                </div>
              </div>
            ))}
          </section>

          <section className="bg-surface-container-lowest rounded-3xl p-6 md:p-8 mb-10 shadow-sm border border-outline-variant/10">
            <div className="h-6 w-32 bg-surface-container rounded animate-pulse mb-2" />
            <div className="h-4 w-48 bg-surface-container rounded animate-pulse mb-6" />
            <div className="h-72 bg-surface-container rounded-xl animate-pulse" />
          </section>
        </main>
      </div>
    );
  }

  // ===== Data-Loaded State =====

  return (
    <div className="bg-background text-on-background h-full overflow-y-auto pb-6">
      <main className="max-w-7xl mx-auto px-4 py-8 md:px-8">
        {/* Header Section */}
        <section className="mb-8 mt-2 flex justify-between items-start">
          <div>
            <h2 className="font-display text-2xl md:text-[32px] font-bold text-on-surface mb-2">
              学习大本营
            </h2>
            <p className="text-body-md text-on-surface-variant font-sans">
              Welcome back. Your mind is clear, ready to absorb new knowledge.
            </p>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            className="w-10 h-10 rounded-full bg-surface-container hover:bg-surface-container-high transition-colors flex items-center justify-center shadow-sm cursor-pointer"
            title="刷新数据"
          >
            <span className="material-symbols-outlined text-on-surface-variant text-[20px]">
              refresh
            </span>
          </button>
        </section>

        {/* Bento Grid Dashboard */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {/* CEFR Level Card */}
          <div className="bg-surface-container-lowest rounded-3xl p-6 flex flex-col justify-between aspect-square md:aspect-auto shadow-sm border border-outline-variant/10">
            <div className="flex justify-between items-start mb-6">
              <span className="text-xs font-bold font-sans text-on-surface-variant uppercase tracking-wider">
                当前等级
              </span>
              <div className="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-primary font-bold">school</span>
              </div>
            </div>
            <div>
              <div className="font-display text-5xl font-bold text-primary mb-2">
                {profile?.cefrLevel ?? '—'}
              </div>
              <p className="text-body-sm text-on-surface-variant font-sans">
                {profile?.cefrLevel && LEVEL_DESC[profile.cefrLevel]
                  ? LEVEL_DESC[profile.cefrLevel]
                  : 'Analyzing your level...'}
              </p>
            </div>
          </div>

          {/* Vocabulary Card */}
          <div className="bg-surface-container-lowest rounded-3xl p-6 flex flex-col justify-between aspect-square md:aspect-auto shadow-sm border border-outline-variant/10">
            <div className="flex justify-between items-start mb-6">
              <span className="text-xs font-bold font-sans text-on-surface-variant uppercase tracking-wider">
                词汇量
              </span>
              <div className="w-10 h-10 rounded-full bg-tertiary-container/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-tertiary font-bold">library_books</span>
              </div>
            </div>
            <div>
              <div className="font-display text-5xl font-bold text-on-surface mb-2">
                {profile?.vocabularySize != null
                  ? profile.vocabularySize.toLocaleString()
                  : '—'}
              </div>
              <p className="text-body-sm text-on-surface-variant font-sans">
                {profile?.summary ?? 'Building your word fortress.'}
              </p>
            </div>
          </div>

          {/* Streak Card */}
          <div className="bg-surface-container-lowest rounded-3xl p-6 flex flex-col justify-between aspect-square md:aspect-auto shadow-sm border border-outline-variant/10">
            <div className="flex justify-between items-start mb-6">
              <span className="text-xs font-bold font-sans text-on-surface-variant uppercase tracking-wider">
                连续学习
              </span>
              <div className="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center animate-pulse">
                <span className="material-symbols-outlined text-primary font-bold">local_fire_department</span>
              </div>
            </div>
            <div>
              <div className="font-display text-5xl font-bold text-primary mb-2">
                {profile?.streak ?? 0}{' '}
                <span className="font-normal text-headline-sm text-on-surface">Days</span>
              </div>
              <p className="text-body-sm text-on-surface-variant font-sans">
                {stats?.check_in_count != null
                  ? `You've checked in ${stats.check_in_count} times.`
                  : `${stats?.learning_days ?? 0} learning days in total.`}
              </p>
            </div>
          </div>
        </section>

        {/* Learning Plan Section */}
        <section className="bg-surface-container-lowest rounded-3xl p-6 md:p-8 mb-10 shadow-sm border border-outline-variant/10">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="font-display font-bold text-headline-md text-on-surface mb-1">
                本周学习计划
              </h3>
              <p className="text-body-sm text-on-surface-variant font-sans">
                {plan ? `主题：${plan.theme} · 第 ${plan.week} 周` : '制定你的学习计划，稳步提升'}
              </p>
            </div>
            {plan && (
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${plan.completed ? 'bg-primary-container text-primary' : 'bg-amber-100 text-amber-700'}`}>
                {plan.completed ? '已完成' : '进行中'}
              </span>
            )}
          </div>

          {plan ? (
            <div className="space-y-3">
              {plan.days.map((day, idx) => (
                <div
                  key={day.day}
                  className={`flex items-center gap-4 p-4 rounded-2xl border transition-all ${
                    plan.completed
                      ? 'bg-surface-container/50 border-outline-variant/5 opacity-60'
                      : 'bg-white border-primary/5 shadow-sm'
                  }`}
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-sm font-bold text-primary font-sans">{day.day}</span>
                  </div>
                  <div className="flex-grow min-w-0">
                    <p className={`text-sm font-medium font-sans ${plan.completed ? 'line-through text-on-surface-variant/60' : 'text-on-surface'}`}>
                      {DAY_NAMES[idx] ?? `Day ${day.day}`}: {day.topic}
                    </p>
                    {day.vocabulary.length > 0 && (
                      <p className="text-xs text-on-surface-variant mt-0.5 truncate">
                        词汇: {day.vocabulary.slice(0, 3).join(', ')}{day.vocabulary.length > 3 ? '...' : ''}
                      </p>
                    )}
                    {day.grammar_point && (
                      <p className="text-xs text-on-surface-variant mt-0.5">
                        语法: {day.grammar_point}
                      </p>
                    )}
                    {day.practice && (
                      <p className="text-xs text-on-surface-variant mt-0.5">
                        练习: {day.practice}
                      </p>
                    )}
                  </div>
                  {!plan.completed && (
                    <button
                      onClick={() => handleCompleteDay(day.day)}
                      disabled={completingDay !== null}
                      className="shrink-0 px-4 py-2 bg-primary/10 text-primary rounded-full text-xs font-semibold hover:bg-primary/20 transition-colors cursor-pointer disabled:opacity-50"
                    >
                      {completingDay === day.day ? '完成中...' : '完成本周'}
                    </button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              {showPlanForm ? (
                <div className="max-w-sm mx-auto space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-1 font-sans">
                      学习周数
                    </label>
                    <select
                      value={planWeek}
                      onChange={(e) => setPlanWeek(Number(e.target.value))}
                      className="w-full px-4 py-2.5 rounded-2xl bg-surface-container border border-outline-variant/20 text-sm text-on-surface focus:outline-none focus:border-primary/40 font-sans"
                    >
                      {[1, 2, 3, 4].map((w) => (
                        <option key={w} value={w}>第 {w} 周</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-1 font-sans">
                      学习主题
                    </label>
                    <input
                      type="text"
                      value={planTheme}
                      onChange={(e) => setPlanTheme(e.target.value)}
                      placeholder="例如：日常对话、旅行英语、商务表达"
                      className="w-full px-4 py-2.5 rounded-2xl bg-surface-container border border-outline-variant/20 text-sm text-on-surface placeholder:text-outline focus:outline-none focus:border-primary/40 font-sans"
                    />
                  </div>
                  <div className="flex gap-3 justify-center">
                    <button
                      onClick={() => setShowPlanForm(false)}
                      className="px-4 py-2 rounded-full text-sm font-semibold text-on-surface-variant bg-surface-container hover:bg-surface-container-high transition-colors cursor-pointer"
                    >
                      取消
                    </button>
                    <button
                      onClick={handleCreatePlan}
                      disabled={!planTheme.trim() || planSubmitting}
                      className="px-6 py-2 bg-primary text-white rounded-full text-sm font-semibold hover:bg-primary/90 transition-colors cursor-pointer disabled:opacity-50"
                    >
                      {planSubmitting ? '创建中...' : '创建计划'}
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-on-surface-variant/60 text-sm mb-4">暂无学习计划，制定一个开始吧</p>
                  <button
                    onClick={() => setShowPlanForm(true)}
                    className="px-6 py-2.5 bg-primary text-white rounded-full text-sm font-semibold hover:bg-primary/90 transition-colors cursor-pointer shadow-md"
                  >
                    创建学习计划
                  </button>
                </>
              )}
            </div>
          )}
        </section>

        {/* Chart Section */}
        <section className="bg-surface-container-lowest rounded-3xl p-6 md:p-8 mb-10 shadow-sm border border-outline-variant/10 relative">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="font-display font-bold text-headline-md text-on-surface mb-1">
                学习进度表
              </h3>
              <p className="text-body-sm text-on-surface-variant font-sans">
                Your journey over the last 7 days.
              </p>
            </div>
          </div>

          {chartPoints.length === 0 ? (
            <div className="relative w-full h-72 flex items-center justify-center border-b border-outline-variant/20 pt-4 pb-10 px-4">
              <p className="text-on-surface-variant text-body-md">暂无学习数据</p>
            </div>
          ) : (
            <div className="relative w-full h-72 border-b border-outline-variant/20 pt-4 pb-10 px-4">
              {/* Hover Tooltip Overlay */}
              {hoveredIndex !== null && (
                <div
                  className="absolute bg-inverse-surface text-inverse-on-surface text-xs rounded-xl shadow-md p-2.5 z-20 pointer-events-none transition-all duration-200 flex flex-col items-center gap-0.5"
                  style={{
                    left: `${chartPoints[hoveredIndex].coordX}%`,
                    top: `${chartPoints[hoveredIndex].coordY - 14}%`,
                    transform: 'translate(-50%, -100%)',
                  }}
                >
                  <span className="font-bold">{chartPoints[hoveredIndex].label}</span>
                  <span className="text-[11px] opacity-90">
                    Score: {chartPoints[hoveredIndex].score}
                  </span>
                </div>
              )}

              {/* SVG Chart Curve */}
              <div className="absolute inset-0 pb-10 flex items-end">
                <svg
                  className="w-full h-full overflow-visible drop-shadow-[0_8px_16px_rgba(78,205,196,0.3)]"
                  preserveAspectRatio="none"
                  viewBox="0 0 100 50"
                >
                  <defs>
                    <linearGradient id="chartGlow" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#4ECDC4" stopOpacity="0.2" />
                      <stop offset="100%" stopColor="#4ECDC4" stopOpacity="0" />
                    </linearGradient>
                  </defs>

                  <path d={fillPath} fill="url(#chartGlow)" />

                  <line x1="5" y1="0" x2="95" y2="0" stroke="rgba(0,106,101,0.03)" strokeWidth="0.5" />
                  <line x1="5" y1="12.5" x2="95" y2="12.5" stroke="rgba(0,106,101,0.03)" strokeWidth="0.5" />
                  <line x1="5" y1="25" x2="95" y2="25" stroke="rgba(0,106,101,0.03)" strokeWidth="0.5" />
                  <line x1="5" y1="37.5" x2="95" y2="37.5" stroke="rgba(0,106,101,0.03)" strokeWidth="0.5" />

                  <path
                    d={curvePath}
                    fill="none"
                    stroke="#4ECDC4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="4"
                    className="transition-all duration-500"
                  />

                  {chartPoints.map((point, index) => {
                    const isHovered = index === hoveredIndex;
                    return (
                      <g key={index}>
                        <circle
                          cx={point.coordX}
                          cy={point.coordY}
                          r="6"
                          fill="transparent"
                          className="cursor-pointer"
                          onMouseEnter={() => setHoveredIndex(index)}
                          onMouseLeave={() => setHoveredIndex(null)}
                        />
                        <circle
                          cx={point.coordX}
                          cy={point.coordY}
                          r={isHovered ? '4' : '3'}
                          fill={isHovered ? '#4ECDC4' : '#ffffff'}
                          stroke="#4ECDC4"
                          strokeWidth="2.5"
                          className="transition-all duration-200 pointer-events-none"
                        />
                      </g>
                    );
                  })}
                </svg>
              </div>

              <div className="absolute bottom-0 left-0 right-0 flex justify-between px-6 font-bold font-sans text-xs text-on-surface-variant/60 pb-2 border-t border-outline-variant/10 pt-2">
                {chartPoints.map((p, index) => (
                  <span key={index}>{p.label}</span>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}