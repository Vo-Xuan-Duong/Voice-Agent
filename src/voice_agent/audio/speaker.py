from __future__ import annotations

import asyncio
import io
import wave

import numpy as np


class WavSpeaker:
    async def play(self, wav_bytes: bytes) -> None:
        await asyncio.to_thread(self._play_blocking, wav_bytes)

    @staticmethod
    def _play_blocking(wav_bytes: bytes) -> None:
        try:
            import sounddevice as sd
        except Exception as exc:
            raise RuntimeError("Audio output is unavailable. Install PortAudio/sounddevice or use --text.") from exc

        with wave.open(io.BytesIO(wav_bytes), "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            sample_rate = wav.getframerate()
            frames = wav.readframes(wav.getnframes())

        if sample_width != 2:
            raise RuntimeError(f"Unsupported WAV sample width: {sample_width}. Expected 16-bit PCM.")

        audio = np.frombuffer(frames, dtype=np.int16)
        if channels > 1:
            audio = audio.reshape(-1, channels)

        try:
            sd.play(audio, samplerate=sample_rate)
            sd.wait()
        except Exception as exc:
            raise RuntimeError(f"Could not play audio: {exc}") from exc
