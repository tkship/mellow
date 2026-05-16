"""API 依赖注入 —— FastAPI Depends 工具函数。"""

from fastapi import Depends

from mellow.auth.jwt_auth import JWTAuthProvider
from mellow.auth.middleware import get_auth_provider, get_current_user
from mellow.di import Container, get_container

__all__ = [
    "get_container",
    "get_current_user",
    "get_auth_provider",
]
