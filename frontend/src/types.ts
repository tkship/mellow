/**
 * Mellow 前端类型定义 — 对齐后端 API 数据模型
 */

// ===== 认证相关 =====

export interface UserInfo {
  id: string;
  username: string;
  is_active: boolean;
}

export interface AuthState {
  user: UserInfo | null;
  isLoggedIn: boolean;
  isLoading: boolean;
}

// ===== 角色相关 =====

/** 后端 Persona ID → 前端显示信息映射 */
export const PERSONA_DISPLAY_MAP: Record<string, { name: string; tagline: string; tag?: string }> = {
  preset_girlfriend: { name: '小雅', tagline: '温柔贴心，陪伴式学习', tag: '推荐' },
  preset_study_buddy: { name: '知夏', tagline: '轻松对聊，像同学一起学' },
  preset_humorous_friend: { name: '晚晴', tagline: '幽默风趣，快乐记单词' },
  preset_strict_teacher: { name: 'Dr. Chen', tagline: '学术严谨，专注语法与结构' },
};

/** 后端 Persona ID → 头像图片映射 */
import xiaoyaAvatar from './assets/images/xiaoya.png';
import zhixiaAvatar from './assets/images/zhixia.jpg';
import wanqingAvatar from './assets/images/wanqing.jpg';

export const PERSONA_AVATAR_MAP: Record<string, string> = {
  preset_girlfriend: xiaoyaAvatar,
  preset_study_buddy: zhixiaAvatar,
  preset_humorous_friend: wanqingAvatar,
  // preset_strict_teacher 没有专属图片，用首字母头像
};

/** 前端选中角色 ID（兼容旧代码） */
export type TutorId = string;

/** 角色的前端展示信息（从后端 Persona 派生） */
export interface PersonaDisplay {
  id: string;
  name: string;
  role: string;
  tagline: string;
  description: string;
  tag?: string;
  avatar: string;  // 图片路径或空字符串（空则用首字母）
}

// ===== 聊天相关 =====

export type Sender = 'user' | 'ai';

export interface Message {
  id: string;
  sender: Sender;
  text: string;
  timestamp: string;
  isFavorite?: boolean;
  suggestedPrompts?: string[];
}

// ===== 路由/页面 =====

export type MainTab = 'chat' | 'learn' | 'profile';

export type ScreenId =
  | 'login'
  | 'register'
  | 'guideSelect'
  | 'main'
  | 'settings'
  | 'voiceCall'
  | 'chat'
  | 'vocabulary'
  | 'knowledge'
  | 'mistakes'
  | 'memory';

// ===== 学习画像相关 =====

export type CEFRLevel = 'A0' | 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';

export interface UserProfile {
  cefrLevel: CEFRLevel;
  vocabularySize: number;
  weakAreas: string[];
  learningDays: number;
  streak: number;
  summary: string;
}

// ===== 应用全局状态 =====

export interface AppState {
  user: UserInfo | null;
  isLoggedIn: boolean;
  authLoading: boolean;
  darkMode: boolean;
  language: string;
  notifications: boolean;
  currentPersonaId: string;
  profile: UserProfile | null;
}
