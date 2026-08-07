from __future__ import annotations

from datetime import datetime

from voice_agent.tools.base import Tool
from voice_agent.tools.registry import ToolRegistry


async def _get_current_time(arguments: dict[str, object]) -> dict[str, str]:
    del arguments
    now = datetime.now().astimezone()
    return {"iso": now.isoformat(timespec="seconds"), "timezone": str(now.tzinfo)}


def register_builtin_tools(registry: ToolRegistry) -> None:
    registry.register(
        Tool(
            name="get_current_time",
            description="Get the current local date, time and timezone from the computer.",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
            handler=_get_current_time,
        )
    )
