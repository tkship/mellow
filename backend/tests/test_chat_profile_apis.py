"""聊天与画像 API 测试。"""

import pytest
from fastapi.testclient import TestClient

from mellow.memory.session_context import ChatMessage, SessionContextManager
from mellow.memory.learning_profile import LearningProfileManager


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
async def test_update_profile():
    mgr = LearningProfileManager()
    profile = await mgr.get_or_create("user1")
    assert profile.cefr_level == "A1"

    updated = await mgr.update("user1", cefr_level="B1")
    assert updated.cefr_level == "B1"
    assert updated.user_id == "user1"


@pytest.mark.asyncio
async def test_update_profile_partial():
    mgr = LearningProfileManager()
    await mgr.get_or_create("user1")
    await mgr.update("user1", vocabulary_size=100)
    profile = await mgr.get_or_create("user1")
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
