"""DashScope (阿里云百炼) Embedding 实现。

模型: text-embedding-v4
API: OpenAI 兼容格式
文档: https://help.aliyun.com/document_detail/2712193.html
"""

import httpx

from mellow.config import Settings
from mellow.providers.embedding import EmbeddingProvider


class DashScopeEmbeddingProvider(EmbeddingProvider):
    """阿里云百炼 Embedding 服务。

    支持 OpenAI 兼容格式，直接复用 openai SDK 或 httpx 调用。
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self._api_key = self._settings.embed_api_key
        self._base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self._model = self._settings.embed_model or "text-embedding-v4"
        self._dimension = self._settings.embed_dimension or 1024
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=30.0,
        )

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return self._model

    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        response = await self._client.post(
            "/embeddings",
            json={
                "model": model or self._model,
                "input": texts,
                "dimensions": self._dimension,
            },
        )
        response.raise_for_status()
        data = response.json()
        # 按 index 排序确保顺序一致
        items = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in items]

    async def close(self):
        await self._client.aclose()
