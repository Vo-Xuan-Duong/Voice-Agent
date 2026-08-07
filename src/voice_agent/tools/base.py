from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

ToolHandler = Callable[[dict[str, object]], Awaitable[object]]


@dataclass(frozen=True, slots=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, object]
    handler: ToolHandler

    def as_openai_schema(self) -> dict[str, object]:
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "strict": True,
        }
