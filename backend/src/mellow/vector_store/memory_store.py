"""对话记忆向量存储 —— LanceDB CRUD。

外部 Embedding API 生成向量 → 手动插入 → 向量检索。
"""

import uuid
import time
from typing import Any

from mellow.providers.embedding import EmbeddingProvider
from mellow.vector_store.connection import LanceDBConnector
from mellow.vector_store.schemas import ConversationMemoryRow


TABLE_NAME = "conversation_memories"


class MemoryVectorStore:
    """对话记忆向量存储。

    用法:
        store = MemoryVectorStore(embedding_provider)
        await store.insert("user_1", "persona_1", "Hello!", role="user")
        results = await store.search("How are you?", user_id="user_1", top_k=5)
    """

    def __init__(self, embedding: EmbeddingProvider):
        self._embedding = embedding
        self._connector = LanceDBConnector()
        self._initialized = False

    async def _ensure_table(self):
        if not self._initialized:
            await self._connector.create_table_if_not_exists(
                TABLE_NAME,
                schema=ConversationMemoryRow,
            )
            self._initialized = True

    async def insert(
        self,
        user_id: str,
        persona_id: str,
        content: str,
        role: str = "user",
        session_id: str = "",
        message_type: str = "text",
    ) -> str:
        """插入一条对话记忆。

        Returns:
            memory_id
        """
        await self._ensure_table()

        vector = await self._embedding.embed_query(content)
        memory_id = str(uuid.uuid4())[:12]

        row = ConversationMemoryRow(
            memory_id=memory_id,
            session_id=session_id or str(uuid.uuid4())[:8],
            user_id=user_id,
            persona_id=persona_id,
            role=role,
            content=content,
            timestamp=time.time(),
            message_type=message_type,
            vector=vector,
        )

        table = await self._connector.get_table(TABLE_NAME)
        await table.add([row.model_dump()])
        return memory_id

    async def search(
        self,
        query: str,
        user_id: str | None = None,
        persona_id: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """向量语义检索对话记忆。"""
        await self._ensure_table()

        query_vector = await self._embedding.embed_query(query)
        table = await self._connector.get_table(TABLE_NAME)

        builder = table.search(query_vector).select(
            ["memory_id", "content", "role", "timestamp", "message_type"]
        ).limit(top_k)

        if user_id:
            builder = builder.where(f"user_id = '{user_id}'")
        if persona_id:
            builder = builder.where(f"persona_id = '{persona_id}'")

        results = await builder.to_list()
        return results

    async def get_recent(
        self,
        user_id: str,
        persona_id: str,
        limit: int = 20,
        days: int = 7,
    ) -> list[dict[str, Any]]:
        """获取最近的对话记录（按时间排序）。"""
        await self._ensure_table()

        cutoff = time.time() - (days * 86400)
        table = await self._connector.get_table(TABLE_NAME)

        results = await (
            table.search([0.0] * self._embedding.dimension)  # dummy vector for filtering
            .select(["memory_id", "content", "role", "timestamp"])
            .where(f"user_id = '{user_id}' AND persona_id = '{persona_id}' AND timestamp >= {cutoff}")
            .limit(limit)
            .to_list()
        )
        return results
