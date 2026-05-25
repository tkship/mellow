"""VocabularyRepository —— 生词本数据访问层。"""

import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mellow.db.models.vocabulary import VocabularyEntryRow
from mellow.exceptions import NotFoundError


class VocabularyRepository(ABC):
    """生词本数据访问抽象接口。"""

    @abstractmethod
    async def list_by_user(self, user_id: str) -> list[VocabularyEntryRow]:
        ...

    @abstractmethod
    async def get_word(self, user_id: str, word: str) -> VocabularyEntryRow | None:
        ...

    @abstractmethod
    async def add_word(self, user_id: str, word: str, phonetic: str,
                       part_of_speech: str, definitions: list[str],
                       examples: list[str], synonyms: list[str],
                       added_at: str) -> VocabularyEntryRow:
        ...

    @abstractmethod
    async def remove_word(self, user_id: str, word: str) -> bool:
        ...

    @abstractmethod
    async def search(self, user_id: str, query: str) -> list[VocabularyEntryRow]:
        ...


class SqlAlchemyVocabularyRepository(VocabularyRepository):
    """基于 SQLAlchemy AsyncSession 的生词本 Repository。"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_by_user(self, user_id: str) -> list[VocabularyEntryRow]:
        stmt = select(VocabularyEntryRow).where(
            VocabularyEntryRow.user_id == user_id
        ).order_by(VocabularyEntryRow.id.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_word(self, user_id: str, word: str) -> VocabularyEntryRow | None:
        stmt = select(VocabularyEntryRow).where(
            VocabularyEntryRow.user_id == user_id,
            VocabularyEntryRow.word == word.lower().strip(),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_word(self, user_id: str, word: str, phonetic: str,
                       part_of_speech: str, definitions: list[str],
                       examples: list[str], synonyms: list[str],
                       added_at: str) -> VocabularyEntryRow:
        word_lower = word.lower().strip()
        # 将字符串 added_at 转为 datetime（兼容 isoformat 格式）
        if added_at:
            try:
                added_at_dt = datetime.fromisoformat(added_at.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                added_at_dt = datetime.now(timezone.utc)
        else:
            added_at_dt = datetime.now(timezone.utc)
        row = VocabularyEntryRow(
            user_id=user_id,
            word=word_lower,
            phonetic=phonetic,
            part_of_speech=part_of_speech,
            definitions_json=json.dumps(definitions, ensure_ascii=False),
            examples_json=json.dumps(examples, ensure_ascii=False),
            synonyms_json=json.dumps(synonyms, ensure_ascii=False),
            added_at=added_at_dt,
        )
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError:
            # (user_id, word) 唯一约束冲突 — 单词已存在
            await self._session.rollback()
            existing = await self.get_word(user_id, word_lower)
            return existing  # type: ignore[return-value]
        return row

    async def remove_word(self, user_id: str, word: str) -> bool:
        row = await self.get_word(user_id, word)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True

    async def search(self, user_id: str, query: str) -> list[VocabularyEntryRow]:
        q = query.strip().lower()
        stmt = select(VocabularyEntryRow).where(
            VocabularyEntryRow.user_id == user_id,
        ).order_by(VocabularyEntryRow.id.desc())
        result = await self._session.execute(stmt)
        all_rows = list(result.scalars().all())
        # Filter in Python for definitions search (JSON field)
        results = []
        for row in all_rows:
            if q in row.word.lower():
                results.append(row)
                continue
            definitions = json.loads(row.definitions_json or "[]")
            if any(q in d.lower() for d in definitions):
                results.append(row)
        return results


# ---- 辅助函数 ----

def row_to_dict(row: VocabularyEntryRow) -> dict:
    """将 ORM VocabularyEntryRow 转换为 API 返回的 dict。"""
    return {
        "word": row.word,
        "phonetic": row.phonetic,
        "part_of_speech": row.part_of_speech,
        "definitions": json.loads(row.definitions_json or "[]"),
        "examples": json.loads(row.examples_json or "[]"),
        "synonyms": json.loads(row.synonyms_json or "[]"),
        "added_at": row.added_at,
    }