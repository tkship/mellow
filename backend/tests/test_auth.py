"""认证模块测试。

使用内存 SQLite 数据库测试完整认证流程。
JWTAuthProvider 每次 操作 创建新 session，测试注入 session_factory。
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from mellow.auth.jwt_auth import JWTAuthProvider
from mellow.config import Settings
from mellow.db.base import Base
from mellow.db.models.user import UserRow
from mellow.db.repos.user_repo import SqlAlchemyUserRepository
from mellow.exceptions import AuthenticationError, ConflictError


@pytest.fixture
async def auth_provider():
    """创建使用内存数据库的 JWTAuthProvider 实例。"""
    settings = Settings(jwt_secret="test-secret", jwt_expire_minutes=60)
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    provider = JWTAuthProvider(settings=settings, session_factory=session_factory)
    yield provider

    await engine.dispose()


@pytest.mark.asyncio
async def test_register_and_login(auth_provider):
    user = await auth_provider.register("testuser", "password123")
    assert user.username == "testuser"
    assert user.id

    token = await auth_provider.login("testuser", "password123")
    assert token.access_token
    assert token.refresh_token


@pytest.mark.asyncio
async def test_login_wrong_password(auth_provider):
    await auth_provider.register("testuser", "correct")
    with pytest.raises(AuthenticationError):
        await auth_provider.login("testuser", "wrong")


@pytest.mark.asyncio
async def test_verify_token(auth_provider):
    await auth_provider.register("testuser", "pass")
    token = await auth_provider.login("testuser", "pass")
    user = await auth_provider.verify_token(token.access_token)
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_duplicate_register(auth_provider):
    await auth_provider.register("testuser", "pass")
    with pytest.raises(ConflictError):
        await auth_provider.register("testuser", "pass2")