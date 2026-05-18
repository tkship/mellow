"""生词本路由 —— 用户词汇库 CRUD。"""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from mellow.api.deps import get_current_user
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

    class Config:
        extra = "ignore"

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

# Persistent storage path
_DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
_VOCAB_FILE = _DATA_DIR / "vocabulary_books.json"


def _load_vocab_books() -> dict[str, dict[str, dict]]:
    """Load vocabulary books from JSON file."""
    if _VOCAB_FILE.exists():
        try:
            with open(_VOCAB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_vocab_books() -> None:
    """Save vocabulary books to JSON file."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(_vocab_books, f, ensure_ascii=False, indent=2)


# In-memory storage, loaded from JSON on startup
_vocab_books: dict[str, dict[str, dict]] = _load_vocab_books()


def _get_book(user_id: str) -> dict[str, dict]:
    """Get or create user's vocabulary book."""
    if user_id not in _vocab_books:
        _vocab_books[user_id] = {}
    return _vocab_books[user_id]


@router.get("/book")
async def list_vocabulary(
    user: UserInfo = Depends(get_current_user),
    sort: str = "recent",
) -> dict:
    """获取用户生词本列表。

    返回按首字母分组的结构，方便前端按字母分组展示。
    """
    book = _get_book(user.id)
    words = list(book.values())

    if sort == "alpha":
        words.sort(key=lambda w: w["word"].lower())

    # Group by first letter
    groups: dict[str, list] = {}
    for w in words:
        letter = w["word"][0].upper() if w["word"] else "#"
        groups.setdefault(letter, []).append(w)

    return {
        "total": len(words),
        "groups": [
            {"letter": k, "words": v, "count": len(v)}
            for k, v in sorted(groups.items())
        ],
    }


@router.post("/book")
async def add_vocabulary(
    word_data: VocabularyCreate,
    user: UserInfo = Depends(get_current_user),
) -> dict:
    """添加单词到生词本。

    Args:
        word_data: Validated vocabulary creation payload (word required, rest optional).
    """
    word = word_data.word.strip().lower()
    if not word:
        raise HTTPException(status_code=400, detail="单词不能为空")

    book = _get_book(user.id)
    if word in book:
        return {"status": "exists", "word": book[word]}

    book[word] = {
        "word": word,
        "phonetic": word_data.phonetic,
        "part_of_speech": word_data.part_of_speech,
        "definitions": word_data.definitions,
        "examples": word_data.examples,
        "synonyms": word_data.synonyms,
        "added_at": word_data.added_at,
    }
    _save_vocab_books()
    return {"status": "added", "word": book[word]}


@router.delete("/book/{word}")
async def remove_vocabulary(
    word: str,
    user: UserInfo = Depends(get_current_user),
) -> dict:
    """从生词本删除单词。"""
    book = _get_book(user.id)
    word_lower = word.strip().lower()

    if word_lower not in book:
        raise HTTPException(status_code=404, detail="单词不在生词本中")

    del book[word_lower]
    _save_vocab_books()
    return {"status": "removed", "word": word_lower}


@router.get("/book/search")
async def search_vocabulary(
    q: str,
    user: UserInfo = Depends(get_current_user),
) -> dict:
    """搜索生词本。"""
    query = q.strip().lower()
    book = _get_book(user.id)

    results = [
        w for w in book.values()
        if query in w["word"].lower()
        or any(query in d.lower() for d in w.get("definitions", []))
    ]
    return {"results": results, "total": len(results)}
