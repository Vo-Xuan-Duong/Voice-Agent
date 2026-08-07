import pytest

from voice_agent.tools.base import Tool
from voice_agent.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_registry_executes_registered_tool() -> None:
    async def echo(arguments: dict[str, object]) -> object:
        return arguments["value"]
    registry = ToolRegistry()
    registry.register(Tool(
        name="echo",
        description="Echo a value",
        parameters={"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"], "additionalProperties": False},
        handler=echo,
    ))
    assert await registry.execute("echo", {"value": "hello"}) == "hello"
    assert registry.schemas()[0]["name"] == "echo"


def test_registry_rejects_duplicate_names() -> None:
    async def noop(arguments: dict[str, object]) -> object:
        return arguments
    tool = Tool(name="same", description="test", parameters={"type": "object", "properties": {}, "additionalProperties": False}, handler=noop)
    registry = ToolRegistry()
    registry.register(tool)
    with pytest.raises(ValueError):
        registry.register(tool)
