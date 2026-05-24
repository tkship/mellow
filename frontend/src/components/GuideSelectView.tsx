import React, { useRef, useEffect, useState } from 'react';
import { PersonaDisplay } from '../types';
import { getPersonaVoiceUrl } from '../api/persona';

interface GuideSelectViewProps {
  personas: PersonaDisplay[];
  loading: boolean;
  selectedId: string;
  onSelectTutor: (id: string) => void;
  onConfirmSelection: () => void;
  playingPersonaId: string | null;
  onPlayVoice: (personaId: string) => void;
}

export default function GuideSelectView({
  personas,
  loading,
  selectedId,
  onSelectTutor,
  onConfirmSelection,
  playingPersonaId,
  onPlayVoice,
}: GuideSelectViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const [dragOffset, setDragOffset] = useState(0);
  const [viewportWidth, setViewportWidth] = useState(375);
  const [isSwiping, setIsSwiping] = useState(false);
  const startX = useRef(0);

  // Split into preset and custom personas
  const presetPersonas = personas.filter((p) => !p.isCustom);
  const customPersonas = personas.filter((p) => p.isCustom);

  // Use ALL personas for carousel, but only preset ones by default
  const carouselPersonas = presetPersonas.length > 0 ? presetPersonas : personas;
  const activeIndex = Math.max(0, carouselPersonas.findIndex((p) => p.id === selectedId));

  // Read client viewport size
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        setViewportWidth(containerRef.current.offsetWidth);
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Isomorphic Mouse and Touch drag coordinates tracking
  const handleDragStart = (clientX: number) => {
    setIsSwiping(true);
    startX.current = clientX;
  };

  const handleDragMove = (clientX: number) => {
    if (!isSwiping) return;
    const distance = clientX - startX.current;
    setDragOffset(distance);
  };

  const handleDragEnd = () => {
    if (!isSwiping) return;
    setIsSwiping(false);

    const swipeThreshold = 55;
    if (dragOffset > swipeThreshold) {
      const prevIdx = (activeIndex - 1 + carouselPersonas.length) % carouselPersonas.length;
      onSelectTutor(carouselPersonas[prevIdx].id);
    } else if (dragOffset < -swipeThreshold) {
      const nextIdx = (activeIndex + 1) % carouselPersonas.length;
      onSelectTutor(carouselPersonas[nextIdx].id);
    }
    setDragOffset(0);
  };

  // Click handler to select side cards directly
  const handleSideCardClick = (index: number) => {
    if (index !== activeIndex) {
      onSelectTutor(carouselPersonas[index].id);
    }
  };

  const getInitialCircleClasses = (id: string): string => {
    const colors = [
      'bg-primary/20 text-primary',
      'bg-amber-500/20 text-amber-400',
      'bg-emerald-500/20 text-emerald-400',
      'bg-violet-500/20 text-violet-400',
      'bg-rose-500/20 text-rose-400',
      'bg-cyan-500/20 text-cyan-400',
    ];
    let hash = 0;
    for (let i = 0; i < id.length; i++) {
      hash = id.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  const getCardTransformAndStyle = (index: number) => {
    let diff = index - activeIndex;

    if (diff > 1) diff -= carouselPersonas.length;
    if (diff < -1) diff += carouselPersonas.length;

    const isMobile = viewportWidth < 640;
    const horizontalSpacing = isMobile ? 75 : 160;
    const dragRatio = dragOffset / 120;

    let translateX = 0;
    let translateY = 10;
    let rotation = 0;
    let scale = 0.88;
    let zIndex = 10;
    let opacity = 0.40;
    let blurPx = 1.5;

    if (diff === 0) {
      translateX = dragOffset;
      translateY = -5;
      rotation = dragRatio * 6;
      scale = 1.02 - Math.abs(dragRatio) * 0.08;
      zIndex = 30;
      opacity = 1;
      blurPx = 0;
    } else if (diff === -1) {
      translateX = -horizontalSpacing + dragOffset * 0.35;
      translateY = 8;
      rotation = -6 + dragRatio * 6;
      scale = 0.88 + dragRatio * 0.08;
      zIndex = 20;
      opacity = 0.45 + dragRatio * 0.35;
      blurPx = Math.max(0, 1.5 - dragRatio * 1.5);
    } else if (diff === 1) {
      translateX = horizontalSpacing + dragOffset * 0.35;
      translateY = 8;
      rotation = 6 + dragRatio * 6;
      scale = 0.88 - dragRatio * 0.08;
      zIndex = 20;
      opacity = 0.45 - dragRatio * 0.35;
      blurPx = Math.max(0, 1.5 + dragRatio * 1.5);
    }

    return {
      style: {
        transform: `translateX(${translateX}px) translateY(${translateY}px) rotate(${rotation}deg) scale(${scale})`,
        zIndex,
        opacity: Math.max(0.1, Math.min(1, opacity)),
        filter: blurPx > 0 ? `blur(${blurPx}px)` : 'none',
        pointerEvents: 'auto',
      } as React.CSSProperties,
      diff,
    };
  };

  return (
    <div className="bg-background text-on-background w-full h-full flex flex-col justify-between items-center relative overflow-hidden bg-tech-pattern p-3 md:p-5 select-none animate-fade-in">
      {/* Background ambient light bubbles */}
      <div className="absolute top-[-5%] left-[10%] w-[500px] h-[500px] bg-primary-container/5 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-5%] right-[10%] w-[500px] h-[500px] bg-secondary-container/5 rounded-full blur-[100px] pointer-events-none" />

      <main className="flex-grow flex flex-col items-center justify-between max-w-[1240px] mx-auto w-full z-10 relative py-1 md:py-2 gap-3">
        {/* Minimalist Compact Header */}
        <div className="text-center w-full animate-fade-in shrink-0">
          <h1 className="font-display text-lg md:text-xl lg:text-2xl font-bold text-primary/95 tracking-tight">
            选择你的口语向导
          </h1>
          <p className="text-[11px] md:text-xs text-on-surface-variant/80 mt-0.5">
            左右滑动卡片发现契合你的陪伴导师
          </p>
        </div>

        {/* Dynamic Generous Card Deck */}
        <div
          ref={containerRef}
          className="relative w-full max-w-4xl h-[42vh] min-h-[290px] max-h-[460px] flex items-center justify-center cursor-grab active:cursor-grabbing my-auto"
          onTouchStart={(e) => handleDragStart(e.touches[0].clientX)}
          onTouchMove={(e) => handleDragMove(e.touches[0].clientX)}
          onTouchEnd={handleDragEnd}
          onMouseDown={(e) => handleDragStart(e.clientX)}
          onMouseMove={(e) => handleDragMove(e.clientX)}
          onMouseUp={handleDragEnd}
          onMouseLeave={handleDragEnd}
        >
          {loading && (
            <>
              {[0, 1, 2].map((i) => (
                <div
                  key={`skeleton-${i}`}
                  className="absolute w-[240px] sm:w-[280px] md:w-[310px] h-[40vh] min-h-[270px] max-h-[420px] flex flex-col bg-slate-950 rounded-2xl overflow-hidden border border-white/10"
                  style={{
                    transform:
                      i === 0
                        ? 'translateX(0px) translateY(-5px) rotate(0deg) scale(1.02)'
                        : i === 1
                          ? 'translateX(160px) translateY(8px) rotate(6deg) scale(0.88)'
                          : 'translateX(-160px) translateY(8px) rotate(-6deg) scale(0.88)',
                    zIndex: i === 0 ? 30 : 20,
                    opacity: i === 0 ? 1 : 0.45,
                    pointerEvents: 'none',
                  }}
                >
                  <div className="h-[62%] w-full bg-slate-800 flex items-center justify-center animate-pulse">
                    <div className="w-24 h-24 rounded-full bg-slate-700" />
                  </div>
                  <div className="p-3.5 flex flex-col flex-grow justify-between bg-slate-950 border-t border-white/5 animate-pulse">
                    <div className="flex flex-col gap-2">
                      <div className="h-4 w-28 bg-slate-700 rounded" />
                      <div className="h-3 w-36 bg-slate-700 rounded" />
                    </div>
                    <div className="space-y-1.5">
                      <div className="h-3 w-full bg-slate-700 rounded" />
                      <div className="h-3 w-2/3 bg-slate-700 rounded" />
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}

          {!loading && carouselPersonas.length === 0 && (
            <div className="text-center py-10">
              <p className="text-on-surface-variant/60 text-sm">暂无可用角色</p>
            </div>
          )}

          {!loading &&
            carouselPersonas.map((persona, idx) => {
              const isSelected = selectedId === persona.id;
              const cardInfo = getCardTransformAndStyle(idx);
              const isPlaying = playingPersonaId === persona.id;

              return (
                <div
                  key={persona.id}
                  style={cardInfo.style}
                  onClick={() => handleSideCardClick(idx)}
                  className={`absolute w-[240px] sm:w-[280px] md:w-[310px] h-[40vh] min-h-[270px] max-h-[420px] flex flex-col bg-slate-950 rounded-2xl overflow-hidden border transition-all duration-300 select-none shadow-[0_24px_54px_rgba(0,106,101,0.15),0_10px_30px_rgba(0,0,0,0.06)] ${
                    isSelected
                      ? 'border-primary/60 bg-slate-950 ring-4 ring-primary/20 ring-offset-2 ring-offset-background'
                      : 'border-white/10 bg-slate-900 scale-90 opacity-45 cursor-pointer'
                  }`}
                >
                  {/* Avatar Area */}
                  <div className="relative h-[62%] w-full bg-slate-950 overflow-hidden pointer-events-none shrink-0">
                    {persona.avatar ? (
                      <>
                        <div
                          className="absolute inset-0 bg-cover bg-center filter blur-[15px] scale-125 opacity-35 brightness-75 transition-all duration-500"
                          style={{ backgroundImage: `url(${persona.avatar})` }}
                        />
                        <img
                          alt={persona.name}
                          className="relative z-10 w-full h-full object-cover transition-transform duration-700 select-none animate-fade-in"
                          src={persona.avatar}
                          referrerPolicy="no-referrer"
                        />
                      </>
                    ) : (
                      <div
                        className={`absolute inset-0 z-[5] w-full h-full flex items-center justify-center font-display font-bold text-3xl ${getInitialCircleClasses(persona.id)}`}
                      >
                        <span className="text-6xl md:text-7xl select-none">
                          {persona.name.charAt(0)}
                        </span>
                      </div>
                    )}
                    <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.08)_1px,transparent_1px)] bg-[size:16px_16px] opacity-20 z-10" />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/10 to-transparent z-15" />
                  </div>

                  {/* Info text */}
                  <div className="p-3.5 flex flex-col flex-grow justify-between select-none bg-slate-950 border-t border-white/5">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <h3 className="font-display font-bold text-sm md:text-base text-white">
                          {persona.name}
                        </h3>
                        <span className="text-[8px] text-primary font-display font-medium px-1.5 py-0.5 bg-primary/10 rounded border border-primary/20 whitespace-nowrap">
                          VIRTUAL TEACHER
                        </span>
                        {persona.tag && (
                          <span className="text-[8px] text-amber-400 font-display font-medium px-1.5 py-0.5 bg-amber-400/10 rounded border border-amber-400/20 whitespace-nowrap">
                            {persona.tag}
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] md:text-xs text-zinc-300 font-sans font-medium leading-snug line-clamp-1">
                        {persona.tagline}
                      </p>
                    </div>

                    {/* Voice Preview Button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onPlayVoice(persona.id);
                      }}
                      className={`mt-2 flex items-center justify-center gap-1.5 w-full py-1.5 rounded-xl text-[10px] font-semibold transition-all cursor-pointer ${
                        isPlaying
                          ? 'bg-primary/20 text-primary border border-primary/30'
                          : 'bg-white/5 text-zinc-400 border border-white/10 hover:bg-primary/10 hover:text-primary hover:border-primary/30'
                      }`}
                    >
                      <span
                        className={`material-symbols-outlined text-[14px] ${isPlaying ? 'animate-pulse' : ''}`}
                        style={{ fontVariationSettings: isPlaying ? "'FILL' 1" : "'FILL' 0" }}
                      >
                        {isPlaying ? 'volume_up' : 'volume_up'}
                      </span>
                      <span>{isPlaying ? '播放中...' : '试听声音'}</span>
                    </button>
                  </div>
                </div>
              );
            })}
        </div>

        {/* Custom Personas Section — only show when custom personas exist */}
        {!loading && customPersonas.length > 0 && (
          <div className="w-full max-w-xl mx-auto mt-2">
            <h3 className="font-display font-bold text-sm text-on-surface-variant mb-2 px-2">
              我的角色
            </h3>
            <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-none">
              {customPersonas.map((persona) => {
                const isSelected = selectedId === persona.id;
                const isPlaying = playingPersonaId === persona.id;
                return (
                  <button
                    key={persona.id}
                    onClick={() => onSelectTutor(persona.id)}
                    className={`flex-shrink-0 w-28 rounded-2xl overflow-hidden border transition-all cursor-pointer ${
                      isSelected
                        ? 'border-primary/60 ring-2 ring-primary/20 bg-white shadow-md'
                        : 'border-outline-variant/20 bg-white hover:border-primary/30 shadow-sm'
                    }`}
                  >
                    <div className={`h-20 w-full flex items-center justify-center ${getInitialCircleClasses(persona.id)}`}>
                      <span className="text-2xl font-display font-bold select-none">
                        {persona.name.charAt(0)}
                      </span>
                    </div>
                    <div className="p-2">
                      <p className="text-xs font-display font-bold text-on-surface truncate">{persona.name}</p>
                      <p className="text-[9px] text-on-surface-variant font-sans truncate">{persona.tagline || persona.role}</p>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onPlayVoice(persona.id);
                        }}
                        className={`mt-1 flex items-center justify-center gap-1 w-full py-0.5 rounded-lg text-[8px] font-semibold transition-all cursor-pointer ${
                          isPlaying
                            ? 'bg-primary/20 text-primary'
                            : 'bg-surface-container text-on-surface-variant hover:bg-primary/10 hover:text-primary'
                        }`}
                      >
                        <span className="material-symbols-outlined text-[10px]" style={{ fontVariationSettings: isPlaying ? "'FILL' 1" : "'FILL' 0" }}>
                          volume_up
                        </span>
                        {isPlaying ? '播放中' : '试听'}
                      </button>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Carousel Pagination Bottom Controls block */}
        {!loading && carouselPersonas.length > 0 && (
          <div className="flex flex-col items-center gap-2 shrink-0 w-full">
            <div className="flex justify-center items-center gap-1.5">
              {carouselPersonas.map((persona) => (
                <button
                  key={persona.id}
                  onClick={() => onSelectTutor(persona.id)}
                  className={`h-1 rounded-full transition-all duration-300 cursor-pointer ${
                    selectedId === persona.id
                      ? 'w-4 bg-primary'
                      : 'w-1 bg-outline-variant/30 hover:bg-outline-variant/60'
                  }`}
                  title={`切换至 ${persona.name}`}
                />
              ))}
            </div>

            <div className="animate-fade-in">
              <button
                onClick={onConfirmSelection}
                className="px-6 py-2 bg-primary text-white rounded-full font-bold text-[10px] tracking-wider uppercase shadow-md hover:brightness-105 active:scale-95 transition-all duration-300 font-sans flex items-center gap-1 cursor-pointer"
              >
                <span>确 定 选 择</span>
                <span className="material-symbols-outlined text-[12px]">arrow_forward</span>
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}