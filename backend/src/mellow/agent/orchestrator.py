"""OrchestratorAgent —— 意图识别 + 路由分发。

核心流程:
    用户输入 → 意图识别 (LLM) → 路由到子 Agent → 聚合响应
"""

import asyncio
import json
import re
from collections.abc import AsyncIterator

from mellow.agent.base import AgentContext, AgentResponse, BaseAgent
from mellow.llm.router import LLMRouter
from mellow.models import Message

# 意图分类 prompt
INTENT_CLASSIFY_PROMPT = """你是一个意图分类器。分析用户输入，判断用户意图。

意图类型：
- "teach" —— 用户想学习英语、制定学习计划、问语法问题、学单词
- "reflect" —— 用户犯了错误需要纠正、用户在反思自己的学习
- "lookup" —— 用户想查一个单词的意思、用法
- "chat" —— 日常闲聊、角色互动、非学习相关

只返回 JSON 格式，不要其他文字：
{"intent": "<意图类型>", "confidence": 0.0~1.0, "reason": "<简短理由>"}"""


class OrchestratorAgent(BaseAgent):
    """编排 Agent —— 意图识别 + 子 Agent 路由。

    不直接处理用户请求，而是：
    1. 用 LLM 识别意图
    2. 路由到对应子 Agent
    3. 返回子 Agent 结果
    """

    def __init__(self, router: LLMRouter):
        super().__init__(router.provider, name="orchestrator")
        self._router = router
        self._chat_agent = None
        self._teach_agent = None
        self._reflect_agent = None

    def _set_agents(self, chat_agent, teach_agent, reflect_agent):
        """注入子 Agent（避免循环导入）。"""
        self._chat_agent = chat_agent
        self._teach_agent = teach_agent
        self._reflect_agent = reflect_agent

    async def _classify_intent(self, user_input: str, history: list[Message] | None = None) -> dict:
        """用 LLM 识别用户意图。"""
        msgs: list[Message] = []

        from mellow.models import Message, MessageRole
        msgs.append(Message(role=MessageRole.SYSTEM, content=INTENT_CLASSIFY_PROMPT))
        if history:
            # 只取最近 3 轮提供上下文
            msgs.extend(history[-6:])
        msgs.append(Message(role=MessageRole.USER, content=user_input))

        response = await self.llm.chat(
            msgs,
            model=self._router._fast_model,
            temperature=0.1,
            max_tokens=128,
        )

        try:
            # 尝试提取 JSON
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        return {"intent": "chat", "confidence": 0.5, "reason": "fallback"}

    async def run(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AgentResponse:
        intent_result = await self._classify_intent(user_input, history)
        intent = intent_result.get("intent", "chat")

        if intent == "lookup":
            # 直接查知识库，不走子 Agent
            from mellow.di import Container
            container = Container.instance()
            kb = await container.knowledge()

            # 提取可能的关键词
            words = user_input.strip().split()
            entry = await kb.lookup(words[-1].strip("?.!")) if words else None

            if entry:
                defs = "; ".join(entry.definitions[:3])
                examples = "; ".join(entry.examples[:2])
                return AgentResponse(
                    content=f"**{entry.word}** {entry.phonetic or ''}\n\n{defs}\n\n例句: {examples}",
                    intent="lookup",
                    metadata={"word": entry.word, "source": entry.source},
                )
            return AgentResponse(
                content=f"抱歉，没有找到「{user_input.strip()}」的相关信息。",
                intent="lookup",
            )

        # 路由到子 Agent
        if intent == "teach" and self._teach_agent:
            return await self._teach_agent.run(user_input, context, history)
        elif intent == "reflect" and self._reflect_agent:
            return await self._reflect_agent.run(user_input, context, history)
        elif self._chat_agent:
            return await self._chat_agent.run(user_input, context, history)

        return AgentResponse(content="系统尚未就绪。", intent="chat")

    async def run_stream(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AsyncIterator[str]:
        try:
            intent_result = await self._classify_intent(user_input, history)
            intent = intent_result.get("intent", "chat")

            if intent == "teach" and self._teach_agent:
                async for token in self._teach_agent.run_stream(user_input, context, history):
                    yield token
            elif intent == "reflect" and self._reflect_agent:
                async for token in self._reflect_agent.run_stream(user_input, context, history):
                    yield token
            elif self._chat_agent:
                async for token in self._chat_agent.run_stream(user_input, context, history):
                    yield token
            else:
                yield "系统尚未就绪。"
        except asyncio.CancelledError:
            # Client disconnected — cancellation propagates to sub-agents
            raise
