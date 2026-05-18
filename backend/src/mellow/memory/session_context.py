"""会话上下文管理器。

管理单次会话的短期上下文 —— 纯内存，不持久化。
"""

from datetime import datetime, timezone
from typing import Any

from mellow.memory.models import MistakeEntry, SessionContext


class ChatMessage:
    """聊天消息 —— 内存存储，不持久化。"""

    def __init__(
        self,
        id: str,
        role: str,
        content: str,
        is_favorite: bool = False,
        timestamp: datetime | None = None,
    ):
        self.id = id
        self.role = role
        self.content = content
        self.is_favorite = is_favorite
        self.timestamp = timestamp or datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "is_favorite": self.is_favorite,
            "timestamp": self.timestamp.isoformat(),
        }


class SessionContextManager:
    """会话上下文管理器。

    每个活跃会话一个实例，会话结束后丢弃。
    """

    def __init__(self, session_id: str, user_id: str, persona_id: str):
        self._ctx = SessionContext(
            session_id=session_id,
            user_id=user_id,
            persona_id=persona_id,
        )
        self._messages: list[ChatMessage] = []

    @property
    def context(self) -> SessionContext:
        return self._ctx

    @property
    def messages(self) -> list[ChatMessage]:
        return self._messages

    def update_topic(self, topic: str):
        self._ctx.current_topic = topic

    def add_mistake(self, entry: MistakeEntry):
        self._ctx.recent_mistakes.append(entry)
        if len(self._ctx.recent_mistakes) > 10:
            self._ctx.recent_mistakes = self._ctx.recent_mistakes[-10:]

    def update_mood(self, mood: str):
        self._ctx.user_mood = mood

    def get_mood(self) -> str:
        return self._ctx.user_mood

    def get_summary_for_agent(self) -> str:
        """生成会话上下文摘要 —— 注入 Agent prompt。"""
        parts = []
        if self._ctx.current_topic:
            parts.append(f"当前话题: {self._ctx.current_topic}")
        if self._ctx.recent_mistakes:
            latest = self._ctx.recent_mistakes[-3:]
            parts.append(f"最近错误: {'; '.join(m.word_or_rule for m in latest)}")
        if self._ctx.user_mood != "neutral":
            parts.append(f"用户情绪: {self._ctx.user_mood}")
        return "\n".join(parts) if parts else "新会话"

    # ---- 消息管理 ----

    def add_message(self, message: ChatMessage) -> None:
        """追加消息到会话。"""
        self._messages.append(message)

    def get_message(self, message_id: str) -> ChatMessage | None:
        """按 ID 查找消息。"""
        for msg in self._messages:
            if msg.id == message_id:
                return msg
        return None

    def toggle_favorite(self, message_id: str) -> ChatMessage | None:
        """切换消息收藏状态，返回更新后的消息。"""
        msg = self.get_message(message_id)
        if msg:
            msg.is_favorite = not msg.is_favorite
        return msg

    def delete_message(self, message_id: str) -> bool:
        """删除消息，返回是否成功。"""
        for i, msg in enumerate(self._messages):
            if msg.id == message_id:
                self._messages.pop(i)
                return True
        return False

    def get_messages(
        self,
        cursor: str | None = None,
        limit: int = 20,
    ) -> tuple[list[ChatMessage], str | None]:
        """分页获取消息。

        按时间倒序返回（最新的在前），cursor 为上一页最后一条消息的 ID。
        返回: (消息列表, next_cursor)
        """
        msgs = list(self._messages)
        # 倒序排列（最新的在前）
        msgs.reverse()

        if cursor:
            # 找到 cursor 对应的消息，返回其之后的消息（更旧的）
            for i, msg in enumerate(msgs):
                if msg.id == cursor:
                    msgs = msgs[i + 1:]
                    break

        result = msgs[:limit]
        next_cursor = result[-1].id if len(result) == limit and msgs[limit:] else None
        return result, next_cursor
