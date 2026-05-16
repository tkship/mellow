"""学习档案管理器 —— 管理 LearningProfile 的 CRUD。

存储：SQLite（Phase 5 先内存实现，后续接入 SQLAlchemy）。
"""

from datetime import datetime, timezone
from typing import Any

from mellow.memory.models import (
    DailyPlan,
    LearningProfile,
    MistakeEntry,
    WeeklyPlan,
)


class LearningProfileManager:
    """学习档案管理器。

    核心职责：
    - 追踪已掌握单词（去重）
    - 记录错误日志
    - 管理学习计划
    - 提供用户画像摘要供 Agent 使用
    """

    def __init__(self):
        # Phase 5: 内存存储 → 后续换 SQLAlchemy
        self._profiles: dict[str, LearningProfile] = {}

    # ---- CRUD ----

    async def get_or_create(self, user_id: str) -> LearningProfile:
        if user_id not in self._profiles:
            self._profiles[user_id] = LearningProfile(user_id=user_id)
        return self._profiles[user_id]

    async def update(self, user_id: str, **kwargs) -> LearningProfile:
        profile = await self.get_or_create(user_id)
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.updated_at = datetime.now(timezone.utc)
        return profile

    # ---- 单词掌握 ----

    async def record_word_mastery(self, user_id: str, word: str, level: float):
        """记录单词掌握度。0.0=新词, 1.0=完全掌握。"""
        profile = await self.get_or_create(user_id)
        word = word.lower().strip()
        if word in profile.mastered_words:
            # 取最高值
            profile.mastered_words[word] = max(profile.mastered_words[word], level)
        else:
            profile.mastered_words[word] = level
        profile.updated_at = datetime.now(timezone.utc)

    async def get_known_words(self, user_id: str, threshold: float = 0.7) -> set[str]:
        """获取已掌握的单词集合（用于计划生成时去重）。"""
        profile = await self.get_or_create(user_id)
        return {w for w, l in profile.mastered_words.items() if l >= threshold}

    async def is_word_known(self, user_id: str, word: str, threshold: float = 0.7) -> bool:
        known = await self.get_known_words(user_id, threshold)
        return word.lower().strip() in known

    # ---- 错误日志 ----

    async def log_mistake(self, user_id: str, entry: MistakeEntry):
        profile = await self.get_or_create(user_id)
        profile.mistake_log.append(entry)
        # 限制最多保留 200 条
        if len(profile.mistake_log) > 200:
            profile.mistake_log = profile.mistake_log[-200:]
        profile.updated_at = datetime.now(timezone.utc)

    async def get_recent_mistakes(self, user_id: str, limit: int = 10) -> list[MistakeEntry]:
        profile = await self.get_or_create(user_id)
        return profile.mistake_log[-limit:]

    async def get_weak_areas(self, user_id: str) -> list[str]:
        """分析弱项 —— 基于错误频率。"""
        profile = await self.get_or_create(user_id)
        if not profile.weak_areas:
            from collections import Counter
            types = Counter(m.mistake_type for m in profile.mistake_log)
            profile.weak_areas = [t for t, _ in types.most_common(5)]
        return profile.weak_areas

    # ---- 学习计划 ----

    async def set_plan(self, user_id: str, plan: WeeklyPlan):
        profile = await self.get_or_create(user_id)
        if profile.current_plan:
            profile.plan_history.append(profile.current_plan)
        profile.current_plan = plan
        profile.updated_at = datetime.now(timezone.utc)

    async def complete_plan(self, user_id: str):
        profile = await self.get_or_create(user_id)
        if profile.current_plan:
            profile.current_plan.completed = True
            profile.completed_lessons.append(profile.current_plan.theme)
            profile.plan_history.append(profile.current_plan)
            profile.current_plan = None
            profile.updated_at = datetime.now(timezone.utc)

    # ---- 画像摘要 ----

    async def get_profile_summary(self, user_id: str) -> str:
        """生成用户画像摘要 —— 供 Agent prompt 使用。"""
        profile = await self.get_or_create(user_id)
        known_count = len([w for w, l in profile.mastered_words.items() if l >= 0.7])
        weak = await self.get_weak_areas(user_id)

        parts = [
            f"CEFR 等级: {profile.cefr_level}",
            f"词汇量: ~{profile.vocabulary_size} (已掌握: {known_count})",
        ]
        if weak:
            parts.append(f"弱项: {', '.join(weak[:3])}")
        if profile.current_plan:
            parts.append(f"当前计划: 第{profile.current_plan.week}周「{profile.current_plan.theme}」")
        if profile.completed_lessons:
            recent = profile.completed_lessons[-3:]
            parts.append(f"最近完成: {', '.join(recent)}")

        return "。".join(parts) + "。"
