"""角色记忆 ORM 模型。"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from mellow.db.base import Base, TimestampMixin


class PersonaMemoryRow(Base, TimestampMixin):
    """角色记忆表 ORM 模型。

    每个 (persona_id, user_id) 组合独立存储。
    JSON 字段（emotional_trajectory, key_facts）存储为 TEXT。
    """

    __tablename__ = "persona_memories"

    persona_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    relationship_summary: Mapped[str] = mapped_column(Text, default="", server_default="", nullable=False)
    emotional_trajectory_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    key_facts_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    interaction_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    last_interaction: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )