"""JWT 认证实现。

基于 python-jose + hashlib，完全自建。
"""

import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from mellow.config import Settings, get_settings
from mellow.exceptions import AuthenticationError, ConflictError
from mellow.providers.auth import AuthProvider, TokenPair, UserInfo


class JWTAuthProvider(AuthProvider):
    """JWT 自建认证实现。

    用户数据存储由外部 Repository 注入（Phase 5 接入 SQLite）。
    Phase 2 提供内存存储用于开发测试。
    """

    def __init__(
        self,
        settings: Settings | None = None,
        user_repo=None,  # Phase 5: UserRepository
    ):
        self._settings = settings or get_settings()
        self._user_repo = user_repo
        # 开发阶段内存存储
        self._users: dict[str, dict] = {}
        # 保护 _users 并发访问
        self._lock = asyncio.Lock()
        # PBKDF2 迭代次数
        self._hash_iterations = 600_000

    def _hash_password(self, password: str) -> str:
        """使用 PBKDF2-SHA256 哈希密码。"""
        salt = secrets.token_hex(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), self._hash_iterations)
        return f"pbkdf2:sha256:{self._hash_iterations}${salt}${dk.hex()}"

    def _verify_password(self, plain: str, hashed: str) -> bool:
        """验证 PBKDF2-SHA256 密码哈希。"""
        try:
            # hash 格式: pbkdf2:sha256:{iterations}${salt}${stored}
            _, _, tail = hashed.split(":", 2)
            iterations_str, salt, stored = tail.split("$", 2)
            dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), int(iterations_str))
            return secrets.compare_digest(dk.hex(), stored)
        except (ValueError, AttributeError):
            return False

    def _create_token(self, user_id: str, username: str) -> TokenPair:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self._settings.jwt_expire_minutes)

        access_payload = {
            "sub": user_id,
            "username": username,
            "iat": now,
            "exp": expire,
            "type": "access",
        }
        refresh_payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(days=30),
            "type": "refresh",
        }

        access_token = jwt.encode(
            access_payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )
        refresh_token = jwt.encode(
            refresh_payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._settings.jwt_expire_minutes * 60,
        )

    def _decode_token(self, token: str, expected_type: str = "access") -> dict:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
            )
            if payload.get("type") != expected_type:
                raise AuthenticationError("Token 类型不匹配")
            return payload
        except JWTError as e:
            raise AuthenticationError(f"Token 无效: {e}")

    async def register(self, username: str, password: str) -> UserInfo:
        username = username.lower().strip()

        # 密码哈希是 CPU 密集型操作，在锁外执行
        password_hash = self._hash_password(password)

        async with self._lock:
            if username in self._users:
                raise ConflictError("用户名已存在")

            import uuid

            user_id = str(uuid.uuid4())
            self._users[username] = {
                "id": user_id,
                "username": username,
                "password_hash": password_hash,
                "is_active": True,
            }

        return UserInfo(id=user_id, username=username)

    async def login(self, username: str, password: str) -> TokenPair:
        username = username.lower().strip()
        user = self._users.get(username)
        if not user:
            raise AuthenticationError("用户名或密码错误")

        if not self._verify_password(password, user["password_hash"]):
            raise AuthenticationError("用户名或密码错误")

        return self._create_token(user["id"], user["username"])

    async def verify_token(self, token: str) -> UserInfo:
        payload = self._decode_token(token, "access")
        username = payload.get("username", "")
        user = self._users.get(username.lower())
        if not user:
            raise AuthenticationError("用户不存在")
        return UserInfo(id=user["id"], username=user["username"], is_active=user["is_active"])

    async def refresh_token(self, refresh_token: str) -> TokenPair:
        payload = self._decode_token(refresh_token, "refresh")
        user_id = payload["sub"]
        # 查找用户
        for user in self._users.values():
            if user["id"] == user_id:
                return self._create_token(user_id, user["username"])
        raise AuthenticationError("用户不存在")
