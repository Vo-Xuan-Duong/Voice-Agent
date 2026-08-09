from __future__ import annotations

import os
import threading
from pathlib import Path

import numpy as np
import sherpa_onnx
import sounddevice as sd

SAMPLE_RATE = 16_000
CHANNELS = 1
MODEL_NAME = "sherpa-onnx-zipformer-vi-int8-2025-04-20"
MODEL_DIR = Path(__file__).resolve().parent / "models" / MODEL_NAME

ENCODER = MODEL_DIR / "encoder-epoch-12-avg-8.int8.onnx"
DECODER = MODEL_DIR / "decoder-epoch-12-avg-8.onnx"
JOINER = MODEL_DIR / "joiner-epoch-12-avg-8.int8.onnx"
TOKENS = MODEL_DIR / "tokens.txt"

NUM_THREADS = max(1, min(4, os.cpu_count() or 1))


def require_model_files() -> None:
    required = [ENCODER, DECODER, JOINER, TOKENS]
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(
            "Vietnamese Sherpa model is missing.\n"
            "Run this command first:\n\n"
            "    python setup_model.py\n"
        )


def create_recognizer() -> sherpa_onnx.OfflineRecognizer:
    require_model_files()
    return sherpa_onnx.OfflineRecognizer.from_transducer(
        tokens=str(TOKENS),
        encoder=str(ENCODER),
        decoder=str(DECODER),
        joiner=str(JOINER),
        num_threads=NUM_THREADS,
        sample_rate=SAMPLE_RATE,
        feature_dim=80,
        decoding_method="greedy_search",
        max_active_paths=4,
        provider="cpu",
    )


def print_microphone_info() -> None:
    try:
        device = sd.query_devices(kind="input")
        name = device.get("name", "Unknown microphone")
        print(f"Microphone: {name}")
    except Exception:
        print("Microphone: default input device")


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
        dtype="float32",
        callback=callback,
    ):
        input()

    with lock:
        if not chunks:
            raise RuntimeError("No microphone audio was captured.")
        audio = np.concatenate(chunks, axis=0).reshape(-1)

    rms = float(np.sqrt(np.mean(np.square(audio, dtype=np.float64))))
    if rms < 0.003:
        print("[warning] Microphone signal is very quiet. Recognition may be inaccurate.")

    return audio.astype(np.float32, copy=False)


def transcribe(recognizer: sherpa_onnx.OfflineRecognizer, audio: np.ndarray) -> str:
    stream = recognizer.create_stream()
    stream.accept_waveform(SAMPLE_RATE, audio)
    recognizer.decode_stream(stream)
    return stream.result.text.strip()


def main() -> None:
    print("Voice-Agent: Vietnamese Speech-to-Text")
    print("Engine: sherpa-onnx")
    print(f"Model: {MODEL_NAME}")
    print_microphone_info()
    print("Loading model...")
    recognizer = create_recognizer()
    print(f"Ready. CPU threads: {NUM_THREADS}. Press Ctrl+C to exit.\n")

    while True:
        input("Press Enter to start recording...")
        audio = record_until_enter()
        print("Transcribing...")
        text = transcribe(recognizer, audio)
        print(f"You: {text or '[no speech recognized]'}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as exc:
        print(f"\nError: {exc}")
