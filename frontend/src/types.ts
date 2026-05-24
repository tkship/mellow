// @ts-ignore
import auraAvatar from './assets/images/female_tutor_aura_1779629353766.png';
// @ts-ignore
import leoAvatar from './assets/images/female_tutor_leo_1779629373242.png';
// @ts-ignore
import chenAvatar from './assets/images/female_tutor_chen_1779629389555.png';

export type TutorId = 'aura' | 'leo' | 'chen';

export interface Tutor {
  id: TutorId;
  name: string;
  avatar: string;
  tagline: string;
  description: string;
  tag?: string;
}

export type Sender = 'user' | 'ai';

export interface Message {
  id: string;
  sender: Sender;
  text: string;
  timestamp: string;
  suggestedPrompts?: string[];
}

export type MainTab = 'chat' | 'learn' | 'profile';

export type ScreenId = 'login' | 'register' | 'guideSelect' | 'main' | 'settings' | 'voiceCall' | 'chat';

export type CEFRGoal = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';

export interface UserState {
  username: string;
  email: string;
  isLoggedIn: boolean;
  level: CEFRGoal;
  streak: number;
  vocabCount: number;
  avatar: string;
  bio: string;
  notifications: boolean;
  language: string;
  darkMode?: boolean;
}

export const TUTORS: Record<TutorId, Tutor> = {
  aura: {
    id: 'aura',
    name: 'Aura',
    avatar: auraAvatar,
    tagline: '对话流利，注重文化细节',
    description: 'Aura focuses on natural conversations, vernacular expressions, and cultural nuances. Perfect for medium-to-advanced learners seeking fluency.',
    tag: '推荐'
  },
  leo: {
    id: 'leo',
    name: 'Leo',
    avatar: leoAvatar,
    tagline: '耐心引导，适合初学者起步',
    description: 'Leo is warm, friendly, and uses clear sentence structures with step-by-step guidance. Ideal for beginners gaining confidence.',
  },
  chen: {
    id: 'chen',
    name: 'Dr. Chen',
    avatar: chenAvatar,
    tagline: '学术严谨，专注语法与结构',
    description: 'Dr. Chen provides academic depth, rigorous grammatical structures, and detailed syntax tutorials. Excellent for exam preparation.',
  }
};
