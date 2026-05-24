"""API 依赖注入 —— FastAPI Depends 工具函数。"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mellow.auth.middleware import get_auth_provider, get_current_user
from mellow.di import Container, get_container


async def get_db_session(
    container: Container = Depends(get_container),
) -> AsyncGenerator[AsyncSession, None]:
    """请求级 session — 请求结束时自动 commit/rollback/close。"""
    session = container.session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


__all__ = [
    "get_container",
    "get_current_user",
    "get_auth_provider",
    "get_db_session",
]
