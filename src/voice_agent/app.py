from __future__ import annotations

from dataclasses import dataclass

from voice_agent.agent.runtime import AgentRuntime
from voice_agent.audio.microphone import PushToTalkMicrophone
from voice_agent.audio.speaker import WavSpeaker
from voice_agent.stt.base import SpeechToText
from voice_agent.tts.base import TextToSpeech

EXIT_PHRASES = {"exit", "quit", "thoát", "thoát đi", "dừng", "dừng lại", "kết thúc"}


@dataclass(slots=True)
class VoiceApplication:
    agent: AgentRuntime
    stt: SpeechToText
    tts: TextToSpeech
    microphone: PushToTalkMicrophone
    speaker: WavSpeaker

    async def run_voice(self) -> None:
        print("Voice Agent v0.1")
        print("Press Enter to begin a turn. Say 'thoát' or press Ctrl+C to stop.\n")
        while True:
            await _wait_for_enter("[Enter] Start speaking...")
            wav_bytes = await self.microphone.capture_wav()
            transcript = (await self.stt.transcribe(wav_bytes)).strip()
            if not transcript:
                print("I could not hear any speech. Try again.\n")
                continue
            print(f"You: {transcript}")
            if _is_exit(transcript):
                print("Agent: Hẹn gặp lại.")
                return
            answer = await self.agent.handle_text(transcript)
            print(f"Agent: {answer}\n")
            wav = await self.tts.synthesize(answer)
            await self.speaker.play(wav)

    async def run_text(self) -> None:
        print("Voice Agent v0.1 — text development mode")
        print("Type 'exit' or 'thoát' to stop.\n")
        while True:
            user_text = (await _read_line("You: ")).strip()
            if not user_text:
                continue
            if _is_exit(user_text):
                print("Agent: Hẹn gặp lại.")
                return
            answer = await self.agent.handle_text(user_text)
            print(f"Agent: {answer}\n")


def _is_exit(text: str) -> bool:
    return text.casefold().strip(" .!?") in EXIT_PHRASES


async def _wait_for_enter(prompt: str) -> None:
    await _read_line(prompt)


async def _read_line(prompt: str) -> str:
    import asyncio
    return await asyncio.to_thread(input, prompt)
