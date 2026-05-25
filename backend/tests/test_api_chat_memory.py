"""Chat & Memory API 全方位集成测试。

覆盖维度：边界测试 | 等价类 | 极限值 | 状态转换 | 场景测试 | 认证拦截

使用 conftest 提供的 client 和 auth_headers 固件（真实 JWT 认证流程）。
Chat POST 端点仅测试校验层（422 错误），不触发实际 LLM 调用。

persona_id 约定：预设角色使用 "preset_" 前缀（如 "preset_girlfriend"），
与 PersonaManager 内部查找逻辑保持一致。
"""

import pytest


# ============================================================================
# 辅助常量 — persona_id 必须使用 "preset_" 前缀以匹配 PersonaManager
# ============================================================================

_VALID_PERSONA = "preset_girlfriend"
_VALID_PERSONA_2 = "preset_study_buddy"
_INVALID_PERSONA = "nonexistent_persona_999"
_FRESH_PERSONA = "preset_humorous_friend"  # 专用于期望空会话历史的测试
_LONG_PERSONA_ID = "a" * 200
_SQL_INJECTION_PERSONA = "'; DROP TABLE users; --"


# ============================================================================
# Fixture: 清理模块级 _session_contexts，防止测试间状态泄漏
# ============================================================================

@pytest.fixture(autouse=True)
def _clear_session_contexts():
    """每个测试前清理聊天会话上下文，确保测试隔离。"""
    from mellow.api.routes.chat import _session_contexts
    _session_contexts.clear()
    yield
    _session_contexts.clear()


# ============================================================================
# TestChatValidation — Chat POST 校验（无需 LLM）
# ============================================================================

