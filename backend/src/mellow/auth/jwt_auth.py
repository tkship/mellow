"""JWT 认证实现。

基于 python-jose + passlib，完全自建、无外部依赖。
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from mellow.config import Settings, get_settings
from mellow.exceptions import AuthenticationError
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
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # 开发阶段内存存储
        self._users: dict[str, dict] = {}

    def _hash_password(self, password: str) -> str:
        return self._pwd_context.hash(password)

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return self._pwd_context.verify(plain, hashed)

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
        if username in self._users:
            raise AuthenticationError("用户名已存在")

        import uuid

        user_id = str(uuid.uuid4())
        self._users[username] = {
            "id": user_id,
            "username": username,
            "password_hash": self._hash_password(password),
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
