"""会话上下文管理器。

管理单次会话的短期上下文 —— 纯内存，不持久化。
"""

from datetime import datetime, timezone

from mellow.memory.models import MistakeEntry, SessionContext


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

    @property
    def context(self) -> SessionContext:
        return self._ctx

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
