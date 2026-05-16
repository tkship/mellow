"""共享数据模型 —— 跨模块使用的核心领域模型。"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# ===== 消息模型 =====

class MessageRole(StrEnum):
    """消息角色。"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """通用消息模型。"""
    role: MessageRole
    content: str
    name: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)

    def to_openai_format(self) -> dict[str, Any]:
        """转换为 OpenAI 兼容的消息格式。"""
        msg: dict[str, Any] = {"role": self.role.value, "content": self.content}
        if self.name:
            msg["name"] = self.name
        return msg


# ===== 用户模型 =====

class User(BaseModel):
    """用户模型。"""
    id: str
    username: str
    created_at: datetime
    is_active: bool = True


class Token(BaseModel):
    """JWT Token 模型。"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ===== 知识库模型 =====

class WordEntry(BaseModel):
    """词条查询结果。"""
    word: str
    part_of_speech: str | None = None
    phonetic: str | None = None
    definitions: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    synonyms: list[str] = Field(default_factory=list)
    source: str = "unknown"


class SearchResult(BaseModel):
    """语义检索结果。"""
    content: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


# ===== 角色模型 =====

class LanguageStyle(BaseModel):
    """语言风格配置。"""
    tone: str = "friendly"
    traits: list[str] = Field(default_factory=list)


class TeachingStyle(BaseModel):
    """教学风格配置。"""
    approach: str = "引导式"
    strictness: float = Field(default=0.5, ge=0.0, le=1.0)
    correction_frequency: str = "major_only"


class Persona(BaseModel):
    """角色定义。"""
    id: str
    name: str
    role: str
    language_style: LanguageStyle = Field(default_factory=LanguageStyle)
    teaching_style: TeachingStyle = Field(default_factory=TeachingStyle)
    intimacy_level: str = "casual"
    interaction_rhythm: tuple[int, int] = (12, 24)
    emotional_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    system_prompt_template: str = ""
    is_preset: bool = False
    created_by: str | None = None
    voice_id: str | None = None
