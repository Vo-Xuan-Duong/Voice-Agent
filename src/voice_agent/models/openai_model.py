from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from voice_agent.domain.message import Message
from voice_agent.tools.registry import ToolRegistry


class OpenAIResponsesModel:
    def __init__(self, client: AsyncOpenAI, model: str, instructions: str) -> None:
        self._client = client
        self._model = model
        self._instructions = instructions

    async def respond(self, messages: list[Message], tools: ToolRegistry, max_tool_rounds: int) -> str:
        if max_tool_rounds <= 0:
            raise ValueError("max_tool_rounds must be greater than zero")

        response = await self._client.responses.create(
            model=self._model,
            instructions=self._instructions,
            input=[{"role": m.role, "content": m.content} for m in messages],
            tools=tools.schemas(),
        )

        for _ in range(max_tool_rounds):
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                text = (response.output_text or "").strip()
                if not text:
                    raise RuntimeError("The model returned no text response.")
                return text

            outputs: list[dict[str, str]] = []
            for call in calls:
                arguments = _parse_arguments(call.arguments)
                try:
                    result = await tools.execute(call.name, arguments)
                    payload = {"ok": True, "result": result}
                except Exception as exc:
                    payload = {"ok": False, "error": str(exc)}

                outputs.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(payload, ensure_ascii=False, default=str),
                })

            response = await self._client.responses.create(
                model=self._model,
                instructions=self._instructions,
                previous_response_id=response.id,
                input=outputs,
                tools=tools.schemas(),
            )

        raise RuntimeError(f"Tool loop exceeded the configured limit of {max_tool_rounds} rounds.")


def _parse_arguments(raw: str) -> dict[str, object]:
    try:
        value: Any = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Tool arguments were not valid JSON: {raw!r}") from exc
    if not isinstance(value, dict):
        raise ValueError("Tool arguments must be a JSON object")
    return value
