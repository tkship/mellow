"""认证路由 —— 注册 / 登录 / 刷新 Token。"""

from fastapi import APIRouter, Depends

from mellow.api.deps import get_auth_provider, get_current_user
from mellow.auth.jwt_auth import JWTAuthProvider
from mellow.auth.models import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
    req: RegisterRequest,
    auth: JWTAuthProvider = Depends(get_auth_provider),
):
    user = await auth.register(req.username, req.password)
    return UserResponse(id=user.id, username=user.username, is_active=user.is_active)


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    auth: JWTAuthProvider = Depends(get_auth_provider),
):
    token = await auth.login(req.username, req.password)
    return TokenResponse(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        token_type=token.token_type,
        expires_in=token.expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    req: RefreshRequest,
    auth: JWTAuthProvider = Depends(get_auth_provider),
):
    token = await auth.refresh_token(req.refresh_token)
    return TokenResponse(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        token_type=token.token_type,
        expires_in=token.expires_in,
    )


@router.get("/me", response_model=UserResponse)
async def me(
    user: UserInfo = Depends(get_current_user),
):
    return UserResponse(id=user.id, username=user.username, is_active=user.is_active)
