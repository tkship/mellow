""""""

from mellow.config import Settings
from mellow.llm.client import LLMProvider, OpenAIProvider


class LLMRouter:
    """LLM 混合路由器。

    根据任务类型自动选择模型：
    - 教学/计划/推理 → 强模型 (llm_model)
    - 闲聊/轻量 → 快速模型 (llm_fast_model)
    """

    def __init__(
        self,
        settings: Settings | None = None,
        provider: LLMProvider | None = None,
    ):
        self._settings = settings or Settings()
        self._provider = provider or OpenAIProvider(self._settings)
        self._strong_model = self._settings.llm_model
        self._fast_model = self._settings.llm_fast_model

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    def resolve_model(self, intent: str) -> str:
        """根据意图选择模型。

        Args:
            intent: 意图类型 —— "teach" | "reflect" | "chat" | "lookup"

        Returns:
            模型名称。
        """
        if intent in ("teach", "reflect"):
            return self._strong_model
        return self._fast_model

    async def route_chat(
        self,
        messages: list,
        intent: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """路由到合适的模型进行对话。"""
        model = self.resolve_model(intent)
        return await self._provider.chat(
            messages, model=model, temperature=temperature, max_tokens=max_tokens
        )

    async def route_stream(
        self,
        messages: list,
        intent: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """路由到合适的模型进行流式对话。"""
        model = self.resolve_model(intent)
        async for token in self._provider.chat_stream(
            messages, model=model, temperature=temperature, max_tokens=max_tokens
        ):
            yield token
