import React, { useState, useEffect } from 'react';
import {
  TutorId,
  Message,
  MainTab,
  ScreenId,
  UserState,
  TUTORS
} from './types';
import LoginView from './components/LoginView';
import GuideSelectView from './components/GuideSelectView';
import ChatView from './components/ChatView';
import LearnView from './components/LearnView';
import ProfileView from './components/ProfileView';
import SettingsView from './components/SettingsView';
import VoiceCallView from './components/VoiceCallView';

const INITIAL_MESSAGES_MAPPING: Record<TutorId, Message[]> = {
  aura: [
    {
      id: 'aura_init',
      sender: 'ai',
      text: "Hello there! I'm Aura, your Mellow AI language guide. How can I help you clear your mind or build fluent speaking habits today?",
      timestamp: 'Today 9:41 AM',
      suggestedPrompts: ["Outline key points", "Suggest natural phrasing", "What is the cultural background?"]
    }
  ],
  leo: [
    {
      id: 'leo_init',
      sender: 'ai',
      text: "Hello! I am Leo, your patient English tutor. Let's make learning very simple and fun! We can talk about foods, standard hobbies, or your morning.",
      timestamp: 'Today 9:41 AM',
      suggestedPrompts: ["Help me learn simple words", "Ask me a simple question", "Let's practice!"]
    }
  ],
  chen: [
    {
      id: 'chen_init',
      sender: 'ai',
      text: "Welcome. This is Dr. Chen, your English grammatical and syntax Guide. How may I assist you with precise sentence analysis, lexical expansion, or lexical exercises today?",
      timestamp: 'Today 9:41 AM',
      suggestedPrompts: ["Analyze standard patterns", "Explain SVO structure", "Verify my expression"]
    }
  ]
};

const INITIAL_CHIPS_MAPPING: Record<TutorId, string[]> = {
  aura: ["Outline key points", "Defind audience", "English culture trivia", "Correct my sentence"],
  leo: ["Say that simply", "Let's discuss food", "Quick beginners tip", "What is 1,200 words equal to?"],
  chen: ["Analyze syntax structure", "Formal verbs vocabulary", "Practice writing grammar rules", "Show academic samples"]
};

