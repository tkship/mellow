"""CEFR 进度追踪 ORM 模型。"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from mellow.db.base import Base


class CefrProgressRow(Base):
    """CEFR 进度追踪表。

    每次用户有活动（对话、查词等）时记录一条快照。
    前端用这些数据绘制 CEFR 历史曲线。
    """

    __tablename__ = "cefr_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    cefr_level: Mapped[str] = mapped_column(String(8), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vocabulary_size: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )