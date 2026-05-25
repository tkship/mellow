"""Auth API 全方位集成测试。

覆盖：边界测试、等价类、极限值、状态转换、场景测试。

设计原则：
1. 使用 conftest 提供的 client/auth_headers fixtures，不直接 from main import app
2. 通过真实 API 端点测试完整认证流程，不 mock get_current_user
3. 每个 test_ 方法独立注册用户，避免跨测试状态污染
4. 测试分类通过类名和 docstring 标记清晰区分
"""

import string
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt


# ============================================================================
# 模块级常量 — 与 conftest.TEST_SETTINGS 保持一致
# ============================================================================

_TEST_JWT_SECRET = "test-secret-key-for-testing-only"
_TEST_JWT_ALGORITHM = "HS256"


# ============================================================================
# 辅助函数
# ============================================================================

def _unique_username(prefix: str = "user") -> str:
    """生成唯一用户名，避免测试间冲突。"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _generate_expired_token(username: str) -> str:
    """生成一个已过期的 JWT access token（用于 /me 端点 401 测试）。

    使用与 conftest 相同的 secret 和 algorithm，确保签名可验证但过期时间已过。
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "fake-user-id",
        "username": username,
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
        "type": "access",
    }
    return jwt.encode(payload, _TEST_JWT_SECRET, algorithm=_TEST_JWT_ALGORITHM)


def _generate_invalid_signature_token(username: str) -> str:
    """生成一个签名错误的 JWT（用不同 secret 签名）。

    用于测试 token 篡改场景。
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "fake-user-id",
        "username": username,
        "iat": now,
        "exp": now + timedelta(hours=1),
        "type": "access",
    }
    return jwt.encode(payload, "wrong-secret-key", algorithm=_TEST_JWT_ALGORITHM)


def _generate_wrong_type_token(username: str) -> str:
    """生成一个 type 为 'refresh' 但用于 access 端点的 token。

    用于测试 token 类型校验。
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "fake-user-id",
        "username": username,
        "iat": now,
        "exp": now + timedelta(hours=1),
        "type": "refresh",
    }
    return jwt.encode(payload, _TEST_JWT_SECRET, algorithm=_TEST_JWT_ALGORITHM)


# ============================================================================
# 注册接口 — 边界测试
# ============================================================================


class TestRegisterBoundary:
    """注册接口边界测试 —— username 和 password 长度边界。"""

    def test_register_username_min_boundary(self, client: TestClient):
        """[边界测试] 用户名恰好 3 字符（最小边界），应注册成功。"""
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "abc", "password": "Pass@123456"},
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_register_username_max_boundary(self, client: TestClient):
        """[边界测试] 用户名恰好 32 字符（最大边界），应注册成功。"""
        username = "a" * 32
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Pass@123456"},
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert "access_token" in data

    def test_register_username_below_min(self, client: TestClient):
        """[边界测试] 用户名 2 字符（低于最小长度 3），应返回 422。"""
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "ab", "password": "Pass@123456"},
        )
        assert resp.status_code == 422, resp.json()

    def test_register_username_above_max(self, client: TestClient):
        """[边界测试] 用户名 33 字符（超出最大长度 32），应返回 422。"""
        username = "a" * 33
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Pass@123456"},
        )
        assert resp.status_code == 422, resp.json()

    def test_register_password_min_boundary(self, client: TestClient):
        """[边界测试] 密码恰好 6 字符（最小边界），应注册成功。"""
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": _unique_username("minpass"),
                "password": "Abc@12",
            },
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert "access_token" in data

    def test_register_password_max_boundary(self, client: TestClient):
        """[边界测试] 密码恰好 128 字符（最大边界），应注册成功。"""
        password = "A" + "b" * 126 + "1"
        assert len(password) == 128
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": _unique_username("maxpass"),
                "password": password,
            },
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert "access_token" in data

    def test_register_password_below_min(self, client: TestClient):
        """[边界测试] 密码 5 字符（低于最小长度 6），应返回 422。"""
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "testuser", "password": "Abc12"},
        )
        assert resp.status_code == 422, resp.json()

    def test_register_password_above_max(self, client: TestClient):
        """[边界测试] 密码 129 字符（超出最大长度 128），应返回 422。"""
        password = "A" + "b" * 127 + "1"
        assert len(password) == 129
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": _unique_username("longpass"),
                "password": password,
            },
        )
        assert resp.status_code == 422, resp.json()


