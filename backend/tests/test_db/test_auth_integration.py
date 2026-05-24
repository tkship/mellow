"""测试 JWTAuthProvider 通过 UserRepository 的注册、登录、验证、刷新流程。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mellow.auth.jwt_auth import JWTAuthProvider
from mellow.config import Settings
from mellow.db.init_db import init_db
from mellow.db.repos.user_repo import SqlAlchemyUserRepository
from mellow.exceptions import AuthenticationError, ConflictError


@pytest.fixture
async def auth_provider():
    """创建使用 SQLite 后端的 JWTAuthProvider。"""
    settings = Settings(
        jwt_secret="test-secret",
        jwt_expire_minutes=60,
        llm_api_key="test-key",
        embed_api_key="test-key",
        database_url="sqlite+aiosqlite://",
        database_echo=False,
    )

    engine = create_async_engine(settings.database_url, echo=settings.database_echo)
    await init_db(engine)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    provider = JWTAuthProvider(settings=settings, session_factory=factory)
    yield provider

    await engine.dispose()


@pytest.mark.asyncio
async def test_register_and_login(auth_provider):
    """注册后应能登录并获取 Token。"""
    user = await auth_provider.register("testuser", "password123")
    assert user.username == "testuser"
    assert user.id

    token = await auth_provider.login("testuser", "password123")
    assert token.access_token
    assert token.refresh_token


@pytest.mark.asyncio
async def test_login_wrong_password(auth_provider):
    """密码错误应抛出 AuthenticationError。"""
    await auth_provider.register("testuser", "correct")
    with pytest.raises(AuthenticationError):
        await auth_provider.login("testuser", "wrong")


@pytest.mark.asyncio
async def test_login_nonexistent_user(auth_provider):
    """登录不存在的用户应抛出 AuthenticationError。"""
    with pytest.raises(AuthenticationError):
        await auth_provider.login("nonexistent", "password")


@pytest.mark.asyncio
async def test_verify_token(auth_provider):
    """验证有效 Token 应返回 UserInfo。"""
    await auth_provider.register("testuser", "pass")
    token = await auth_provider.login("testuser", "pass")
    user = await auth_provider.verify_token(token.access_token)
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_refresh_token(auth_provider):
    """刷新 Token 应返回新的 TokenPair。"""
    await auth_provider.register("testuser", "pass")
    token = await auth_provider.login("testuser", "pass")
    new_token = await auth_provider.refresh_token(token.refresh_token)
    assert new_token.access_token
    assert new_token.refresh_token


@pytest.mark.asyncio
async def test_duplicate_register(auth_provider):
    """重复注册应抛出 ConflictError。"""
    await auth_provider.register("testuser", "pass")
    with pytest.raises(ConflictError):
        await auth_provider.register("testuser", "pass2")


@pytest.mark.asyncio
async def test_verify_invalid_token(auth_provider):
    """验证无效 Token 应抛出 AuthenticationError。"""
    with pytest.raises(AuthenticationError):
        await auth_provider.verify_token("invalid-token")


@pytest.mark.asyncio
async def test_refresh_invalid_token(auth_provider):
    """刷新无效 Token 应抛出 AuthenticationError。"""
    with pytest.raises(AuthenticationError):
        await auth_provider.refresh_token("invalid-token")