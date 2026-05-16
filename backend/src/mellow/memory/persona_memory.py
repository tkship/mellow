"""角色记忆管理器 —— 管理 PersonaMemory。

存储策略（混合）：
- 7 天内原始对话 → LanceDB（向量可检索）
- 超出 7 天 → 压缩为摘要存入 SQLite
- 关键事件（情绪转折、学习里程碑）→ 永久保留
"""

from datetime import datetime, timedelta, timezone

from mellow.memory.models import MoodEvent, PersonaMemory


class PersonaMemoryManager:
    """角色记忆管理器。

    每个 (persona_id, user_id) 组合独立存储。
    """

    def __init__(self):
        # Phase 5: 内存存储 → 后续换 SQLite + LanceDB
        self._memories: dict[str, PersonaMemory] = {}

    def _key(self, persona_id: str, user_id: str) -> str:
        return f"{persona_id}:{user_id}"

    async def get_or_create(self, persona_id: str, user_id: str) -> PersonaMemory:
        key = self._key(persona_id, user_id)
        if key not in self._memories:
            self._memories[key] = PersonaMemory(
                persona_id=persona_id,
                user_id=user_id,
            )
        return self._memories[key]

    async def record_interaction(
        self,
        persona_id: str,
        user_id: str,
        summary: str = "",
    ):
        """记录一次互动。"""
        memory = await self.get_or_create(persona_id, user_id)
        memory.last_interaction = datetime.now(timezone.utc)
        memory.interaction_count += 1
        memory.updated_at = datetime.now(timezone.utc)
        if summary:
            # 简单追加到关系摘要（后续用 LLM 压缩）
            if memory.relationship_summary:
                memory.relationship_summary += f"\n{summary}"
            else:
                memory.relationship_summary = summary

    async def record_mood(
        self,
        persona_id: str,
        user_id: str,
        mood: str,
        reason: str = "",
        intensity: float = 0.5,
    ):
        """记录情绪事件。"""
        memory = await self.get_or_create(persona_id, user_id)
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

    async def add_key_fact(self, persona_id: str, user_id: str, fact: str):
        """添加角色对用户的关键认知。"""
        memory = await self.get_or_create(persona_id, user_id)
        if fact not in memory.key_facts:
            memory.key_facts.append(fact)
        # 限制 30 条
        if len(memory.key_facts) > 30:
            memory.key_facts = memory.key_facts[-30:]

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
            hours_ago = (datetime.now(timezone.utc) - memory.last_interaction).total_seconds() / 3600
            parts.append(f"上次互动: {hours_ago:.0f} 小时前")

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
        elapsed = (datetime.now(timezone.utc) - memory.last_interaction).total_seconds() / 3600
        return elapsed >= min_hours
