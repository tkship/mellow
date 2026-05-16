"""主动联系定时调度器。

每隔 proactive_check_interval_minutes 检查所有用户，
对超过 interaction_rhythm 未互动的用户生成角色化开场白。
"""

import asyncio
import logging

from mellow.di import Container
from mellow.memory.proactive import ProactiveMessenger

logger = logging.getLogger(__name__)


class ProactiveScheduler:
    """主动联系调度器。

    在 FastAPI lifespan 中启动后台任务。
    """

    def __init__(self, container: Container):
        self._container = container
        self._messenger: ProactiveMessenger | None = None
        self._task: asyncio.Task | None = None

    async def start(self):
        """启动后台检查循环。"""
        llm = await self._container.llm()
        self._messenger = ProactiveMessenger(llm)
        interval = self._container.settings.proactive_check_interval_minutes * 60
        self._task = asyncio.create_task(self._loop(interval))

    async def _loop(self, interval: int):
        while True:
            try:
                await self._check_all_users()
            except Exception:
                logger.exception("ProactiveScheduler check_all_users failed")
            await asyncio.sleep(interval)

    async def _check_all_users(self):
        """检查所有用户是否需要主动联系。"""
        # Phase 9: 简化实现 —— 遍历内存中的用户记忆
        memory_mgr = await self._container.memory_manager()
        profile_mgr = await self._container.profile_manager()
        persona_mgr = await self._container.persona_manager()

        # 获取所有 (persona_id, user_id) 组合
        for key, memory in memory_mgr._memories.items():
            persona_id, user_id = key.split(":", 1)

            persona = persona_mgr.get_persona(persona_id)
            if not persona or not persona.interaction_rhythm:
                continue

            min_h, max_h = persona.interaction_rhythm

            if not await memory_mgr.needs_proactive_poke(persona_id, user_id, min_h, max_h):
                continue

            profile_summary = await profile_mgr.get_profile_summary(user_id)

            msg = await self._messenger.check_and_generate(
                user_id=user_id,
                persona_id=persona_id,
                memory=memory,
                persona_name=persona.name,
                persona_role=persona.role,
                personality=persona.language_style.tone,
                intimacy=persona.intimacy_level,
                profile_summary=profile_summary,
                min_hours=min_h,
            )

            if msg:
                # 消息已生成，存入待投递队列
                # 用户下次连接时通过 memory 端点获取
                pass

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
