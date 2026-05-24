"""User ORM 模型。"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, String, func
from sqlalchemy.orm import Mapped, mapped_column

from mellow.db.base import Base, TimestampMixin
from mellow.providers.auth import UserInfo


class UserRow(Base, TimestampMixin):
    """用户表 ORM 模型。"""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", nullable=False)

    def to_user_info(self) -> UserInfo:
        """转换为 UserInfo 数据类。"""
        return UserInfo(
            id=self.id,
            username=self.username,
            is_active=self.is_active,
        )