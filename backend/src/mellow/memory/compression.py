"""对话压缩器 —— 用 LLM 将长对话总结为简短摘要。

当对话轮次超过阈值时触发压缩，保留关键信息。
"""

from mellow.llm.client import LLMProvider
from mellow.models import Message, MessageRole


COMPRESSION_PROMPT = """请将以下对话历史总结为一段简短的关系摘要。保留：
1. 用户的英语水平和学习进展
2. 用户表达的情绪和重要事件
3. 用户提到的个人信息（兴趣、经历等）
4. 教学中的关键节点

忽略日常寒暄。用中文。"""


class ConversationCompressor:
    """对话压缩器。

    用法:
        compressor = ConversationCompressor(llm)
        summary = await compressor.compress(messages)
    """

    def __init__(self, llm: LLMProvider):
        self._llm = llm

    async def compress(
        self,
        messages: list[Message],
        existing_summary: str = "",
    ) -> str:
        """将对话消息列表压缩为一段摘要。

        Args:
            messages: 待压缩的对话消息。
            existing_summary: 已有的摘要，会拼接到 prompt 中。

        Returns:
            压缩后的摘要文本。
        """
        if not messages:
            return existing_summary

        # 构建压缩请求
        conversation_text = "\n".join(
            f"[{m.role.value}]: {m.content[:200]}" for m in messages[-20:]
        )

        system_msg = COMPRESSION_PROMPT
        if existing_summary:
            system_msg += f"\n\n之前的摘要：{existing_summary}"

        compress_messages = [
            Message(role=MessageRole.SYSTEM, content=system_msg),
            Message(role=MessageRole.USER, content=conversation_text),
        ]

        try:
            summary = await self._llm.chat(
                compress_messages,
                temperature=0.2,
                max_tokens=512,
            )
            return summary.strip()
        except Exception:
            # 压缩失败不阻塞主流程
            return existing_summary

    async def extract_key_facts(self, messages: list[Message]) -> list[str]:
        """从对话中提取关键事实。"""
        if not messages:
            return []

        conversation_text = "\n".join(
            f"[{m.role.value}]: {m.content[:200]}" for m in messages[-10:]
        )

        compress_messages = [
            Message(
                role=MessageRole.SYSTEM,
                content="从对话中提取用户透露的关键个人信息。每行一条。只返回事实，不要解释。",
            ),
            Message(role=MessageRole.USER, content=conversation_text),
        ]

        try:
            response = await self._llm.chat(compress_messages, temperature=0.1, max_tokens=256)
            return [line.strip("- ").strip() for line in response.strip().split("\n") if line.strip()]
        except Exception:
            return []
