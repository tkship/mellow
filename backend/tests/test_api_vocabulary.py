"""Vocabulary API 全方位集成测试。

覆盖生词本 (Vocabulary Book) 的四类 API 端点：
  A. GET  /api/v1/vocabulary/book        — 按首字母分组的生词列表
  B. GET  /api/v1/vocabulary/book/search — 生词搜索
  C. POST /api/v1/vocabulary/book        — 添加生词
  D. DELETE /api/v1/vocabulary/book/{word} — 删除生词

测试维度：边界测试 / 等价类 / 极限值 / 状态转换 / 场景测试 / 安全测试。
"""

import itertools
from typing import Any

import pytest

# pytest fixtures (client, auth_headers) are auto-discovered from conftest.py

# =============================================================================
# 工具函数与常量
# =============================================================================

VOCAB_URL = "/api/v1/vocabulary/book"
_counter = itertools.count()


def _uid(prefix: str = "w") -> str:
    """生成模块内唯一单词名，避免测试间数据干扰。"""
    return f"{prefix}{next(_counter):05d}"


def _post(client: Any, headers: dict, word: str, **kwargs) -> dict:
    """POST /book 辅助：发送添加请求，返回 JSON。"""
    resp = client.post(VOCAB_URL, json={"word": word, **kwargs}, headers=headers)
    return resp


def _add(client: Any, headers: dict, word: str, **kwargs) -> dict:
    """POST /book 辅助：断言 200，返回 JSON body。"""
    resp = _post(client, headers, word, **kwargs)
    assert resp.status_code == 200, f"添加 {word!r} 失败: {resp.status_code} {resp.json()}"
    return resp.json()


def _defs(n: int, ch: int) -> list[str]:
    """生成 n 个每个 ch 字符的释义列表。"""
    return ["d" * ch for _ in range(n)]


def _items(n: int, ch: int, c: str = "x") -> list[str]:
    """生成 n 个每个 ch 字符的字符串列表。"""
    return [c * ch for _ in range(n)]


# =============================================================================
# 每个测试前自动清空生词表，保证测试隔离
# =============================================================================

@pytest.fixture(autouse=True)
async def _clean_vocab_table(test_engine) -> None:
    """autouse：每个测试函数前清空 vocabulary_entries 表，确保隔离。"""
    from sqlalchemy import text as sa_text

    async with test_engine.begin() as conn:
        await conn.execute(sa_text("DELETE FROM vocabulary_entries"))
    yield


# =============================================================================
# 边界测试 —— VocabularyCreate 各字段长度/数量边界
# =============================================================================

