from __future__ import annotations

from voice_agent.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name!r} is already registered")
        self._tools[tool.name] = tool

    def schemas(self) -> list[dict[str, object]]:
        return [tool.as_openai_schema() for tool in self._tools.values()]

    async def execute(self, name: str, arguments: dict[str, object]) -> object:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Unknown tool: {name}")
        return await tool.handler(arguments)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
