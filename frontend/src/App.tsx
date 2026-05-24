import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from './contexts/AuthContext';
import { listPersonas, listCustomPersonas, getPersonaVoiceUrl, type Persona } from './api/persona';
import { sendChatMessage, getChatStream, getChatHistory, getQuickPhrases, toggleMessageFavorite, deleteMessage, type ChatMessage as ApiChatMessage } from './api/chat';
import { getProfile, getProfileStats, getPlan, setPlan as setPlanApi, completePlan } from './api/profile';
import type { ProfileStats, WeeklyPlan } from './api/profile';
import { getEmotions, getFacts, getSummary, getProactiveMessages } from './api/memory';
import type { ProactiveMessage } from './api/memory';
import type {
  ScreenId,
  MainTab,
  Message,
  PersonaDisplay,
  UserProfile,
  ToastMessage,
} from './types';
import { PERSONA_DISPLAY_MAP, PERSONA_AVATAR_MAP } from './types';
import LoginView from './components/LoginView';
import GuideSelectView from './components/GuideSelectView';
import ChatView from './components/ChatView';
import LearnView from './components/LearnView';
import ProfileView from './components/ProfileView';
import SettingsView from './components/SettingsView';
import VoiceCallView from './components/VoiceCallView';
import VocabularyView from './components/VocabularyView';
import KnowledgeView from './components/KnowledgeView';
import MistakesView from './components/MistakesView';
import Toast from './components/Toast';
import ConfirmDialog from './components/ConfirmDialog';

// ===== Persona → Display 转换 =====

function personaToDisplay(p: Persona, isCustom = false): PersonaDisplay {
  const display = PERSONA_DISPLAY_MAP[p.id] || { name: p.name, tagline: p.language_style?.tone || '' };
  const avatar = PERSONA_AVATAR_MAP[p.id] || '';
  return {
    id: p.id,
    name: display.name,
    role: p.role,
    tagline: display.tagline || p.language_style?.tone || '',
    description: `${display.name} focuses on ${p.language_style?.tone || 'natural'} communication with a ${p.teaching_style?.approach || 'guided'} approach.`,
    tag: display.tag,
    avatar,
    isCustom,
  };
}

// ===== App =====

