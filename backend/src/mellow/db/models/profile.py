"""学习档案 ORM 模型。"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from mellow.db.base import Base, TimestampMixin


class LearningProfileRow(Base, TimestampMixin):
    """学习档案表 ORM 模型。

    将 Pydantic LearningProfile 的字段持久化。
    JSON 字段（mastered_words, weak_areas, completed_lessons, mistake_log）
    存储为 TEXT，运行时序列化/反序列化。
    """

    __tablename__ = "learning_profiles"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    vocabulary_size: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    cefr_level: Mapped[str] = mapped_column(String(8), default="A1", server_default="A1", nullable=False)
    mastered_words_json: Mapped[str] = mapped_column(Text, default="{}", server_default="{}", nullable=False)
    weak_areas_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    mistake_log_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    completed_lessons_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    current_plan_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan_history_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )