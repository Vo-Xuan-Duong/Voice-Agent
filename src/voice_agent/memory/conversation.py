from __future__ import annotations

from collections import deque

from voice_agent.domain.message import Message


class ConversationMemory:
    """Bounded in-memory conversation history."""

    def __init__(self, max_turns: int = 12) -> None:
        if max_turns <= 0:
            raise ValueError("max_turns must be greater than zero")
        self._messages: deque[Message] = deque(maxlen=max_turns * 2)

    def add_user(self, content: str) -> None:
        content = content.strip()
        if content:
            self._messages.append(Message(role="user", content=content))

    def add_assistant(self, content: str) -> None:
        content = content.strip()
        if content:
            self._messages.append(Message(role="assistant", content=content))

    def snapshot(self) -> list[Message]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)
