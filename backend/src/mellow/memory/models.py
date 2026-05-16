"""记忆系统数据模型 —— 三层记忆结构。

1. LearningProfile: 学习档案（永久）
2. PersonaMemory:  角色记忆（长期）
3. SessionContext: 会话上下文（单会话）
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# ===== 学习档案 =====

class MasteryLevel(StrEnum):
    NEW = "new"
    LEARNING = "learning"
    FAMILIAR = "familiar"
    MASTERED = "mastered"


class MistakeEntry(BaseModel):
    """错误记录。"""
    word_or_rule: str
    mistake_type: str  # "grammar" | "vocabulary" | "pronunciation" | "spelling"
    context: str       # 当时对话上下文
    correction: str
    timestamp: datetime = Field(default_factory=datetime.now)


class DailyPlan(BaseModel):
    """每日学习计划条目。"""
    day: int
    topic: str
    vocabulary: list[str] = Field(default_factory=list)
    grammar_point: str = ""
    practice: str = ""


class WeeklyPlan(BaseModel):
    """周学习计划。"""
    week: int
    theme: str
    days: list[DailyPlan] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    completed: bool = False


class LearningProfile(BaseModel):
    """用户学习档案。"""
    user_id: str
    vocabulary_size: int = 0
    cefr_level: str = "A1"
    weak_areas: list[str] = Field(default_factory=list)
    mastered_words: dict[str, float] = Field(default_factory=dict)  # word → mastery 0.0~1.0
    mistake_log: list[MistakeEntry] = Field(default_factory=list)
    completed_lessons: list[str] = Field(default_factory=list)
    current_plan: WeeklyPlan | None = None
    plan_history: list[WeeklyPlan] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ===== 角色记忆 =====

class MoodEvent(BaseModel):
    """情绪事件。"""
    date: str
    mood: str       # "happy" | "frustrated" | "tired" | "motivated" | "neutral"
    reason: str = ""
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)


class PersonaMemory(BaseModel):
    """角色记忆 —— 每个角色对用户的独立记忆。"""
    persona_id: str
    user_id: str
    relationship_summary: str = ""        # LLM 生成的关系摘要
    emotional_trajectory: list[MoodEvent] = Field(default_factory=list)
    key_facts: list[str] = Field(default_factory=list)  # 从对话提取的关键信息
    last_interaction: datetime | None = None
    interaction_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ===== 会话上下文 =====

class SessionContext(BaseModel):
    """会话上下文 —— 内存中，不持久化。"""
    session_id: str
    user_id: str
    persona_id: str
    current_topic: str | None = None
    recent_mistakes: list[MistakeEntry] = Field(default_factory=list)
    conversation_summary: str = ""        # 当前会话的简要摘要
    user_mood: str = "neutral"
    started_at: datetime = Field(default_factory=datetime.now)


# ===== 主动联系 =====

class ProactiveMessage(BaseModel):
    """Agent 主动发送的消息。"""
    id: str
    user_id: str
    persona_id: str
    content: str                          # LLM 生成的角色化文案
    scheduled_at: datetime
    delivered: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
