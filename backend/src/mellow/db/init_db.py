"""数据库初始化 —— 自动建表。"""

from sqlalchemy.ext.asyncio import AsyncEngine

from mellow.db.base import Base


async def init_db(engine: AsyncEngine) -> None:
    """初始化数据库：创建所有已注册的表。

    在 FastAPI lifespan 启动时调用。
    仅创建不存在的表，不会修改已有表结构。
    """
    # 确保所有模型已导入，以便注册到 Base.metadata
    import mellow.db.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)