export default function App() {
  const { user, isLoggedIn, isLoading: authLoading, logout } = useAuth();

  // 路由
  const [activeScreen, setActiveScreen] = useState<ScreenId>('login');
  const [activeTab, setActiveTab] = useState<MainTab>('chat');

  // 角色
  const [personas, setPersonas] = useState<PersonaDisplay[]>([]);
  const [currentPersonaId, setCurrentPersonaId] = useState('preset_girlfriend');
  const [personasLoading, setPersonasLoading] = useState(false);

  // 聊天
  const [messages, setMessages] = useState<Message[]>([]);
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>([]);
  const [isWaitingForAi, setIsWaitingForAi] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [historyCursor, setHistoryCursor] = useState<string | null>(null);
  const [hasMoreHistory, setHasMoreHistory] = useState(false);

  // 学习数据
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<ProfileStats | null>(null);
  const [plan, setPlanState] = useState<WeeklyPlan | null>(null);
  const [learnError, setLearnError] = useState<string | null>(null);

  // 记忆数据
  const [emotions, setEmotions] = useState<any[]>([]);
  const [facts, setFacts] = useState<string[]>([]);
  const [memorySummary, setMemorySummary] = useState('');

  // 主动消息
  const [proactiveMessage, setProactiveMessage] = useState<ProactiveMessage | null>(null);
  const [proactiveDismissed, setProactiveDismissed] = useState(false);

  // 角色语音试听
  const [playingPersonaId, setPlayingPersonaId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Toast
  const [toast, setToast] = useState<ToastMessage | null>(null);
  const showToast = useCallback((text: string, type: 'success' | 'error' = 'success') => {
    setToast({ text, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  // 设置
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState('简体中文');
  const [notifications, setNotifications] = useState(true);

  // 深色模式
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // 登录后加载角色列表（预设 + 自定义）
  useEffect(() => {
    if (isLoggedIn && personas.length === 0) {
      setPersonasLoading(true);
      Promise.all([
        listPersonas(),
        listCustomPersonas().catch(() => ({ personas: [] })),
      ])
        .then(([presetRes, customRes]) => {
          const presetDisplays = presetRes.personas.map((p) => personaToDisplay(p, false));
          const customDisplays = (customRes as { personas: Persona[] }).personas.map((p) => personaToDisplay(p, true));
          setPersonas([...presetDisplays, ...customDisplays]);
          // 尝试加载开场白
          getQuickPhrases(currentPersonaId)
            .then((r) => setSuggestedPrompts(r.phrases))
            .catch(() => {});
        })
        .catch((err) => console.error('加载角色失败:', err))
        .finally(() => setPersonasLoading(false));
    }
  }, [isLoggedIn]);

  // auth 状态变化
  useEffect(() => {
    if (!authLoading) {
      if (isLoggedIn) {
        setActiveScreen('main');
        setActiveTab('chat');
      } else {
        setActiveScreen('login');
      }
    }
  }, [isLoggedIn, authLoading]);

  // ===== 角色选择 =====

  const handleSelectTutor = useCallback((id: string) => {
    setCurrentPersonaId(id);
    // 停止语音播放
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setPlayingPersonaId(null);
    // 加载开场白
    getQuickPhrases(id)
      .then((r) => setSuggestedPrompts(r.phrases))
      .catch(() => setSuggestedPrompts(['Hello!', 'How are you?', "Let's practice!"]));
    // 加载聊天历史
    setMessages([]);
    setHistoryCursor(null);
    setHasMoreHistory(false);
    setProactiveDismissed(false);
    fetchHistory(id, null);
  }, []);

  const handleConfirmTutor = useCallback(() => {
    setActiveScreen('chat');
    // 进入聊天时加载主动消息
    getProactiveMessages(currentPersonaId)
      .then((res) => {
        if (res.messages && res.messages.length > 0) {
          setProactiveMessage(res.messages[0]);
        } else {
          setProactiveMessage(null);
        }
      })
      .catch(() => setProactiveMessage(null));
  }, [currentPersonaId]);

  // ===== 语音试听 =====

  const handlePlayVoice = useCallback((personaId: string) => {
    // 如果正在播放同一个角色，停止播放
    if (playingPersonaId === personaId) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setPlayingPersonaId(null);
      return;
    }

    // 停止之前的播放
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    const url = getPersonaVoiceUrl(personaId);
    const audio = new Audio(url);
    audioRef.current = audio;
    setPlayingPersonaId(personaId);

    audio.onended = () => {
      setPlayingPersonaId(null);
      audioRef.current = null;
    };

    audio.onerror = () => {
      setPlayingPersonaId(null);
      audioRef.current = null;
      showToast('该角色暂无配音', 'error');
    };

    audio.play().catch(() => {
      setPlayingPersonaId(null);
      audioRef.current = null;
      showToast('语音播放失败', 'error');
    });
  }, [playingPersonaId, showToast]);

  // ===== 历史消息加载 =====

  const fetchHistory = async (personaId: string, cursor: string | null) => {
    try {
      const res = await getChatHistory(personaId, 20, cursor);
      const historyMsgs: Message[] = res.messages
        .reverse()
        .map((m) => ({
          id: m.id,
          sender: m.role === 'user' ? 'user' : 'ai',
          text: m.content,
          timestamp: new Date(m.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          }),
          isFavorite: m.is_favorite,
        }));
      if (cursor) {
        setMessages((prev) => [...historyMsgs, ...prev]);
      } else {
        setMessages(historyMsgs);
      }
      setHistoryCursor(res.next_cursor);
      setHasMoreHistory(!!res.next_cursor);
    } catch (err) {
      console.error('加载历史失败:', err);
    }
  };

  const handleLoadMoreHistory = useCallback(() => {
    if (historyCursor) {
      fetchHistory(currentPersonaId, historyCursor);
    }
  }, [currentPersonaId, historyCursor]);

  // ===== 消息收藏 =====

  const handleToggleFavorite = useCallback(async (messageId: string) => {
    // 乐观更新：立即切换收藏状态
    const previousMessages = messages;
    setMessages((prev) =>
      prev.map((m) =>
        m.id === messageId ? { ...m, isFavorite: !m.isFavorite } : m
      )
    );
    try {
      await toggleMessageFavorite(messageId, currentPersonaId);
    } catch {
      // 回滚
      setMessages(previousMessages);
      showToast('操作失败，请重试', 'error');
    }
  }, [messages, currentPersonaId, showToast]);

  // ===== 消息删除 =====

  const [deleteConfirmMessageId, setDeleteConfirmMessageId] = useState<string | null>(null);

  const handleDeleteMessage = useCallback(async (messageId: string) => {
    // 乐观更新：立即移除消息
    const previousMessages = messages;
    setMessages((prev) => prev.filter((m) => m.id !== messageId));
    try {
      await deleteMessage(messageId, currentPersonaId);
      showToast('消息已删除');
    } catch {
      // 回滚
      setMessages(previousMessages);
      showToast('删除失败，请重试', 'error');
    }
  }, [messages, currentPersonaId, showToast]);

  // ===== 发送消息 =====

  const handleSendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsWaitingForAi(true);

    const newSessionId = sessionId || '';
    let aiReply = '';
    const aiMsgId = (Date.now() + 1).toString();

    try {
      await getChatStream(currentPersonaId, text.trim(), newSessionId, {
        onToken: (token) => {
          aiReply += token;
          setMessages((prev) => {
            const existing = prev.find((m) => m.id === aiMsgId);
            if (existing) {
              return prev.map((m) => (m.id === aiMsgId ? { ...m, text: aiReply } : m));
            }
            return [
              ...prev,
              {
                id: aiMsgId,
                sender: 'ai',
                text: aiReply,
                timestamp: new Date().toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                }),
              },
            ];
          });
        },
        onDone: () => {
          setIsWaitingForAi(false);
          // 保存 session_id
          if (!sessionId && newSessionId) {
            setSessionId(newSessionId);
          }
        },
        onError: (err) => {
          console.error('SSE 错误:', err);
          setIsWaitingForAi(false);
          // Fallback to sync chat
          sendChatMessage({
            persona_id: currentPersonaId,
            message: text.trim(),
            session_id: newSessionId,
          })
            .then((res) => {
              setMessages((prev) => [
                ...prev.filter((m) => m.id !== aiMsgId),
                {
                  id: aiMsgId,
                  sender: 'ai',
                  text: res.reply,
                  timestamp: new Date().toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  }),
                },
              ]);
            })
            .catch(() => {
              setMessages((prev) => [
                ...prev.filter((m) => m.id !== aiMsgId),
                {
                  id: aiMsgId,
                  sender: 'ai',
                  text: '抱歉，我现在无法回复。请稍后再试。',
                  timestamp: new Date().toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  }),
                },
              ]);
            });
        },
      });
    } catch (err: any) {
      // SSE 完全失败，直接用同步 API
      try {
        const res = await sendChatMessage({
          persona_id: currentPersonaId,
          message: text.trim(),
          session_id: newSessionId,
        });
        setMessages((prev) => [
          ...prev.filter((m) => m.id !== aiMsgId),
          {
            id: aiMsgId,
            sender: 'ai',
            text: res.reply,
            timestamp: new Date().toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            }),
          },
        ]);
      } catch {
        setMessages((prev) => [
          ...prev.filter((m) => m.id !== aiMsgId),
          {
            id: aiMsgId,
            sender: 'ai',
            text: '抱歉，网络连接出现问题，请稍后再试。',
            timestamp: new Date().toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            }),
          },
        ]);
      } finally {
        setIsWaitingForAi(false);
      }
    }
  }, [currentPersonaId, sessionId]);

  // ===== 主动消息 =====

  const handleDismissProactive = useCallback(() => {
    setProactiveDismissed(true);
    setProactiveMessage(null);
  }, []);

  const handleAcceptProactive = useCallback(() => {
    if (!proactiveMessage) return;
    // 将主动消息内容作为 AI 消息插入聊天
    const aiMsg: Message = {
      id: `proactive-${Date.now()}`,
      sender: 'ai',
      text: proactiveMessage.content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, aiMsg]);
    setProactiveDismissed(true);
    setProactiveMessage(null);
  }, [proactiveMessage]);

  // ===== 学习数据加载 =====

  const loadLearnData = useCallback(async () => {
    setLearnError(null);
    // 顺序调用避免 SQLite 并发写锁冲突
    try {
      const statsData = await getProfileStats('month');
      const profileData = await getProfile();
      setStats(statsData);
      setProfile({
        cefrLevel: profileData.cefr_level as any,
        vocabularySize: profileData.vocabulary_size,
        weakAreas: profileData.weak_areas,
        learningDays: statsData.learning_days,
        streak: statsData.check_in_count,
        summary: profileData.summary,
      });
    } catch (err) {
      console.error('加载学习数据失败:', err);
      setLearnError('加载学习数据失败，请检查网络后重试');
    }
    try {
      const planRes = await getPlan();
      setPlanState(planRes.plan);
    } catch {
      setPlanState(null);
    }
  }, []);

  // 学习 tab 切过去时加载数据
  useEffect(() => {
    if (activeTab === 'learn' && isLoggedIn) {
      loadLearnData();
    }
  }, [activeTab, isLoggedIn, loadLearnData]);

  // ===== 学习计划操作 =====

  const handleCompletePlan = useCallback(async () => {
    try {
      await completePlan();
      showToast('任务已完成');
      // 刷新计划数据
      const planRes = await getPlan();
      setPlanState(planRes.plan);
    } catch {
      showToast('完成操作失败', 'error');
    }
  }, [showToast]);

  const handleSetPlan = useCallback(async (data: WeeklyPlan) => {
    try {
      const res = await setPlanApi(data);
      setPlanState(res.plan);
      showToast('学习计划已创建');
    } catch {
      showToast('创建计划失败', 'error');
    }
  }, [showToast]);

  // 记忆数据加载
  const loadMemoryData = useCallback(async () => {
    try {
      const [emotionRes, factRes, summaryRes] = await Promise.all([
        getEmotions(currentPersonaId),
        getFacts(currentPersonaId),
        getSummary(currentPersonaId),
      ]);
      setEmotions(emotionRes.emotions);
      setFacts(factRes.facts);
      setMemorySummary(summaryRes.summary);
    } catch (err) {
      console.error('加载记忆数据失败:', err);
    }
  }, [currentPersonaId]);

  // ===== 导航 =====

  const handleLogout = useCallback(() => {
    logout();
    setActiveScreen('login');
    setMessages([]);
    setPersonas([]);
    setProfile(null);
    setStats(null);
    setPlanState(null);
  }, [logout]);

  const currentDisplay = personas.find((p) => p.id === currentPersonaId) || {
    id: currentPersonaId,
    name: PERSONA_DISPLAY_MAP[currentPersonaId]?.name || currentPersonaId,
    role: '',
    tagline: PERSONA_DISPLAY_MAP[currentPersonaId]?.tagline || '',
    description: '',
    avatar: PERSONA_AVATAR_MAP[currentPersonaId] || '',
  };

  // ===== 底部 Tab =====

  const renderBottomTabs = () => {
    const isChatActive = activeTab === 'chat';
    const isLearnActive = activeTab === 'learn';
    const isProfileActive = activeTab === 'profile';

    return (
      <footer className="sticky bottom-0 z-50 border-t px-6 h-16 shrink-0 flex items-center justify-around select-none shadow-[0_-4px_16px_rgba(0,0,0,0.02)] transition-colors duration-300 bg-white/90 border-primary/5 backdrop-blur-md text-outline/75">
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex flex-col items-center gap-1 cursor-pointer py-1 px-4 transition-all duration-300 ${
            isChatActive ? 'text-primary scale-105 font-semibold' : 'text-outline/75 hover:text-primary/70'
          }`}
        >
          <span className="material-symbols-outlined text-[23px]" style={{ fontVariationSettings: isChatActive ? "'FILL' 1" : "'FILL' 0" }}>
            chat_bubble
          </span>
          <span className="text-[10px] font-sans tracking-wide">AI导师</span>
        </button>

        <button
          onClick={() => setActiveTab('learn')}
          className={`flex flex-col items-center gap-1 cursor-pointer py-1 px-4 transition-all duration-300 ${
            isLearnActive ? 'text-primary scale-105 font-semibold' : 'text-outline/75 hover:text-primary/70'
          }`}
        >
          <span className="material-symbols-outlined text-[23px]" style={{ fontVariationSettings: isLearnActive ? "'FILL' 1" : "'FILL' 0" }}>
            school
          </span>
          <span className="text-[10px] font-sans tracking-wide">学习</span>
        </button>

        <button
          onClick={() => setActiveTab('profile')}
          className={`flex flex-col items-center gap-1 cursor-pointer py-1 px-4 transition-all duration-300 ${
            isProfileActive ? 'text-primary scale-105 font-semibold' : 'text-outline/75 hover:text-primary/70'
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

  // ===== Loading =====

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <span className="material-symbols-outlined text-primary text-[48px] animate-spin">progress_activity</span>
          <p className="text-on-surface-variant font-sans text-sm">正在加载 Mellow...</p>
        </div>
      </div>
    );
  }

  // ===== 判断是否显示主动消息横幅 =====
  const showProactiveBanner = !proactiveDismissed && proactiveMessage !== null;

  // ===== Render =====

  return (
    <div className="min-h-screen bg-background">
      {/* 全局 Toast */}
      <Toast toast={toast} />

      {/* 登录 */}
      {activeScreen === 'login' && (
        <LoginView onLoginSuccess={() => { setActiveScreen('main'); setActiveTab('chat'); }} />
      )}

      {/* 全屏聊天 */}
      {activeScreen === 'chat' && (
        <div className="flex flex-col h-screen min-h-screen max-h-screen relative overflow-hidden bg-background animate-fade-in">
          <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-primary/5 px-6 h-16 flex items-center justify-between shrink-0">
            <button
              onClick={() => { setActiveScreen('main'); setActiveTab('chat'); }}
              className="w-10 h-10 flex items-center justify-center text-on-surface-variant hover:bg-primary-container/15 rounded-full transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined text-[20px]">arrow_back</span>
            </button>
            <div className="text-center flex items-center gap-2 justify-center">
              <div className="w-8 h-8 rounded-full bg-primary/15 flex items-center justify-center text-primary font-display font-bold text-sm">
                {currentDisplay.name[0]}
              </div>
              <div className="text-left">
                <h1 className="font-display font-semibold text-sm md:text-base text-on-surface leading-tight">{currentDisplay.name}</h1>
                <span className="text-[9px] text-primary/75 font-semibold font-sans tracking-wide block">
                  Online Language Partner
                </span>
              </div>
            </div>
            <button
              onClick={() => setActiveScreen('voiceCall')}
              className="w-10 h-10 flex items-center justify-center text-primary bg-primary-container/10 hover:bg-primary-container/25 rounded-full transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined text-[20px]">call</span>
            </button>
          </header>
          <div className="flex-grow overflow-hidden relative">
            <ChatView
              personaName={currentDisplay.name}
              messages={messages}
              onSendMessage={handleSendMessage}
              suggestedPrompts={suggestedPrompts}
              isWaitingForAi={isWaitingForAi}
              hasMoreHistory={hasMoreHistory}
              onLoadMoreHistory={handleLoadMoreHistory}
              onToggleFavorite={handleToggleFavorite}
              onDeleteMessage={(messageId: string) => setDeleteConfirmMessageId(messageId)}
              proactiveMessage={showProactiveBanner ? proactiveMessage : null}
              onDismissProactive={handleDismissProactive}
              onAcceptProactive={handleAcceptProactive}
              onShowToast={showToast}
            />
          </div>
        </div>
      )}

      {/* 删除确认对话框 */}
      <ConfirmDialog
        visible={deleteConfirmMessageId !== null}
        title="删除消息"
        message="确定删除这条消息吗？此操作无法撤销。"
        confirmLabel="删除"
        cancelLabel="取消"
        danger
        onConfirm={() => {
          if (deleteConfirmMessageId) {
            handleDeleteMessage(deleteConfirmMessageId);
            setDeleteConfirmMessageId(null);
          }
        }}
        onCancel={() => setDeleteConfirmMessageId(null)}
      />

      {/* 语音通话 */}
      {activeScreen === 'voiceCall' && (
        <VoiceCallView
          personaName={currentDisplay.name}
          onEndCall={() => setActiveScreen('chat')}
          onShowToast={(text: string, type: 'success' | 'error' = 'success') => showToast(text, type)}
        />
      )}

      {/* 设置 */}
      {activeScreen === 'settings' && (
        <SettingsView
          user={{ username: user?.username || '', level: profile?.cefrLevel || 'B2' }}
          darkMode={darkMode}
          language={language}
          notifications={notifications}
          onUpdateDarkMode={setDarkMode}
          onUpdateLanguage={setLanguage}
          onUpdateNotifications={setNotifications}
          onGoBack={() => setActiveScreen('main')}
          onLogout={handleLogout}
        />
      )}

      {/* 主 Hub */}
      {activeScreen === 'main' && (
        <div className="flex flex-col h-screen min-h-screen max-h-screen relative overflow-hidden bg-background">
          <main className="flex-grow overflow-hidden relative">
            {activeTab === 'chat' && (
              <GuideSelectView
                personas={personas}
                loading={personasLoading}
                selectedId={currentPersonaId}
                onSelectTutor={handleSelectTutor}
                onConfirmSelection={handleConfirmTutor}
                playingPersonaId={playingPersonaId}
                onPlayVoice={handlePlayVoice}
              />
            )}

            {activeTab === 'learn' && (
              <LearnView
                profile={profile}
                stats={stats}
                isLoading={!profile || !stats}
                learnError={learnError}
                onRefresh={loadLearnData}
                plan={plan}
                onCompletePlan={handleCompletePlan}
                onSetPlan={handleSetPlan}
              />
            )}

            {activeTab === 'profile' && (
              <ProfileView
                user={user}
                profile={profile}
                personas={personas}
                currentPersonaId={currentPersonaId}
                onSelectPersona={handleSelectTutor}
                onOpenVocabulary={() => setActiveScreen('vocabulary')}
                onOpenKnowledge={() => setActiveScreen('knowledge')}
                onOpenMistakes={() => setActiveScreen('mistakes')}
                onOpenMemory={() => {
                  loadMemoryData();
                  setActiveScreen('memory');
                }}
                onOpenSettings={() => setActiveScreen('settings')}
                onLogout={handleLogout}
                darkMode={darkMode}
                onUpdateDarkMode={setDarkMode}
                language={language}
                onUpdateLanguage={setLanguage}
                notifications={notifications}
                onUpdateNotifications={setNotifications}
              />
            )}
          </main>
          {renderBottomTabs()}
        </div>
      )}

      {/* 生词本 */}
      {activeScreen === 'vocabulary' && (
        <VocabularyView onGoBack={() => setActiveScreen('main')} />
      )}

      {/* 知识库 */}
      {activeScreen === 'knowledge' && (
        <KnowledgeView onGoBack={() => setActiveScreen('main')} />
      )}

      {/* 错题本 */}
      {activeScreen === 'mistakes' && (
        <MistakesView onGoBack={() => setActiveScreen('main')} />
      )}

      {/* 记忆页面 */}
      {activeScreen === 'memory' && (
        <div className="bg-background text-on-background h-screen max-h-screen flex flex-col overflow-hidden">
          <header className="w-full bg-white border-b border-primary/5 px-6 h-16 flex items-center justify-between shrink-0">
            <button onClick={() => setActiveScreen('main')} className="w-10 h-10 flex items-center justify-center text-on-surface hover:bg-primary-container/10 rounded-full">
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <h1 className="font-display font-medium text-headline-sm">角色记忆</h1>
            <div className="w-10"></div>
          </header>
          <main className="flex-grow overflow-y-auto p-6 space-y-6">
            <section className="bg-white rounded-2xl p-5 shadow-sm">
              <h2 className="font-display font-bold text-lg mb-3">记忆摘要</h2>
              <p className="text-on-surface-variant text-sm leading-relaxed">{memorySummary || '暂无记忆摘要'}</p>
            </section>
            <section className="bg-white rounded-2xl p-5 shadow-sm">
              <h2 className="font-display font-bold text-lg mb-3">关键认知</h2>
              {facts.length > 0 ? (
                <ul className="space-y-2">
                  {facts.map((fact, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-on-surface-variant">
                      <span className="text-primary mt-1">•</span>
                      <span>{fact}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-on-surface-variant/60 text-sm">暂无关键认知</p>
              )}
            </section>
            <section className="bg-white rounded-2xl p-5 shadow-sm">
              <h2 className="font-display font-bold text-lg mb-3">情绪轨迹</h2>
              {emotions.length > 0 ? (
                <div className="space-y-3">
                  {emotions.map((e, i) => (
                    <div key={i} className="flex items-center gap-3 p-2 rounded-lg bg-surface-container-low">
                      <span className="text-lg">{e.mood === 'happy' ? '😊' : e.mood === 'frustrated' ? '😤' : e.mood === 'tired' ? '😴' : e.mood === 'motivated' ? '💪' : '😐'}</span>
                      <div>
                        <p className="text-sm font-medium">{e.mood} ({Math.round(e.intensity * 100)}%)</p>
                        <p className="text-xs text-on-surface-variant">{e.reason}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-on-surface-variant/60 text-sm">暂无情绪记录</p>
              )}
            </section>
          </main>
        </div>
      )}
    </div>
  );
}