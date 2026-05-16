"""LLM 客户端抽象层 —— 统一接口 + OpenAI 兼容实现。"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI

from mellow.config import Settings
from mellow.models import Message


class LLMProvider(ABC):
    """LLM 提供商抽象接口。

    所有 LLM 调用必须通过此接口，支持可拔插替换。
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        """同步聊天 —— 返回完整回复文本。"""
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """流式聊天 —— 逐个 token 返回。"""
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        """默认模型名称。"""
        ...


class OpenAIProvider(LLMProvider):
    """OpenAI 兼容 LLM 实现。

    支持任何兼容 OpenAI API 的提供商：
    OpenAI / DeepSeek / Qwen / DashScope / SiliconFlow 等。
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self._client = AsyncOpenAI(
            api_key=self._settings.llm_api_key,
            base_url=self._settings.llm_base_url,
        )
        self._default_model = self._settings.llm_model

    @property
    def default_model(self) -> str:
        return self._default_model

    def _to_openai_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        return [m.to_openai_format() for m in messages]

    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        response = await self._client.chat.completions.create(
            model=model or self._default_model,
            messages=self._to_openai_messages(messages),
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def chat_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=model or self._default_model,
            messages=self._to_openai_messages(messages),
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
