from __future__ import annotations

import io

from openai import AsyncOpenAI


class OpenAISpeechToText:
    def __init__(self, client: AsyncOpenAI, model: str, language: str | None = None) -> None:
        self._client = client
        self._model = model
        self._language = language or None

    async def transcribe(self, wav_bytes: bytes) -> str:
        audio_file = io.BytesIO(wav_bytes)
        audio_file.name = "speech.wav"
        kwargs: dict[str, object] = {"model": self._model, "file": audio_file}
        if self._language:
            kwargs["language"] = self._language
        result = await self._client.audio.transcriptions.create(**kwargs)
        return (result.text or "").strip()
