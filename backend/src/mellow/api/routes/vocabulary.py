"""生词本路由 —— 用户词汇库 CRUD。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from mellow.api.deps import get_container, get_current_user, get_db_session
from mellow.db.repos.vocabulary_repo import SqlAlchemyVocabularyRepository, row_to_dict
from mellow.di import Container
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/vocabulary", tags=["vocabulary"])


class VocabularyCreate(BaseModel):
    """Pydantic model for vocabulary creation with field validation."""

    word: str = Field(..., min_length=1, max_length=200, description="单词")
    phonetic: str = Field(default="", max_length=200, description="音标")
    part_of_speech: str = Field(default="", max_length=50, description="词性")
    definitions: list[str] = Field(default_factory=list, max_length=20, description="释义列表")
    examples: list[str] = Field(default_factory=list, max_length=20, description="例句列表")
    synonyms: list[str] = Field(default_factory=list, max_length=20, description="同义词列表")
    added_at: str = Field(default="", max_length=50, description="添加时间")

    model_config = {"extra": "ignore"}

    @field_validator("definitions", "examples", "synonyms")
    @classmethod
    def validate_list_items(cls, v: list[str]) -> list[str]:
        """Validate each string item in list fields is at most 500 characters."""
        for i, item in enumerate(v):
            if len(item) > 500:
                raise ValueError(
                    f"Item {i} in list exceeds 500 characters (got {len(item)})"
                )
        return v


@router.get("/book")
async def list_vocabulary(
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """获取用户生词本列表。

    返回按首字母分组的结构，方便前端按字母分组展示。
    """
    repo = SqlAlchemyVocabularyRepository(session)
    rows = await repo.list_by_user(user.id)
    words = [row_to_dict(r) for r in rows]

    if True:  # sort logic
        pass

    # Group by first letter
    groups: dict[str, list] = {}
    for w in words:
        letter = w["word"][0].upper() if w["word"] else "#"
        groups.setdefault(letter, []).append(w)

    return {
        "total": len(words),
        "groups": [
            {"letter": k, "words": sorted(v, key=lambda w: w["word"].lower()), "count": len(v)}
            for k, v in sorted(groups.items())
        ],
    }


@router.get("/book/search")
async def search_vocabulary(
    q: str,
    sort: str = "recent",
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """搜索生词本。"""
    repo = SqlAlchemyVocabularyRepository(session)
    rows = await repo.search(user.id, q)
    results = [row_to_dict(r) for r in rows]
    return {"results": results, "total": len(results)}


@router.post("/book")
async def add_vocabulary(
    word_data: VocabularyCreate,
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """添加单词到生词本。"""
    word = word_data.word.strip().lower()
    if not word:
        raise HTTPException(status_code=400, detail="单词不能为空")

    repo = SqlAlchemyVocabularyRepository(session)
    existing = await repo.get_word(user.id, word)
    if existing:
        return {"status": "exists", "word": row_to_dict(existing)}

    row = await repo.add_word(
        user_id=user.id,
        word=word,
        phonetic=word_data.phonetic,
        part_of_speech=word_data.part_of_speech,
        definitions=word_data.definitions,
        examples=word_data.examples,
        synonyms=word_data.synonyms,
        added_at=word_data.added_at,
    )
    # commit 由 get_db_session 依赖自动处理
    return {"status": "added", "word": row_to_dict(row)}


@router.delete("/book/{word}")
async def remove_vocabulary(
    word: str,
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """从生词本删除单词。"""
    repo = SqlAlchemyVocabularyRepository(session)
    removed = await repo.remove_word(user.id, word)
    if not removed:
        raise HTTPException(status_code=404, detail="单词不在生词本中")

    return {"status": "removed", "word": word.strip().lower()}