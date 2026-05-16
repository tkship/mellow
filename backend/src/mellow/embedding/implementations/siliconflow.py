"""SiliconFlow (硅基流动) Embedding 实现。

模型: Qwen3-Embedding-4B (推荐)
API: OpenAI 兼容格式
文档: https://docs.siliconflow.cn/
"""

import httpx

from mellow.config import Settings
from mellow.providers.embedding import EmbeddingProvider


class SiliconFlowEmbeddingProvider(EmbeddingProvider):
    """硅基流动 Embedding 服务。

    推荐模型：
    - Qwen3-Embedding-4B: $0.02/M, 2560 dims, MTEB 69.45
    - Qwen3-Embedding-8B: $0.04/M, 4096 dims, MTEB 70.58
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self._api_key = self._settings.embed_api_key
        self._base_url = "https://api.siliconflow.cn/v1"
        self._model = self._settings.embed_model or "Qwen/Qwen3-Embedding-4B"
        self._dimension = self._settings.embed_dimension or 2560
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
            },
        )
        response.raise_for_status()
        data = response.json()
        items = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in items]

    async def close(self):
        await self._client.aclose()
