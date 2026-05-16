"""认证模块测试。"""

import pytest
from mellow.auth.jwt_auth import JWTAuthProvider
from mellow.config import Settings
from mellow.exceptions import AuthenticationError


@pytest.fixture
def auth_provider():
    settings = Settings(jwt_secret="test-secret", jwt_expire_minutes=60)
    return JWTAuthProvider(settings)


@pytest.mark.asyncio
async def test_register_and_login(auth_provider):
    user = await auth_provider.register("testuser", "password123")
    assert user.username == "testuser"
    assert user.id

    token = await auth_provider.login("testuser", "password123")
    assert token.access_token
    assert token.refresh_token


@pytest.mark.asyncio
async def test_login_wrong_password(auth_provider):
    await auth_provider.register("testuser", "correct")
    with pytest.raises(AuthenticationError):
        await auth_provider.login("testuser", "wrong")


@pytest.mark.asyncio
async def test_verify_token(auth_provider):
    await auth_provider.register("testuser", "pass")
    token = await auth_provider.login("testuser", "pass")
    user = await auth_provider.verify_token(token.access_token)
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_duplicate_register(auth_provider):
    await auth_provider.register("testuser", "pass")
    with pytest.raises(AuthenticationError):
        await auth_provider.register("testuser", "pass2")
