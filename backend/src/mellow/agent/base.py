"""Agent 基类 —— 所有 Agent 的共同抽象。"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from mellow.llm.client import LLMProvider
from mellow.models import Message


@dataclass
class AgentContext:
    """Agent 执行上下文 —— 聚合所有需要的外部数据。"""
    user_id: str
    persona_name: str = ""
    system_prompt: str = ""
    session_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Agent 执行结果。"""
    content: str
    intent: str = "chat"
    metadata: dict[str, Any] = field(default_factory=dict)
    messages: list[Message] = field(default_factory=list)


class BaseAgent(ABC):
    """所有 Agent 的抽象基类。

    子类必须实现 run() 和 run_stream()。
    """

    def __init__(self, llm: LLMProvider, name: str = "base"):
        self.llm = llm
        self.name = name
        self.system_prompt: str = ""

    def _build_messages(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> list[Message]:
        """构建发送给 LLM 的消息列表。"""
        messages: list[Message] = []

        if context.system_prompt:
            from mellow.models import Message, MessageRole
            messages.append(Message(role=MessageRole.SYSTEM, content=context.system_prompt))

        if history:
            messages.extend(history)

        from mellow.models import Message, MessageRole
        messages.append(Message(role=MessageRole.USER, content=user_input))
        return messages

    @abstractmethod
    async def run(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AgentResponse:
        """执行 Agent —— 同步返回完整结果。"""
        ...

    @abstractmethod
    async def run_stream(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AsyncIterator[str]:
        """执行 Agent —— 流式逐 token 返回。"""
        ...
