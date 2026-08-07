from __future__ import annotations

import argparse
import asyncio
import sys

from voice_agent.bootstrap import build_application
from voice_agent.config.settings import Settings
from voice_agent.doctor import run_doctor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="voice-agent", description="Modular desktop Voice Agent")
    parser.add_argument("--text", action="store_true", help="Use text input/output instead of microphone and speaker.")
    parser.add_argument("--doctor", action="store_true", help="Check API and audio configuration, then exit.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        settings = Settings.from_env()
        if args.doctor:
            raise SystemExit(run_doctor(settings))
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
