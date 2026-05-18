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


# ===== HTTP 集成测试 =====

from main import app
from mellow.api.deps import get_current_user
from mellow.providers.auth import UserInfo


def _mock_current_user():
    return UserInfo(id="test-user", username="tester")


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

    def test_get_chat_history_with_messages(self):
        # 先发送一条消息来创建会话和消息
        client.post("/api/v1/chat", json={"persona_id": "p1", "message": "hello"})

        response = client.get("/api/v1/chat/history?persona_id=p1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) > 0
        # 消息应该包含用户消息和AI回复
        roles = [m["role"] for m in data["messages"]]
        assert "user" in roles

    def test_chat_history_pagination(self):
        # 每次发送产生 2 条消息（user + ai），发 5 次 = 10 条
        for i in range(5):
            client.post("/api/v1/chat", json={"persona_id": "p2", "message": f"msg{i}"})

        response = client.get("/api/v1/chat/history?persona_id=p2&limit=2")
        data = response.json()
        assert len(data["messages"]) == 2
        assert data["next_cursor"] is not None

        cursor = data["next_cursor"]
        response2 = client.get(f"/api/v1/chat/history?persona_id=p2&limit=2&cursor={cursor}")
        data2 = response2.json()
        assert len(data2["messages"]) == 2
        assert data2["next_cursor"] is not None

        cursor2 = data2["next_cursor"]
        response3 = client.get(f"/api/v1/chat/history?persona_id=p2&limit=2&cursor={cursor2}")
        data3 = response3.json()
        # 10 条消息，每页 2 条，第三页应还有 2 条
        assert len(data3["messages"]) == 2
        assert data3["next_cursor"] is not None

        # 继续翻到最后一页
        cursor3 = data3["next_cursor"]
        response4 = client.get(f"/api/v1/chat/history?persona_id=p2&limit=2&cursor={cursor3}")
        data4 = response4.json()
        assert len(data4["messages"]) == 2
        assert data4["next_cursor"] is not None

        cursor4 = data4["next_cursor"]
        response5 = client.get(f"/api/v1/chat/history?persona_id=p2&limit=2&cursor={cursor4}")
        data5 = response5.json()
        assert len(data5["messages"]) == 2
        assert data5["next_cursor"] is None


class TestChatMessageActionsAPI:
    def test_toggle_favorite(self):
        # 先创建消息
        client.post("/api/v1/chat", json={"persona_id": "p3", "message": "fav me"})

        # 获取历史找到消息ID
        history = client.get("/api/v1/chat/history?persona_id=p3").json()
        msg_id = history["messages"][0]["id"]
        assert history["messages"][0]["is_favorite"] is False

        # 收藏
        response = client.put(f"/api/v1/chat/messages/{msg_id}/favorite?persona_id=p3")
        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] is True

        # 再次调用取消收藏
        response2 = client.put(f"/api/v1/chat/messages/{msg_id}/favorite?persona_id=p3")
        assert response2.status_code == 200
        assert response2.json()["is_favorite"] is False

    def test_toggle_favorite_not_found(self):
        response = client.put("/api/v1/chat/messages/nonexistent/favorite?persona_id=p999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["message"] == "会话不存在"

    def test_delete_message(self):
        # 先创建消息
        client.post("/api/v1/chat", json={"persona_id": "p4", "message": "delete me"})

        history = client.get("/api/v1/chat/history?persona_id=p4").json()
        initial_count = len(history["messages"])
        msg_id = history["messages"][0]["id"]

        # 删除
        response = client.delete(f"/api/v1/chat/messages/{msg_id}?persona_id=p4")
        assert response.status_code == 204

        # 验证已删除
        history_after = client.get("/api/v1/chat/history?persona_id=p4").json()
        assert len(history_after["messages"]) == initial_count - 1

    def test_delete_message_not_found(self):
        response = client.delete("/api/v1/chat/messages/nonexistent?persona_id=p999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["message"] == "会话不存在"
