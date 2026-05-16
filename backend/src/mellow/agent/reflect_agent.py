"""ReflectAgent —— 纠错与反思 Agent。

Reflection 范式:
  检测错误 → 分析原因 → 给出纠正 + 学习建议
"""

from collections.abc import AsyncIterator

from mellow.agent.base import AgentContext, AgentResponse, BaseAgent
from mellow.agent.tool_registry import ToolRegistry
from mellow.llm.client import LLMProvider
from mellow.models import Message


REFLECT_SYSTEM_PROMPT = """你是一个英语纠错专家。你的任务是：
1. 识别用户英语中的错误（语法、用词、发音相关）
2. 用友善的方式指出错误
3. 解释为什么错了，给出正确用法
4. 提供 1-2 个例句帮助巩固
5. 记录这个错误类型，用于后续学习计划调整

注意：
- 不要一次纠正太多错误，优先纠正最重要/最频繁的
- 纠错后给予鼓励，不要打击学习信心
- 如果用户的表达基本正确，不要强行找错"""


class ReflectAgent(BaseAgent):
    """纠错反思 Agent。"""

    def __init__(
        self,
        llm: LLMProvider,
        tools: ToolRegistry | None = None,
    ):
        super().__init__(llm, name="reflect")
        self.tools = tools or ToolRegistry()

    async def run(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AgentResponse:
        context.system_prompt = REFLECT_SYSTEM_PROMPT
        messages = self._build_messages(user_input, context, history)

        response = await self.llm.chat(
            messages,
            temperature=0.4,
            max_tokens=1024,
        )

        return AgentResponse(
            content=response,
            intent="reflect",
            metadata={
                "agent": self.name,
                "mistake_type": "auto_detected",
            },
        )

    async def run_stream(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AsyncIterator[str]:
        context.system_prompt = REFLECT_SYSTEM_PROMPT
        messages = self._build_messages(user_input, context, history)

        async for token in self.llm.chat_stream(
            messages,
            temperature=0.4,
            max_tokens=1024,
        ):
            yield token
