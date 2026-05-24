"""测试 SqlAlchemyUserRepository 的 CRUD 操作。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mellow.db.init_db import init_db
from mellow.db.repos.user_repo import SqlAlchemyUserRepository
from mellow.db.models.user import UserRow
from mellow.exceptions import ConflictError, NotFoundError


@pytest.fixture
async def session():
    """创建内存数据库的测试 session。"""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    await init_db(engine)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as sess:
        yield sess

    await engine.dispose()


@pytest.fixture
def user_repo(session):
    """创建 UserRepository 实例。"""
    return SqlAlchemyUserRepository(session)


@pytest.mark.asyncio
async def test_create_user(user_repo, session):
    """创建用户应成功并返回 UserRow。"""
    user = await user_repo.create("testuser", "hash123")
    await session.commit()

    assert user.id is not None
    assert user.username == "testuser"
    assert user.password_hash == "hash123"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_create_duplicate_username_raises_conflict(user_repo, session):
    """创建重复用户名应抛出 ConflictError。"""
    await user_repo.create("duplicate", "hash1")
    await session.commit()

    with pytest.raises(ConflictError):
        await user_repo.create("duplicate", "hash2")


@pytest.mark.asyncio
async def test_get_by_username(user_repo, session):
    """按用户名查找应返回对应 UserRow。"""
    created = await user_repo.create("findme", "hash123")
    await session.commit()

    found = await user_repo.get_by_username("findme")
    assert found is not None
    assert found.id == created.id
    assert found.username == "findme"


@pytest.mark.asyncio
async def test_get_by_username_not_found(user_repo):
    """查找不存在的用户名应返回 None。"""
    result = await user_repo.get_by_username("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_get_by_username_case_insensitive(user_repo, session):
    """按用户名查找应不区分大小写（存储时已 lower）。"""
    await user_repo.create("TestUser", "hash123")
    await session.commit()

    found = await user_repo.get_by_username("testuser")
    assert found is not None


@pytest.mark.asyncio
async def test_get_by_id(user_repo, session):
    """按 ID 查找应返回对应 UserRow。"""
    created = await user_repo.create("byid", "hash123")
    await session.commit()

    found = await user_repo.get_by_id(created.id)
    assert found is not None
    assert found.username == "byid"


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_repo):
    """查找不存在的 ID 应返回 None。"""
    result = await user_repo.get_by_id("nonexistent-id")
    assert result is None


@pytest.mark.asyncio
async def test_update_active(user_repo, session):
    """更新活跃状态应成功。"""
    created = await user_repo.create("activeuser", "hash123")
    await session.commit()

    updated = await user_repo.update_active(created.id, False)
    await session.commit()

    assert updated.is_active is False


@pytest.mark.asyncio
async def test_update_active_user_not_found(user_repo):
    """更新不存在的用户应抛出 NotFoundError。"""
    with pytest.raises(NotFoundError):
        await user_repo.update_active("nonexistent-id", False)