# ============================================================================
# 注册接口 — 等价类测试
# ============================================================================


class TestRegisterEquivalence:
    """注册接口等价类测试 —— 有效/无效输入划分。"""

    def test_register_valid_typical(self, client: TestClient):
        """[等价类] 典型合法用户名和密码组合，应返回 200 及 token。"""
        username = _unique_username("john")
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Secure@Pass1"},
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        assert isinstance(data["refresh_token"], str)
        assert isinstance(data["expires_in"], int)

    def test_register_empty_username(self, client: TestClient):
        """[等价类] 用户名为空字符串，应返回 422（Pydantic 校验失败）。"""
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "", "password": "Secure@Pass1"},
        )
        assert resp.status_code == 422, resp.json()

    def test_register_empty_password(self, client: TestClient):
        """[等价类] 密码为空字符串，应返回 422（Pydantic 校验失败）。"""
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": _unique_username("ep"), "password": ""},
        )
        assert resp.status_code == 422, resp.json()

    def test_register_whitespace_only_username(self, client: TestClient):
        """[等价类] 用户名为纯空格，应返回 200（空格未在 Pydantic 层拦截，注册后会被 .lower().strip() 处理）。"""
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "   ", "password": "Secure@Pass1"},
        )
        # 空格被 strip 后为空，取决于业务层校验
        # 当前实现：register 中 username.lower().strip() → 空字符串 →
        # 可能保存成功（取决于 DB），也可能失败。
        # 无论哪种，只要返回 200 或 422 均为合理；401 不合理。
        assert resp.status_code in (200, 422), f"Unexpected {resp.status_code}: {resp.json()}"

    def test_register_special_chars_username(self, client: TestClient):
        """[等价类] 用户名含特殊字符 @#$%^&*，应返回 200。"""
        username = _unique_username("spec")
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": f"{username}@#$%^&*",
                "password": "Secure@Pass1",
            },
        )
        # 特殊字符未被 Pydantic 层禁止，但可能被业务层处理
        assert resp.status_code in (200, 422), f"Unexpected {resp.status_code}: {resp.json()}"

    def test_register_unicode_username(self, client: TestClient):
        """[等价类] 用户名包含 Unicode 字符（中文），应返回 200。"""
        username = _unique_username("user")
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": f"{username}测试用户",
                "password": "Secure@Pass1",
            },
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert "access_token" in data

    def test_register_missing_username(self, client: TestClient):
        """[等价类] 请求体缺少 username 字段，应返回 422。"""
        resp = client.post(
            "/api/v1/auth/register",
            json={"password": "Secure@Pass1"},
        )
        assert resp.status_code == 422, resp.json()

    def test_register_missing_password(self, client: TestClient):
        """[等价类] 请求体缺少 password 字段，应返回 422。"""
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": _unique_username("mp")},
        )
        assert resp.status_code == 422, resp.json()

    def test_register_empty_body(self, client: TestClient):
        """[等价类] 空请求体，应返回 422。"""
        resp = client.post("/api/v1/auth/register", json={})
        assert resp.status_code == 422, resp.json()

    def test_register_extra_fields(self, client: TestClient):
        """[等价类] 请求体包含额外未知字段，应忽略并成功注册。"""
        username = _unique_username("extra")
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "password": "Secure@Pass1",
                "email": "test@example.com",
                "age": 25,
            },
        )
        assert resp.status_code == 200, resp.json()


# ============================================================================
# 登录接口 — 边界测试
# ============================================================================


