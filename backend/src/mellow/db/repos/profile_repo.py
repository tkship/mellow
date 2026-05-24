"""LearningProfileRepository —— 学习档案数据访问层。"""

import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mellow.db.models.profile import LearningProfileRow
from mellow.memory.models import (
    DailyPlan,
    LearningProfile,
    MistakeEntry,
    WeeklyPlan,
)
from mellow.exceptions import NotFoundError


class LearningProfileRepository(ABC):
    """学习档案数据访问抽象接口。"""

    @abstractmethod
    async def get(self, user_id: str) -> LearningProfileRow | None:
        """按 user_id 查找学习档案。"""
        ...

    @abstractmethod
    async def get_or_create(self, user_id: str) -> LearningProfileRow:
        """获取或创建学习档案。"""
        ...

    @abstractmethod
    async def save(self, row: LearningProfileRow) -> LearningProfileRow:
        """保存（upsert）学习档案。"""
        ...

    @abstractmethod
    async def update_fields(self, user_id: str, **kwargs) -> LearningProfileRow:
        """更新指定字段。"""
        ...


class SqlAlchemyLearningProfileRepository(LearningProfileRepository):
    """基于 SQLAlchemy AsyncSession 的学习档案 Repository。"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: str) -> LearningProfileRow | None:
        return await self._session.get(LearningProfileRow, user_id)

    async def get_or_create(self, user_id: str) -> LearningProfileRow:
        row = await self.get(user_id)
        if row is None:
            row = LearningProfileRow(user_id=user_id)
            self._session.add(row)
            await self._session.flush()
        return row

    async def save(self, row: LearningProfileRow) -> LearningProfileRow:
        self._session.add(row)
        await self._session.flush()
        return row

    async def update_fields(self, user_id: str, **kwargs) -> LearningProfileRow:
        row = await self.get_or_create(user_id)
        for key, value in kwargs.items():
            if hasattr(row, key) and value is not None:
                setattr(row, key, value)
        row.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return row


# ---- JSON 序列化辅助 ----

def profile_to_row(profile: LearningProfile, row: LearningProfileRow | None = None) -> LearningProfileRow:
    """将 Pydantic LearningProfile 转换为 ORM LearningProfileRow。"""
    if row is None:
        row = LearningProfileRow(user_id=profile.user_id)

    row.vocabulary_size = profile.vocabulary_size
    row.cefr_level = profile.cefr_level
    row.mastered_words_json = json.dumps(profile.mastered_words, ensure_ascii=False)
    row.weak_areas_json = json.dumps(profile.weak_areas, ensure_ascii=False)
    row.mistake_log_json = json.dumps([m.model_dump(mode='json') for m in profile.mistake_log], ensure_ascii=False)
    row.completed_lessons_json = json.dumps(profile.completed_lessons, ensure_ascii=False)
    row.current_plan_json = profile.current_plan.model_dump_json() if profile.current_plan else None
    row.plan_history_json = json.dumps([p.model_dump(mode='json') for p in profile.plan_history], ensure_ascii=False)
    row.updated_at = profile.updated_at
    return row


def row_to_profile(row: LearningProfileRow) -> LearningProfile:
    """将 ORM LearningProfileRow 转换为 Pydantic LearningProfile。"""
    mastered_words: dict[str, float] = json.loads(row.mastered_words_json or "{}")
    weak_areas: list[str] = json.loads(row.weak_areas_json or "[]")
    completed_lessons: list[str] = json.loads(row.completed_lessons_json or "[]")
    mistake_log = [
        MistakeEntry(**m)
        for m in json.loads(row.mistake_log_json or "[]")
    ]
    current_plan = WeeklyPlan(**json.loads(row.current_plan_json)) if row.current_plan_json else None
    plan_history = [
        WeeklyPlan(**p)
        for p in json.loads(row.plan_history_json or "[]")
    ]

    return LearningProfile(
        user_id=row.user_id,
        vocabulary_size=row.vocabulary_size,
        cefr_level=row.cefr_level,
        weak_areas=weak_areas,
        mastered_words=mastered_words,
        mistake_log=mistake_log,
        completed_lessons=completed_lessons,
        current_plan=current_plan,
        plan_history=plan_history,
        created_at=row.created_at,
        updated_at=row.updated_at if row.updated_at else row.created_at,
    )