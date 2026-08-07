from __future__ import annotations

from typing import Protocol


class TextToSpeech(Protocol):
    async def synthesize(self, text: str) -> bytes:
        """Convert text into WAV bytes."""
        ...
