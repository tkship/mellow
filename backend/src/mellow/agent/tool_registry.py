"""工具注册中心 —— 参考 hello-agents-src ToolRegistry 模式。

工具通过名称注册，支持函数和对象两种形式。
Agent 通过 [TOOL_CALL:name:params] 文本协议调用工具。
"""

import json
from collections.abc import Callable
from typing import Any


class Tool:
    """工具定义。"""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: dict[str, Any] | None = None,
    ):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or {}

    async def execute(self, **kwargs) -> str:
        """执行工具，返回字符串结果。"""
        result = self.func(**kwargs)
        if hasattr(result, "__await__"):
            result = await result
        return str(result)


class ToolRegistry:
    """工具注册中心。

    用法:
        registry = ToolRegistry()
        registry.register(Tool("search", "搜索", search_func))
        result = await registry.execute("search", query="hello")
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def register_function(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: dict[str, Any] | None = None,
    ) -> Tool:
        tool = Tool(name, description, func, parameters)
        self._tools[name] = tool
        return tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def get_tools_description(self) -> str:
        """生成工具描述 —— 注入 Agent system prompt。"""
        if not self._tools:
            return ""

        lines = ["可用工具："]
        for name, tool in self._tools.items():
            params = json.dumps(tool.parameters, ensure_ascii=False) if tool.parameters else "无参数"
            lines.append(f"- {name}: {tool.description} | 参数: {params}")

        lines.append("使用格式: [TOOL_CALL:工具名:参数JSON]")
        return "\n".join(lines)

    async def execute(self, name: str, **kwargs) -> str:
        """执行指定工具。"""
        tool = self._tools.get(name)
        if not tool:
            return f"错误: 工具 '{name}' 不存在。可用工具: {self.list_tools()}"
        return await tool.execute(**kwargs)

    @staticmethod
    def parse_tool_call(text: str) -> tuple[str, dict[str, Any]] | None:
        """从文本中解析 [TOOL_CALL:name:params] 协议。

        Returns:
            (tool_name, params_dict) 或 None。
        """
        import re

        match = re.search(r"\[TOOL_CALL:(\w+):(.*?)\]", text)
        if not match:
            return None

        name = match.group(1)
        params_str = match.group(2).strip()

        try:
            params = json.loads(params_str)
        except json.JSONDecodeError:
            params = {"query": params_str}

        return name, params
