"""生词本 ORM 模型。"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mellow.db.base import Base, TimestampMixin


class VocabularyEntryRow(Base, TimestampMixin):
    """生词本表 ORM 模型。

    每个 (user_id, word) 组合唯一。
    JSON 字段（definitions, examples, synonyms）存储为 TEXT。
    """

    __tablename__ = "vocabulary_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "word", name="uq_vocab_user_word"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    word: Mapped[str] = mapped_column(String(200), nullable=False)
    phonetic: Mapped[str] = mapped_column(String(200), default="", server_default="", nullable=False)
    part_of_speech: Mapped[str] = mapped_column(String(50), default="", server_default="", nullable=False)
    definitions_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    examples_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    synonyms_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        server_default="1970-01-01 00:00:00", nullable=False,
    )