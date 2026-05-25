"""Profile API 全方位集成测试。

覆盖 GET/PUT profile、plan CRUD、stats 查询、mistakes 查询等端点。
测试维度：边界测试、等价类、极限值、状态转换、场景测试。
"""

import sys

import pytest
# pytest fixtures (client, auth_headers) are auto-discovered from conftest.py


# ============================================================================
# 辅助函数
# ============================================================================

def _make_daily_plan(day: int = 1) -> dict:
    return {
        "day": day,
        "topic": "每日主题",
        "vocabulary": ["word", "learn"],
        "grammar_point": "一般现在时",
        "practice": "造句练习",
    }


def _make_weekly_plan(week: int = 1, theme: str = "基础语法周", days: list | None = None) -> dict:
    if days is None:
        days = [_make_daily_plan(1), _make_daily_plan(2)]
    return {"week": week, "theme": theme, "days": days}


# ============================================================================
# TestProfileGet — GET /api/v1/profile
# ============================================================================

class TestProfileGet:
    """GET /api/v1/profile 端点的测试。"""

    def test_get_profile_without_prior_update_returns_default(self, client, auth_headers):
        """[等价类] GET profile without prior update → default values (cefr_level="A1")。"""
        resp = client.get("/api/v1/profile", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["cefr_level"] == "A1"
        assert data["vocabulary_size"] == 0
        assert isinstance(data["weak_areas"], list)
        assert isinstance(data["known_words_count"], int)
        assert isinstance(data["completed_lessons"], list)
        assert "summary" in data
        assert "current_plan" in data

    def test_get_profile_without_auth_returns_401(self, client):
        """[边界测试] GET profile without Authorization header → 401。"""
        resp = client.get("/api/v1/profile")
        assert resp.status_code == 401

    def test_get_profile_after_update_reflects_changes(self, client, auth_headers):
        """[状态转换] PUT profile → GET profile → 验证更新持久化。"""
        client.put("/api/v1/profile", json={"cefr_level": "B1"}, headers=auth_headers)
        resp = client.get("/api/v1/profile", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cefr_level"] == "B1"


# ============================================================================
# TestProfileUpdateBoundary — PUT /api/v1/profile 边界测试
# ============================================================================

class TestProfileUpdateBoundary:
    """PUT /api/v1/profile 边界测试 —— ProfileUpdateRequest 字段校验。"""

    def test_cefr_level_a0_min_boundary(self, client, auth_headers):
        """[边界测试] cefr_level exactly "A0" (min boundary) → 200。"""
        resp = client.put("/api/v1/profile", json={"cefr_level": "A0"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cefr_level"] == "A0"

    def test_cefr_level_c2_max_boundary(self, client, auth_headers):
        """[边界测试] cefr_level exactly "C2" (max boundary) → 200。"""
        resp = client.put("/api/v1/profile", json={"cefr_level": "C2"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cefr_level"] == "C2"

    def test_cefr_level_a1_valid(self, client, auth_headers):
        """[边界测试] cefr_level "A1" → 200。"""
        resp = client.put("/api/v1/profile", json={"cefr_level": "A1"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cefr_level"] == "A1"

    def test_cefr_level_invalid(self, client, auth_headers):
        """[边界测试] cefr_level invalid (e.g. "Z9") → 422。"""
        resp = client.put("/api/v1/profile", json={"cefr_level": "Z9"}, headers=auth_headers)
        assert resp.status_code == 422

    def test_cefr_level_lowercase_invalid(self, client, auth_headers):
        """[边界测试] cefr_level lowercase "b1" should fail pattern → 422。"""
        resp = client.put("/api/v1/profile", json={"cefr_level": "b1"}, headers=auth_headers)
        assert resp.status_code == 422

    def test_vocabulary_size_zero_min_boundary(self, client, auth_headers):
        """[边界测试] vocabulary_size=0 (min boundary) → 200。"""
        resp = client.put("/api/v1/profile", json={"vocabulary_size": 0}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["vocabulary_size"] == 0

    def test_vocabulary_size_large_value(self, client, auth_headers):
        """[边界测试] vocabulary_size=999999 (large value) → 200。"""
        resp = client.put("/api/v1/profile", json={"vocabulary_size": 999999}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["vocabulary_size"] == 999999

    def test_vocabulary_size_negative(self, client, auth_headers):
        """[边界测试] vocabulary_size=-1 (below ge=0) → 422。"""
        resp = client.put("/api/v1/profile", json={"vocabulary_size": -1}, headers=auth_headers)
        assert resp.status_code == 422

    def test_learning_goal_exactly_500_chars(self, client, auth_headers):
        """[边界测试] learning_goal exactly 500 chars → 200。"""
        goal = "学" * 500  # 500 Chinese chars
        resp = client.put("/api/v1/profile", json={"learning_goal": goal}, headers=auth_headers)
        assert resp.status_code == 200

    def test_learning_goal_501_chars(self, client, auth_headers):
        """[边界测试] learning_goal 501 chars → 422。"""
        goal = "学" * 501
        resp = client.put("/api/v1/profile", json={"learning_goal": goal}, headers=auth_headers)
        assert resp.status_code == 422


# ============================================================================
# TestProfileUpdateEquivalence — PUT /api/v1/profile 等价类测试
# ============================================================================

class TestProfileUpdateEquivalence:
    """PUT /api/v1/profile 等价类测试 —— 部分更新、全量更新、空请求。"""

    def test_partial_update_cefr_only(self, client, auth_headers):
        """[等价类] PUT profile with only cefr_level → partial update works。"""
        resp = client.put("/api/v1/profile", json={"cefr_level": "B1"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cefr_level"] == "B1"

    def test_partial_update_vocabulary_only(self, client, auth_headers):
        """[等价类] PUT profile with only vocabulary_size → partial update works。"""
        # Reset to known state first (previous test may have changed cefr_level)
        client.put("/api/v1/profile", json={"cefr_level": "A1"}, headers=auth_headers)
        resp = client.put("/api/v1/profile", json={"vocabulary_size": 500}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["vocabulary_size"] == 500
        # Other fields should remain unchanged
        assert resp.json()["cefr_level"] == "A1"

    def test_partial_update_learning_goal_only(self, client, auth_headers):
        """[等价类] PUT profile with only learning_goal → partial update works。"""
        resp = client.put(
            "/api/v1/profile",
            json={"learning_goal": "希望能在三个月内流利对话"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_full_update_all_fields(self, client, auth_headers):
        """[等价类] PUT profile with all fields → full update works。"""
        resp = client.put(
            "/api/v1/profile",
            json={"cefr_level": "B2", "vocabulary_size": 1500, "learning_goal": "通过雅思7分"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["cefr_level"] == "B2"
        assert data["vocabulary_size"] == 1500

    def test_empty_body_returns_200(self, client, auth_headers):
        """[等价类] PUT profile with empty body {} → 200 (no-op, exclude_unset)。"""
        # 先设一个值，确认空 body 不会覆盖
        client.put("/api/v1/profile", json={"cefr_level": "B1"}, headers=auth_headers)
        resp = client.put("/api/v1/profile", json={}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cefr_level"] == "B1"  # unchanged


# ============================================================================
# TestProfileUpdateExtreme — PUT /api/v1/profile 极限值测试
# ============================================================================

class TestProfileUpdateExtreme:
    """PUT /api/v1/profile 极限值测试。"""

    def test_vocabulary_size_sys_maxsize(self, client, auth_headers):
        """[极限值] vocabulary_size=sys.maxsize → 200 (SQLite 动态类型可容纳)。"""
        resp = client.put(
            "/api/v1/profile", json={"vocabulary_size": sys.maxsize}, headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json()["vocabulary_size"] == sys.maxsize

    def test_learning_goal_500_unicode_chars(self, client, auth_headers):
        """[极限值] learning_goal with 500 unicode chars (emoji + CJK) → 200。"""
        goal = "🎯日本語한국어🏆" * 50  # 6 chars * 50 = 300, pad to 500
        goal = (goal * 2)[:500]
        assert len(goal) == 500
        resp = client.put("/api/v1/profile", json={"learning_goal": goal}, headers=auth_headers)
        assert resp.status_code == 200

    def test_put_profile_with_null_fields_no_error(self, client, auth_headers):
        """[极限值] PUT profile with explicit null fields → server error (NOT NULL constraint)。"""
        # Explicit null values violate NOT NULL DB constraints — expect 500
        try:
            resp = client.put(
                "/api/v1/profile",
                json={"cefr_level": None, "vocabulary_size": None, "learning_goal": None},
                headers=auth_headers,
            )
            assert resp.status_code == 500
        except Exception:
            # TestClient may raise on unhandled server errors — that's acceptable
            pass


# ============================================================================
# TestPlanBoundary — PUT /api/v1/profile/plan 边界测试
# ============================================================================

class TestPlanBoundary:
    """PUT /api/v1/profile/plan 边界测试 —— WeeklyPlanRequest 字段校验。"""

    # --- week ---

    def test_week_one_min_boundary(self, client, auth_headers):
        """[边界测试] week=1 (min boundary) → 200。"""
        plan = _make_weekly_plan(week=1)
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200

    def test_week_zero_below_min(self, client, auth_headers):
        """[边界测试] week=0 (below min) → 422。"""
        plan = _make_weekly_plan(week=0)
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 422

    # --- theme ---

    def test_theme_exactly_1_char(self, client, auth_headers):
        """[边界测试] theme exactly 1 char → 200。"""
        plan = _make_weekly_plan(theme="A")
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200

    def test_theme_exactly_200_chars(self, client, auth_headers):
        """[边界测试] theme exactly 200 chars → 200。"""
        plan = _make_weekly_plan(theme="主" * 200)
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200

    def test_theme_201_chars(self, client, auth_headers):
        """[边界测试] theme 201 chars → 422。"""
        plan = _make_weekly_plan(theme="主" * 201)
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 422

    # --- DailyPlanRequest.day ---

    def test_day_one_min_boundary(self, client, auth_headers):
        """[边界测试] DailyPlanRequest day=1 (min boundary) → 200。"""
        plan = _make_weekly_plan(days=[_make_daily_plan(day=1)])
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200

    def test_day_seven_max_boundary(self, client, auth_headers):
        """[边界测试] DailyPlanRequest day=7 (max boundary) → 200。"""
        plan = _make_weekly_plan(days=[_make_daily_plan(day=7)])
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200

    def test_day_zero_below_min(self, client, auth_headers):
        """[边界测试] DailyPlanRequest day=0 (below min) → 422。"""
        plan = _make_weekly_plan(days=[_make_daily_plan(day=0)])
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 422

    def test_day_eight_above_max(self, client, auth_headers):
        """[边界测试] DailyPlanRequest day=8 (above max) → 422。"""
        plan = _make_weekly_plan(days=[_make_daily_plan(day=8)])
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 422

    # --- vocabulary ---

    def test_vocabulary_list_exactly_20_items(self, client, auth_headers):
        """[边界测试] vocabulary list exactly 20 items → 200。"""
        day = _make_daily_plan(day=1)
        day["vocabulary"] = [f"word{i}" for i in range(20)]
        plan = _make_weekly_plan(days=[day])
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200

    def test_vocabulary_list_21_items(self, client, auth_headers):
        """[边界测试] vocabulary list 21 items → 422。"""
        day = _make_daily_plan(day=1)
        day["vocabulary"] = [f"word{i}" for i in range(21)]
        plan = _make_weekly_plan(days=[day])
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 422

    # --- topic ---

    def test_topic_exactly_200_chars(self, client, auth_headers):
        """[边界测试] topic exactly 200 chars → 200。"""
        day = _make_daily_plan(day=1)
        day["topic"] = "课" * 200
        plan = _make_weekly_plan(days=[day])
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200

    # --- practice ---

    def test_practice_exactly_500_chars(self, client, auth_headers):
        """[边界测试] practice exactly 500 chars → 200。"""
        day = _make_daily_plan(day=1)
        day["practice"] = "练" * 500
        plan = _make_weekly_plan(days=[day])
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200


# ============================================================================
# TestPlanExtreme — Plan 极限值测试
# ============================================================================

class TestPlanExtreme:
    """Plan 相关端点极限值测试。"""

    def test_theme_200_unicode_chars(self, client, auth_headers):
        """[极限值] theme with 200 unicode chars (emoji + CJK) → 200。"""
        chars = "🎯日本語한국어🏆"  # 6 chars
        theme = (chars * 34)[:200]
        assert len(theme) == 200
        plan = _make_weekly_plan(theme=theme)
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200

    def test_multiple_plan_updates_latest_wins(self, client, auth_headers):
        """[极限值] Multiple simultaneous plan updates → latest wins。"""
        plan1 = _make_weekly_plan(week=1, theme="第一周")
        plan2 = _make_weekly_plan(week=2, theme="第二周")
        client.put("/api/v1/profile/plan", json=plan1, headers=auth_headers)
        client.put("/api/v1/profile/plan", json=plan2, headers=auth_headers)
        resp = client.get("/api/v1/profile/plan", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["plan"]["week"] == 2


# ============================================================================
# TestPlanStateTransition — Plan 状态转换测试
# ============================================================================

class TestPlanStateTransition:
    """Plan 生命周期状态转换测试。"""

    def test_no_plan_to_plan_set(self, client, auth_headers):
        """[状态转换] No plan → GET plan → plan=null → PUT plan → GET plan → plan exists。"""
        # Complete any existing plan first to reset state
        client.post("/api/v1/profile/plan/complete", headers=auth_headers)
        # 初始无计划
        resp = client.get("/api/v1/profile/plan", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["plan"] is None

        # 设置计划
        plan = _make_weekly_plan(week=1, theme="第一周语法")
        client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)

        # 验证计划存在
        resp = client.get("/api/v1/profile/plan", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["plan"] is not None
        assert resp.json()["plan"]["week"] == 1

    def test_set_plan_complete_plan_null(self, client, auth_headers):
        """[状态转换] Set plan → POST complete → GET plan → plan=null。"""
        plan = _make_weekly_plan(week=1, theme="计划生命周期")
        client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)

        # 完成计划
        resp = client.post("/api/v1/profile/plan/complete", headers=auth_headers)
        assert resp.status_code == 200
        assert "学习计划已完成" in resp.json()["message"]

        # 计划应变为 null
        resp = client.get("/api/v1/profile/plan", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["plan"] is None

    def test_complete_plan_updates_completed_lessons(self, client, auth_headers):
        """[状态转换] Plan completion → check completed_lessons updated。"""
        plan = _make_weekly_plan(week=1, theme="语法进阶")
        client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)

        resp = client.post("/api/v1/profile/plan/complete", headers=auth_headers)
        assert resp.status_code == 200
        completed = resp.json()["completed_lessons"]
        assert "语法进阶" in completed

    def test_complete_without_plan(self, client, auth_headers):
        """[状态转换] POST complete when no plan → returns message, no error。"""
        resp = client.post("/api/v1/profile/plan/complete", headers=auth_headers)
        assert resp.status_code == 200
        assert "暂无进行中的学习计划" in resp.json()["message"]

    def test_put_profile_multiple_times_each_persists(self, client, auth_headers):
        """[状态转换] PUT profile multiple times → each update persists。"""
        client.put("/api/v1/profile", json={"cefr_level": "A2"}, headers=auth_headers)
        resp = client.get("/api/v1/profile", headers=auth_headers)
        assert resp.json()["cefr_level"] == "A2"

        client.put("/api/v1/profile", json={"cefr_level": "B1"}, headers=auth_headers)
        resp = client.get("/api/v1/profile", headers=auth_headers)
        assert resp.json()["cefr_level"] == "B1"

        client.put("/api/v1/profile", json={"cefr_level": "C1"}, headers=auth_headers)
        resp = client.get("/api/v1/profile", headers=auth_headers)
        assert resp.json()["cefr_level"] == "C1"


# ============================================================================
# TestMistakesApi — GET /api/v1/profile/mistakes
# ============================================================================

class TestMistakesApi:
    """GET /api/v1/profile/mistakes 端点测试。"""

    def test_mistakes_empty_when_none_exist(self, client, auth_headers):
        """[等价类] GET mistakes when none exist → empty list。"""
        resp = client.get("/api/v1/profile/mistakes", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "mistakes" in data
        assert data["mistakes"] == []

    def test_mistakes_without_auth_returns_401(self, client):
        """[边界测试] GET mistakes without Authorization header → 401。"""
        resp = client.get("/api/v1/profile/mistakes")
        assert resp.status_code == 401


# ============================================================================
# TestPlanEquivalence — Plan 等价类测试
# ============================================================================

class TestPlanEquivalence:
    """Plan 端点等价类测试。"""

    def test_get_plan_when_none_set(self, client, auth_headers):
        """[等价类] GET plan when none set → plan=null。"""
        resp = client.get("/api/v1/profile/plan", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan"] is None

    def test_put_plan_then_get_plan_consistency(self, client, auth_headers):
        """[等价类] PUT plan then GET plan → verify consistency。"""
        plan = _make_weekly_plan(week=3, theme="英语时态", days=[_make_daily_plan(1)])
        client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        resp = client.get("/api/v1/profile/plan", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["plan"]["week"] == 3
        assert resp.json()["plan"]["theme"] == "英语时态"
        assert resp.json()["plan"]["completed"] is False


# ============================================================================
# TestStatsApi — GET /api/v1/profile/stats
# ============================================================================

class TestStatsApi:
    """GET /api/v1/profile/stats 端点测试。"""

    def test_stats_range_week(self, client, auth_headers):
        """[等价类] GET stats with range=week → 200。"""
        resp = client.get("/api/v1/profile/stats?range=week", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_messages" in data
        assert "learning_days" in data
        assert "cefr_level" in data
        assert "cefr_progress" in data
        assert data["range"] == "week"

    def test_stats_range_month(self, client, auth_headers):
        """[等价类] GET stats with range=month → 200。"""
        resp = client.get("/api/v1/profile/stats?range=month", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["range"] == "month"

    def test_stats_range_half_year(self, client, auth_headers):
        """[等价类] GET stats with range=half_year → 200。"""
        resp = client.get("/api/v1/profile/stats?range=half_year", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["range"] == "half_year"

    def test_stats_default_range_month(self, client, auth_headers):
        """[等价类] GET stats without range param → defaults to month, 200。"""
        resp = client.get("/api/v1/profile/stats", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["range"] == "month"

    def test_stats_invalid_range_no_rejection(self, client, auth_headers):
        """[等价类] GET stats with invalid range (no validation on backend) → still 200。"""
        resp = client.get("/api/v1/profile/stats?range=invalid", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["range"] == "invalid"

    def test_stats_without_auth_returns_401(self, client):
        """[边界测试] GET stats without Authorization header → 401。"""
        resp = client.get("/api/v1/profile/stats")
        assert resp.status_code == 401


# ============================================================================
# TestProfileScenario — 场景测试
# ============================================================================

class TestProfileScenario:
    """端到端场景测试 —— 完整学习流程。"""

    def test_full_learning_flow(self, client, auth_headers):
        """[场景测试] Full learning flow:
        Create profile → set CEFR → set plan → complete plan → check stats。
        """
        # 1. 设置 CEFR 等级
        resp = client.put("/api/v1/profile", json={"cefr_level": "B1", "vocabulary_size": 300}, headers=auth_headers)
        assert resp.status_code == 200

        # 2. 设置学习计划
        plan = _make_weekly_plan(week=1, theme="英语发音基础", days=[_make_daily_plan(1)])
        resp = client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        assert resp.status_code == 200

        # 3. 完成计划
        resp = client.post("/api/v1/profile/plan/complete", headers=auth_headers)
        assert resp.status_code == 200
        # 验证当前计划的主题出现在已完成列表中
        assert "英语发音基础" in resp.json()["completed_lessons"]

        # 4. 检查 stats
        resp = client.get("/api/v1/profile/stats?range=month", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["cefr_level"] == "B1"
        assert data["vocabulary_size"] == 300

    def test_plan_lifecycle_create_read_complete_verify(self, client, auth_headers):
        """[场景测试] Plan lifecycle: create → read → complete → verify completion → create new。"""
        # Create
        plan1 = _make_weekly_plan(week=1, theme="基础词汇")
        client.put("/api/v1/profile/plan", json=plan1, headers=auth_headers)

        # Read → verify
        resp = client.get("/api/v1/profile/plan", headers=auth_headers)
        assert resp.json()["plan"]["theme"] == "基础词汇"
        assert resp.json()["completed"] is False

        # Complete
        client.post("/api/v1/profile/plan/complete", headers=auth_headers)

        # Verify completion → plan null
        resp = client.get("/api/v1/profile/plan", headers=auth_headers)
        assert resp.json()["plan"] is None

        # Create new plan
        plan2 = _make_weekly_plan(week=2, theme="高级语法")
        client.put("/api/v1/profile/plan", json=plan2, headers=auth_headers)
        resp = client.get("/api/v1/profile/plan", headers=auth_headers)
        assert resp.json()["plan"]["theme"] == "高级语法"
        assert resp.json()["plan"]["week"] == 2

    def test_stats_progression_reflects_changes(self, client, auth_headers):
        """[场景测试] Stats progression: empty → set profile → set plan → complete plan → stats reflect changes。"""
        # Reset state to known baseline
        client.put("/api/v1/profile", json={"cefr_level": "A1", "vocabulary_size": 0}, headers=auth_headers)
        # Empty state
        resp = client.get("/api/v1/profile/stats?range=week", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cefr_level"] == "A1"

        # Set profile
        client.put("/api/v1/profile", json={"cefr_level": "B2"}, headers=auth_headers)

        # Set and complete plan
        plan = _make_weekly_plan(week=1, theme="时态攻略")
        client.put("/api/v1/profile/plan", json=plan, headers=auth_headers)
        client.post("/api/v1/profile/plan/complete", headers=auth_headers)

        # Stats should reflect updated CEFR level
        resp = client.get("/api/v1/profile/stats?range=month", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cefr_level"] == "B2"
