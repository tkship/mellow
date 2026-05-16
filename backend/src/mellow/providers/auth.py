"""认证 (Auth) 抽象接口。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class UserInfo:
    """用户信息。"""
    id: str
    username: str
    is_active: bool = True


@dataclass
class TokenPair:
    """Token 对。"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400


class AuthProvider(ABC):
    """认证提供者抽象接口。"""

    @abstractmethod
    async def register(self, username: str, password: str) -> UserInfo:
        """用户注册。"""
        ...

    @abstractmethod
    async def login(self, username: str, password: str) -> TokenPair:
        """用户登录，返回 Token 对。"""
        ...

    @abstractmethod
    async def verify_token(self, token: str) -> UserInfo:
        """验证 access token，返回用户信息。"""
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """刷新 access token。"""
        ...
