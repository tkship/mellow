"""LanceDB Schema 定义。

使用 LanceModel (Pydantic) 定义向量表结构。
"""

from lancedb.pydantic import LanceModel, Vector


class ConversationMemoryRow(LanceModel):
    """对话记忆向量行。"""
    memory_id: str
    session_id: str
    user_id: str
    persona_id: str
    role: str         # "user" | "assistant" | "system"
    content: str
    timestamp: float  # Unix timestamp
    token_count: int = 0
    message_type: str = "text"  # "text" | "correction" | "feedback"
    vector: Vector(1024)  # embedding 维度


class KnowledgeChunkRow(LanceModel):
    """知识库分块向量行。"""
    chunk_id: str
    content: str
    source: str       # 来源标识
    topic: str        # 主题分类
    difficulty: str   # "beginner" | "intermediate" | "advanced"
    chunk_index: int
    metadata_json: str = "{}"
    vector: Vector(1024)