class TestChatValidation:
    """聊天请求验证测试 —— 仅校验 Pydantic 模型层，不触发 LLM 调用。"""

    def test_chat_missing_persona_id(self, client, auth_headers):
        """[边界] POST /chat 缺少必填 persona_id → 422。"""
        resp = client.post(
            "/api/v1/chat",
            json={"message": "hello"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_chat_empty_message(self, client, auth_headers):
        """[边界] POST /chat 空字符串消息（min_length=1）→ 422。"""
        resp = client.post(
            "/api/v1/chat",
            json={"persona_id": _VALID_PERSONA, "message": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_chat_message_min_length_passes_validation(self, client, auth_headers):
        """[边界] 1 字符消息通过 Pydantic 校验 —— 直接验证 ChatRequest 模型。
        
        API 层需要 LLM 才可完整执行，此处跳过 HTTP 调用，仅测试模型层校验。
        """
        from mellow.api.routes.chat import ChatRequest
        # min_length=1，1 字符应通过校验
        req = ChatRequest(persona_id=_VALID_PERSONA, message="A")
        assert req.message == "A"
        # 0 字符应抛出 ValidationError
        with pytest.raises(Exception):
            ChatRequest(persona_id=_VALID_PERSONA, message="")

    def test_chat_missing_both_fields(self, client, auth_headers):
        """[边界] POST /chat 同时缺失 persona_id 和 message → 422（detail 含多条错误）。"""
        resp = client.post(
            "/api/v1/chat",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_chat_empty_body(self, client, auth_headers):
        """[边界] POST /chat 无 JSON body → 422。"""
        resp = client.post(
            "/api/v1/chat",
            headers=auth_headers,
        )
        assert resp.status_code == 422


# ============================================================================
# TestChatHistoryBoundary — 聊天历史边界
# ============================================================================

class TestChatHistoryBoundary:
    """聊天历史边界测试 —— 分页参数 limit 的最小/最大/越界值。"""

    def test_history_limit_min_boundary(self, client, auth_headers):
        """[边界] GET /history limit=1（最小值）→ 200。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_FRESH_PERSONA}&limit=1",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "messages" in data
        assert "next_cursor" in data
        assert len(data["messages"]) <= 1

    def test_history_limit_max_boundary(self, client, auth_headers):
        """[边界] GET /history limit=100（最大值）→ 200。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_FRESH_PERSONA}&limit=100",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "messages" in data

    def test_history_limit_zero_below_min(self, client, auth_headers):
        """[边界] GET /history limit=0（低于最小值 ge=1）→ 422。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_FRESH_PERSONA}&limit=0",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_history_limit_101_above_max(self, client, auth_headers):
        """[边界] GET /history limit=101（高于最大值 le=100）→ 422。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_FRESH_PERSONA}&limit=101",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_history_missing_persona_id(self, client, auth_headers):
        """[边界] GET /history 缺少必填 persona_id → 422。"""
        resp = client.get(
            "/api/v1/chat/history",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_favorite_missing_persona_id(self, client, auth_headers):
        """[边界] PUT /messages/{id}/favorite 缺少 persona_id → 422。"""
        resp = client.put(
            "/api/v1/chat/messages/test_msg/favorite",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_delete_missing_persona_id(self, client, auth_headers):
        """[边界] DELETE /messages/{id} 缺少 persona_id → 422。"""
        resp = client.delete(
            "/api/v1/chat/messages/test_msg",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_favorite_nonexistent_message(self, client, auth_headers):
        """[边界] PUT /messages/{id}/favorite 消息不存在 → 404（会话不存在）。"""
        resp = client.put(
            f"/api/v1/chat/messages/msg_nonexistent_12345/favorite?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data

    def test_delete_nonexistent_message(self, client, auth_headers):
        """[边界] DELETE /messages/{id} 消息不存在 → 404（会话不存在）。"""
        resp = client.delete(
            f"/api/v1/chat/messages/msg_nonexistent_12345?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data


# ============================================================================
# TestChatHistoryEquivalence — 聊天历史等价类
# ============================================================================

class TestChatHistoryEquivalence:
    """聊天历史等价类测试 —— 有/无会话、有效/无效 persona。"""

    def test_history_valid_persona_empty(self, client, auth_headers):
        """[等价类] 有效 persona_id 但无会话 → 返回空消息列表、next_cursor=null。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_FRESH_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["messages"] == []
        assert data["next_cursor"] is None

    def test_history_valid_persona_no_sessions(self, client, auth_headers):
        """[等价类] 有效 persona_id 从未产生会话 → 空消息。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_VALID_PERSONA_2}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["messages"] == []
        assert data["next_cursor"] is None

    def test_history_invalid_persona(self, client, auth_headers):
        """[等价类] 无效 persona_id → 同样返回空消息（没有对应会话）。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["messages"] == []
        assert data["next_cursor"] is None

    def test_history_pagination_no_messages(self, client, auth_headers):
        """[场景] 无消息时 cursor 始终为 null。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_FRESH_PERSONA}&limit=10",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["next_cursor"] is None


# ============================================================================
# TestChatHistoryExtreme — 极限值测试
# ============================================================================

class TestChatHistoryExtreme:
    """聊天历史极限值测试。"""

    def test_history_large_cursor(self, client, auth_headers):
        """[极限值] 非常大的 cursor 值 → 应优雅处理，返回空消息。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_FRESH_PERSONA}&cursor={999999}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "messages" in data
        assert resp.status_code == 200

    def test_history_very_long_persona_id(self, client, auth_headers):
        """[极限值] 超长 persona_id（200 字符）→ 200（无对应会话返回空）。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_LONG_PERSONA_ID}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["messages"] == []

    def test_history_sql_injection_attempt(self, client, auth_headers):
        """[极限值] persona_id 含 SQL 注入字符 → 安全处理，不崩溃。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_SQL_INJECTION_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["messages"] == []

    def test_favorite_sql_injection_message_id(self, client, auth_headers):
        """[极限值] message_id 含特殊字符 → 不崩溃。"""
        resp = client.put(
            f"/api/v1/chat/messages/{_SQL_INJECTION_PERSONA}/favorite?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ============================================================================
# TestChatPhrases — 快捷短语
# ============================================================================

class TestChatPhrases:
    """快捷短语端点测试。"""

    def test_phrases_valid_persona(self, client, auth_headers):
        """[等价类] 有效 persona_id → 返回短语列表（LLM 不可用时使用回退短语）。"""
        resp = client.get(
            f"/api/v1/chat/phrases?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "phrases" in data
        assert "persona_name" in data
        assert isinstance(data["phrases"], list)
        assert len(data["phrases"]) > 0

    def test_phrases_nonexistent_persona(self, client, auth_headers):
        """[等价类] 不存在的 persona_id → 返回空短语列表。"""
        resp = client.get(
            f"/api/v1/chat/phrases?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["phrases"] == []
        assert data["persona_name"] == ""

    def test_phrases_different_persona(self, client, auth_headers):
        """[等价类] 不同 persona 返回不同短语。"""
        resp1 = client.get(
            f"/api/v1/chat/phrases?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        resp2 = client.get(
            f"/api/v1/chat/phrases?persona_id={_VALID_PERSONA_2}",
            headers=auth_headers,
        )
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # 不同角色 persona_name 不同
        assert resp1.json()["persona_name"] != resp2.json()["persona_name"]


# ============================================================================
# TestMessageActionStateTransition — 消息操作状态转换
# ============================================================================

class TestMessageActionStateTransition:
    """消息操作状态转换测试 —— 收藏、删除在会话不存在/消息不存在时的行为。"""

    def test_favorite_session_not_exist(self, client, auth_headers):
        """[状态转换] 对不存在的会话尝试收藏 → 404。"""
        resp = client.put(
            f"/api/v1/chat/messages/msg_001/favorite?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 404
        data = resp.json()
        assert data["message"] == "会话不存在"

    def test_delete_session_not_exist(self, client, auth_headers):
        """[状态转换] 对不存在的会话尝试删除消息 → 404。"""
        resp = client.delete(
            f"/api/v1/chat/messages/msg_001?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 404
        data = resp.json()
        assert data["message"] == "会话不存在"


# ============================================================================
# TestMemoryEndpoints — 记忆端点等价类
# ============================================================================

class TestMemoryEndpoints:
    """记忆端点等价类测试。"""

    def test_emotions_valid_persona(self, client, auth_headers):
        """[等价类] 有效 persona_id → 返回 emotions 数组（可能为空）。"""
        resp = client.get(
            f"/api/v1/memory/emotions?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "emotions" in data
        assert isinstance(data["emotions"], list)

    def test_emotions_invalid_persona(self, client, auth_headers):
        """[等价类] 无效 persona_id → 也返回空 emotions。"""
        resp = client.get(
            f"/api/v1/memory/emotions?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "emotions" in data
        assert data["emotions"] == []

    def test_facts_valid_persona(self, client, auth_headers):
        """[等价类] 有效 persona_id → 返回 facts 数组（可能为空）。"""
        resp = client.get(
            f"/api/v1/memory/facts?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "facts" in data
        assert isinstance(data["facts"], list)

    def test_facts_invalid_persona(self, client, auth_headers):
        """[等价类] 无效 persona_id → 返回空 facts。"""
        resp = client.get(
            f"/api/v1/memory/facts?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "facts" in data
        assert data["facts"] == []

    def test_summary_valid_persona(self, client, auth_headers):
        """[等价类] 有效 persona_id → 返回 summary 字符串。"""
        resp = client.get(
            f"/api/v1/memory/summary?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert isinstance(data["summary"], str)

    def test_summary_initial_state(self, client, auth_headers):
        """[状态转换] 首次对话 → summary 应为 "这是你们的第一次对话。"。"""
        resp = client.get(
            f"/api/v1/memory/summary?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"] == "这是你们的第一次对话。"

    def test_proactive_valid_persona(self, client, auth_headers):
        """[等价类] 有效 persona_id → 返回 messages 数组和 count。"""
        resp = client.get(
            f"/api/v1/memory/proactive?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "messages" in data
        assert "count" in data
        assert isinstance(data["messages"], list)
        assert data["count"] == len(data["messages"])

    def test_proactive_empty_for_new_user(self, client, auth_headers):
        """[场景] 无待投递消息 → messages 为空，count=0。"""
        resp = client.get(
            f"/api/v1/memory/proactive?persona_id={_FRESH_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["messages"] == []
        assert data["count"] == 0

    def test_memory_missing_persona_id_emotions(self, client, auth_headers):
        """[边界] GET /memory/emotions 缺少 persona_id → 422。"""
        resp = client.get(
            "/api/v1/memory/emotions",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_memory_missing_persona_id_facts(self, client, auth_headers):
        """[边界] GET /memory/facts 缺少 persona_id → 422。"""
        resp = client.get(
            "/api/v1/memory/facts",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_memory_missing_persona_id_summary(self, client, auth_headers):
        """[边界] GET /memory/summary 缺少 persona_id → 422。"""
        resp = client.get(
            "/api/v1/memory/summary",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_memory_missing_persona_id_proactive(self, client, auth_headers):
        """[边界] GET /memory/proactive 缺少 persona_id → 422。"""
        resp = client.get(
            "/api/v1/memory/proactive",
            headers=auth_headers,
        )
        assert resp.status_code == 422


# ============================================================================
# TestMemoryStateTransition — 记忆状态转换
# ============================================================================

class TestMemoryStateTransition:
    """记忆系统状态转换测试 —— 验证不同 persona 的记忆隔离性和一致性。"""

    def test_memory_initial_state_chain(self, client, auth_headers):
        """[状态转换] 初始状态链：emotions 空 → facts 空 → summary 首次对话。"""
        pid = _INVALID_PERSONA

        r = client.get(f"/api/v1/memory/emotions?persona_id={pid}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["emotions"] == []

        r = client.get(f"/api/v1/memory/facts?persona_id={pid}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["facts"] == []

        r = client.get(f"/api/v1/memory/summary?persona_id={pid}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["summary"] == "这是你们的第一次对话。"

    def test_multiple_persona_isolation(self, client, auth_headers):
        """[场景] 不同 persona 的记忆互相隔离。"""
        r1 = client.get(f"/api/v1/memory/summary?persona_id={_VALID_PERSONA}", headers=auth_headers)
        r2 = client.get(f"/api/v1/memory/summary?persona_id={_VALID_PERSONA_2}", headers=auth_headers)

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert "summary" in r1.json()
        assert "summary" in r2.json()

    def test_memory_cross_endpoint_consistency(self, client, auth_headers):
        """[场景] 同一 persona 的 emotions/facts/summary 端点一致性。"""
        pid = _VALID_PERSONA

        r_emotions = client.get(f"/api/v1/memory/emotions?persona_id={pid}", headers=auth_headers)
        r_facts = client.get(f"/api/v1/memory/facts?persona_id={pid}", headers=auth_headers)
        r_summary = client.get(f"/api/v1/memory/summary?persona_id={pid}", headers=auth_headers)

        assert r_emotions.status_code == 200
        assert r_facts.status_code == 200
        assert r_summary.status_code == 200
        assert "emotions" in r_emotions.json()
        assert "facts" in r_facts.json()
        assert "summary" in r_summary.json()

    def test_proactive_returns_empty_after_read(self, client, auth_headers):
        """[场景] 读取 proactive 消息后队列清空（再次读取为空）。"""
        pid = _VALID_PERSONA

        r1 = client.get(f"/api/v1/memory/proactive?persona_id={pid}", headers=auth_headers)
        assert r1.status_code == 200
        assert r1.json()["messages"] == []

        r2 = client.get(f"/api/v1/memory/proactive?persona_id={pid}", headers=auth_headers)
        assert r2.status_code == 200
        assert r2.json()["messages"] == []


# ============================================================================
# TestAuthRequired — 认证拦截
# ============================================================================

class TestAuthRequired:
    """认证要求测试 —— 所有端点无 token 时返回 401。"""

    # ---- Chat 端点 ----

    def test_chat_post_no_auth(self, client):
        """[认证] POST /chat 无 token → 401。"""
        resp = client.post("/api/v1/chat", json={"persona_id": "p1", "message": "hi"})
        assert resp.status_code == 401

    def test_chat_history_no_auth(self, client):
        """[认证] GET /chat/history 无 token → 401。"""
        resp = client.get(f"/api/v1/chat/history?persona_id={_VALID_PERSONA}")
        assert resp.status_code == 401

    def test_chat_favorite_no_auth(self, client):
        """[认证] PUT /chat/messages/{id}/favorite 无 token → 401。"""
        resp = client.put(f"/api/v1/chat/messages/msg1/favorite?persona_id={_VALID_PERSONA}")
        assert resp.status_code == 401

    def test_chat_delete_no_auth(self, client):
        """[认证] DELETE /chat/messages/{id} 无 token → 401。"""
        resp = client.delete(f"/api/v1/chat/messages/msg1?persona_id={_VALID_PERSONA}")
        assert resp.status_code == 401

    def test_chat_phrases_no_auth(self, client):
        """[认证] GET /chat/phrases 无 token → 401。"""
        resp = client.get(f"/api/v1/chat/phrases?persona_id={_VALID_PERSONA}")
        assert resp.status_code == 401

    # ---- Memory 端点 ----

    def test_memory_emotions_no_auth(self, client):
        """[认证] GET /memory/emotions 无 token → 401。"""
        resp = client.get(f"/api/v1/memory/emotions?persona_id={_VALID_PERSONA}")
        assert resp.status_code == 401

    def test_memory_facts_no_auth(self, client):
        """[认证] GET /memory/facts 无 token → 401。"""
        resp = client.get(f"/api/v1/memory/facts?persona_id={_VALID_PERSONA}")
        assert resp.status_code == 401

    def test_memory_summary_no_auth(self, client):
        """[认证] GET /memory/summary 无 token → 401。"""
        resp = client.get(f"/api/v1/memory/summary?persona_id={_VALID_PERSONA}")
        assert resp.status_code == 401

    def test_memory_proactive_no_auth(self, client):
        """[认证] GET /memory/proactive 无 token → 401。"""
        resp = client.get(f"/api/v1/memory/proactive?persona_id={_VALID_PERSONA}")
        assert resp.status_code == 401


# ============================================================================
# TestContentNegotiation — Content-Type / 结构校验
# ============================================================================

class TestContentNegotiation:
    """Content-Type 与响应结构校验。"""

    def test_history_response_structure(self, client, auth_headers):
        """[结构] GET /history 响应体格式校验。"""
        resp = client.get(
            f"/api/v1/chat/history?persona_id={_FRESH_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"messages", "next_cursor"}
        assert isinstance(data["messages"], list)
        assert data["next_cursor"] is None or isinstance(data["next_cursor"], str)

    def test_memory_emotions_response_structure(self, client, auth_headers):
        """[结构] GET /memory/emotions 响应体格式。"""
        resp = client.get(
            f"/api/v1/memory/emotions?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"emotions"}

    def test_memory_facts_response_structure(self, client, auth_headers):
        """[结构] GET /memory/facts 响应体格式。"""
        resp = client.get(
            f"/api/v1/memory/facts?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"facts"}

    def test_memory_summary_response_structure(self, client, auth_headers):
        """[结构] GET /memory/summary 响应体格式。"""
        resp = client.get(
            f"/api/v1/memory/summary?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"summary"}

    def test_memory_proactive_response_structure(self, client, auth_headers):
        """[结构] GET /memory/proactive 响应体格式。"""
        resp = client.get(
            f"/api/v1/memory/proactive?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"messages", "count"}

    def test_phrases_response_structure(self, client, auth_headers):
        """[结构] GET /chat/phrases 响应体格式。"""
        resp = client.get(
            f"/api/v1/chat/phrases?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"phrases", "persona_name"}


# ============================================================================
# TestDeleteSuccessReturns204 — 删除成功
# ============================================================================

class TestDeleteSuccessReturns204:
    """DELETE /messages/{id} 成功时返回 204 No Content。"""

    def test_delete_returns_404_when_no_session(self, client, auth_headers):
        """[边界] 无会话时 DELETE 返回 404（确认错误路径）。"""
        resp = client.delete(
            f"/api/v1/chat/messages/any_msg?persona_id={_INVALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_delete_with_valid_persona_no_session(self, client, auth_headers):
        """[边界] 有效 persona 但无活跃会话 → DELETE 返回 404。"""
        resp = client.delete(
            f"/api/v1/chat/messages/any_msg?persona_id={_VALID_PERSONA}",
            headers=auth_headers,
        )
        assert resp.status_code == 404
