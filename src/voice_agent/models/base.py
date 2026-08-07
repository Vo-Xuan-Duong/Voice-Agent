from __future__ import annotations

from typing import Protocol

from voice_agent.domain.message import Message
from voice_agent.tools.registry import ToolRegistry


class ChatModel(Protocol):
    async def respond(self, messages: list[Message], tools: ToolRegistry, max_tool_rounds: int) -> str:
        """Generate a final response, executing tool calls when required."""
        ...
