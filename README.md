# Voice-Agent

Voice-Agent is a modular Python desktop voice agent designed to grow from a simple speech recognizer into a realtime, interruptible, tool-using desktop agent.

## Start here: Speech-to-Text only

The first building block is intentionally small:

```text
Microphone -> WAV audio -> Local Speech-to-Text -> Terminal text
```

This mode does **not** use an LLM, TTS, or an OpenAI API key.

### Install

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[local-stt,dev]"
```

#### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[local-stt,dev]'
```

### Run local speech recognition

```bash
voice-agent --stt-only
```

or:

```bash
python -m voice_agent --stt-only
```

Flow:

1. Press Enter to start recording.
2. Speak into the microphone.
3. Press Enter to stop recording.
4. The local Whisper model transcribes the audio.
5. The recognized text is printed to the terminal.

Default local STT configuration:

```env
VOICE_AGENT_LANGUAGE=vi
VOICE_AGENT_LOCAL_STT_MODEL=small
VOICE_AGENT_LOCAL_STT_DEVICE=cpu
VOICE_AGENT_LOCAL_STT_COMPUTE_TYPE=int8
VOICE_AGENT_LOCAL_STT_BEAM_SIZE=5
```

The model is loaded lazily. On the first run, faster-whisper may need to download the selected model weights. Later runs reuse the local model cache.

## Current Voice Agent milestone: v0.1

The repository also contains the next chained-agent foundation:

```text
Microphone -> Speech-to-Text -> Agent Core -> LLM -> Text-to-Speech -> Speaker
                                |      |
                                |      +-> Tool calls
                                +-> Conversation memory
```

Included today:

- Push-to-talk microphone capture.
- Local faster-whisper speech recognition mode.
- OpenAI speech transcription provider as an optional cloud provider.
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
- A working microphone for `--stt-only`
- Speaker + OpenAI API key only when using the full cloud-backed voice mode

## Full Voice Agent install

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

Set the key in `.env` only if using OpenAI-backed modes:

```env
OPENAI_API_KEY=your_key_here
```

## Run

### Speech-to-Text only — local, no LLM

```bash
voice-agent --stt-only
```

### Full voice mode

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
| `OPENAI_API_KEY` | optional for local STT | API key for OpenAI-backed modes |
| `VOICE_AGENT_CHAT_MODEL` | `gpt-5-mini` | LLM used by the Agent Core |
| `VOICE_AGENT_STT_MODEL` | `gpt-4o-mini-transcribe` | OpenAI speech-to-text model |
| `VOICE_AGENT_TTS_MODEL` | `gpt-4o-mini-tts` | OpenAI text-to-speech model |
| `VOICE_AGENT_TTS_VOICE` | `marin` | Voice used for speech output |
| `VOICE_AGENT_LANGUAGE` | `vi` | STT language hint |
| `VOICE_AGENT_SAMPLE_RATE` | `16000` | Microphone sample rate |
| `VOICE_AGENT_CHANNELS` | `1` | Microphone channels |
| `VOICE_AGENT_LOCAL_STT_MODEL` | `small` | faster-whisper model size/name |
| `VOICE_AGENT_LOCAL_STT_DEVICE` | `cpu` | Local inference device |
| `VOICE_AGENT_LOCAL_STT_COMPUTE_TYPE` | `int8` | Local inference compute type |
| `VOICE_AGENT_LOCAL_STT_BEAM_SIZE` | `5` | Local transcription beam size |
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
├── stt/            # STT interfaces, local faster-whisper, OpenAI STT, STT runner
├── tools/          # Tool contract, registry and built-ins
└── tts/            # TTS provider interface + OpenAI implementation
```

For the full design, decisions, safety model and development phases, see [`docs/VOICE_AGENT_DESIGN.md`](docs/VOICE_AGENT_DESIGN.md).

## Validation

```bash
python -m compileall -q src tests
pytest -q
```

## Next STT milestone

After the basic push-to-talk recognizer is stable, the next speech milestone is:

```text
Continuous microphone
        ↓
Audio chunks
        ↓
VAD / speech start-end detection
        ↓
Incremental transcription
        ↓
Partial text events
```

Only after that should the project reconnect the STT stream to the Agent Core and later add streaming TTS and interruption/barge-in.
