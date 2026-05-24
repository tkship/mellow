"""聊天与画像 API 测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mellow.db.base import Base
from mellow.db.repos.profile_repo import SqlAlchemyLearningProfileRepository
from mellow.memory.learning_profile import LearningProfileManager
from mellow.memory.session_context import ChatMessage, SessionContextManager


# ===== 共享内存数据库 fixtures =====

@pytest.fixture
async def profile_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def profile_session(profile_engine):
    session_factory = async_sessionmaker(
        profile_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
async def profile_manager(profile_session):
    repo = SqlAlchemyLearningProfileRepository(profile_session)
    return LearningProfileManager(repo)


# ===== SessionContextManager 测试 =====

class TestSessionContextManager:
    def test_add_and_get_messages(self):
        mgr = SessionContextManager("s1", "user1", "p1")
        msg = ChatMessage(id="m1", role="user", content="hello")
        mgr.add_message(msg)
        assert len(mgr.messages) == 1
        assert mgr.get_message("m1") == msg

    def test_toggle_favorite(self):
        mgr = SessionContextManager("s1", "user1", "p1")
        msg = ChatMessage(id="m1", role="user", content="hello")
        mgr.add_message(msg)
        result = mgr.toggle_favorite("m1")
        assert result is not None
        assert result.is_favorite is True
        result2 = mgr.toggle_favorite("m1")
        assert result2.is_favorite is False

    def test_toggle_favorite_not_found(self):
        mgr = SessionContextManager("s1", "user1", "p1")
        assert mgr.toggle_favorite("nonexistent") is None

    def test_delete_message(self):
        mgr = SessionContextManager("s1", "user1", "p1")
        mgr.add_message(ChatMessage(id="m1", role="user", content="hello"))
        assert mgr.delete_message("m1") is True
        assert len(mgr.messages) == 0

    def test_delete_message_not_found(self):
        mgr = SessionContextManager("s1", "user1", "p1")
        assert mgr.delete_message("nonexistent") is False

    def test_get_messages_pagination(self):
        mgr = SessionContextManager("s1", "user1", "p1")
        for i in range(25):
            mgr.add_message(ChatMessage(id=f"m{i}", role="user", content=f"msg{i}"))

        # 默认 limit=20，返回最新的 20 条（倒序）
        msgs, cursor = mgr.get_messages()
        assert len(msgs) == 20
        assert cursor is not None  # 还有 5 条

        # 使用 cursor 加载更多
        msgs2, cursor2 = mgr.get_messages(cursor=cursor)
        assert len(msgs2) == 5
        assert cursor2 is None  # 没有更多了

    def test_lru_eviction(self):
        from mellow.api.routes.chat import _get_session_context, _session_contexts, _MAX_SESSIONS
        # 清空现有会话
        _session_contexts.clear()
        for i in range(_MAX_SESSIONS + 5):
            _get_session_context(f"s{i}", "user1", "p1")
        assert len(_session_contexts) == _MAX_SESSIONS


# ===== LearningProfileManager 测试 =====

@pytest.mark.asyncio
async def test_update_profile(profile_manager):
    profile = await profile_manager.get_or_create("user1")
    assert profile.cefr_level == "A1"

    updated = await profile_manager.update("user1", cefr_level="B1")
    assert updated.cefr_level == "B1"
    assert updated.user_id == "user1"


@pytest.mark.asyncio
async def test_update_profile_partial(profile_manager):
    await profile_manager.get_or_create("user1")
    await profile_manager.update("user1", vocabulary_size=100)
    profile = await profile_manager.get_or_create("user1")
    assert profile.vocabulary_size == 100
    # 未更新的字段应保持不变
    assert profile.cefr_level == "A1"


# ===== ProfileUpdateRequest 验证测试 =====

from mellow.api.routes.profile import ProfileUpdateRequest


def test_profile_update_request_valid():
    req = ProfileUpdateRequest(cefr_level="B1")
    assert req.cefr_level == "B1"


def test_profile_update_request_invalid_cefr():
    with pytest.raises(ValueError):
        ProfileUpdateRequest(cefr_level="D1")


# ===== HTTP 集成测试 =====

from main import app
from mellow.api.deps import get_current_user
from mellow.providers.auth import UserInfo
from mellow.di import Container
from mellow.config import Settings
from mellow.db.engine import get_engine, get_session_factory
from mellow.db.init_db import init_db


def _mock_current_user():
    return UserInfo(id="test-user", username="tester")


# 为集成测试初始化真实数据库
_test_settings = Settings(
    jwt_secret="test-secret",
    jwt_expire_minutes=60,
    llm_api_key="test-key",
    embed_api_key="test-key",
    database_url="sqlite+aiosqlite:///./data/test.db",
    lancedb_path="./data/test_lancedb",
    database_echo=False,
)
_test_engine = get_engine(_test_settings)


# 在模块级别确保数据库表存在
import asyncio


def _init_test_db():
    async def _async_init():
        async with _test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.get_event_loop().run_until_complete(_async_init())


_init_test_db()

# 覆盖 Container 以使用测试数据库
_test_container = Container(_test_settings)
_test_container.__dict__["_db_engine_val"] = _test_engine
_test_container.__dict__["_db_engine"] = True
_test_container.__dict__["_session_factory_val"] = get_session_factory(_test_engine)
_test_container.__dict__["_session_factory"] = True

# 注入测试 mock 用户
_original_auth = _test_container.auth


async def _mock_auth():
    from mellow.auth.jwt_auth import JWTAuthProvider
    from mellow.db.repos.user_repo import SqlAlchemyUserRepository

    # 创建一个有测试用户的 auth provider
    auth = JWTAuthProvider(settings=_test_settings, user_repo=SqlAlchemyUserRepository(_test_container.session()))
    # 确保测试用户存在
    try:
        await auth.register("tester", "testpass")
        _test_container.session().commit()
    except Exception:
        await _test_container.session().rollback()
    return auth


# 覆盖依赖
from mellow.api.deps import get_container, get_current_user


def _mock_container():
    return _test_container


app.dependency_overrides[get_container] = _mock_container
app.dependency_overrides[get_current_user] = _mock_current_user

client = TestClient(app)


class TestProfileAPI:
    def test_put_profile(self):
        response = client.put("/api/v1/profile", json={"cefr_level": "B2"})
        assert response.status_code == 200
        data = response.json()
        assert data["cefr_level"] == "B2"

    def test_put_profile_invalid_cefr(self):
        response = client.put("/api/v1/profile", json={"cefr_level": "Z9"})
        assert response.status_code == 422

    def test_get_profile(self):
        # 先更新再获取，验证一致性
        client.put("/api/v1/profile", json={"cefr_level": "C1"})
        response = client.get("/api/v1/profile")
        assert response.status_code == 200
        data = response.json()
        assert data["cefr_level"] == "C1"


class TestChatHistoryAPI:
    def test_get_chat_history_empty(self):
        response = client.get("/api/v1/chat/history?persona_id=p1")
        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []
        assert data["next_cursor"] is None


class TestChatMessageActionsAPI:
    def test_toggle_favorite_not_found(self):
        response = client.put("/api/v1/chat/messages/nonexistent/favorite?persona_id=p999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["message"] == "会话不存在"

    def test_delete_message_not_found(self):
        response = client.delete("/api/v1/chat/messages/nonexistent?persona_id=p999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["message"] == "会话不存在"