# Voice-Agent

Voice-Agent is a modular Python desktop voice agent designed to grow from a simple push-to-talk assistant into a realtime, interruptible, tool-using desktop agent.

## Current milestone: v0.1

The first milestone implements a working chained voice pipeline:

```text
Microphone -> Speech-to-Text -> Agent Core -> LLM -> Text-to-Speech -> Speaker
                                |      |
                                |      +-> Tool calls
                                +-> Conversation memory
```

Included today:

- Push-to-talk microphone capture.
- OpenAI speech transcription provider.
- OpenAI Responses API model provider.
- OpenAI speech synthesis provider.
- Short-term conversation memory.
- Tool registry and a real `get_current_time` tool.
- Provider interfaces so STT, LLM and TTS can be replaced later.
- Text mode for development without a microphone.
- Doctor command for configuration/audio diagnostics.
- Architecture and roadmap documentation.

The design intentionally keeps voice I/O separate from the Agent Core. Future clients such as Telegram, a desktop UI or an API can reuse the same core.

## Requirements

- Python 3.11+
- A working microphone and speaker for voice mode
- An OpenAI API key for the default providers

## Install

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
Copy-Item .env.example .env
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
cp .env.example .env
```

Set the key in `.env`:

```env
OPENAI_API_KEY=your_key_here
```

## Run

### Voice mode

```bash
voice-agent
```

or:

```bash
python -m voice_agent
```

Press Enter to start recording, speak, then press Enter again to stop recording. The agent transcribes the audio, reasons, optionally calls tools, and speaks the result.

### Text mode

Useful when developing on a machine without a microphone:

```bash
voice-agent --text
```

### Diagnostics

```bash
voice-agent --doctor
```

This checks environment configuration and attempts to enumerate PortAudio devices.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | required | API key for the default providers |
| `VOICE_AGENT_CHAT_MODEL` | `gpt-5-mini` | LLM used by the Agent Core |
| `VOICE_AGENT_STT_MODEL` | `gpt-4o-mini-transcribe` | Speech-to-text model |
| `VOICE_AGENT_TTS_MODEL` | `gpt-4o-mini-tts` | Text-to-speech model |
| `VOICE_AGENT_TTS_VOICE` | `marin` | Voice used for speech output |
| `VOICE_AGENT_LANGUAGE` | `vi` | STT language hint |
| `VOICE_AGENT_SAMPLE_RATE` | `16000` | Microphone sample rate |
| `VOICE_AGENT_CHANNELS` | `1` | Microphone channels |
| `VOICE_AGENT_MAX_HISTORY_TURNS` | `12` | Short-term conversation history |
| `VOICE_AGENT_MAX_TOOL_ROUNDS` | `4` | Safety limit for tool loops |

## Project layout

```text
src/voice_agent/
├── agent/          # Agent runtime and orchestration
├── audio/          # Microphone and speaker adapters
├── config/         # Environment/settings
├── domain/         # Shared message types
├── memory/         # Conversation memory
├── models/         # LLM provider interface + OpenAI implementation
├── prompts/        # Voice-specific instructions
├── stt/            # STT provider interface + OpenAI implementation
├── tools/          # Tool contract, registry and built-ins
└── tts/            # TTS provider interface + OpenAI implementation
```

For the full design, decisions, safety model and development phases, see [`docs/VOICE_AGENT_DESIGN.md`](docs/VOICE_AGENT_DESIGN.md).

## Validation

```bash
python -m compileall -q src tests
pytest -q
```

## Next milestone

v0.2 will replace manual push-to-talk boundaries with streaming audio + VAD/turn detection. After that the project can add streaming TTS, interruption/barge-in, realtime speech-to-speech, long-term memory and desktop tools.