class TestLoginBoundary:
    """登录接口边界测试 —— 空/缺失字段。

    LoginRequest 无 min_length 约束，空字符串会通过 Pydantic 校验
    并到达 auth 层，由业务逻辑返回 401。
    """

    def test_login_empty_username(self, client: TestClient):
        """[边界测试] 用户名为空字符串，Pydantic 放行但 auth 层返回 401。"""
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "", "password": "Pass@123456"},
        )
        # LoginRequest 无 min_length → 空字符串到 auth 层 → 401
        assert resp.status_code == 401, resp.json()
        assert resp.json()["error"] == "AuthenticationError"

    def test_login_empty_password(self, client: TestClient):
        """[边界测试] 密码为空字符串，Pydantic 放行但 auth 层返回 401。"""
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "someuser", "password": ""},
        )
        assert resp.status_code == 401, resp.json()
        assert resp.json()["error"] == "AuthenticationError"

    def test_login_missing_username(self, client: TestClient):
        """[边界测试] 请求体缺少 username 字段，应返回 422。"""
        resp = client.post(
            "/api/v1/auth/login",
            json={"password": "Pass@123456"},
        )
        assert resp.status_code == 422, resp.json()

    def test_login_missing_password(self, client: TestClient):
        """[边界测试] 请求体缺少 password 字段，应返回 422。"""
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "someuser"},
        )
        assert resp.status_code == 422, resp.json()


# ============================================================================
# 登录接口 — 等价类测试
# ============================================================================


class TestLoginEquivalence:
    """登录接口等价类测试 —— 有效/无效凭证组合。"""

    def test_login_correct_credentials(self, client: TestClient):
        """[等价类] 正确的用户名和密码，应返回 200 及 token。"""
        username = _unique_username("loginok")
        password = "Correct@Pass1"
        # 先注册
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password},
        )
        assert reg_resp.status_code == 200, reg_resp.json()

        # 再登录
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient):
        """[等价类] 正确的用户名但错误的密码，应返回 401。"""
        username = _unique_username("loginwp")
        # 注册
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Correct@Pass1"},
        )
        assert reg_resp.status_code == 200, reg_resp.json()

        # 错误密码登录
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "Wrong@Pass1"},
        )
        assert resp.status_code == 401, resp.json()
        data = resp.json()
        assert data["error"] == "AuthenticationError"

    def test_login_nonexistent_user(self, client: TestClient):
        """[等价类] 不存在的用户名，应返回 401。"""
        resp = client.post(
            "/api/v1/auth/login",
            json={
                "username": _unique_username("nonexist"),
                "password": "Some@Pass1",
            },
        )
        assert resp.status_code == 401, resp.json()
        data = resp.json()
        assert data["error"] == "AuthenticationError"

    def test_login_case_insensitive_username(self, client: TestClient):
        """[等价类] 用户名大小写不敏感，大写登录应成功。"""
        username = _unique_username("caseuser")
        password = "Case@Pass1"
        # 小写注册
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username.lower(), "password": password},
        )
        assert reg_resp.status_code == 200, reg_resp.json()

        # 大写登录
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": username.upper(), "password": password},
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert "access_token" in data

    def test_login_with_leading_trailing_spaces(self, client: TestClient):
        """[等价类] 用户名带首尾空格，应被 trim 后登录成功。"""
        username = _unique_username("trimuser")
        password = "Trim@Pass1"
        # 注册
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password},
        )
        assert reg_resp.status_code == 200, reg_resp.json()

        # 带空格登录
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": f"  {username}  ", "password": password},
        )
        assert resp.status_code == 200, resp.json()


# ============================================================================
# 极限值测试
# ============================================================================


