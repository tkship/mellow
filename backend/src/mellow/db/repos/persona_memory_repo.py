"""PersonaMemoryRepository —— 角色记忆数据访问层。"""

import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mellow.db.models.persona_memory import PersonaMemoryRow
from mellow.memory.models import MoodEvent, PersonaMemory


class PersonaMemoryRepository(ABC):
    """角色记忆数据访问抽象接口。"""

    @abstractmethod
    async def get(self, persona_id: str, user_id: str) -> PersonaMemoryRow | None:
        ...

    @abstractmethod
    async def get_or_create(self, persona_id: str, user_id: str) -> PersonaMemoryRow:
        ...

    @abstractmethod
    async def save(self, row: PersonaMemoryRow) -> PersonaMemoryRow:
        ...

    @abstractmethod
    async def list_all(self) -> list[PersonaMemoryRow]:
        """获取所有记忆记录。"""
        ...


class SqlAlchemyPersonaMemoryRepository(PersonaMemoryRepository):
    """基于 SQLAlchemy AsyncSession 的角色记忆 Repository。"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, persona_id: str, user_id: str) -> PersonaMemoryRow | None:
        stmt = select(PersonaMemoryRow).where(
            PersonaMemoryRow.persona_id == persona_id,
            PersonaMemoryRow.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, persona_id: str, user_id: str) -> PersonaMemoryRow:
        row = await self.get(persona_id, user_id)
        if row is None:
            row = PersonaMemoryRow(persona_id=persona_id, user_id=user_id)
            self._session.add(row)
            await self._session.flush()
        return row

    async def save(self, row: PersonaMemoryRow) -> PersonaMemoryRow:
        self._session.add(row)
        await self._session.flush()
        return row

    async def list_all(self) -> list[PersonaMemoryRow]:
        """获取所有记忆记录。"""
        stmt = select(PersonaMemoryRow)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


# ---- JSON 序列化辅助 ----

def mem_to_row(memory: PersonaMemory, row: PersonaMemoryRow | None = None) -> PersonaMemoryRow:
    """将 Pydantic PersonaMemory 转换为 ORM PersonaMemoryRow。"""
    if row is None:
        row = PersonaMemoryRow(persona_id=memory.persona_id, user_id=memory.user_id)

    row.relationship_summary = memory.relationship_summary
    row.emotional_trajectory_json = json.dumps(
        [m.model_dump(mode='json') for m in memory.emotional_trajectory], ensure_ascii=False
    )
    row.key_facts_json = json.dumps(memory.key_facts, ensure_ascii=False)
    row.interaction_count = memory.interaction_count
    row.last_interaction = memory.last_interaction
    row.updated_at = memory.updated_at
    return row


def row_to_mem(row: PersonaMemoryRow) -> PersonaMemory:
    """将 ORM PersonaMemoryRow 转换为 Pydantic PersonaMemory。"""
    emotional_trajectory = [
        MoodEvent(**m)
        for m in json.loads(row.emotional_trajectory_json or "[]")
    ]
    key_facts: list[str] = json.loads(row.key_facts_json or "[]")

    # SQLite 不保留时区信息，读取后手动恢复 UTC
    last_interaction = row.last_interaction
    if last_interaction is not None and last_interaction.tzinfo is None:
        last_interaction = last_interaction.replace(tzinfo=timezone.utc)

    created_at = row.created_at
    if created_at is not None and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    updated_at = row.updated_at if row.updated_at else row.created_at
    if updated_at is not None and updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)

    return PersonaMemory(
        persona_id=row.persona_id,
        user_id=row.user_id,
        relationship_summary=row.relationship_summary or "",
        emotional_trajectory=emotional_trajectory,
        key_facts=key_facts,
        last_interaction=last_interaction,
        interaction_count=row.interaction_count,
        created_at=created_at,
        updated_at=updated_at,
    )