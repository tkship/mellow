import React, { useState, useRef, useEffect } from 'react';
import { Tutor, Message, TUTORS, TutorId } from '../types';

interface ChatViewProps {
  currentTutor: Tutor;
  messages: Message[];
  onSendMessage: (text: string) => void;
  onStartVoiceCall: () => void;
  suggestedPrompts: string[];
  isWaitingForAi: boolean;
}

export default function ChatView({
  currentTutor,
  messages,
  onSendMessage,
  onStartVoiceCall,
  suggestedPrompts,
  isWaitingForAi,
}: ChatViewProps) {
  const [inputText, setInputText] = useState('');
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isWaitingForAi]);

  const handleSend = () => {
    if (!inputText.trim()) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-background relative selection:bg-primary-container selection:text-on-primary-container">
      {/* Scrollable Chat Area */}
      <div className="flex-grow overflow-y-auto scrollbar-none px-4 py-6 md:px-8 space-y-6 pb-[160px] max-w-3xl mx-auto w-full">
        {/* Chat History */}
        <div className="flex flex-col gap-6">
          {/* System Timestamp */}
          <div className="text-center">
            <span className="inline-block px-3 py-1 bg-surface-container-high rounded-full text-xs font-bold font-sans text-on-surface-variant/70 shadow-sm">
              Today 9:41 AM
            </span>
          </div>

          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            if (isUser) {
              return (
                <div key={msg.id} className="flex items-end justify-end gap-3 animate-fade-in-up">
                  <div className="max-w-[85%] bg-primary-container rounded-2xl rounded-tr-none p-4 shadow-[0_4px_15px_rgba(78,205,196,0.15)] text-on-primary-container">
                    <p className="font-sans text-[15px] leading-relaxed whitespace-pre-line">{msg.text}</p>
                  </div>
                </div>
              );
            } else {
              return (
                <div key={msg.id} className="flex items-start gap-3 animate-fade-in-up">
                  {/* Tutor Avatar */}
                  <div className="flex-shrink-0 w-10 h-10 bg-surface-container-highest rounded-full flex items-center justify-center shadow-sm overflow-hidden border border-primary/10">
                    <img
                      alt={currentTutor.name}
                      className="w-full h-full object-cover"
                      src={currentTutor.avatar}
                      referrerPolicy="no-referrer"
                    />
                  </div>
                  <div className="max-w-[85%] bg-surface-container-low rounded-2xl rounded-tl-none p-4 shadow-[0_2px_10px_rgba(0,0,0,0.02)] border border-primary/5">
                    <p className="font-sans text-[15px] text-on-surface leading-relaxed whitespace-pre-line">{msg.text}</p>

                    {/* Dynamic Suggested prompts nested inside AI bubble */}
                    {msg.suggestedPrompts && msg.suggestedPrompts.length > 0 && (
                      <div className="bg-surface-container-lowest p-3 rounded-xl border border-primary/10 mt-3">
                        <p className="text-[11px] font-bold text-primary uppercase tracking-wider mb-1 font-sans">
                          Suggested Answers / Prompts
                        </p>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {msg.suggestedPrompts.map((prompt, pIdx) => (
                            <button
                              key={pIdx}
                              onClick={() => {
                                onSendMessage(prompt);
                              }}
                              className="px-3 py-1.5 bg-surface rounded-full text-xs text-primary border border-primary/25 hover:bg-primary/5 hover:border-primary/50 transition-colors cursor-pointer font-sans"
                            >
                              {prompt}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            }
          })}

          {/* AI Busy Indicator */}
          {isWaitingForAi && (
            <div className="flex items-start gap-3 opacity-70 animate-pulse">
              <div className="flex-shrink-0 w-10 h-10 bg-surface-container-highest rounded-full flex items-center justify-center overflow-hidden">
                <img
                  alt={currentTutor.name}
                  className="w-full h-full object-cover"
                  src={currentTutor.avatar}
                  referrerPolicy="no-referrer"
                />
              </div>
              <div className="bg-surface-container-low rounded-2xl rounded-tl-none px-4 py-3 flex gap-1 items-center shadow-sm">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
              </div>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>
      </div>

      {/* Input Area Bottom Panel */}
      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-background via-background/95 to-transparent pt-12 pb-6 px-4 z-40">
        <div className="max-w-3xl mx-auto flex gap-3 items-center">
          {/* Suggestion Quick Chips on Top of Textarea for Active screen context */}
          {suggestedPrompts && suggestedPrompts.length > 0 && !isWaitingForAi && (
            <div className="absolute top-0 left-4 right-4 flex gap-2 overflow-x-auto py-1 scrollbar-none max-w-3xl mx-auto justify-start">
              {suggestedPrompts.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => onSendMessage(chip)}
                  className="whitespace-nowrap px-3 py-1 bg-surface-container-lowest hover:bg-surface-container border border-primary/10 rounded-full text-xs text-primary transition-colors cursor-pointer shadow-sm font-sans shrink-0"
                >
                  {chip}
                </button>
              ))}
            </div>
          )}

          {/* Input Box Wrapper */}
          <div className="flex-grow flex items-center bg-surface-container-lowest border border-primary/10 rounded-3xl pl-4 pr-2 py-1.5 focus-within:border-primary/35 focus-within:ring-1 focus-within:ring-primary/25 shadow-[0_4px_20px_rgba(0,0,0,0.03)] min-h-[52px]">
            <textarea
              className="flex-grow bg-transparent text-[15px] text-on-surface resize-none overflow-hidden max-h-[120px] focus:outline-none placeholder:text-outline py-2 pr-2"
              placeholder={`Message ${currentTutor.name}... (Enter to send)`}
              rows={1}
              value={inputText}
              onKeyDown={handleKeyDown}
              onChange={(e) => setInputText(e.target.value)}
            />
            <button
              onClick={handleSend}
              className="text-primary hover:bg-primary-container/10 rounded-full transition-colors w-9 h-9 flex items-center justify-center cursor-pointer shrink-0"
            >
              <span className="material-symbols-outlined text-[20px] leading-none" style={{ fontVariationSettings: "'FILL' 1" }}>
                send
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
