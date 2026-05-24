import React, { useState, useEffect } from 'react';

interface VoiceCallViewProps {
  personaName: string;
  onEndCall: () => void;
  onShowToast: (text: string, type?: 'success' | 'error') => void;
}

export default function VoiceCallView({ personaName, onEndCall, onShowToast }: VoiceCallViewProps) {
  const [seconds, setSeconds] = useState(0);
  const [isMuted, setIsMuted] = useState(false);

  // Counter Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (totalSecs: number) => {
    const mins = Math.floor(totalSecs / 60).toString().padStart(2, '0');
    const secs = (totalSecs % 60).toString().padStart(2, '0');
    return `${mins}:${secs}`;
  };

  return (
    <div className="bg-background flex flex-col font-sans text-on-surface bg-gradient-to-tr from-primary/10 via-surface to-surface-bright relative overflow-hidden h-screen max-h-screen">
      {/* Background Ambient Aura Spotlights */}
      <div className="absolute inset-0 z-0 flex items-center justify-center opacity-30 pointer-events-none">
        <div className="w-[450px] h-[450px] bg-primary-container rounded-full blur-[100px] mix-blend-multiply" />
      </div>

      <main className="flex-1 flex flex-col relative z-10 px-4 py-3 h-full max-h-full justify-between">
        {/* Top Header: Centered pristine Name & Status */}
        <header className="flex flex-col items-center pb-1 pt-2 shrink-0 text-center select-none">
          <h1 className="font-display font-bold text-xl text-on-surface mb-0.5">{personaName}</h1>
          <p className="text-[11px] text-primary font-bold animate-pulse font-sans tracking-wide uppercase">
            Voice Calling... {formatTime(seconds)}
          </p>
        </header>

        {/* Placeholder: Feature Under Development */}
        <section className="flex-grow flex flex-col items-center justify-center w-full max-w-2xl mx-auto my-2 px-2 border-t border-b border-primary/5 py-4">
          <div className="flex flex-col items-center gap-4 text-center animate-fade-in">
            <span className="text-5xl">🚧</span>
            <h2 className="font-display font-bold text-xl text-on-surface">
              语音功能开发中
            </h2>
            <p className="text-sm text-on-surface-variant font-sans max-w-xs leading-relaxed">
              下个版本上线，敬请期待
            </p>
            <div className="flex items-center gap-1.5 mt-2">
              <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
              <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
              <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
            </div>
          </div>
        </section>

        {/* Action Controls Footer */}
        <footer className="flex justify-center items-center gap-32 w-full pb-6 shrink-0 select-none">
          {/* Mute Microphone Button */}
          <button
            onClick={() => {
              onShowToast('语音功能开发中，下个版本上线', 'error');
            }}
            className="flex flex-col items-center gap-2 group cursor-pointer transition-transform duration-300 active:scale-95 hover:scale-105"
            title="语音功能开发中"
          >
            <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white shadow-md transition-all duration-300 ${
              !isMuted 
                ? 'bg-primary ring-4 ring-primary/20 animate-pulse shadow-[0_8px_24px_rgba(0,106,101,0.2)]' 
                : 'bg-slate-700 hover:bg-slate-600 shadow-[0_8px_24px_rgba(0,0,0,0.15)]'
            }`}>
              <span className="material-symbols-outlined text-[30px]" style={{ fontVariationSettings: `'FILL' ${!isMuted ? 1 : 0}` }}>
                {isMuted ? 'mic_off' : 'mic'}
              </span>
            </div>
            <span className="text-xs text-outline font-bold font-sans tracking-wide uppercase opacity-75">
              {isMuted ? '已静音' : '发言中'}
            </span>
          </button>

          {/* Hang-Up CTA Trigger */}
          <button
            onClick={() => {
              if ('speechSynthesis' in window) window.speechSynthesis.cancel();
              onEndCall();
            }}
            className="flex flex-col items-center gap-2 group cursor-pointer transition-transform duration-300 active:scale-95 hover:scale-105"
            title="挂断通话"
          >
            <div className="w-16 h-16 rounded-full bg-error flex items-center justify-center text-white shadow-[0_8px_24px_rgba(186,26,26,0.35)] hover:bg-red-700 transition-colors duration-300">
              <span className="material-symbols-outlined text-[30px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                call_end
              </span>
            </div>
            <span className="text-xs text-outline font-bold font-sans tracking-wide uppercase opacity-75">挂断</span>
          </button>
        </footer>
      </main>
    </div>
  );
}