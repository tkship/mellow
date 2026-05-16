"""主动联系管理器 —— 定时器驱动的 Agent 主动消息。

核心流程：
1. 每次用户互动后，随机生成下次主动联系的时间窗口
2. 定时检查到期用户
3. LLM 根据角色记忆生成自然的开场白
4. 写入消息队列，用户下次上线时展示
"""

import random
import uuid
from datetime import datetime, timedelta, timezone

from mellow.llm.client import LLMProvider
from mellow.memory.models import PersonaMemory, ProactiveMessage
from mellow.models import Message, MessageRole

PROACTIVE_PROMPT = """你是一个名为 {name} 的{role}。你注意到 {user_name} 已经一段时间没有和你互动了。

基于以下信息，生成一段自然、符合你角色的开场白：
- 你的性格: {personality}
- 你们的关系: {intimacy}
- 用户学习情况: {profile_summary}
- 你们的记忆: {memory_context}

规则：
1. 语气完全符合你的角色设定
2. 自然地关心对方，不要像系统通知
3. 适当提及对方的学习，但不要催促
4. 50 字以内，简洁自然
5. 用中文回复"""


class ProactiveMessenger:
    """主动联系管理器。"""

    def __init__(self, llm: LLMProvider):
        self._llm = llm
        self._pending_messages: dict[str, list[ProactiveMessage]] = {}

    def generate_poke_window(self, min_hours: int, max_hours: int) -> timedelta:
        """根据角色的 interaction_rhythm 随机生成下次联系时间。"""
        if min_hours >= max_hours:
            max_hours = min_hours + 1
        hours = random.randint(min_hours, max_hours)
        return timedelta(hours=hours)

    async def check_and_generate(
        self,
        user_id: str,
        persona_id: str,
        memory: PersonaMemory,
        persona_name: str,
        persona_role: str,
        personality: str,
        intimacy: str,
        profile_summary: str,
        min_hours: int = 12,
    ) -> ProactiveMessage | None:
        """检查是否需要主动联系，如果需要则生成消息。"""
        if not memory.last_interaction:
            return None

        now = datetime.now(timezone.utc)
        elapsed = (now - memory.last_interaction).total_seconds() / 3600

        if elapsed < min_hours:
            return None

        # 已生成过但未投递的消息，跳过
        key = f"{user_id}:{persona_id}"
        if key in self._pending_messages:
            return None

        memory_context = (
            f"关系: {memory.relationship_summary[:200]}" if memory.relationship_summary else "新朋友"
        )

        msgs = [
            Message(
                role=MessageRole.SYSTEM,
                content=PROACTIVE_PROMPT.format(
                    name=persona_name,
                    role=persona_role,
                    user_name=user_id,
                    personality=personality,
                    intimacy=intimacy,
                    profile_summary=profile_summary,
                    memory_context=memory_context,
                ),
            ),
        ]

        try:
            content = await self._llm.chat(msgs, temperature=0.9, max_tokens=128)
        except Exception:
            return None

        msg = ProactiveMessage(
            id=str(uuid.uuid4())[:8],
            user_id=user_id,
            persona_id=persona_id,
            content=content.strip(),
            scheduled_at=now,
        )

        self._pending_messages.setdefault(key, []).append(msg)
        return msg

    def get_pending(self, user_id: str, persona_id: str) -> list[ProactiveMessage]:
        """获取用户的待投递主动消息。"""
        key = f"{user_id}:{persona_id}"
        return self._pending_messages.pop(key, [])

    def mark_delivered(self, user_id: str, persona_id: str):
        """标记消息已投递。"""
        key = f"{user_id}:{persona_id}"
        self._pending_messages.pop(key, None)
