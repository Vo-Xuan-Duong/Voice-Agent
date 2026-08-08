from __future__ import annotations

import tempfile
import threading
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16_000
CHANNELS = 1
MODEL_NAME = "small"
LANGUAGE = "vi"


def record_until_enter() -> np.ndarray:
    chunks: list[np.ndarray] = []
    lock = threading.Lock()

    def callback(indata: np.ndarray, frames: int, time_info: object, status: object) -> None:
        del frames, time_info
        if status:
            print(f"[audio] {status}")
        with lock:
            chunks.append(indata.copy())

    print("Recording... speak now, then press Enter to stop.")
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=callback,
    ):
        input()

    with lock:
        if not chunks:
            raise RuntimeError("No microphone audio was captured.")
        return np.concatenate(chunks, axis=0)


def save_wav(audio: np.ndarray, path: Path) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio.astype(np.int16, copy=False).tobytes())


def transcribe(model: WhisperModel, audio: np.ndarray) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        save_wav(audio, temp_path)
        segments, _ = model.transcribe(
            str(temp_path),
            language=LANGUAGE,
            beam_size=5,
        )
        return " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text and segment.text.strip()
        ).strip()
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> None:
    print("Voice-Agent: Speech-to-Text")
    print("Loading local Whisper model...")
    model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")
    print("Ready. Press Ctrl+C to exit.\n")

    while True:
        input("Press Enter to start recording...")
        audio = record_until_enter()
        print("Transcribing...")
        text = transcribe(model, audio)
        print(f"You: {text or '[no speech recognized]'}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
