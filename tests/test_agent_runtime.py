import pytest

from voice_agent.agent.runtime import AgentRuntime
from voice_agent.memory.conversation import ConversationMemory
from voice_agent.tools.registry import ToolRegistry


class FakeModel:
    async def respond(self, messages, tools, max_tool_rounds):
        del tools, max_tool_rounds
        return f"echo:{messages[-1].content}"


@pytest.mark.asyncio
async def test_agent_runtime_updates_memory() -> None:
    memory = ConversationMemory(max_turns=2)
    runtime = AgentRuntime(model=FakeModel(), memory=memory, tools=ToolRegistry())
    answer = await runtime.handle_text("hello")
    assert answer == "echo:hello"
    assert [(m.role, m.content) for m in memory.snapshot()] == [("user", "hello"), ("assistant", "echo:hello")]


@pytest.mark.asyncio
async def test_agent_runtime_rejects_blank_input() -> None:
    runtime = AgentRuntime(model=FakeModel(), memory=ConversationMemory(), tools=ToolRegistry())
    with pytest.raises(ValueError):
        await runtime.handle_text("  ")
