import React, { useState } from 'react';
import { CEFRGoal } from '../types';

interface LearnViewProps {
  level: CEFRGoal;
  vocabCount: number;
  streak: number;
}

interface ChartDataPoint {
  day: string;
  minutes: number;
  coordX: number;
  coordY: number;
}

const WEEK_DATA_CURRENT: ChartDataPoint[] = [
  { day: 'Mon', minutes: 15, coordX: 5, coordY: 45 },
  { day: 'Tue', minutes: 22, coordX: 20, coordY: 38 },
  { day: 'Wed', minutes: 18, coordX: 35, coordY: 41 },
  { day: 'Thu', minutes: 35, coordX: 50, coordY: 28 },
  { day: 'Fri', minutes: 48, coordX: 65, coordY: 18 },
  { day: 'Sat', minutes: 42, coordX: 80, coordY: 22 },
  { day: 'Sun', minutes: 60, coordX: 95, coordY: 5 }
];

const WEEK_DATA_PREVIOUS: ChartDataPoint[] = [
  { day: 'Mon', minutes: 30, coordX: 5, coordY: 25 },
  { day: 'Tue', minutes: 25, coordX: 20, coordY: 30 },
  { day: 'Wed', minutes: 40, coordX: 35, coordY: 18 },
  { day: 'Thu', minutes: 10, coordX: 50, coordY: 47 },
  { day: 'Fri', minutes: 28, coordX: 65, coordY: 32 },
  { day: 'Sat', minutes: 55, coordX: 80, coordY: 9 },
  { day: 'Sun', minutes: 50, coordX: 95, coordY: 12 }
];

const LEVEL_DESC: Record<CEFRGoal, string> = {
  A1: 'Beginner. Laying down strong linguistic foundations.',
  A2: 'Elementary. Building practical conversational phrases.',
  B1: 'Intermediate. Navigating daily expressions standardly.',
  B2: 'Upper Intermediate. You are flowing beautifully.',
  C1: 'Advanced. Expressing abstract thoughts with precision.',
  C2: 'Proficient. Perfect integration and near-native structure.'
};

