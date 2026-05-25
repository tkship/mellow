"""Persona & Knowledge API 全方位集成测试。

覆盖 Persona 路由（预设/自定义角色列表、详情、语音）和
Knowledge 路由（精确查词、语义搜索），测试维度包括：
边界测试、等价类、极限值、状态转换、安全测试、场景测试。

设计原则：
1. 使用 conftest 提供的 client/auth_headers fixtures，不直接 mock
2. 测试真实 PersonaManager 和 OpenEnglishDictProvider 行为
3. 知识库查词/搜索在词典 DB 不可用时优雅降级（返回错误信息或空结果）
4. 语音 MP3 文件缺失时预期 404，不是测试失败
5. 每个 test_ 方法 docstring 标注测试类别
"""

import pytest
# pytest fixtures (client, auth_headers) are auto-discovered from conftest.py
from fastapi.testclient import TestClient


# ============================================================================
# TestPersonaList — 角色列表测试（公开端点，无需 auth）
# ============================================================================


class TestPersonaList:
    """角色列表测试"""

    def test_list_presets_returns_personas(self, client: TestClient):
        """[等价类] 获取预设角色列表应返回非空数组。"""
        resp = client.get("/api/v1/personas")
        assert resp.status_code == 200
        data = resp.json()
        assert "personas" in data
        assert len(data["personas"]) > 0

    def test_each_persona_has_id_name_role(self, client: TestClient):
        """[等价类] 每个预设角色必须包含 id、name、role 字段。"""
        resp = client.get("/api/v1/personas")
        assert resp.status_code == 200
        for p in resp.json()["personas"]:
            for field in ("id", "name", "role"):
                assert field in p, f"Persona missing field {field}: {p}"

    def test_no_auth_required(self, client: TestClient):
        """[等价类] 预设角色列表是公开端点，无需认证。"""
        resp = client.get("/api/v1/personas")
        assert resp.status_code == 200


# ============================================================================
# TestPersonaDetail — 角色详情测试
# ============================================================================


class TestPersonaDetail:
    """角色详情测试"""

    def test_get_valid_preset_returns_200(self, client: TestClient):
        """[等价类] GET /api/v1/personas/{valid_id} 返回 200 及角色详情。"""
        resp = client.get("/api/v1/personas/preset_girlfriend")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "preset_girlfriend"
        assert data["name"] == "Sara"
        assert data["role"] == "girlfriend"

    def test_persona_has_full_structure(self, client: TestClient):
        """[等价类] 角色详情包含 language_style、teaching_style 等完整嵌套字段。"""
        resp = client.get("/api/v1/personas/preset_girlfriend")
        assert resp.status_code == 200
        data = resp.json()
        # 顶层字段
        for field in (
            "id", "name", "role", "language_style", "teaching_style",
            "intimacy_level", "interaction_rhythm", "emotional_sensitivity",
            "system_prompt_template", "is_preset", "voice_id",
        ):
            assert field in data, f"Missing field: {field}"
        # language_style 子字段
        assert "tone" in data["language_style"]
        assert "traits" in data["language_style"]
        # teaching_style 子字段
        assert "approach" in data["teaching_style"]
        assert "strictness" in data["teaching_style"]
        assert "correction_frequency" in data["teaching_style"]
        assert data["is_preset"] is True

    def test_get_nonexistent_persona_returns_404(self, client: TestClient):
        """[等价类] 不存在的 persona_id 返回 404 错误。"""
        resp = client.get("/api/v1/personas/nonexistent_xyz_999")
        assert resp.status_code == 404
        assert "detail" in resp.json()

    def test_get_preset_study_buddy(self, client: TestClient):
        """[等价类] 请求 preset_study_buddy 应返回 200。"""
        resp = client.get("/api/v1/personas/preset_study_buddy")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "preset_study_buddy"
        assert data["role"] == "study buddy"
        assert data["is_preset"] is True

    def test_get_preset_strict_teacher(self, client: TestClient):
        """[等价类] 请求 preset_strict_teacher 应返回 200。"""
        resp = client.get("/api/v1/personas/preset_strict_teacher")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "preset_strict_teacher"
        assert data["role"] == "strict teacher"

    def test_get_preset_humorous_friend(self, client: TestClient):
        """[等价类] 请求 preset_humorous_friend 应返回 200。"""
        resp = client.get("/api/v1/personas/preset_humorous_friend")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "preset_humorous_friend"
        assert data["role"] == "humorous friend"


# ============================================================================
# TestPersonaDetailBoundary — 角色详情边界测试
# ============================================================================


