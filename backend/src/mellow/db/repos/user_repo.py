"""UserRepository —— 用户数据访问抽象接口与 SQLAlchemy 实现。"""

import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mellow.db.models.user import UserRow
from mellow.exceptions import ConflictError, NotFoundError


class UserRepository(ABC):
    """用户数据访问抽象接口。"""

    @abstractmethod
    async def get_by_username(self, username: str) -> UserRow | None:
        """按用户名查找用户。"""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> UserRow | None:
        """按 ID 查找用户。"""
        ...

    @abstractmethod
    async def create(self, username: str, password_hash: str) -> UserRow:
        """创建新用户。用户名重复时抛出 ConflictError。"""
        ...

    @abstractmethod
    async def update_active(self, user_id: str, is_active: bool) -> UserRow:
        """更新用户活跃状态。用户不存在时抛出 NotFoundError。"""
        ...


class SqlAlchemyUserRepository(UserRepository):
    """基于 SQLAlchemy AsyncSession 的 UserRepository 实现。"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_username(self, username: str) -> UserRow | None:
        """按用户名查找用户（不区分大小写）。"""
        stmt = select(UserRow).where(UserRow.username == username.lower().strip())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> UserRow | None:
        """按 ID 查找用户。"""
        return await self._session.get(UserRow, user_id)

    async def create(self, username: str, password_hash: str) -> UserRow:
        """创建新用户。"""
        username = username.lower().strip()
        user_id = str(uuid.uuid4())
        user_row = UserRow(
            id=user_id,
            username=username,
            password_hash=password_hash,
            is_active=True,
        )
        self._session.add(user_row)
        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            raise ConflictError("用户名已存在")
        return user_row

    async def update_active(self, user_id: str, is_active: bool) -> UserRow:
        """更新用户活跃状态。"""
        user_row = await self.get_by_id(user_id)
        if user_row is None:
            raise NotFoundError("用户不存在")
        user_row.is_active = is_active
        await self._session.flush()
        return user_row