export default function App() {
  const [user, setUser] = useState<UserState>({
    username: 'Elena Rostova',
    email: 'elena@mellow.ai',
    isLoggedIn: false, // Start at login screen
    level: 'B2',
    streak: 30,
    vocabCount: 1204,
    avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDY8CblACtq0jmq_2pHIOPIoPxWxlzl_Lakq_Omn5CJQfe7IOztNDDTVdX3rVrmof_NP7AlZBg9zhmpalLBRgcgQFfCyYhOjh7SvLSuaEu5wcf3PfTBkiaLdflB6t94bV3-SK1__haO5R10M-f02jAuV-7fP_Ym7Oe5Hfa4b6WojGt7dbP60Q0Eexn8lLTbIotzi4KphuP8ETCZOo3baR6KPxgMufW649ta8AI1JHT1SEyr_--LSwAfec7T0NywHRgaK_aVuyZ0Dg',
    bio: 'Curious Mind & Language Enthusiast',
    notifications: true,
    language: '简体中文',
    darkMode: false
  });

  useEffect(() => {
    if (user.darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [user.darkMode]);

  const [activeScreen, setActiveScreen] = useState<ScreenId>('login');
  const [activeTab, setActiveTab] = useState<MainTab>('chat');
  const [profileSection, setProfileSection] = useState<'main' | 'security'>('main');
  const [currentTutorId, setCurrentTutorId] = useState<TutorId>('aura');
  
  // Dynamic messages history mapping
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES_MAPPING.aura);
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>(INITIAL_CHIPS_MAPPING.aura);
  const [isWaitingForAi, setIsWaitingForAi] = useState(false);

  // Sync initial message context when changing tutors
  const handleSelectTutor = (id: TutorId) => {
    setCurrentTutorId(id);
    setMessages(INITIAL_MESSAGES_MAPPING[id]);
    setSuggestedPrompts(INITIAL_CHIPS_MAPPING[id]);
  };

  const handleSendMessage = async (newText: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: newText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setIsWaitingForAi(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tutorId: currentTutorId,
          messages: updatedMessages.map((m) => ({ sender: m.sender, text: m.text }))
        })
      });

      const data = await res.json();
      if (res.ok) {
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: data.text,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          suggestedPrompts: data.suggestedPrompts
        };
        setMessages((prev) => [...prev, aiMsg]);
        setSuggestedPrompts(data.suggestedPrompts || []);
        // Incremental Gamification Word count bonus when speaking! It builds massive joy
        setUser((prev) => {
          const countBonus = Math.floor(Math.random() * 3) + 2;
          return { ...prev, vocabCount: prev.vocabCount + countBonus };
        });
      } else {
        throw new Error(data.error || 'API Query Failed');
      }
    } catch (err: any) {
      console.error(err);
      // Fallback
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: "Looks like my neural connection experienced a slight ripple. Let's try again in a bit! (Please verify GEMINI_API_KEY in secrets setup for true AI answers!)",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsWaitingForAi(false);
    }
  };

  const handleLoginSuccess = (loginInfo: Partial<UserState>) => {
    setUser((prev) => ({ ...prev, ...loginInfo, isLoggedIn: true }));
    setActiveScreen('main'); // Direct to main screen (which has the bottom tabs)
    setActiveTab('chat');    // Landing page tab is character selection
  };

  const handleConfirmTutor = () => {
    setActiveScreen('chat'); // Go directly tofullscreen chat layout
  };

  const currentTutor = TUTORS[currentTutorId] || TUTORS.aura;

  const renderBottomTabs = () => {
    const isChatActive = activeTab === 'chat';
    const isLearnActive = activeTab === 'learn';
    const isProfileActive = activeTab === 'profile';

    return (
      <footer className="sticky bottom-0 z-50 border-t px-6 h-16 shrink-0 flex items-center justify-around select-none shadow-[0_-4px_16px_rgba(0,0,0,0.02)] transition-colors duration-300 bg-white/90 border-primary/5 backdrop-blur-md text-outline/75">
        <button
          onClick={() => {
            setActiveTab('chat');
          }}
          className={`flex flex-col items-center gap-1 cursor-pointer py-1 px-4 transition-all duration-300 ${
            isChatActive
              ? 'text-primary scale-105 font-semibold'
              : 'text-outline/75 hover:text-primary/70'
          }`}
        >
          <span className="material-symbols-outlined text-[23px]" style={{ fontVariationSettings: isChatActive ? "'FILL' 1" : "'FILL' 0" }}>
            chat_bubble
          </span>
          <span className="text-[10px] font-sans tracking-wide">AI导师</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('learn');
          }}
          className={`flex flex-col items-center gap-1 cursor-pointer py-1 px-4 transition-all duration-300 ${
            isLearnActive
              ? 'text-primary scale-105 font-semibold'
              : 'text-outline/75 hover:text-primary/70'
          }`}
        >
          <span className="material-symbols-outlined text-[23px]" style={{ fontVariationSettings: isLearnActive ? "'FILL' 1" : "'FILL' 0" }}>
            school
          </span>
          <span className="text-[10px] font-sans tracking-wide">学习</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('profile');
          }}
          className={`flex flex-col items-center gap-1 cursor-pointer py-1 px-4 transition-all duration-300 ${
            isProfileActive
              ? 'text-primary scale-105 font-semibold'
              : 'text-outline/75 hover:text-primary/70'
          }`}
        >
          <span className="material-symbols-outlined text-[23px]" style={{ fontVariationSettings: isProfileActive ? "'FILL' 1" : "'FILL' 0" }}>
            person
          </span>
          <span className="text-[10px] font-sans tracking-wide">我的</span>
        </button>
      </footer>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      {/* 1. LOGIN / REGISTER VIEW */}
      {activeScreen === 'login' && (
        <LoginView onLoginSuccess={handleLoginSuccess} />
      )}

      {/* 2. TUTOR GUIDE SELECTION */}
      {activeScreen === 'guideSelect' && (
        <GuideSelectView
          selectedTutorId={currentTutorId}
          onSelectTutor={handleSelectTutor}
          onConfirmSelection={handleConfirmTutor}
        />
      )}

      {/* 3. SIMULATED VOICE CALL (IMMERSIVE INTERACTIVE STATE) */}
      {activeScreen === 'voiceCall' && (
        <VoiceCallView
          currentTutor={currentTutor}
          onEndCall={() => setActiveScreen('chat')}
        />
      )}

      {/* 4. SETTINGS SECTION */}
      {activeScreen === 'settings' && (
        <SettingsView
          user={user}
          onUpdateUser={(updated) => setUser((prev) => ({ ...prev, ...updated }))}
          onGoBack={() => setActiveScreen('main')}
          onLogout={() => {
            setUser((prev) => ({ ...prev, isLoggedIn: false }));
            setActiveScreen('login');
          }}
        />
      )}

      {/* 5. MAIN HUB SCREEN */}
      {activeScreen === 'main' && (
        <div className="flex flex-col h-screen min-h-screen max-h-screen relative overflow-hidden bg-background">
          {/* Nav Tab Content Canvas */}
          <main className="flex-grow overflow-hidden relative">
            {activeTab === 'chat' && (
              <GuideSelectView
                selectedTutorId={currentTutorId}
                onSelectTutor={handleSelectTutor}
                onConfirmSelection={handleConfirmTutor}
              />
            )}
            
            {activeTab === 'learn' && (
              <LearnView
                level={user.level}
                vocabCount={user.vocabCount}
                streak={user.streak}
              />
            )}

            {activeTab === 'profile' && (
              <ProfileView
                user={user}
                onUpdateUser={(updated) => setUser((prev) => ({ ...prev, ...updated }))}
                currentSection={profileSection}
                onSectionChange={setProfileSection}
                onLogout={() => {
                  setUser((prev) => ({ ...prev, isLoggedIn: false }));
                  setProfileSection('main');
                  setActiveScreen('login');
                }}
              />
            )}
          </main>
          {renderBottomTabs()}
        </div>
      )}

      {/* 6. FULLSCREEN CHAT WINDOW (NO BOTTOM FOOTER TABS) */}
      {activeScreen === 'chat' && (
        <div className="flex flex-col h-screen min-h-screen max-h-screen relative overflow-hidden bg-background animate-fade-in">
          {/* Header specific to Chat, with BACK button and Call button */}
          <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-primary/5 px-6 h-16 flex items-center justify-between shrink-0">
            <div className="w-10">
              {/* Back to main selector tab */}
              <button
                onClick={() => {
                  setActiveScreen('main');
                  setActiveTab('chat');
                }}
                title="返回角色选择"
                className="w-10 h-10 flex items-center justify-center text-on-surface-variant hover:bg-primary-container/15 rounded-full transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined text-[20px]">arrow_back</span>
              </button>
            </div>
            
            {/* Header Title with chosen tutor guide context */}
            <div className="text-center flex items-center gap-2 justify-center">
              <div className="w-8 h-8 rounded-full overflow-hidden border border-primary/10 bg-surface shadow-sm shrink-0">
                <img
                  alt={currentTutor.name}
                  className="w-full h-full object-cover"
                  src={currentTutor.avatar}
                  referrerPolicy="no-referrer"
                />
              </div>
              <div className="text-left">
                <h1 className="font-display font-semibold text-sm md:text-base text-on-surface leading-tight">{currentTutor.name}</h1>
                <span className="text-[9px] text-primary/75 font-semibold font-sans tracking-wide block">
                  Online Language Partner
                </span>
              </div>
            </div>

            {/* Quick action: Launch Call inside Chat screen! */}
            <button
              onClick={() => setActiveScreen('voiceCall')}
              title="拨打实时语音通话"
              className="w-10 h-10 flex items-center justify-center text-primary bg-primary-container/10 hover:bg-primary-container/25 rounded-full transition-colors cursor-pointer animate-bounce-subtle shrink-0"
            >
              <span className="material-symbols-outlined text-[20px]">call</span>
            </button>
          </header>

          {/* Full Screen Chat Box wrapper */}
          <div className="flex-grow overflow-hidden relative">
            <ChatView
              currentTutor={currentTutor}
              messages={messages}
              onSendMessage={handleSendMessage}
              onStartVoiceCall={() => setActiveScreen('voiceCall')}
              suggestedPrompts={suggestedPrompts}
              isWaitingForAi={isWaitingForAi}
            />
          </div>
        </div>
      )}
    </div>
  );
}
