from __future__ import annotations

import asyncio
import io
import threading
import wave

import numpy as np


class PushToTalkMicrophone:
    def __init__(self, sample_rate: int = 16_000, channels: int = 1) -> None:
        self.sample_rate = sample_rate
        self.channels = channels

    async def capture_wav(self) -> bytes:
        return await asyncio.to_thread(self._capture_blocking)

    def _capture_blocking(self) -> bytes:
        try:
            import sounddevice as sd
        except Exception as exc:
            raise RuntimeError("Audio input is unavailable. Install PortAudio/sounddevice or use --text.") from exc

        chunks: list[np.ndarray] = []
        lock = threading.Lock()

        def callback(indata: np.ndarray, frames: int, time_info: object, status: object) -> None:
            del frames, time_info
            if status:
                print(f"[audio] {status}")
            with lock:
                chunks.append(indata.copy())

        print("Recording... speak now, then press Enter to stop.")
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype="int16", callback=callback):
                input()
        except Exception as exc:
            raise RuntimeError(f"Could not record from the microphone: {exc}") from exc

        with lock:
            if not chunks:
                raise RuntimeError("No microphone audio was captured.")
            pcm = np.concatenate(chunks, axis=0)

        return _pcm_to_wav(pcm, self.sample_rate, self.channels)


def _pcm_to_wav(pcm: np.ndarray, sample_rate: int, channels: int) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.astype(np.int16, copy=False).tobytes())
    return buffer.getvalue()
