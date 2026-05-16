"""FastAPI 认证中间件。

提供 JWT 认证的 FastAPI 依赖注入。
"""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mellow.auth.jwt_auth import JWTAuthProvider
from mellow.di import Container, get_container
from mellow.exceptions import AuthenticationError
from mellow.providers.auth import UserInfo

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_auth_provider(
    container: Container = Depends(get_container),
) -> JWTAuthProvider:
    """获取认证提供者实例。"""
    return container._lazy("auth", lambda: JWTAuthProvider(container.settings))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth: JWTAuthProvider = Depends(get_auth_provider),
) -> UserInfo:
    """从请求头中提取 JWT Token 并返回当前用户。

    Raises:
        AuthenticationError: Token 缺失或无效。
    """
    if credentials is None:
        # 尝试从 query string 获取（WebSocket/Sse）
        raise AuthenticationError("未提供认证 Token")

    return await auth.verify_token(credentials.credentials)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth: JWTAuthProvider = Depends(get_auth_provider),
) -> UserInfo | None:
    """可选认证 —— Token 不存在时返回 None 而不报错。"""
    if credentials is None:
        return None
    try:
        return await auth.verify_token(credentials.credentials)
    except AuthenticationError:
        return None
