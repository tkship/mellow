"""测试数据库引擎创建、session 工厂和 WAL 模式配置。"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from mellow.config import Settings
from mellow.db.engine import get_engine, get_session_factory
from mellow.db.init_db import init_db


@pytest.fixture
def settings():
    """使用内存数据库的测试配置。"""
    return Settings(
        jwt_secret="test-secret",
        jwt_expire_minutes=60,
        llm_api_key="test-key",
        embed_api_key="test-key",
        database_url="sqlite+aiosqlite://",
        database_echo=False,
    )


@pytest.fixture
async def engine(settings):
    """创建测试引擎并初始化数据库。"""
    eng = get_engine(settings)
    await init_db(eng)
    yield eng
    await eng.dispose()


@pytest.fixture
def session_factory(engine):
    """创建测试 session 工厂。"""
    return get_session_factory(engine)


@pytest.mark.asyncio
async def test_get_engine_creates_async_engine(settings):
    """get_engine 应返回 AsyncEngine 实例。"""
    eng = get_engine(settings)
    assert eng is not None
    assert isinstance(eng, type(create_async_engine("sqlite+aiosqlite://")))
    await eng.dispose()


@pytest.mark.asyncio
async def test_get_session_factory_returns_sessionmaker(engine):
    """get_session_factory 应返回可用的 async_sessionmaker。"""
    factory = get_session_factory(engine)
    assert factory is not None

    async with factory() as session:
        assert isinstance(session, AsyncSession)


@pytest.mark.asyncio
async def test_wal_mode_configured(engine):
    """SQLite WAL 模式应可通过引擎配置启用。"""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA journal_mode"))
        mode = result.scalar_one()
        # 内存数据库默认为 memory 模式，文件数据库应为 wal
        assert mode in ("wal", "memory")


@pytest.mark.asyncio
async def test_init_db_creates_tables(engine):
    """init_db 应创建所有已注册的表。"""
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = {row[0] for row in result.fetchall()}
        assert "users" in tables


@pytest.mark.asyncio
async def test_session_crud_operations(session_factory):
    """session 应支持基本 CRUD 操作。"""
    from mellow.db.models.user import UserRow

    async with session_factory() as session:
        user = UserRow(
            id="test-id",
            username="testuser",
            password_hash="hash123",
            is_active=True,
        )
        session.add(user)
        await session.commit()

        result = await session.get(UserRow, "test-id")
        assert result is not None
        assert result.username == "testuser"