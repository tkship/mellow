import React, { useRef, useEffect, useState } from 'react';
import { TutorId, Tutor, TUTORS } from '../types';

interface GuideSelectViewProps {
  onSelectTutor: (id: TutorId) => void;
  selectedTutorId: TutorId;
  onConfirmSelection: () => void;
}

export default function GuideSelectView({
  onSelectTutor,
  selectedTutorId,
  onConfirmSelection,
}: GuideSelectViewProps) {
  const tutorsList = Object.values(TUTORS);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const [dragOffset, setDragOffset] = useState(0);
  const [viewportWidth, setViewportWidth] = useState(375);
  const [isSwiping, setIsSwiping] = useState(false);
  const startX = useRef(0);
  const activeIndex = tutorsList.findIndex((t) => t.id === selectedTutorId);

  // Read client viewport size for highly accurate responsive offsets
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

    const swipeThreshold = 55; // Quick responsive trigger distance to cycle roles
    if (dragOffset > swipeThreshold) {
      // Swiped right -> go to previous tutor
      const prevIdx = (activeIndex - 1 + tutorsList.length) % tutorsList.length;
      onSelectTutor(tutorsList[prevIdx].id);
    } else if (dragOffset < -swipeThreshold) {
      // Swiped left -> go to next tutor
      const nextIdx = (activeIndex + 1) % tutorsList.length;
      onSelectTutor(tutorsList[nextIdx].id);
    }
    setDragOffset(0);
  };

  // Click handler to select side cards directly
  const handleSideCardClick = (index: number) => {
    if (index !== activeIndex) {
      onSelectTutor(tutorsList[index].id);
    }
  };

  // Dynamic layout & transformations styling logic
  const getCardTransformAndStyle = (index: number) => {
    let diff = index - activeIndex;
    
    // Circular wrap for 3 items
    if (diff > 1) diff -= tutorsList.length;
    if (diff < -1) diff += tutorsList.length;

    const isMobile = viewportWidth < 640;
    const horizontalSpacing = isMobile ? 75 : 160; 
    const dragRatio = dragOffset / 120; // scale drag effect

    let translateX = 0;
    let translateY = 10;
    let rotation = 0;
    let scale = 0.88;
    let zIndex = 10;
    let opacity = 0.40;
    let blurPx = 1.5;

    if (diff === 0) {
      // CENTER CARD - active focused role
      translateX = dragOffset; // translates 1:1 with drag gesture for highly physical feel
      translateY = -5;
      rotation = dragRatio * 6; // active card rotates dynamically with drag direction
      scale = 1.02 - Math.abs(dragRatio) * 0.08;
      zIndex = 30;
      opacity = 1;
      blurPx = 0;
    } else if (diff === -1) {
      // LEFT GHOST CARD - fanning out to left background
      translateX = -horizontalSpacing + dragOffset * 0.35;
      translateY = 8;
      rotation = -6 + dragRatio * 6; // rotates towards center as dragged right
      scale = 0.88 + dragRatio * 0.08;
      zIndex = 20;
      opacity = 0.45 + dragRatio * 0.35;
      blurPx = Math.max(0, 1.5 - dragRatio * 1.5);
    } else if (diff === 1) {
      // RIGHT GHOST CARD - fanning out to right background
      translateX = horizontalSpacing + dragOffset * 0.35;
      translateY = 8;
      rotation = 6 + dragRatio * 6; // rotates towards center as dragged left
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
        pointerEvents: 'auto'
      } as React.CSSProperties,
      diff
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
          <h1 className="font-display text-lg md:text-xl lg:text-2xl font-bold text-primary/95 tracking-tight">选择你的口语向导</h1>
          <p className="text-[11px] md:text-xs text-on-surface-variant/80 mt-0.5">
            左右滑动卡片发现契合你的陪伴导师
          </p>
        </div>

        {/* Dynamic Generous Card Deck Interactive Stack Stage */}
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
          {tutorsList.map((tutor, idx) => {
            const isSelected = selectedTutorId === tutor.id;
            const cardInfo = getCardTransformAndStyle(idx);

            return (
              <div
                key={tutor.id}
                style={cardInfo.style}
                onClick={() => handleSideCardClick(idx)}
                className={`absolute w-[240px] sm:w-[280px] md:w-[310px] h-[40vh] min-h-[270px] max-h-[420px] flex flex-col bg-slate-950 rounded-2xl overflow-hidden border transition-all duration-300 select-none shadow-[0_24px_54px_rgba(0,106,101,0.15),0_10px_30px_rgba(0,0,0,0.06)] ${
                  isSelected 
                    ? 'border-primary/60 bg-slate-950 ring-4 ring-primary/20 ring-offset-2 ring-offset-background' 
                    : 'border-white/10 bg-slate-900 scale-90 opacity-45 cursor-pointer'
                }`}
              >
                {/* 1. Large Anime-style Character Frame */}
                <div className="relative h-[62%] w-full bg-slate-950 overflow-hidden pointer-events-none shrink-0">
                  {/* Backdrop Blurred Replication */}
                  <div 
                    className="absolute inset-0 bg-cover bg-center filter blur-[15px] scale-125 opacity-35 brightness-75 transition-all duration-500" 
                    style={{ backgroundImage: `url(${tutor.avatar})` }}
                  />
                  {/* High quality sci-fi overlays */}
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.08)_1px,transparent_1px)] bg-[size:16px_16px] opacity-20 z-10" />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/10 to-transparent z-15" />
                  
                  {/* Character image */}
                  <img
                    alt={tutor.name}
                    className="relative z-20 w-full h-full object-cover transition-transform duration-700 select-none animate-fade-in"
                    src={tutor.avatar}
                    referrerPolicy="no-referrer"
                  />
                </div>

                {/* 2. Compact Info text fitted inside the smaller card */}
                <div className="p-3.5 flex flex-col flex-grow justify-between select-none bg-slate-950 border-t border-white/5">
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-1.5">
                      <h3 className="font-display font-bold text-sm md:text-base text-white">
                        {tutor.name}
                      </h3>
                      <span className="text-[8px] text-primary font-display font-medium px-1.5 py-0.5 bg-primary/10 rounded border border-primary/20 whitespace-nowrap">
                        VIRTUAL TEACHER
                      </span>
                    </div>
                    <p className="text-[10px] md:text-xs text-zinc-300 font-sans font-medium leading-snug line-clamp-1">{tutor.tagline}</p>
                  </div>
                  <p className="text-[9px] md:text-[10px] text-zinc-400 font-sans leading-relaxed line-clamp-2">
                    {tutor.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Carousel Pagination Bottom Controls block */}
        <div className="flex flex-col items-center gap-2 shrink-0 w-full">
          {/* Carousel Pagination Indicator Dots */}
          <div className="flex justify-center items-center gap-1.5">
            {tutorsList.map((tutor) => (
              <button
                key={tutor.id}
                onClick={() => onSelectTutor(tutor.id)}
                className={`h-1 rounded-full transition-all duration-300 cursor-pointer ${
                  selectedTutorId === tutor.id ? 'w-4 bg-primary' : 'w-1 bg-outline-variant/30 hover:bg-outline-variant/60'
                }`}
                title={`切换至 ${tutor.name}`}
              />
            ))}
          </div>

          {/* Compact bottom selection confirm button */}
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
      </main>
    </div>
  );
}