class TestPersonaDetailBoundary:
    """角色详情边界测试"""

    def test_persona_id_empty_string(self, client: TestClient):
        """[边界测试] persona_id 为空字符串 → 匹配到 / 列表端点返回 200。"""
        resp = client.get("/api/v1/personas/")
        # 路由到 GET / 列表端点
        assert resp.status_code == 200
        assert "personas" in resp.json()

    def test_persona_id_very_long_string(self, client: TestClient):
        """[边界测试] persona_id 为超长字符串 → 返回 404（不崩溃）。"""
        long_id = "x" * 500
        resp = client.get(f"/api/v1/personas/{long_id}")
        assert resp.status_code == 404


# ============================================================================
# TestPersonaVoice — 角色语音测试
# ============================================================================


class TestPersonaVoice:
    """角色语音测试"""

    def test_voice_nonexistent_persona_returns_404(self, client: TestClient):
        """[边界测试] 不存在角色的语音端点 → 404。"""
        resp = client.get("/api/v1/personas/nonexistent_abc_42/voice")
        assert resp.status_code == 404

    def test_voice_valid_preset(self, client: TestClient):
        """[等价类] 存在角色的语音端点 → 200（有 mp3）或 404（无 mp3）。"""
        resp = client.get("/api/v1/personas/preset_girlfriend/voice")
        assert resp.status_code in (200, 404), (
            f"Unexpected {resp.status_code}: {resp.json()}"
        )
        if resp.status_code == 200:
            assert resp.headers.get("content-type", "").startswith("audio/")


# ============================================================================
# TestPersonaCustom — 自定义角色测试（需 auth）
# ============================================================================


