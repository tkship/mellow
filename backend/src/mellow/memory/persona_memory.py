"""角色记忆管理器 —— 管理 PersonaMemory。

存储策略：SQLite via SQLAlchemy（持久化）。
Pydantic 模型在校验层使用，ORM 模型在持久化层使用。
"""

from datetime import datetime, timezone

from mellow.db.repos.persona_memory_repo import (
    PersonaMemoryRepository,
    mem_to_row,
    row_to_mem,
)
from mellow.memory.models import MoodEvent, PersonaMemory


class PersonaMemoryManager:
    """角色记忆管理器。

    每个 (persona_id, user_id) 组合独立存储。
    数据通过 PersonaMemoryRepository 持久化到 SQLite。
    每次 操作 使用传入的 repo 的 session。
    """

    def __init__(self, repo: PersonaMemoryRepository, session_factory=None):
        self._repo = repo
        self._session_factory = session_factory

    async def get_or_create(self, persona_id: str, user_id: str) -> PersonaMemory:
        row = await self._repo.get_or_create(persona_id, user_id)
        return row_to_mem(row)

    async def record_interaction(
        self,
        persona_id: str,
        user_id: str,
        summary: str = "",
    ):
        """记录一次互动。"""
        row = await self._repo.get_or_create(persona_id, user_id)
        memory = row_to_mem(row)
        memory.last_interaction = datetime.now(timezone.utc)
        memory.interaction_count += 1
        memory.updated_at = datetime.now(timezone.utc)
        if summary:
            if memory.relationship_summary:
                memory.relationship_summary += f"\n{summary}"
            else:
                memory.relationship_summary = summary
        mem_to_row(memory, row)
        await self._repo.save(row)

    async def record_mood(
        self,
        persona_id: str,
        user_id: str,
        mood: str,
        reason: str = "",
        intensity: float = 0.5,
    ):
        """记录情绪事件。"""
        row = await self._repo.get_or_create(persona_id, user_id)
        memory = row_to_mem(row)
        event = MoodEvent(
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            mood=mood,
            reason=reason,
            intensity=intensity,
        )
        memory.emotional_trajectory.append(event)
        # 保留最近 50 条
        if len(memory.emotional_trajectory) > 50:
            memory.emotional_trajectory = memory.emotional_trajectory[-50:]
        memory.updated_at = datetime.now(timezone.utc)
        mem_to_row(memory, row)
        await self._repo.save(row)

    async def add_key_fact(self, persona_id: str, user_id: str, fact: str):
        """添加角色对用户的关键认知。"""
        row = await self._repo.get_or_create(persona_id, user_id)
        memory = row_to_mem(row)
        if fact not in memory.key_facts:
            memory.key_facts.append(fact)
        # 限制 30 条
        if len(memory.key_facts) > 30:
            memory.key_facts = memory.key_facts[-30:]
        mem_to_row(memory, row)
        await self._repo.save(row)

    async def get_memory_context(self, persona_id: str, user_id: str) -> str:
        """生成角色记忆上下文 —— 供 Agent prompt 使用。"""
        memory = await self.get_or_create(persona_id, user_id)
        parts = []

        if memory.relationship_summary:
            parts.append(f"关系摘要: {memory.relationship_summary}")

        if memory.emotional_trajectory:
            recent_moods = memory.emotional_trajectory[-3:]
            mood_str = ", ".join(
                f"{m.date} {m.mood} ({m.reason})" for m in recent_moods
            )
            parts.append(f"最近情绪: {mood_str}")

        if memory.key_facts:
            parts.append(f"关键信息: {'; '.join(memory.key_facts[-5:])}")

        if memory.last_interaction:
            try:
                last = memory.last_interaction
                if isinstance(last, str):
                    from datetime import datetime as dt
                    last = dt.fromisoformat(last.replace('Z', '+00:00'))
                hours_ago = (datetime.now(timezone.utc) - last).total_seconds() / 3600
                parts.append(f"上次互动: {hours_ago:.0f} 小时前")
            except Exception:
                pass  # skip if datetime arithmetic fails

        return "\n".join(parts) if parts else "这是你们的第一次对话。"

    async def needs_proactive_poke(
        self,
        persona_id: str,
        user_id: str,
        min_hours: int = 12,
        max_hours: int = 24,
    ) -> bool:
        """检查是否需要主动联系。"""
        memory = await self.get_or_create(persona_id, user_id)
        if not memory.last_interaction:
            return False
        try:
            last = memory.last_interaction
            if isinstance(last, str):
                last = datetime.fromisoformat(last.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - last).total_seconds() / 3600
            return elapsed >= min_hours
        except Exception:
            return False