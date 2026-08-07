from __future__ import annotations

from voice_agent.config.settings import Settings


def run_doctor(settings: Settings) -> int:
    ok = True
    print("Voice Agent doctor")
    print("------------------")
    if settings.openai_api_key:
        print("[OK] OPENAI_API_KEY is configured")
    else:
        print("[FAIL] OPENAI_API_KEY is missing")
        ok = False
    print(f"[INFO] Chat model: {settings.chat_model}")
    print(f"[INFO] STT model: {settings.stt_model}")
    print(f"[INFO] TTS model: {settings.tts_model}")
    print(f"[INFO] TTS voice: {settings.tts_voice}")
    print(f"[INFO] Audio: {settings.sample_rate} Hz, {settings.channels} channel(s)")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"[OK] PortAudio detected {len(devices)} device(s)")
        default_input, default_output = sd.default.device
        print(f"[INFO] Default input device: {default_input}")
        print(f"[INFO] Default output device: {default_output}")
    except Exception as exc:
        print(f"[FAIL] Audio device check failed: {exc}")
        ok = False
    return 0 if ok else 1