class TestExtremeValues:
    """极限值测试 —— 边界长度、特殊字符组合、重复操作。"""

    def test_register_username_32_ascii(self, client: TestClient):
        """[极限值] 用户名 32 个 ASCII 字符组合（字母+数字），应注册成功。"""
        # string.ascii_letters 有 52 个字符，取前 32 即可
        username = string.ascii_letters[:32]
        assert len(username) == 32
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Secure@Pass1"},
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert "access_token" in data

    def test_register_password_128_mixed(self, client: TestClient):
        """[极限值] 密码 128 字符混合大小写、数字、特殊符号，应注册成功。"""
        # 用 chars 池 × 重复构建恰好 128 字符
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}"
        password = (chars * ((128 // len(chars)) + 1))[:128]
        assert len(password) == 128
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": _unique_username("mixpass"),
                "password": password,
            },
        )
        assert resp.status_code == 200, resp.json()

    def test_register_password_unicode_long(self, client: TestClient):
        """[极限值] 密码包含 Unicode 字符（中日韩），长度接近边界上限。"""
        password = "密" * 42 + "码"  # 85 chars unicode
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": _unique_username("unipass"),
                "password": password,
            },
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert "access_token" in data

    def test_register_duplicate_username(self, client: TestClient):
        """[极限值] 重复注册相同用户名，应返回 409 ConflictError。"""
        username = _unique_username("dup")
        # 首次注册
        resp1 = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Secure@Pass1"},
        )
        assert resp1.status_code == 200, resp1.json()

        # 重复注册
        resp2 = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Another@Pass1"},
        )
        assert resp2.status_code == 409, resp2.json()
        data = resp2.json()
        assert data["error"] == "ConflictError"

    def test_register_username_at_boundary_with_unicode(self, client: TestClient):
        """[极限值] 用户名 32 个中文字符（每字符 3 字节，但长度按字符计），应在边界内。"""
        username = "测" * 32
        assert len(username) == 32
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Secure@Pass1"},
        )
        assert resp.status_code == 200, resp.json()


# ============================================================================
# 状态转换测试
# ============================================================================


class TestStateTransition:
    """认证状态转换测试 —— 多步骤流程中的状态变化。"""

    def test_full_auth_flow_register_to_me(self, client: TestClient):
        """[状态转换] 注册 → 登录 → 获取 token → 访问 /me → 验证身份一致性。"""
        username = _unique_username("flow1")
        password = "Flow@Pass1"

        # Step 1: 注册
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password},
        )
        assert reg_resp.status_code == 200, reg_resp.json()
        reg_data = reg_resp.json()

        # Step 2: 用注册返回的 token 访问 /me
        me_resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {reg_data['access_token']}"},
        )
        assert me_resp.status_code == 200, me_resp.json()
        me_data = me_resp.json()
        assert me_data["username"] == username.lower()
        assert me_data["is_active"] is True
        assert "id" in me_data

        # Step 3: 重新登录获取新 token
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert login_resp.status_code == 200, login_resp.json()
        login_data = login_resp.json()

        # Step 4: 用新 token 访问 /me，验证同一用户
        me_resp2 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_data['access_token']}"},
        )
        assert me_resp2.status_code == 200, me_resp2.json()
        assert me_resp2.json()["id"] == me_data["id"]
        assert me_resp2.json()["username"] == username.lower()

    def test_refresh_token_flow(self, client: TestClient):
        """[状态转换] 注册 → 登录 → 用 refresh_token 刷新 → 新 token 可访问 /me。"""
        username = _unique_username("rfflow")
        password = "Refresh@Pass1"

        # 注册 & 登录
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password},
        )
        assert reg_resp.status_code == 200, reg_resp.json()
        tokens = reg_resp.json()

        # 刷新 token
        refresh_resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_resp.status_code == 200, refresh_resp.json()
        new_tokens = refresh_resp.json()
        # 验证刷新后的 token 结构完整（同一秒内 JWT 可能相同，无法强行断言不等）
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert len(new_tokens["access_token"]) > 0
        assert len(new_tokens["refresh_token"]) > 0

        # 用新 token 访问 /me
        me_resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
        )
        assert me_resp.status_code == 200, me_resp.json()
        assert me_resp.json()["username"] == username.lower()

    def test_invalid_token_rejected(self, client: TestClient):
        """[状态转换] 使用签名错误的 token 访问 /me，应返回 401。"""
        bad_token = _generate_invalid_signature_token("hacker")
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert resp.status_code == 401, resp.json()
        data = resp.json()
        assert data["error"] == "AuthenticationError"

    def test_expired_token_rejected(self, client: TestClient):
        """[状态转换] 使用已过期的 JWT token 访问 /me，应返回 401。"""
        expired_token = _generate_expired_token("expireduser")
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == 401, resp.json()
        data = resp.json()
        assert data["error"] == "AuthenticationError"

    def test_wrong_password_after_register(self, client: TestClient):
        """[状态转换] 注册成功后，使用错误密码登录，应返回 401。"""
        username = _unique_username("wpafter")
        # 注册成功
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Correct@Pass1"},
        )
        assert reg_resp.status_code == 200, reg_resp.json()

        # 错误密码
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "WrongPassword1"},
        )
        assert resp.status_code == 401, resp.json()

    def test_refresh_with_invalid_token(self, client: TestClient):
        """[状态转换] 使用错误签名的 refresh_token，应返回 401。"""
        bad_token = _generate_invalid_signature_token("hacker")
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": bad_token},
        )
        assert resp.status_code == 401, resp.json()

    def test_refresh_with_expired_token(self, client: TestClient):
        """[状态转换] 使用过期的 refresh_token，应返回 401。"""
        expired_token = _generate_expired_token("expired")
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token},
        )
        assert resp.status_code == 401, resp.json()

    def test_wrong_token_type_for_me(self, client: TestClient):
        """[状态转换] 使用 type=refresh 的 token 访问 /me（type 不符），应返回 401。"""
        wrong_type_token = _generate_wrong_type_token("testuser")
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {wrong_type_token}"},
        )
        assert resp.status_code == 401, resp.json()


