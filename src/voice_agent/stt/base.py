from __future__ import annotations

from typing import Protocol


class SpeechToText(Protocol):
    async def transcribe(self, wav_bytes: bytes) -> str:
        """Convert WAV bytes into text."""
        ...
