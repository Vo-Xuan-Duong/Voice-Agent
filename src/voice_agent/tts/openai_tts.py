from __future__ import annotations

from openai import AsyncOpenAI


class OpenAITextToSpeech:
    def __init__(self, client: AsyncOpenAI, model: str, voice: str) -> None:
        self._client = client
        self._model = model
        self._voice = voice

    async def synthesize(self, text: str) -> bytes:
        response = await self._client.audio.speech.create(
            model=self._model,
            voice=self._voice,
            input=text,
            response_format="wav",
            instructions=(
                "Speak naturally and conversationally. Match the language of the text. "
                "Use a warm, clear pace suitable for a desktop voice assistant."
            ),
        )
        return response.read()
