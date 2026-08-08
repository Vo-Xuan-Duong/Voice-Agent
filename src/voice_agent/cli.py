from __future__ import annotations

import argparse
import asyncio
import sys

from voice_agent.audio.microphone import PushToTalkMicrophone
from voice_agent.bootstrap import build_application
from voice_agent.config.settings import Settings
from voice_agent.doctor import run_doctor
from voice_agent.stt.faster_whisper_stt import FasterWhisperSpeechToText
from voice_agent.stt.runner import SpeechRecognitionRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="voice-agent", description="Modular desktop Voice Agent")
    parser.add_argument("--text", action="store_true", help="Use text input/output instead of microphone and speaker.")
    parser.add_argument(
        "--stt-only",
        action="store_true",
        help="Run local microphone -> text recognition only. No LLM, TTS, or OpenAI API key is required.",
    )
    parser.add_argument("--doctor", action="store_true", help="Check API and audio configuration, then exit.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        settings = Settings.from_env()
        if args.doctor:
            raise SystemExit(run_doctor(settings))

        if args.stt_only:
            microphone = PushToTalkMicrophone(
                sample_rate=settings.sample_rate,
                channels=settings.channels,
            )
            stt = FasterWhisperSpeechToText(
                model_name=settings.local_stt_model,
                device=settings.local_stt_device,
                compute_type=settings.local_stt_compute_type,
                language=settings.language,
                beam_size=settings.local_stt_beam_size,
            )
            runner = SpeechRecognitionRunner(microphone, stt)
            asyncio.run(runner.run())
            return

        app = build_application(settings)
        if args.text:
            asyncio.run(app.run_text())
        else:
            asyncio.run(app.run_voice())
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