export default function LearnView({ level, vocabCount, streak }: LearnViewProps) {
  const [activeWeek, setActiveWeek] = useState<'current' | 'previous'>('current');
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const chartPoints = activeWeek === 'current' ? WEEK_DATA_CURRENT : WEEK_DATA_PREVIOUS;

  // Render SVG Smooth Curve Helper
  // Generates d="M px py C ..." SVG path
  const curvePath = "M 5, " + chartPoints[0].coordY + " " + chartPoints.map((p, i) => {
    if (i === 0) return '';
    const prev = chartPoints[i - 1];
    const cpX1 = prev.coordX + (p.coordX - prev.coordX) / 2;
    const cpY1 = prev.coordY;
    const cpX2 = prev.coordX + (p.coordX - prev.coordX) / 2;
    const cpY2 = p.coordY;
    return `C ${cpX1},${cpY1} ${cpX2},${cpY2} ${p.coordX},${p.coordY}`;
  }).join(' ');

  // SVG Area path for gradient background fill under the curve
  const fillPath = `${curvePath} L 95,50 L 5,50 Z`;

  return (
    <div className="bg-background text-on-background h-full overflow-y-auto pb-6">
      <main className="max-w-7xl mx-auto px-4 py-8 md:px-8">
        {/* Header Section */}
        <section className="mb-8 mt-2">
          <h2 className="font-display text-2xl md:text-[32px] font-bold text-on-surface mb-2">学习大本营</h2>
          <p className="text-body-md text-on-surface-variant font-sans">
            Welcome back. Your mind is clear, ready to absorb new knowledge.
          </p>
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
              <div className="font-display text-5xl font-bold text-primary mb-2">{level}</div>
              <p className="text-body-sm text-on-surface-variant font-sans">
                {LEVEL_DESC[level] || LEVEL_DESC.B2}
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
                {vocabCount.toLocaleString()}
              </div>
              <p className="text-body-sm text-on-surface-variant font-sans">
                +42 words this week. Expanding horizons.
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
                {streak} <span className="font-normal text-headline-sm text-on-surface">Days</span>
              </div>
              <p className="text-body-sm text-on-surface-variant font-sans">
                Unbroken stillness. A perfect month.
              </p>
            </div>
          </div>
        </section>

        {/* Chart Section */}
        <section className="bg-surface-container-lowest rounded-3xl p-6 md:p-8 mb-10 shadow-sm border border-outline-variant/10 relative">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="font-display font-bold text-headline-md text-on-surface mb-1">学习进度表</h3>
              <p className="text-body-sm text-on-surface-variant font-sans">
                Your journey over the last 7 days.
              </p>
            </div>

            {/* Toggle Dropdown Option */}
            <div className="relative">
              <button
                onClick={() => setActiveWeek(activeWeek === 'current' ? 'previous' : 'current')}
                className="px-4 py-2 rounded-full bg-surface-container hover:bg-surface-container-high transition-colors text-xs font-bold text-on-surface flex items-center gap-2 cursor-pointer shadow-sm"
              >
                <span>{activeWeek === 'current' ? 'This Week' : 'Last Week'}</span>
                <span className="material-symbols-outlined text-[16px]">expand_more</span>
              </button>
            </div>
          </div>

          {/* Interactive Chart Core using pixel accurate scalable vector graphics */}
          <div className="relative w-full h-72 border-b border-outline-variant/20 pt-4 pb-10 px-4">
            {/* Hover Tooltip Overlay */}
            {hoveredIndex !== null && (
              <div
                className="absolute bg-inverse-surface text-inverse-on-surface text-xs rounded-xl shadow-md p-2.5 z-20 pointer-events-none transition-all duration-200 flex flex-col items-center gap-0.5"
                style={{
                  left: `${chartPoints[hoveredIndex].coordX}%`,
                  top: `${chartPoints[hoveredIndex].coordY - 14}%`,
                  transform: 'translate(-50%, -100%)'
                }}
              >
                <span className="font-bold">{chartPoints[hoveredIndex].day}</span>
                <span className="text-[11px] opacity-90">{chartPoints[hoveredIndex].minutes} min practiced</span>
              </div>
            )}

            {/* SVG Chart Curve */}
            <div className="absolute inset-0 pb-10 flex items-end">
              <svg
                className="w-full h-full overflow-visible drop-shadow-[0_8px_16px_rgba(78,205,196,0.3)]Ref"
                preserveAspectRatio="none"
                viewBox="0 0 100 50"
              >
                <defs>
                  <linearGradient id="chartGlow" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="#4ECDC4" stopOpacity="0.2" />
                    <stop offset="100%" stopColor="#4ECDC4" stopOpacity="0" />
                  </linearGradient>
                </defs>

                {/* Shaded Area Under Curve */}
                <path d={fillPath} fill="url(#chartGlow)" />

                {/* Structural Grid lines (Dynamic still ripples) */}
                <line x1="5" y1="0" x2="95" y2="0" stroke="rgba(0,106,101,0.03)" strokeWidth="0.5" />
                <line x1="5" y1="12.5" x2="95" y2="12.5" stroke="rgba(0,106,101,0.03)" strokeWidth="0.5" />
                <line x1="5" y1="25" x2="95" y2="25" stroke="rgba(0,106,101,0.03)" strokeWidth="0.5" />
                <line x1="5" y1="37.5" x2="95" y2="37.5" stroke="rgba(0,106,101,0.03)" strokeWidth="0.5" />

                {/* The Main Curve */}
                <path
                  d={curvePath}
                  fill="none"
                  stroke="#4ECDC4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="4"
                  className="transition-all duration-500"
                />

                {/* Node Circles */}
                {chartPoints.map((point, index) => {
                  const isHovered = index === hoveredIndex;
                  return (
                    <g key={index}>
                      {/* Interactive invisible touch target overlay */}
                      <circle
                        cx={point.coordX}
                        cy={point.coordY}
                        r="6"
                        fill="transparent"
                        className="cursor-pointer"
                        onMouseEnter={() => setHoveredIndex(index)}
                        onMouseLeave={() => setHoveredIndex(null)}
                      />
                      {/* Visual styling stroke circle */}
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

            {/* X-Axis Labels */}
            <div className="absolute bottom-0 left-0 right-0 flex justify-between px-6 font-bold font-sans text-xs text-on-surface-variant/60 pb-2 border-t border-outline-variant/10 pt-2">
              {chartPoints.map((p) => (
                <span key={p.day}>{p.day}</span>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
