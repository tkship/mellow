"""ChatAgent —— 角色扮演对话。

SimpleAgent 范式：注入角色 system prompt + 记忆上下文，直接对话。
"""

from collections.abc import AsyncIterator

from mellow.agent.base import AgentContext, AgentResponse, BaseAgent
from mellow.agent.tool_registry import ToolRegistry
from mellow.llm.client import LLMProvider
from mellow.models import Message


class ChatAgent(BaseAgent):
    """角色扮演对话 Agent。

    核心能力：
    - 注入角色 system prompt（从 Persona 渲染）
    - 注入角色记忆（关系摘要 + 情感状态）
    - 流式输出自然对话
    """

    def __init__(
        self,
        llm: LLMProvider,
        tools: ToolRegistry | None = None,
    ):
        super().__init__(llm, name="chat")
        self.tools = tools or ToolRegistry()

    async def run(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AgentResponse:
        messages = self._build_messages(user_input, context, history)

        response = await self.llm.chat(messages, temperature=0.8, max_tokens=1024)

        # 检查是否需要工具调用
        tool_call = ToolRegistry.parse_tool_call(response)
        if tool_call:
            name, params = tool_call
            result = await self.tools.execute(name, **params)
            response = f"{response}\n\n[工具结果] {result}"

        return AgentResponse(
            content=response,
            intent="chat",
            metadata={"agent": self.name, "persona": context.persona_name},
        )

    async def run_stream(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AsyncIterator[str]:
        messages = self._build_messages(user_input, context, history)

        async for token in self.llm.chat_stream(
            messages, temperature=0.8, max_tokens=1024
        ):
            yield token
