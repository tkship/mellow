"""pytest 共享固件 —— 为所有 API 集成测试提供基础设施。

设计思路：
1. 使用内存 SQLite 数据库，每次测试自动建表
2. 创建独立的 FastAPI app 实例，避免模块级 overrides 污染
3. 通过真实的 auth 端点注册用户获取 JWT，而非覆写 get_current_user
4. 通用的 client fixture 可直接用于所有 HTTP 测试
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mellow.config import Settings
from mellow.db.base import Base
from mellow.db.engine import get_session_factory
from mellow.di import Container
from mellow.exceptions import MellowError, mellow_exception_handler

# ============================================================================
# 模块级常量
# ============================================================================

TEST_SETTINGS = Settings(
    jwt_secret="test-secret-key-for-testing-only",
    jwt_expire_minutes=60,
    llm_api_key="test-key",
    embed_api_key="test-key",
    database_url="sqlite+aiosqlite:///:memory:",
    database_echo=False,
)

TEST_USERNAME = "testuser"
TEST_PASSWORD = "Test@123456"


# ============================================================================
# 创建独立的测试 FastAPI app（避免模块级 overrides 污染）
# ============================================================================


def _create_test_app() -> FastAPI:
    """创建用于测试的独立 FastAPI 应用实例。

    使用独立的 app 实例，完全隔离模块级 dependency_overrides 污染。
    """
    test_app = FastAPI(
        title="Mellow Test",
        version="0.1.0",
        description="Test app instance",
    )

    # CORS
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 异常处理（从 main.py 复制）
    async def _general_exception_handler(request, exc: Exception) -> JSONResponse:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "服务器内部错误，请稍后重试。",
            },
        )

    test_app.add_exception_handler(MellowError, mellow_exception_handler)
    test_app.add_exception_handler(Exception, _general_exception_handler)

    # 注册路由（与 main.py 相同）
    from mellow.api.routes import (
        auth, chat, persona, knowledge, profile, memory, voice, vocabulary,
    )
    test_app.include_router(auth.router)
    test_app.include_router(chat.router)
    test_app.include_router(persona.router)
    test_app.include_router(knowledge.router)
    test_app.include_router(profile.router)
    test_app.include_router(memory.router)
    test_app.include_router(voice.router)
    test_app.include_router(vocabulary.router)

    @test_app.get("/health")
    async def health_check():
        return {"status": "ok", "app": "mellow-test", "version": "0.1.0"}

    return test_app

# ============================================================================
# 模块级常量
# ============================================================================

TEST_SETTINGS = Settings(
    jwt_secret="test-secret-key-for-testing-only",
    jwt_expire_minutes=60,
    llm_api_key="test-key",
    embed_api_key="test-key",
    database_url="sqlite+aiosqlite:///:memory:",
    database_echo=False,
)

TEST_USERNAME = "testuser"
TEST_PASSWORD = "Test@123456"
TEST_USER_ID = None  # 注册后填充

# ============================================================================
# Session 级事件循环（pytest-asyncio 要求）
# ============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Any:
    """创建 session 级事件循环，供所有异步 fixture 共享。"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# 数据库引擎（session 级，整个测试会话共享一个引擎）
# ============================================================================


@pytest.fixture(scope="session")
async def test_engine():
    """创建内存 SQLite 引擎，建表。"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


# ============================================================================
# 数据库 Session（function 级，每个测试独立会话）
# ============================================================================


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """每个测试的独立数据库会话。"""
    factory = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


# ============================================================================
# 测试 Container
# ============================================================================


@pytest.fixture
def test_container(test_engine) -> Container:
    """创建使用测试数据库的 Container 实例。"""
    container = Container(TEST_SETTINGS)
    factory = get_session_factory(test_engine)
    # 注入测试引擎和 session 工厂
    container.__dict__["_db_engine_val"] = test_engine
    container.__dict__["_db_engine"] = True
    container.__dict__["_session_factory_val"] = factory
    container.__dict__["_session_factory"] = True
    return container


# ============================================================================
# FastAPI TestClient（使用独立 app 实例，完全隔离）
# ============================================================================


@pytest.fixture
def client(test_container) -> TestClient:
    """创建 FastAPI TestClient，覆写 get_container 依赖。

    使用独立的 app 实例，避免被其他测试文件的模块级 overrides 污染。
    所有需要 auth 的端点通过 Bearer token 访问（见 auth_headers fixture）。
    """
    from mellow.api.deps import get_container as original_get_container

    def _mock_container():
        return test_container

    test_app = _create_test_app()
    test_app.dependency_overrides[original_get_container] = _mock_container

    c = TestClient(test_app)
    yield c


# ============================================================================
# Auth 辅助 —— 注册测试用户并返回 Bearer headers
# ============================================================================


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    """注册测试用户，返回 Bearer token headers。

    每次调用都会创建新用户（首次调用），后续调用复用缓存。
    """
    global TEST_USER_ID
    # 注册
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    if resp.status_code not in (200, 409):
        raise RuntimeError(f"注册测试用户失败: {resp.status_code} {resp.json()}")

    # 登录获取 token
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200, f"登录失败: {resp.json()}"
    data = resp.json()
    TEST_USER_ID = data.get("user_id")
    return {"Authorization": f"Bearer {data['access_token']}"}


# ============================================================================
# 便捷 fixture：带 auth 的 client
# ============================================================================


@pytest.fixture
def auth_client(client, auth_headers) -> TestClient:
    """返回已配置好 auth headers 的 TestClient。

    注意：TestClient 不支持全局 headers，调用时需显式传入 headers。
    此 fixture 主要用于标记 auth_headers 已准备好。
    """
    return client


# ============================================================================
# Settings fixture（向后兼容）
# ============================================================================


@pytest.fixture
def settings() -> Settings:
    """测试环境配置。"""
    return Settings(
        jwt_secret="test-secret",
        jwt_expire_minutes=60,
        llm_api_key="test-key",
        embed_api_key="test-key",
        database_url="sqlite+aiosqlite:///./data/test.db",
        lancedb_path="./data/test_lancedb",
    )
