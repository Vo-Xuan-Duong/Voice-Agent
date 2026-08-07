from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    openai_api_key: str
    chat_model: str = "gpt-5-mini"
    stt_model: str = "gpt-4o-mini-transcribe"
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "marin"
    language: str = "vi"
    sample_rate: int = 16_000
    channels: int = 1
    max_history_turns: int = 12
    max_tool_rounds: int = 4

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            chat_model=os.getenv("VOICE_AGENT_CHAT_MODEL", "gpt-5-mini").strip(),
            stt_model=os.getenv("VOICE_AGENT_STT_MODEL", "gpt-4o-mini-transcribe").strip(),
            tts_model=os.getenv("VOICE_AGENT_TTS_MODEL", "gpt-4o-mini-tts").strip(),
            tts_voice=os.getenv("VOICE_AGENT_TTS_VOICE", "marin").strip(),
            language=os.getenv("VOICE_AGENT_LANGUAGE", "vi").strip(),
            sample_rate=_int_env("VOICE_AGENT_SAMPLE_RATE", 16_000),
            channels=_int_env("VOICE_AGENT_CHANNELS", 1),
            max_history_turns=_int_env("VOICE_AGENT_MAX_HISTORY_TURNS", 12),
            max_tool_rounds=_int_env("VOICE_AGENT_MAX_TOOL_ROUNDS", 4),
        )

    def validate_for_openai(self) -> None:
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is missing. Copy .env.example to .env and set your key.")


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value
