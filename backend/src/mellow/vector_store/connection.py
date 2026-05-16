"""LanceDB 连接管理器 —— Singleton 模式。

参考：lancedb>=0.25.0 推荐 Singleton，避免 context manager 内存泄漏。
"""

import lancedb
from lancedb.db import AsyncConnection, AsyncTable

from mellow.config import Settings, get_settings


class LanceDBConnector:
    """LanceDB 连接单例。

    用法:
        connector = LanceDBConnector()
        table = await connector.get_table("conversation_memories")
    """

    _instance: "LanceDBConnector | None" = None
    _conn: AsyncConnection | None = None
    _tables: dict[str, AsyncTable] = {}

    def __new__(cls, settings: Settings | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = settings or get_settings()
        return cls._instance

    async def get_connection(self) -> AsyncConnection:
        if self._conn is None:
            path = str(self._settings.lancedb_path)
            self._conn = await lancedb.connect_async(path)
        return self._conn

    async def get_table(self, name: str) -> AsyncTable:
        if name not in self._tables:
            conn = await self.get_connection()
            self._tables[name] = await conn.open_table(name)
        return self._tables[name]

    async def create_table_if_not_exists(self, name: str, schema):
        """创建表（如不存在）。"""
        conn = await self.get_connection()
        try:
            table = await conn.open_table(name)
            self._tables[name] = table
        except Exception:
            table = await conn.create_table(name, schema=schema)
            self._tables[name] = table
        return table

    async def close(self):
        for table in self._tables.values():
            table.close()
        self._tables.clear()
        if self._conn:
            self._conn.close()
            self._conn = None
