"""SQLAlchemy async 引擎和 session 工厂。"""

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from mellow.config import Settings


def get_engine(settings: Settings) -> AsyncEngine:
    """根据配置创建 SQLAlchemy async 引擎。

    配置 SQLite WAL 模式和线程安全参数。
    """
    # 确保数据库文件所在目录存在
    db_path = _extract_db_path(settings.database_url)
    if db_path:
        db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        connect_args={"check_same_thread": False},
    )

    # 设置 SQLite WAL 模式和外键支持
    if "sqlite" in settings.database_url:

        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """创建 async session 工厂。"""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def _extract_db_path(database_url: str) -> Path | None:
    """从 SQLite 连接字符串中提取数据库文件路径。

    例如: "sqlite+aiosqlite:///./data/mellow.db" -> Path("./data/mellow.db")
    """
    if "sqlite" not in database_url:
        return None

    # 格式: sqlite+aiosqlite:///./data/mellow.db
    # 或: sqlite:///./data/mellow.db
    # 去掉 scheme 部分，提取路径
    after_scheme = database_url.split(":///", 2)
    if len(after_scheme) < 2:
        return None

    path_str = after_scheme[1]
    if not path_str:
        return None

    return Path(path_str)