"""Embedding 抽象接口。"""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """向量嵌入提供者抽象接口。

    所有 embedding 调用必须通过此接口。
    """

    @abstractmethod
    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        """批量生成嵌入向量。

        Args:
            texts: 待嵌入的文本列表。
            model: 可选模型覆盖。

        Returns:
            向量列表，每个向量长度为 self.dimension。
        """
        ...

    async def embed_query(self, text: str, model: str | None = None) -> list[float]:
        """单条查询嵌入 —— 默认复用 embed()。"""
        results = await self.embed([text], model=model)
        return results[0]

    @property
    @abstractmethod
    def dimension(self) -> int:
        """当前嵌入维度。"""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """当前模型名称。"""
        ...