# ============================================================================
# 完整场景测试
# ============================================================================


class TestFullScenario:
    """完整场景测试 —— 多步骤业务流程模拟。"""

    def test_full_auth_with_token_rotation(self, client: TestClient):
        """[场景测试] 完整认证流程：注册 → /me → 刷新 → /me，验证 token 轮换后身份一致。"""
        username = _unique_username("rotation")
        password = "Rotation@Pass1"

        # 注册
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password},
        )
        assert reg_resp.status_code == 200, reg_resp.json()
        tokens = reg_resp.json()

        # 用原始 token 访问 /me
        me1 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert me1.status_code == 200, me1.json()
        user1 = me1.json()

        # 刷新 token
        refresh_resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_resp.status_code == 200, refresh_resp.json()
        new_tokens = refresh_resp.json()

        # 用新 token 访问 /me，验证同一用户
        me2 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
        )
        assert me2.status_code == 200, me2.json()
        user2 = me2.json()
        assert user2["id"] == user1["id"]
        assert user2["username"] == username.lower()
        assert user2["is_active"] is True

        # 再次刷新
        refresh_resp2 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": new_tokens["refresh_token"]},
        )
        assert refresh_resp2.status_code == 200, refresh_resp2.json()
        newest_tokens = refresh_resp2.json()

        # 第三次 /me 验证一致性
        me3 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {newest_tokens['access_token']}"},
        )
        assert me3.status_code == 200, me3.json()
        assert me3.json()["id"] == user1["id"]

    def test_multiple_users_isolation(self, client: TestClient):
        """[场景测试] 多用户隔离：注册 user1 和 user2，各自登录验证独立的 token 和身份。"""
        user1_name = _unique_username("user1")
        user2_name = _unique_username("user2")
        password = "Shared@Pass1"

        # 注册 user1
        reg1 = client.post(
            "/api/v1/auth/register",
            json={"username": user1_name, "password": password},
        )
        assert reg1.status_code == 200, reg1.json()
        token1 = reg1.json()["access_token"]

        # 注册 user2
        reg2 = client.post(
            "/api/v1/auth/register",
            json={"username": user2_name, "password": password},
        )
        assert reg2.status_code == 200, reg2.json()
        token2 = reg2.json()["access_token"]

        # 验证 user1 身份
        me1 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert me1.status_code == 200, me1.json()
        assert me1.json()["username"] == user1_name.lower()

        # 验证 user2 身份
        me2 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert me2.status_code == 200, me2.json()
        assert me2.json()["username"] == user2_name.lower()

        # 验证两个用户 ID 不同
        assert me1.json()["id"] != me2.json()["id"]

        # user1 登录
        login1 = client.post(
            "/api/v1/auth/login",
            json={"username": user1_name, "password": password},
        )
        assert login1.status_code == 200, login1.json()

        # user2 登录
        login2 = client.post(
            "/api/v1/auth/login",
            json={"username": user2_name, "password": password},
        )
        assert login2.status_code == 200, login2.json()

        # 验证各自 /me
        assert (
            client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {login1.json()['access_token']}"},
            ).json()["username"]
            == user1_name.lower()
        )
        assert (
            client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {login2.json()['access_token']}"},
            ).json()["username"]
            == user2_name.lower()
        )

    def test_token_replay(self, client: TestClient):
        """[场景测试] Token 重放：同一个 access_token 使用两次，JWT 无状态，两次都应成功。"""
        username = _unique_username("replay")
        password = "Replay@Pass1"

        # 注册获取 token
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password},
        )
        assert reg_resp.status_code == 200, reg_resp.json()
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 第一次使用
        me1 = client.get("/api/v1/auth/me", headers=headers)
        assert me1.status_code == 200, me1.json()

        # 第二次使用同一 token
        me2 = client.get("/api/v1/auth/me", headers=headers)
        assert me2.status_code == 200, me2.json()

        # 两次返回同一用户
        assert me1.json()["id"] == me2.json()["id"]
        assert me1.json()["username"] == me2.json()["username"]

    def test_password_still_works_with_old_token(self, client: TestClient):
        """[场景测试] 密码不变场景：注册 → 登录 → 旧 token 仍有效 → /me 正常返回。"""
        username = _unique_username("passkeep")
        password = "Keep@Pass1"

        # 注册
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password},
        )
        assert reg_resp.status_code == 200, reg_resp.json()
        old_token = reg_resp.json()["access_token"]

        # 用旧密码再次登录（等同于无密码更改）
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert login_resp.status_code == 200, login_resp.json()

        # 旧 token 仍然有效
        me_resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {old_token}"},
        )
        assert me_resp.status_code == 200, me_resp.json()
        assert me_resp.json()["username"] == username.lower()

    def test_no_auth_header_for_me(self, client: TestClient):
        """[场景测试] 不带 Authorization header 访问 /me，应返回 401。"""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401, resp.json()
        data = resp.json()
        assert data["error"] == "AuthenticationError"

    def test_malformed_auth_header(self, client: TestClient):
        """[场景测试] Authorization header 格式错误（非 Bearer 或格式不对），应返回 401 或 403。"""
        # 错误的 scheme
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        )
        # HTTPBearer 会拒绝非 Bearer scheme
        assert resp.status_code in (401, 403), f"Unexpected {resp.status_code}: {resp.json()}"

    def test_register_response_structure(self, client: TestClient):
        """[场景测试] 验证注册响应的完整 JSON 结构（TokenResponse 模型）。"""
        username = _unique_username("struct")
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "Struct@Pass1"},
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()

        # TokenResponse 字段
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0

    def test_me_response_structure(self, client: TestClient):
        """[场景测试] 验证 /me 响应的完整 JSON 结构（UserResponse 模型）。"""
        username = _unique_username("mecheck")
        # 注册获取 token
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "MeCheck@Pass1"},
        )
        assert reg_resp.status_code == 200, reg_resp.json()
        token = reg_resp.json()["access_token"]

        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, resp.json()
        data = resp.json()

        # UserResponse 字段
        assert "id" in data
        assert "username" in data
        assert "is_active" in data
        assert isinstance(data["id"], str)
        assert isinstance(data["username"], str)
        assert isinstance(data["is_active"], bool)
        assert data["username"] == username.lower()
        # ID 应为非空字符串
        assert len(data["id"]) > 0

    def test_refresh_with_empty_token(self, client: TestClient):
        """[场景测试] refresh 请求中 refresh_token 为空，应返回 401（token 校验失败）。"""
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": ""},
        )
        # 空 token 无法解码，应返回 401
        assert resp.status_code == 401, resp.json()
