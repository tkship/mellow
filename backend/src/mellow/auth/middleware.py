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
    return await container.auth()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth: JWTAuthProvider = Depends(get_auth_provider),
) -> UserInfo:
    """从请求中提取 JWT Token 并返回当前用户。

    优先级：Authorization Header > query param `token`（SSE/WebSocket 用）

    Raises:
        AuthenticationError: Token 缺失或无效。
    """
    # 优先 Bearer header
    if credentials is not None:
        return await auth.verify_token(credentials.credentials)

    # 降级：query string token（浏览器 SSE EventSource 不支持自定义 header）
    token = request.query_params.get("token")
    if token:
        return await auth.verify_token(token)

    raise AuthenticationError("未提供认证 Token")


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
