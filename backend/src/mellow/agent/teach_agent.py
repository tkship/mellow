"""TeachAgent —— 英语教学 Plan & Solve Agent。

Plan & Solve 范式:
  Planner: 分析用户画像 → 确定学习主题 → 生成学习计划
  Executor: 逐步骤执行教学 → 嵌入练习 → 记录进度
"""

from collections.abc import AsyncIterator

from mellow.agent.base import AgentContext, AgentResponse, BaseAgent
from mellow.agent.tool_registry import ToolRegistry
from mellow.llm.client import LLMProvider
from mellow.models import Message


TEACH_SYSTEM_PROMPT = """你是一个专业的英语教师。根据用户的学习情况，制定个性化教学计划。

教学原则：
1. 基于用户当前水平（CEFR 等级）选择合适的难度
2. 避免重复教授用户已掌握的单词和语法
3. 每次教学包含：新知识点 → 例句 → 互动练习 → 纠错反馈
4. 使用鼓励性语言，保持学习动力
5. 教学内容的单词释义必须从知识库验证，确保准确

输出格式：
当制定学习计划时，用以下 JSON 格式：
{{
  "plan": {{
    "week": <第几周>,
    "theme": "<主题>",
    "days": [
      {{
        "day": 1,
        "topic": "<当日主题>",
        "vocabulary": ["word1", "word2"],
        "grammar_point": "<语法点>",
        "practice": "<练习内容>"
      }}
    ]
  }}
}}"""


class TeachAgent(BaseAgent):
    """教学 Agent —— 计划制定 + 分步教学。"""

    def __init__(
        self,
        llm: LLMProvider,
        tools: ToolRegistry | None = None,
    ):
        super().__init__(llm, name="teach")
        self.tools = tools or ToolRegistry()

    async def run(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AgentResponse:
        # 注入教学 system prompt
        context.system_prompt = TEACH_SYSTEM_PROMPT + "\n\n" + context.extra.get("profile_summary", "")
        messages = self._build_messages(user_input, context, history)

        response = await self.llm.chat(
            messages,
            model=None,  # 使用路由器选择的强模型
            temperature=0.4,
            max_tokens=2048,
        )

        # Record vocabulary exposure for learning tracking
        try:
            import json as _json, re as _re
            json_match = _re.search(r'\{.*"vocabulary".*\}', response, _re.DOTALL)
            if json_match:
                plan_data = _json.loads(json_match.group())
                words: list[str] = plan_data.get("plan", {}).get("vocabulary", []) or []
                for day in plan_data.get("plan", {}).get("days", []):
                    words.extend(day.get("vocabulary", []))
                for word in set(words):
                    from mellow.di import Container
                    pm = await Container.instance().profile_manager()
                    await pm.record_word_mastery(context.user_id, word, 0.3)
        except Exception:
            pass  # Best effort — don't break teaching flow

        return AgentResponse(
            content=response,
            intent="teach",
            metadata={"agent": self.name},
        )

    async def run_stream(
        self,
        user_input: str,
        context: AgentContext,
        history: list[Message] | None = None,
    ) -> AsyncIterator[str]:
        context.system_prompt = TEACH_SYSTEM_PROMPT + "\n\n" + context.extra.get("profile_summary", "")
        messages = self._build_messages(user_input, context, history)

        async for token in self.llm.chat_stream(
            messages,
            model=None,
            temperature=0.4,
            max_tokens=2048,
        ):
            yield token