class TestPersonaCustom:
    """自定义角色测试"""

    def test_custom_without_auth_returns_401(self, client: TestClient):
        """[等价类] 不带 Authorization header → 401。"""
        resp = client.get("/api/v1/personas/custom")
        assert resp.status_code == 401

    def test_custom_with_auth_returns_personas(self, client: TestClient, auth_headers):
        """[等价类] 带有效 token → 返回 personas 列表（可为空）。"""
        resp = client.get("/api/v1/personas/custom", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "personas" in data
        assert isinstance(data["personas"], list)

    def test_custom_with_invalid_token(self, client: TestClient):
        """[等价类] 伪造 Bearer token → 401。"""
        resp = client.get(
            "/api/v1/personas/custom",
            headers={"Authorization": "Bearer fake-token-998877"},
        )
        assert resp.status_code == 401


# ============================================================================
# TestKnowledgeLookup — 精确查词测试（需 auth）
# ============================================================================


class TestKnowledgeLookup:
    """知识库查词测试"""

    def test_lookup_without_auth_returns_401(self, client: TestClient):
        """[等价类] 不带 Authorization header → 401。"""
        resp = client.get("/api/v1/knowledge/lookup?word=hello")
        assert resp.status_code == 401

    def test_lookup_common_word_check_structure(self, client: TestClient, auth_headers):
        """[等价类] 查常见词 → 200，验证响应结构。"""
        resp = client.get("/api/v1/knowledge/lookup?word=hello", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        # 词典可用 → word 字段；不可用 → error 字段
        assert "word" in data or "error" in data

    def test_lookup_nonexistent_word_returns_error(self, client: TestClient, auth_headers):
        """[等价类] 查不存在的单词 → 返回 error 信息。"""
        resp = client.get(
            "/api/v1/knowledge/lookup?word=zzzzznotexist9999",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data or "message" in data

    def test_lookup_response_full_structure(self, client: TestClient, auth_headers):
        """[等价类] 查到词条时应包含 definitions、phonetic、source 等字段。"""
        resp = client.get("/api/v1/knowledge/lookup?word=apple", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        if "error" not in data:
            assert "word" in data
            assert "definitions" in data
            assert isinstance(data["definitions"], list)
            assert "source" in data


# ============================================================================
# TestKnowledgeLookupBoundary — 查词边界测试
# ============================================================================


class TestKnowledgeLookupBoundary:
    """知识库查词边界测试"""

    def test_lookup_word_empty_string(self, client: TestClient, auth_headers):
        """[边界测试] word 为空字符串（min_length=1）→ 422。"""
        resp = client.get("/api/v1/knowledge/lookup?word=", headers=auth_headers)
        assert resp.status_code == 422

    def test_lookup_word_exactly_1_char(self, client: TestClient, auth_headers):
        """[边界测试] word 恰好 1 字符（最小边界）→ 200。"""
        resp = client.get("/api/v1/knowledge/lookup?word=a", headers=auth_headers)
        assert resp.status_code == 200

    def test_lookup_missing_word_param(self, client: TestClient, auth_headers):
        """[边界测试] 缺少 word 查询参数 → 422。"""
        resp = client.get("/api/v1/knowledge/lookup", headers=auth_headers)
        assert resp.status_code == 422


# ============================================================================
# TestKnowledgeSearch — 语义搜索测试（需 auth）
# ============================================================================


class TestKnowledgeSearch:
    """知识库搜索测试"""

    def test_search_without_auth_returns_401(self, client: TestClient):
        """[等价类] 不带 Authorization header → 401。"""
        resp = client.get("/api/v1/knowledge/search?q=test")
        assert resp.status_code == 401

    def test_search_with_auth_returns_results_array(self, client: TestClient, auth_headers):
        """[等价类] 带有效 token 搜索 → 返回 200 及 results 数组。"""
        resp = client.get("/api/v1/knowledge/search?q=greeting", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "query" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_search_nonexistent_query_empty_results(self, client: TestClient, auth_headers):
        """[等价类] 搜索不存在的内容 → 返回空 results。"""
        resp = client.get(
            "/api/v1/knowledge/search?q=xyznonexistent123456",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.json()["results"], list)

    def test_search_result_structure(self, client: TestClient, auth_headers):
        """[等价类] 搜索结果项应包含 content、score、metadata 字段。"""
        resp = client.get("/api/v1/knowledge/search?q=fruit", headers=auth_headers)
        assert resp.status_code == 200
        for item in resp.json()["results"]:
            assert "content" in item
            assert "score" in item
            assert "metadata" in item


# ============================================================================
# TestKnowledgeSearchBoundary — 搜索边界测试
# ============================================================================


class TestKnowledgeSearchBoundary:
    """知识库搜索边界测试"""

    def test_search_q_empty_string(self, client: TestClient, auth_headers):
        """[边界测试] q 为空字符串（min_length=1）→ 422。"""
        resp = client.get("/api/v1/knowledge/search?q=", headers=auth_headers)
        assert resp.status_code == 422

    def test_search_top_k_1_min_boundary(self, client: TestClient, auth_headers):
        """[边界测试] top_k=1（最小边界）→ 200。"""
        resp = client.get(
            "/api/v1/knowledge/search?q=test&top_k=1",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_search_top_k_20_max_boundary(self, client: TestClient, auth_headers):
        """[边界测试] top_k=20（最大边界）→ 200。"""
        resp = client.get(
            "/api/v1/knowledge/search?q=test&top_k=20",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_search_top_k_0_below_min(self, client: TestClient, auth_headers):
        """[边界测试] top_k=0（低于最小边界）→ 422。"""
        resp = client.get(
            "/api/v1/knowledge/search?q=test&top_k=0",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_search_top_k_21_above_max(self, client: TestClient, auth_headers):
        """[边界测试] top_k=21（超过最大边界）→ 422。"""
        resp = client.get(
            "/api/v1/knowledge/search?q=test&top_k=21",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_search_missing_q_param(self, client: TestClient, auth_headers):
        """[边界测试] 缺少 q 参数 → 422。"""
        resp = client.get("/api/v1/knowledge/search", headers=auth_headers)
        assert resp.status_code == 422

    def test_search_default_top_k_is_5(self, client: TestClient, auth_headers):
        """[等价类] 不传 top_k 时默认值为 5，请求应正常返回。"""
        resp = client.get("/api/v1/knowledge/search?q=hello", headers=auth_headers)
        assert resp.status_code == 200

    def test_search_q_exactly_1_char(self, client: TestClient, auth_headers):
        """[边界测试] q 恰好 1 字符（最小边界）→ 200。"""
        resp = client.get("/api/v1/knowledge/search?q=x", headers=auth_headers)
        assert resp.status_code == 200


# ============================================================================
# TestExtremeValues — 极限值测试
# ============================================================================


class TestExtremeValues:
    """极限值测试"""

    def test_lookup_very_long_word(self, client: TestClient, auth_headers):
        """[极限值] 超长单词应优雅处理，不产生 500。"""
        long_word = "supercalifragilisticexpialidocious" * 150
        resp = client.get(
            f"/api/v1/knowledge/lookup?word={long_word}",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 422), (
            f"Unexpected {resp.status_code}: {resp.json()}"
        )

    def test_search_very_long_query(self, client: TestClient, auth_headers):
        """[极限值] 超长搜索词应优雅处理。"""
        long_query = "test query " * 500
        resp = client.get(
            f"/api/v1/knowledge/search?q={long_query}",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 422), (
            f"Unexpected {resp.status_code}: {resp.json()}"
        )

    def test_search_sql_injection_safe(self, client: TestClient, auth_headers):
        """[极限值] SQL 注入式查询应安全处理，不触发 500。"""
        sql_payload = "'; DROP TABLE entries; --"
        resp = client.get(
            f"/api/v1/knowledge/search?q={sql_payload}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        # 服务端使用参数化查询，注入应被安全处理
        data = resp.json()
        assert "results" in data

    def test_search_special_characters(self, client: TestClient, auth_headers):
        """[极限值] q 含 Unicode 和特殊符号应正常返回。"""
        resp = client.get(
            "/api/v1/knowledge/search?q=🎉日本語한국어test",
            headers=auth_headers,
        )
        assert resp.status_code == 200


# ============================================================================
# TestSecurity — 安全测试
# ============================================================================


class TestSecurity:
    """安全测试 —— 路径穿越、SQL注入防护"""

    def test_persona_path_traversal_dot_dot(self, client: TestClient):
        """[安全测试] persona_id 含 ../../ 路径穿越 → 被安全拒绝（404 或 400）。"""
        resp = client.get("/api/v1/personas/../../etc/passwd")
        assert resp.status_code in (400, 404), (
            f"Path traversal not blocked: {resp.status_code}"
        )

    def test_persona_path_traversal_encoded(self, client: TestClient):
        """[安全测试] persona_id 含 URL 编码的路径穿越 → 被安全拒绝。"""
        resp = client.get("/api/v1/personas/%2e%2e%2f%2e%2e%2fetc%2fpasswd")
        assert resp.status_code in (400, 404, 422), (
            f"Encoded traversal not blocked: {resp.status_code}"
        )

    def test_voice_path_traversal(self, client: TestClient):
        """[安全测试] 语音端点 persona_id 含 ../ 路径穿越 → 被 sanitize 或拒绝。"""
        resp = client.get("/api/v1/personas/../etc%2Fpasswd/voice")
        assert resp.status_code in (400, 404), (
            f"Voice path traversal not blocked: {resp.status_code}"
        )

    def test_knowledge_search_sql_injection_2(self, client: TestClient, auth_headers):
        """[安全测试] 搜索参数含 UNION SELECT 注入 → 应安全处理。"""
        resp = client.get(
            "/api/v1/knowledge/search?q=test' UNION SELECT * FROM users--",
            headers=auth_headers,
        )
        assert resp.status_code == 200


# ============================================================================
# TestStateTransition — 状态转换测试
# ============================================================================


class TestStateTransition:
    """状态转换测试"""

    def test_persona_list_to_detail_consistency(self, client: TestClient):
        """[状态转换] 列表获取角色 → 取其 ID 获取详情 → ID 和名称一致。"""
        list_resp = client.get("/api/v1/personas")
        assert list_resp.status_code == 200
        personas = list_resp.json()["personas"]

        for p in personas:
            detail_resp = client.get(f"/api/v1/personas/{p['id']}")
            assert detail_resp.status_code == 200
            detail = detail_resp.json()
            assert detail["id"] == p["id"]
            assert detail["name"] == p["name"]
            assert detail["role"] == p["role"]

    def test_knowledge_lookup_verify_word_field(self, client: TestClient, auth_headers):
        """[状态转换] lookup "hello" → 验证响应包含 word 或 error 字段。"""
        resp = client.get("/api/v1/knowledge/lookup?word=hello", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "word" in data or "error" in data

    def test_knowledge_search_verify_results_array(self, client: TestClient, auth_headers):
        """[状态转换] search "greeting" → 验证 results 是数组且 query 值正确。"""
        resp = client.get("/api/v1/knowledge/search?q=greeting", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert data["query"] == "greeting"

    def test_presets_then_custom_independence(self, client: TestClient, auth_headers):
        """[状态转换] 预设列表和自定义列表相互独立，互不影响。"""
        pub_resp = client.get("/api/v1/personas")
        assert pub_resp.status_code == 200
        pub_count = len(pub_resp.json()["personas"])

        cust_resp = client.get("/api/v1/personas/custom", headers=auth_headers)
        assert cust_resp.status_code == 200

        # 再次获取预设列表，数量不变
        pub_resp2 = client.get("/api/v1/personas")
        assert len(pub_resp2.json()["personas"]) == pub_count


# ============================================================================
# TestScenario — 端到端场景测试
# ============================================================================


class TestScenario:
    """端到端场景测试"""

    def test_full_persona_browsing_flow(self, client: TestClient):
        """[场景测试] 完整角色浏览流程：列表 → 选取 → 详情 → 尝试语音 → 换一个角色。"""
        # Step 1: 列出所有预设角色
        list_resp = client.get("/api/v1/personas")
        assert list_resp.status_code == 200
        personas = list_resp.json()["personas"]
        assert len(personas) >= 4

        # Step 2: 选择 girlfriend 获取详情
        detail = client.get("/api/v1/personas/preset_girlfriend").json()
        assert detail["name"] == "Sara"
        assert detail["is_preset"] is True
        assert detail["voice_id"] is not None

        # Step 3: 尝试语音（文件可能不存在）
        voice_resp = client.get("/api/v1/personas/preset_girlfriend/voice")
        assert voice_resp.status_code in (200, 404)

        # Step 4: 换一个角色 strict_teacher
        detail2 = client.get("/api/v1/personas/preset_strict_teacher").json()
        assert detail2["id"] != detail["id"]
        assert detail2["name"] != detail["name"]

    def test_knowledge_lookup_scenario(self, client: TestClient, auth_headers):
        """[场景测试] 知识查词场景：查 "apple" → 验证词条 → 查不存在词 → 错误信息。"""
        # Lookup 1: 常见词
        resp1 = client.get(
            "/api/v1/knowledge/lookup?word=apple",
            headers=auth_headers,
        )
        assert resp1.status_code == 200
        data1 = resp1.json()
        if "error" not in data1:
            assert "word" in data1

        # Lookup 2: 不存在的词
        resp2 = client.get(
            "/api/v1/knowledge/lookup?word=zzzzznotexist",
            headers=auth_headers,
        )
        assert resp2.status_code == 200
        assert "error" in resp2.json() or "message" in resp2.json()

    def test_knowledge_search_scenario(self, client: TestClient, auth_headers):
        """[场景测试] 知识搜索场景：搜 "fruit" → 获取结果 → 验证结果结构。"""
        resp = client.get(
            "/api/v1/knowledge/search?q=fruit&top_k=3",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "fruit"
        assert "results" in data
        assert isinstance(data["results"], list)

        for item in data["results"]:
            assert "content" in item
            assert "score" in item
            assert isinstance(item["score"], (int, float))

    def test_cross_module_independence(self, client: TestClient, auth_headers):
        """[场景测试] 跨模块独立：获取角色 → 知识库搜索 → 角色数据不受影响。"""
        # 获取角色
        persona_resp = client.get("/api/v1/personas/preset_study_buddy")
        assert persona_resp.status_code == 200
        persona = persona_resp.json()

        # 用无关词搜索知识库
        search_resp = client.get(
            "/api/v1/knowledge/search?q=vocabulary",
            headers=auth_headers,
        )
        assert search_resp.status_code == 200

        # 再次获取角色，验证数据不受影响
        persona2 = client.get("/api/v1/personas/preset_study_buddy").json()
        assert persona2 == persona

    def test_auth_mixed_endpoints(self, client: TestClient, auth_headers):
        """[场景测试] 认证混合场景：公开端点无需 auth，需 auth 端点不带 token 返回 401。"""
        # 公开端点 — 不带 auth 也应成功
        pub_urls = [
            "/api/v1/personas",
            "/api/v1/personas/preset_girlfriend",
        ]
        for url in pub_urls:
            resp = client.get(url)
            assert resp.status_code == 200, f"Public {url} failed"
            # 带 auth 也应成功
            resp_auth = client.get(url, headers=auth_headers)
            assert resp_auth.status_code == 200, f"Auth-on-public {url} failed"

        # 需 auth 端点 — 不带 auth 返回 401
        auth_urls = [
            "/api/v1/personas/custom",
            "/api/v1/knowledge/lookup?word=test",
            "/api/v1/knowledge/search?q=test",
        ]
        for url in auth_urls:
            resp = client.get(url)
            assert resp.status_code == 401, (
                f"Unauthenticated {url} should return 401, got {resp.status_code}"
            )
            resp_auth = client.get(url, headers=auth_headers)
            assert resp_auth.status_code == 200, (
                f"Authenticated {url} failed with {resp_auth.status_code}"
            )

    def test_all_four_presets_exist(self, client: TestClient):
        """[场景测试] 预设角色应包含全部 4 个角色。"""
        resp = client.get("/api/v1/personas")
        assert resp.status_code == 200
        actual_ids = {p["id"] for p in resp.json()["personas"]}
        expected_ids = {
            "preset_girlfriend",
            "preset_strict_teacher",
            "preset_study_buddy",
            "preset_humorous_friend",
        }
        missing = expected_ids - actual_ids
        assert not missing, f"Missing presets: {missing}"
        assert len(actual_ids) >= 4
