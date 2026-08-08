from __future__ import annotations

import asyncio

from voice_agent.audio.microphone import PushToTalkMicrophone
from voice_agent.stt.base import SpeechToText


class SpeechRecognitionRunner:
    """Minimal microphone -> speech-to-text loop with no LLM or TTS."""

    def __init__(self, microphone: PushToTalkMicrophone, stt: SpeechToText) -> None:
        self._microphone = microphone
        self._stt = stt

    async def run(self) -> None:
        print("Speech-to-Text mode")
        print("No LLM and no TTS are used in this mode.")
        print("Press Ctrl+C to exit.\n")

        while True:
            await asyncio.to_thread(input, "Press Enter to start recording...")
            wav_bytes = await self._microphone.capture_wav()

            print("Transcribing...")
            text = await self._stt.transcribe(wav_bytes)
            if text:
                print(f"You: {text}\n")
            else:
                print("No speech was recognized.\n")
