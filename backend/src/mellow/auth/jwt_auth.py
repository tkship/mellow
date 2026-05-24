"""JWT 认证实现。

基于 python-jose + hashlib，完全自建。
用户数据通过 UserRepository 持久化到 SQLite。
每次操作创建新 session，避免 stale session 问题。
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from mellow.config import Settings, get_settings
from mellow.db.repos.user_repo import SqlAlchemyUserRepository
from mellow.exceptions import AuthenticationError, ConflictError
from mellow.providers.auth import AuthProvider, TokenPair, UserInfo


# 模块级缓存的 engine 和 session factory
_cached_engine = None
_cached_session_factory = None


def _default_session_factory():
    """获取一个新 AsyncSession（延迟导入，避免循环依赖）。"""
    global _cached_engine, _cached_session_factory
    if _cached_session_factory is None:
        from mellow.db.engine import get_session_factory, get_engine
        settings = get_settings()
        _cached_engine = get_engine(settings)
        _cached_session_factory = get_session_factory(_cached_engine)
    return _cached_session_factory()


class JWTAuthProvider(AuthProvider):
    """JWT 自建认证实现。

    用户数据通过 UserRepository 持久化到 SQLite 数据库。
    每次操作创建新 session，确保不会出现 stale session 问题。
    """

    def __init__(
        self,
        settings: Settings | None = None,
        user_repo=None,
        session_factory=None,
    ):
        self._settings = settings or get_settings()
        self._session_factory = session_factory or _default_session_factory
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
            raise AuthenticationError("Token 无效")

    async def register(self, username: str, password: str) -> UserInfo:
        username = username.lower().strip()

        # 密码哈希是 CPU 密集型操作
        password_hash = self._hash_password(password)

        session = self._session_factory()
        try:
            repo = SqlAlchemyUserRepository(session)
            user_row = await repo.create(username, password_hash)
            await session.commit()
            return user_row.to_user_info()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def login(self, username: str, password: str) -> TokenPair:
        username = username.lower().strip()
        session = self._session_factory()
        try:
            repo = SqlAlchemyUserRepository(session)
            user_row = await repo.get_by_username(username)
        finally:
            await session.close()
        if not user_row:
            raise AuthenticationError("用户名或密码错误")

        if not self._verify_password(password, user_row.password_hash):
            raise AuthenticationError("用户名或密码错误")

        return self._create_token(user_row.id, user_row.username)

    async def verify_token(self, token: str) -> UserInfo:
        payload = self._decode_token(token, "access")
        username = payload.get("username", "").lower()
        session = self._session_factory()
        try:
            repo = SqlAlchemyUserRepository(session)
            user_row = await repo.get_by_username(username)
        finally:
            await session.close()
        if not user_row:
            raise AuthenticationError("用户不存在")
        return user_row.to_user_info()

    async def refresh_token(self, refresh_token: str) -> TokenPair:
        payload = self._decode_token(refresh_token, "refresh")
        user_id = payload["sub"]
        session = self._session_factory()
        try:
            repo = SqlAlchemyUserRepository(session)
            user_row = await repo.get_by_id(user_id)
        finally:
            await session.close()
        if not user_row:
            raise AuthenticationError("用户不存在")
        return self._create_token(user_row.id, user_row.username)