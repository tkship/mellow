import React, { useState, useEffect, useRef } from 'react';
import { Tutor } from '../types';

interface VoiceCallViewProps {
  currentTutor: Tutor;
  onEndCall: () => void;
}

interface CallHistoryItem {
  speaker: 'tutor' | 'user';
  text: string;
}

const CONVERSATIONS: Record<string, CallHistoryItem[]> = {
  aura: [
    { speaker: 'tutor', text: "Hello there! I'm Aura. How was your day today?" },
    { speaker: 'user', text: "It was really nice, actually! I spent some time studying and relaxing." },
    { speaker: 'tutor', text: "That sounds wonderfully productive! What are you studying currently?" },
    { speaker: 'user', text: "I'm focusing on improving my fluent English speaking and listening." },
    { speaker: 'tutor', text: "A fantastic goal! Speaking daily is the single fastest way to gain confidence and flow." },
    { speaker: 'user', text: "I agree. Conversing with you is incredibly helpful." },
    { speaker: 'tutor', text: "Thank you! I'm always here to share ideas, explain idioms, and practice with you." },
  ],
  leo: [
    { speaker: 'tutor', text: "Hi! I'm Leo. Let's practice some English! How are you doing today?" },
    { speaker: 'user', text: "I am doing great, thank you! Ready to learn with you." },
    { speaker: 'tutor', text: "Awesome! Let's talk about food. What is your favorite daily meal?" },
    { speaker: 'user', text: "I really like home-cooked pasta. It is warm and comforting." },
    { speaker: 'tutor', text: "Yum, pasta is delicious! Simple recipes are often the best. Do you cook it yourself?" },
    { speaker: 'user', text: "Yes, I cook it with olive oil, garlic, and fresh herbs." },
    { speaker: 'tutor', text: "Splendid! Cooking is such a cozy, beautiful skill to practice." },
  ],
  chen: [
    { speaker: 'tutor', text: "Welcome. This is Dr. Chen. Let us focus on precise syntax and structured speaking today." },
    { speaker: 'user', text: "Yes, Doctor. I would like to structure my sentences with better grammar." },
    { speaker: 'tutor', text: "Excellent. Let us analyze a conditional statement first. What is your career goal?" },
    { speaker: 'user', text: "If I master oral English, I will represent my company globally." },
    { speaker: 'tutor', text: "Perfect usage of the first conditional! It specifies a probable future result." },
    { speaker: 'user', text: "Thank you, Dr. Chen. Your analysis makes grammar very easy to comprehend." },
    { speaker: 'tutor', text: "You are most welcome. Consistent practice will consolidate your structural elegance." },
  ],
};

export default function VoiceCallView({ currentTutor, onEndCall }: VoiceCallViewProps) {
  const [seconds, setSeconds] = useState(0);
  const tutorConvo = CONVERSATIONS[currentTutor.id] || CONVERSATIONS.aura;
  const [history, setHistory] = useState<CallHistoryItem[]>([tutorConvo[0]]);
  const [currentLineIndex, setCurrentLineIndex] = useState(1);
  const [isAiResponding, setIsAiResponding] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Counter Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Automatic spoken speech simulation with audio voice synthesis if supported
  useEffect(() => {
    const lastItem = history[history.length - 1];
    if (lastItem && lastItem.speaker === 'tutor' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(lastItem.text);
      utterance.lang = 'en-US';
      const voices = window.speechSynthesis.getVoices();
      const idealVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google'));
      if (idealVoice) utterance.voice = idealVoice;
      window.speechSynthesis.speak(utterance);
    }
  }, [history]);

  // Handle continuous simulation of natural voice dialog
  useEffect(() => {
    if (currentLineIndex < tutorConvo.length) {
      const nextLine = tutorConvo[currentLineIndex];
      const isNextUser = nextLine.speaker === 'user';
      
      const timeout = setTimeout(() => {
        if (isNextUser) {
          setIsAiResponding(false);
          setHistory((prev) => [...prev, nextLine]);
          setCurrentLineIndex((prev) => prev + 1);
        } else {
          setIsAiResponding(true);
          // AI processing ripple pause
          setTimeout(() => {
            setHistory((prev) => [...prev, nextLine]);
            setIsAiResponding(false);
            setCurrentLineIndex((prev) => prev + 1);
          }, 1500);
        }
      }, 4200); // beautiful interactive delay
      
      return () => clearTimeout(timeout);
    }
  }, [currentLineIndex, tutorConvo]);

  useEffect(() => {
    scrollContainerRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

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
          <h1 className="font-display font-bold text-xl text-on-surface mb-0.5">{currentTutor.name}</h1>
          <p className="text-[11px] text-primary font-bold animate-pulse font-sans tracking-wide uppercase">
            Voice Calling... {formatTime(seconds)}
          </p>
        </header>

        {/* Expanded Transcription dialog layout with scrollbar disabled */}
        <section className="flex-grow overflow-y-auto scrollbar-none w-full max-w-2xl mx-auto my-2 flex flex-col justify-end px-2 border-t border-b border-primary/5 py-4">
          <div className="space-y-4 overflow-y-auto scrollbar-none pr-1 w-full">
            {history.map((item, idx) => {
              const isUser = item.speaker === 'user';
              return (
                <div
                  key={idx}
                  className={`flex flex-col ${isUser ? 'items-end text-left' : 'items-start text-left'} gap-1 animate-fade-in`}
                >
                  <span className="text-[10px] font-bold tracking-wider text-primary/60 uppercase select-none">
                    {isUser ? 'You' : currentTutor.name}
                  </span>
                  <p
                    className={`font-display text-[15px] font-medium leading-relaxed max-w-[85%] p-3.5 rounded-2xl shadow-sm ${
                      isUser
                        ? 'bg-primary-container/20 text-on-surface rounded-tr-none'
                        : 'bg-primary text-white rounded-tl-none'
                    }`}
                  >
                    {item.text}
                  </p>
                </div>
              );
            })}
            
            {isAiResponding && (
              <div className="flex flex-col items-start gap-1">
                <span className="text-[10px] font-bold tracking-wider text-primary/60 uppercase select-none">
                  {currentTutor.name}
                </span>
                <div className="flex items-center gap-1.5 p-3.5 bg-primary/10 rounded-2xl rounded-tl-none">
                  <span className="w-2.5 h-2.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                  <span className="w-2.5 h-2.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
                  <span className="w-2.5 h-2.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
                </div>
              </div>
            )}
            <div ref={scrollContainerRef} />
          </div>
        </section>

        {/* Action Controls Footer */}
        <footer className="flex justify-center items-center gap-32 w-full pb-6 shrink-0 select-none">
          {/* Mute Microphone Button */}
          <button
            onClick={() => setIsMuted((prev) => !prev)}
            className="flex flex-col items-center gap-2 group cursor-pointer transition-transform duration-300 active:scale-95 hover:scale-105"
            title={isMuted ? "低调静音中 - 点击开启麦克风" : "发言中 - 点击静音麦克风"}
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