class TestAddWordBoundary:
    """[边界测试] VocabularyCreate 字段边界值验证。"""

    # ── word 字段 ──

    def test_word_exactly_1_char_returns_200(self, client, auth_headers):
        """[边界测试] word=1字符 → 200，status='added'。"""
        resp = _post(client, auth_headers, "a")
        assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}"
        assert resp.json()["status"] == "added"
        assert resp.json()["word"]["word"] == "a"

    def test_word_exactly_200_chars_returns_200(self, client, auth_headers):
        """[边界测试] word=200字符（上限） → 200。"""
        w = "a" * 200
        resp = _post(client, auth_headers, w)
        assert resp.status_code == 200, f"200字符单词应接受: {resp.status_code}"
        assert resp.json()["status"] == "added"

    def test_word_empty_string_returns_422(self, client, auth_headers):
        """[边界测试] word="" → 422（min_length=1 校验失败）。"""
        resp = client.post(VOCAB_URL, json={"word": ""}, headers=auth_headers)
        assert resp.status_code == 422, f"空字符串应 422，实际 {resp.status_code}"
        assert "word" in str(resp.json()["detail"]).lower()

    def test_word_201_chars_returns_422(self, client, auth_headers):
        """[边界测试] word=201字符 → 422（max_length=200 超限）。"""
        resp = _post(client, auth_headers, "a" * 201)
        assert resp.status_code == 422, f"201字符应 422，实际 {resp.status_code}"

    def test_word_spaces_only_returns_400(self, client, auth_headers):
        """[边界测试] word="   "（纯空格） → 400（strip后为空）。"""
        resp = client.post(VOCAB_URL, json={"word": "   "}, headers=auth_headers)
        assert resp.status_code == 400, f"纯空格应 400，实际 {resp.status_code}"

    # ── phonetic 字段 ──

    def test_phonetic_exactly_200_chars_returns_200(self, client, auth_headers):
        """[边界测试] phonetic=200字符 → 200。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("ph"), "phonetic": "p" * 200},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"200字符音标应接受: {resp.status_code}"

    # ── part_of_speech 字段 ──

    def test_part_of_speech_exactly_50_chars_returns_200(self, client, auth_headers):
        """[边界测试] part_of_speech=50字符 → 200。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("ps"), "part_of_speech": "p" * 50},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"50字符词性应接受: {resp.status_code}"

    # ── definitions 列表 ──

    def test_definitions_list_exactly_20_items_returns_200(self, client, auth_headers):
        """[边界测试] definitions=20项 → 200。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("dl"), "definitions": _defs(20, 10)},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"20项释义应接受: {resp.status_code}"

    def test_definitions_list_21_items_returns_422(self, client, auth_headers):
        """[边界测试] definitions=21项 → 422（max_length=20 超限）。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("d21"), "definitions": _defs(21, 10)},
            headers=auth_headers,
        )
        assert resp.status_code == 422, f"21项释义应 422，实际 {resp.status_code}"

    def test_definition_item_exactly_500_chars_returns_200(self, client, auth_headers):
        """[边界测试] definition单元素=500字符 → 200。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("di5"), "definitions": ["d" * 500]},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"500字符释义项应接受: {resp.status_code}"

    def test_definition_item_501_chars_returns_422(self, client, auth_headers):
        """[边界测试] definition单元素=501字符 → 422。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("di6"), "definitions": ["d" * 501]},
            headers=auth_headers,
        )
        assert resp.status_code == 422, f"501字符释义项应 422，实际 {resp.status_code}"

    # ── examples / synonyms 列表 ──

    def test_examples_list_exactly_20_items_returns_200(self, client, auth_headers):
        """[边界测试] examples=20项 → 200。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("ex"), "examples": _defs(20, 10)},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"20项例句应接受: {resp.status_code}"

    def test_synonyms_list_exactly_20_items_returns_200(self, client, auth_headers):
        """[边界测试] synonyms=20项 → 200。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("sy"), "synonyms": _defs(20, 10)},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"20项同义词应接受: {resp.status_code}"

    # ── added_at 字段 ──

    def test_added_at_exactly_50_chars_returns_200(self, client, auth_headers):
        """[边界测试] added_at=50字符 → 200。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("at"), "added_at": "t" * 50},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"50字符时间戳应接受: {resp.status_code}"


# =============================================================================
# 等价类测试 —— 正常输入的各种变体
# =============================================================================

class TestAddWordEquivalence:
    """[等价类] 添加单词的各等价场景。"""

    def test_add_simple_word_returns_added(self, client, auth_headers):
        """[等价类] 添加简单单词 → 200, status='added'。"""
        data = _add(client, auth_headers, _uid("simple"))
        assert data["status"] == "added", f"首次添加应为 added，实际 {data['status']}"

    def test_add_same_word_again_returns_exists(self, client, auth_headers):
        """[等价类] 重复添加同一单词 → 200, status='exists'。"""
        w = _uid("dup")
        r1 = _add(client, auth_headers, w)
        assert r1["status"] == "added"

        r2 = _post(client, auth_headers, w)
        assert r2.status_code == 200
        assert r2.json()["status"] == "exists", f"重复添加应 exists，实际 {r2.json()['status']}"

    def test_add_word_with_full_details_returns_200(self, client, auth_headers):
        """[等价类] 添加完整字段（音标/词性/释义/例句/同义词） → 200。"""
        w = _uid("full")
        resp = client.post(
            VOCAB_URL,
            json={
                "word": w,
                "phonetic": "/ˈtest/",
                "part_of_speech": "noun",
                "definitions": ["A procedure for evaluation"],
                "examples": ["Run a quick test."],
                "synonyms": ["trial", "exam"],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "added"
        assert data["word"]["phonetic"] == "/ˈtest/"
        assert len(data["word"]["definitions"]) == 1

    def test_add_word_only_required_field_returns_200(self, client, auth_headers):
        """[等价类] 仅提供必填word → 200，其余用默认值。"""
        w = _uid("req")
        data = _add(client, auth_headers, w)
        assert data["word"]["phonetic"] == ""
        assert data["word"]["part_of_speech"] == ""
        assert data["word"]["definitions"] == []

    def test_add_word_unicode_characters_returns_200(self, client, auth_headers):
        """[等价类] 含Unicode字符（é, ñ） → 200。"""
        data = _add(client, auth_headers, "café")
        assert data["word"]["word"] == "café"

    def test_add_word_chinese_characters_returns_200(self, client, auth_headers):
        """[等价类] 含中文字符 → 200。"""
        data = _add(client, auth_headers, "测试")
        assert "测试" in data["word"]["word"]

    def test_word_case_normalization_stores_lowercase(self, client, auth_headers):
        """[等价类] 添加 'Hello' → 存储为 'hello'（大小写归一化）。"""
        data = _add(client, auth_headers, "Hello")
        assert data["word"]["word"] == "hello", (
            f"应小写存储，实际 {data['word']['word']}"
        )

    def test_word_leading_trailing_spaces_trimmed(self, client, auth_headers):
        """[等价类] 添加 '  Hello  ' → 去空格后存为 'hello'。"""
        data = _add(client, auth_headers, "  Hello  ")
        assert data["word"]["word"] == "hello", (
            f"应去除空格，实际 {data['word']['word']}"
        )


class TestGetBook:
    """[等价类] GET /book 端点 —— 按首字母分组。"""

    def test_get_book_when_empty_returns_zero_total(self, client, auth_headers):
        """[等价类] 空生词本 → total=0, groups=[]。"""
        resp = client.get(VOCAB_URL, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0, f"空生词本 total 应为 0，实际 {data['total']}"
        assert data["groups"] == [], f"空生词本 groups 应为 []，实际 {data['groups']}"

    def test_get_book_with_words_returns_correct_grouping(self, client, auth_headers):
        """[等价类] 不同首字母单词 → 按首字母分组建。"""
        _add(client, auth_headers, "apple")
        _add(client, auth_headers, "banana")
        _add(client, auth_headers, "cherry")

        resp = client.get(VOCAB_URL, headers=auth_headers)
        data = resp.json()
        assert data["total"] == 3
        letters = {g["letter"] for g in data["groups"]}
        assert letters == {"A", "B", "C"}, f"分组字母应为A/B/C，实际 {letters}"

    def test_get_book_multiple_words_same_letter_count_and_sort(
        self, client, auth_headers
    ):
        """[等价类] 同首字母多词 → 验证组合数量和排序。"""
        for w in ["cat", "car", "cup"]:
            _add(client, auth_headers, w)

        resp = client.get(VOCAB_URL, headers=auth_headers)
        data = resp.json()
        c_group = next(g for g in data["groups"] if g["letter"] == "C")
        assert c_group["count"] == 3, f"C组应有3个单词，实际 {c_group['count']}"
        words_in_group = [w["word"] for w in c_group["words"]]
        assert words_in_group == sorted(words_in_group), "组内单词应按字母排序"


class TestWordSearch:
    """[等价类] GET /book/search 搜索端点。"""

    def test_search_exact_match_returns_word(self, client, auth_headers):
        """[等价类] 精确搜索 → 返回匹配单词。"""
        w = _uid("findme")
        _add(client, auth_headers, w)

        resp = client.get(f"{VOCAB_URL}/search?q={w}", headers=auth_headers)
        data = resp.json()
        assert data["total"] == 1, f"精确匹配应 1 条，实际 {data['total']}"
        assert data["results"][0]["word"] == w

    def test_search_partial_match_returns_matching_words(self, client, auth_headers):
        """[等价类] 部分匹配 → 返回所有包含搜索词的单词。"""
        for w in ["apple", "application", "banana"]:
            _add(client, auth_headers, w)

        resp = client.get(f"{VOCAB_URL}/search?q=app", headers=auth_headers)
        data = resp.json()
        assert data["total"] == 2, f"'app'应匹配2个，实际 {data['total']}"
        result_words = {r["word"] for r in data["results"]}
        assert result_words == {"apple", "application"}

    def test_search_no_match_returns_empty(self, client, auth_headers):
        """[等价类] 无匹配搜索 → 空结果集。"""
        _add(client, auth_headers, "apple")

        resp = client.get(
            f"{VOCAB_URL}/search?q=xyznonexistent", headers=auth_headers
        )
        data = resp.json()
        assert data["total"] == 0
        assert data["results"] == []

    def test_search_in_definitions_finds_match(self, client, auth_headers):
        """[等价类] 搜索释义内容 → 返回对应单词。"""
        _add(
            client, auth_headers, _uid("def"),
            definitions=["a round juicy fruit"],
        )

        resp = client.get(f"{VOCAB_URL}/search?q=juicy", headers=auth_headers)
        assert resp.json()["total"] >= 1, "搜索释义中的词应有结果"

    def test_search_is_case_insensitive(self, client, auth_headers):
        """[等价类] 搜索大小写不敏感。"""
        _add(client, auth_headers, "Apple")

        resp = client.get(f"{VOCAB_URL}/search?q=APPLE", headers=auth_headers)
        assert resp.json()["total"] == 1, "大写搜索应匹配小写存储的单词"


class TestWordDelete:
    """[等价类] DELETE /book/{word} 删除端点。"""

    def test_delete_existing_word_returns_removed(self, client, auth_headers):
        """[等价类] 删除存在的单词 → 200, status='removed'。"""
        w = _uid("del")
        _add(client, auth_headers, w)

        resp = client.delete(f"{VOCAB_URL}/{w}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "removed"
        assert data["word"] == w.lower()

    def test_delete_nonexistent_word_returns_404(self, client, auth_headers):
        """[等价类] 删除不存在的单词 → 404。"""
        resp = client.delete(
            f"{VOCAB_URL}/nonexistent_xyz", headers=auth_headers
        )
        assert resp.status_code == 404, f"不存在单词应 404，实际 {resp.status_code}"

    def test_delete_already_deleted_word_returns_404(self, client, auth_headers):
        """[等价类] 重复删除已删除单词 → 404。"""
        w = _uid("redel")
        _add(client, auth_headers, w)
        client.delete(f"{VOCAB_URL}/{w}", headers=auth_headers)

        r2 = client.delete(f"{VOCAB_URL}/{w}", headers=auth_headers)
        assert r2.status_code == 404, "二次删除应返回 404"

    def test_delete_url_encoded_special_char_word(self, client, auth_headers):
        """[等价类] 删除含空格/特殊字符的单词（URL编码正常）。"""
        _add(client, auth_headers, "hello world")

        resp = client.delete(
            f"{VOCAB_URL}/hello%20world", headers=auth_headers
        )
        assert resp.status_code == 200


# =============================================================================
# 极限值测试 —— 所有字段同时达到上限
# =============================================================================

class TestVocabularyExtreme:
    """[极限值] 所有字段逼近上限时的负载表现。"""

    def test_all_20_definitions_each_500_chars_returns_200(self, client, auth_headers):
        """[极限值] 20条释义，每条500字符 → 200。"""
        resp = client.post(
            VOCAB_URL,
            json={
                "word": _uid("edef"),
                "definitions": _items(20, 500, "d"),
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"20×500释义应200: {resp.status_code}"
        assert len(resp.json()["word"]["definitions"]) == 20

    def test_all_20_examples_and_20_synonyms_returns_200(self, client, auth_headers):
        """[极限值] 20条例句+20条同义词同时存在 → 200。"""
        resp = client.post(
            VOCAB_URL,
            json={
                "word": _uid("esyn"),
                "examples": _items(20, 100, "e"),
                "synonyms": _items(20, 100, "s"),
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"双20项应200: {resp.status_code}"

    def test_phonetic_200_chars_special_chars_returns_200(self, client, auth_headers):
        """[极限值] 音标=200字符特殊符号 → 200。"""
        special = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" * 10  # >200
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("sp"), "phonetic": special[:200]},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"特殊符号音标应200: {resp.status_code}"

    def test_maximum_fields_all_at_limits_returns_200(self, client, auth_headers):
        """[极限值] 所有字段同时达到上限 → 200（全负载测试）。"""
        payload = {
            "word": "a" * 200,
            "phonetic": "f" * 200,
            "part_of_speech": "p" * 50,
            "definitions": _items(20, 500, "d"),
            "examples": _items(20, 500, "e"),
            "synonyms": _items(20, 500, "s"),
            "added_at": "t" * 50,
        }
        resp = client.post(VOCAB_URL, json=payload, headers=auth_headers)
        assert resp.status_code == 200, (
            f"全字段上限应200，实际{resp.status_code}: {resp.json()}"
        )

    def test_very_long_unicode_word_200_chars(self, client, auth_headers):
        """[极限值] 200字符混合Unicode单词 → 200。"""
        w = "语言" * 100  # exactly 200 chars
        assert len(w) == 200
        resp = _post(client, auth_headers, w)
        assert resp.status_code == 200, f"200字符Unicode应200: {resp.status_code}"
        assert len(resp.json()["word"]["word"]) == 200


# =============================================================================
# 状态转换测试 —— 连续操作下生词本状态变迁
# =============================================================================

class TestWordBookStateTransition:
    """[状态转换] 单词在添加/删除/再添加中的状态迁移。"""

    def test_empty_to_add_to_verify_group(self, client, auth_headers):
        """[状态转换] 空生词本→添加1词→生词本有1项→验证分组。"""
        assert client.get(VOCAB_URL, headers=auth_headers).json()["total"] == 0

        w = _uid("st")
        _add(client, auth_headers, w)

        data = client.get(VOCAB_URL, headers=auth_headers).json()
        assert data["total"] == 1
        assert len(data["groups"]) == 1
        assert data["groups"][0]["count"] == 1
        assert data["groups"][0]["letter"] == w[0].upper()

    def test_add_search_delete_search_cycle(self, client, auth_headers):
        """[状态转换] 添加→搜索能找到→删除→搜索不能找到→生词本空。"""
        w = _uid("cyc")
        _add(client, auth_headers, w)

        # 搜索能找到
        r1 = client.get(f"{VOCAB_URL}/search?q={w}", headers=auth_headers)
        assert r1.json()["total"] == 1

        # 删除
        client.delete(f"{VOCAB_URL}/{w}", headers=auth_headers)

        # 搜索不能找到
        r2 = client.get(f"{VOCAB_URL}/search?q={w}", headers=auth_headers)
        assert r2.json()["total"] == 0

        # 生词本空
        assert client.get(VOCAB_URL, headers=auth_headers).json()["total"] == 0

    def test_two_words_same_letter_group_count_2(self, client, auth_headers):
        """[状态转换] 添加同首字母单词A、B → 分组count=2。"""
        _add(client, auth_headers, "apple")
        _add(client, auth_headers, "ant")

        groups = client.get(VOCAB_URL, headers=auth_headers).json()["groups"]
        a_group = next(g for g in groups if g["letter"] == "A")
        assert a_group["count"] == 2, f"A组count应为2，实际{a_group['count']}"

    def test_two_words_different_letter_two_groups(self, client, auth_headers):
        """[状态转换] 添加不同首字母单词 → 2个分组。"""
        _add(client, auth_headers, "apple")
        _add(client, auth_headers, "zebra")

        groups = client.get(VOCAB_URL, headers=auth_headers).json()["groups"]
        assert len(groups) == 2
        letters = {g["letter"] for g in groups}
        assert letters == {"A", "Z"}

    def test_add_delete_add_same_word_returns_added(self, client, auth_headers):
        """[状态转换] 添加→删除→再添加同一单词 → status='added'（非exists）。"""
        w = _uid("rdd")
        _add(client, auth_headers, w)
        client.delete(f"{VOCAB_URL}/{w}", headers=auth_headers)

        r3 = _post(client, auth_headers, w)
        assert r3.status_code == 200
        assert r3.json()["status"] == "added", (
            f"删除后重加应返回 added，实际 {r3.json()['status']}"
        )

    def test_add_exists_delete_readd_returns_added(self, client, auth_headers):
        """[状态转换] 添加→重复(返回exists)→删除→再添加 → status='added'。"""
        w = _uid("edr")
        _add(client, auth_headers, w)

        r_dup = _post(client, auth_headers, w)
        assert r_dup.json()["status"] == "exists"

        client.delete(f"{VOCAB_URL}/{w}", headers=auth_headers)

        r_re = _post(client, auth_headers, w)
        assert r_re.status_code == 200
        assert r_re.json()["status"] == "added", (
            f"exists后删除再添加应为 added，实际 {r_re.json()['status']}"
        )


# =============================================================================
# 场景测试 —— 多步骤综合业务流程
# =============================================================================

class TestVocabularyScenario:
    """[场景测试] 多单词、多步骤的综合使用场景。"""

    def test_full_lifecycle_five_words_different_letters(
        self, client, auth_headers
    ):
        """[场景测试] 完整生命周期：添加5个不同首字母词→验证分组→
        搜索其中一个→删除一个→验证生词本更新。"""
        words = ["apple", "banana", "cherry", "dragon", "elephant"]
        for w in words:
            _add(client, auth_headers, w)

        # 验证5组
        book = client.get(VOCAB_URL, headers=auth_headers).json()
        assert book["total"] == 5
        assert len(book["groups"]) == 5

        # 搜索cherry
        sr = client.get(f"{VOCAB_URL}/search?q=cherry", headers=auth_headers).json()
        assert sr["total"] == 1
        assert sr["results"][0]["word"] == "cherry"

        # 删除dragon
        client.delete(f"{VOCAB_URL}/dragon", headers=auth_headers)

        # 验证更新
        book2 = client.get(VOCAB_URL, headers=auth_headers).json()
        assert book2["total"] == 4, f"删除后应有4个词，实际 {book2['total']}"
        assert len(book2["groups"]) == 4

    def test_multiple_words_same_letter_grouping(self, client, auth_headers):
        """[场景测试] 同首字母apple, ant, art → 验证A组count=3且排序。"""
        for w in ["apple", "ant", "art"]:
            _add(client, auth_headers, w)

        groups = client.get(VOCAB_URL, headers=auth_headers).json()["groups"]
        a_group = next(g for g in groups if g["letter"] == "A")
        assert a_group["count"] == 3, f"A组count应为3，实际 {a_group['count']}"
        words_in_a = [w["word"] for w in a_group["words"]]
        assert words_in_a == sorted(words_in_a), f"应按字母排序: {words_in_a}"

    def test_search_scenario_partial_and_no_match(self, client, auth_headers):
        """[场景测试] 搜索app→2结果，搜索xyz→空。"""
        for w in ["apple", "application", "banana"]:
            _add(client, auth_headers, w)

        r1 = client.get(f"{VOCAB_URL}/search?q=app", headers=auth_headers).json()
        assert r1["total"] == 2

        r2 = client.get(f"{VOCAB_URL}/search?q=xyz", headers=auth_headers).json()
        assert r2["total"] == 0
        assert r2["results"] == []

    def test_mixed_case_scenario(self, client, auth_headers):
        """[场景测试] 添加'Hello'存为'hello'，再添加'HELLO'→返回'exists'。"""
        r1 = _add(client, auth_headers, "Hello")
        assert r1["word"]["word"] == "hello"

        r2 = _post(client, auth_headers, "HELLO")
        assert r2.status_code == 200
        assert r2.json()["status"] == "exists", "大写变体应识别为已存在"

        # 验证生词本只有一条hello
        book = client.get(VOCAB_URL, headers=auth_headers).json()
        assert book["total"] == 1, f"大小写变体不应新增，实际total={book['total']}"

    def test_extra_fields_are_ignored(self, client, auth_headers):
        """[场景测试] 请求体含未定义字段 → 正常添加（extra='ignore'）。"""
        resp = client.post(
            VOCAB_URL,
            json={"word": _uid("extf"), "unknown_field": "should_be_ignored"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"额外字段应忽略: {resp.status_code}"
        assert resp.json()["status"] == "added"

    def test_search_sort_param_accepted(self, client, auth_headers):
        """[场景测试] sort=recent 参数正常接受。"""
        _add(client, auth_headers, "zebra")
        _add(client, auth_headers, "apple")

        resp = client.get(
            f"{VOCAB_URL}/search?q=a&sort=recent", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1


# =============================================================================
# 安全测试 —— 所有端点需要认证
# =============================================================================

class TestVocabularyAuthRequired:
    """[安全测试] 验证未认证时所有端点返回 401/403。"""

    def test_get_book_without_auth_returns_401(self, client):
        """GET /book 无认证 → 401/403。"""
        resp = client.get(VOCAB_URL)
        assert resp.status_code in (401, 403), f"应 401/403，实际 {resp.status_code}"

    def test_post_book_without_auth_returns_401(self, client):
        """POST /book 无认证 → 401/403。"""
        resp = client.post(VOCAB_URL, json={"word": "test"})
        assert resp.status_code in (401, 403), f"应 401/403，实际 {resp.status_code}"

    def test_search_book_without_auth_returns_401(self, client):
        """GET /book/search 无认证 → 401/403。"""
        resp = client.get(f"{VOCAB_URL}/search?q=test")
        assert resp.status_code in (401, 403), f"应 401/403，实际 {resp.status_code}"

    def test_delete_word_without_auth_returns_401(self, client):
        """DELETE /book/{word} 无认证 → 401/403。"""
        resp = client.delete(f"{VOCAB_URL}/test")
        assert resp.status_code in (401, 403), f"应 401/403，实际 {resp.status_code}"
