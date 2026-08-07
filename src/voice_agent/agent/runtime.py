from __future__ import annotations

from voice_agent.memory.conversation import ConversationMemory
from voice_agent.models.base import ChatModel
from voice_agent.tools.registry import ToolRegistry


class AgentRuntime:
    def __init__(self, model: ChatModel, memory: ConversationMemory, tools: ToolRegistry, max_tool_rounds: int = 4) -> None:
        self._model = model
        self._memory = memory
        self._tools = tools
        self._max_tool_rounds = max_tool_rounds

    async def handle_text(self, user_text: str) -> str:
        user_text = user_text.strip()
        if not user_text:
            raise ValueError("user_text cannot be empty")
        self._memory.add_user(user_text)
        answer = await self._model.respond(self._memory.snapshot(), self._tools, self._max_tool_rounds)
        self._memory.add_assistant(answer)
        return answer
