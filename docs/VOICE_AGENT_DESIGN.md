# Voice Agent — Architecture, Design and Development Roadmap

## 1. Goal

The goal is to build a desktop Voice Agent that can eventually converse naturally, remember context, call tools and control desktop capabilities while remaining modular enough to replace any individual AI provider.

The long-term target is not merely a voice chatbot. It is an agent runtime with voice as one interaction surface.

```text
Voice ─────┐
Text ──────┼──> Agent Core ──> Models / Memory / Tools
Desktop UI ┤
Telegram ──┘
```

The first version deliberately starts smaller: reliable push-to-talk speech input, transcription, LLM reasoning, tool use, speech output and conversation state.

---

## 2. Core design principles

### 2.1 Voice is an interface, not the brain

Audio capture, transcription and speech synthesis must not own agent logic. The Agent Core should be reusable by future interfaces.

### 2.2 Providers are replaceable

The project must not hard-code the core to one STT, LLM or TTS vendor.

```text
SpeechToText
├── OpenAI
├── Deepgram       (future)
└── Local Whisper  (future)

ChatModel
├── OpenAI
├── Gemini         (future)
├── Claude         (future)
├── Ollama         (future)
└── AI Gateway     (future)

TextToSpeech
├── OpenAI
├── ElevenLabs     (future)
├── Deepgram       (future)
└── Local TTS      (future)
```

### 2.3 Start chained, evolve to realtime

Two voice paths should eventually coexist.

**Chained mode**

```text
Audio -> STT -> Text -> Agent -> Text -> TTS -> Audio
```

This is easy to debug and allows every component to be swapped independently.

**Realtime speech-to-speech mode**

```text
Microphone <-> Realtime voice provider <-> Agent/tool runtime <-> Speaker
```

This mode is the long-term choice when natural turn taking and low latency matter most.

### 2.4 Deterministic code controls the loop

The LLM proposes actions; application code owns limits, state, tool execution, retries and termination. A model must never be allowed to run an unbounded loop.

### 2.5 Safety before desktop control

Desktop operations will later pass through a policy layer:

```text
Tool call -> Policy -> Allow / Ask / Deny -> Execution -> Verification
```

---

## 3. Target architecture

```text
                         USER
                           |
                    +------v------+
                    | Voice Layer |
                    +------+------+
                           |
                 transcript / events
                           |
                    +------v------+
                    | Agent Core  |
                    |             |
                    | loop        |
                    | context     |
                    | state       |
                    | tool calls  |
                    +--+---+---+--+
                       |   |   |
             +---------+   |   +----------+
             |             |              |
      +------v------+ +----v-----+ +------v------+
      | Model Layer | | Memory   | | Tool Layer  |
      +------+------+ +----------+ +------+------+
             |                            |
       model providers               MCP / Desktop
             |
        AI Gateway (future)
```

### Runtime voice path in v0.1

```text
Press Enter
    |
    v
Microphone recorder
    |
    | WAV bytes
    v
SpeechToText
    |
    | transcript
    v
ConversationMemory
    |
    v
AgentRuntime
    |
    +--> ChatModel
    |      |
    |      +--> function/tool call?
    |               |
    |               v
    |          ToolRegistry
    |               |
    |          tool result
    |               |
    +<--------------+
    |
    | final text
    v
TextToSpeech
    |
    | WAV bytes
    v
Speaker
```

---

## 4. Components

### 4.1 Audio Input

Responsibilities:

- Capture microphone audio.
- Produce a stable PCM/WAV representation.
- Keep audio capture separate from STT.

v0.1 uses manual start/stop boundaries. This intentionally avoids mixing VAD bugs with the first end-to-end integration.

Future responsibilities:

- continuous input stream;
- configurable device selection;
- echo cancellation;
- noise suppression;
- automatic gain control.

### 4.2 VAD and Turn Detection

Not required for v0.1, but essential for natural conversation.

VAD answers: “is the user currently speaking?”

Turn detection answers: “has the user finished this conversational turn?”

Future flow:

```text
silence -> speech_started -> speech -> pause -> end_of_turn
```

Semantic turn detection can later complement timing-based VAD so a short thinking pause is not always interpreted as the end of a sentence.

### 4.3 Speech-to-Text

Contract:

```python
class SpeechToText(Protocol):
    async def transcribe(self, wav_bytes: bytes) -> str: ...
```

The default provider uses OpenAI transcription. The contract is intentionally independent of the OpenAI SDK.

### 4.4 Agent Core

The Agent Core is the orchestration layer. It receives text, adds it to conversation context, invokes the model, executes allowed tool calls, stores the final assistant message and returns the answer.

It must own:

- maximum tool rounds;
- state transitions;
- tool execution;
- error boundaries;
- final response selection.

### 4.5 LLM provider

Contract:

```python
class ChatModel(Protocol):
    async def respond(self, messages, tools, executor, max_tool_rounds) -> str: ...
```

The provider may internally use a vendor-specific API, but the rest of the application sees only this contract.

v0.1 uses the OpenAI Responses API and exposes custom tools to the model.

### 4.6 Conversation memory

v0.1 uses in-memory bounded history. This gives contextual multi-turn conversation without prematurely introducing a database or vector store.

Rules:

- keep complete user/assistant pairs where possible;
- cap history by turns;
- do not store tool-internal reasoning as user-visible memory;
- long-term memory is a later subsystem.

Future memory layers:

```text
Working memory    -> current turn/task
Short-term memory -> recent conversation
Long-term memory  -> stable facts/preferences/project state
Semantic memory   -> retrieved knowledge
```

### 4.7 Tool system

A tool is a deterministic capability exposed to the model.

Each tool contains:

- `name`;
- `description`;
- JSON schema parameters;
- an async executor.

The first built-in tool is `get_current_time` to prove the full Agent path works.

Future tools:

- application launcher;
- filesystem read/search/edit;
- process inspection;
- shell commands;
- browser automation;
- clipboard;
- Git/GitHub;
- database;
- MCP servers.

### 4.8 Text-to-Speech

Contract:

```python
class TextToSpeech(Protocol):
    async def synthesize(self, text: str) -> bytes: ...
```

v0.1 asks the provider for WAV output so the speaker adapter can play it without an additional codec library.

Future requirements:

- streaming chunks;
- phrase buffering;
- speaking style controls;
- cancellation tokens for interruption.

### 4.9 Audio Output

The speaker adapter accepts WAV bytes. It knows nothing about the model or conversation.

Future versions need an interruptible audio queue rather than a single blocking playback call.

---

## 5. Natural conversation requirements

A Voice Agent begins to feel human when these properties work together.

### Streaming

Do not wait for every stage to finish the full payload before starting the next stage. Future pipelines should stream microphone frames, transcription deltas, model text and TTS audio.

### Turn taking

The system should infer when the user has finished rather than relying on a button.

### Barge-in / interruption

While the agent is speaking, new user speech should:

1. cancel current model/TTS work when possible;
2. clear pending audio output;
3. switch immediately to listening;
4. preserve enough context to understand the interruption.

### Spoken response style

Voice answers should normally be shorter than text answers. The prompt therefore instructs the model to avoid unnecessary headings, markdown and long lists unless the user requests them.

### Latency

Latency should be measured as separate stages:

```text
turn-end detection
+ STT first result
+ LLM first token
+ TTS first audio
+ audio device buffering
```

Optimizing total latency without measuring each stage hides the true bottleneck.

---

## 6. v0.1 implementation

The current implementation provides:

- modular STT/LLM/TTS interfaces;
- OpenAI implementations;
- push-to-talk microphone capture;
- WAV speaker playback;
- bounded short-term memory;
- OpenAI function calling through a tool registry;
- `get_current_time` built-in tool;
- voice-specific system instructions;
- CLI voice mode;
- CLI text mode;
- diagnostics command;
- unit tests for deterministic core components.

This is intentionally the smallest architecture that proves the full path without prematurely implementing realtime complexity.

---

## 7. Development roadmap

### Phase 1 — Voice MVP (v0.1)

Goal: reliable end-to-end conversation.

```text
push-to-talk -> STT -> Agent -> TTS -> speaker
```

Exit criteria:

- one command starts the app;
- multiple conversation turns work;
- the agent can call at least one deterministic tool;
- provider boundaries are tested;
- no secrets are committed.

### Phase 2 — Streaming + VAD (v0.2)

Add:

- microphone frame stream;
- VAD;
- automatic speech-start and speech-end events;
- streaming transcription;
- event bus or async queues for voice events.

Exit criteria:

- no Enter key is required for normal conversation;
- false end-of-turn behavior is measurable/configurable.

### Phase 3 — Natural conversation (v0.3)

Add:

- streaming model output;
- streaming TTS;
- interruption/barge-in;
- cancellation propagation;
- interruptible speaker queue;
- semantic turn detection where supported.

Exit criteria:

- user can interrupt the agent mid-sentence;
- the agent begins responding before a full audio response has been generated.

### Phase 4 — Agent Harness (v0.4)

Add:

- explicit task/turn state machine;
- policy engine;
- permission prompts;
- retry/timeout/budget rules;
- verification hooks;
- tracing and token/latency metrics.

### Phase 5 — Memory (v0.5)

Add:

- SQLite or PostgreSQL persistence;
- stable long-term facts separate from chat logs;
- retrieval policy;
- memory write/delete controls;
- context compression/summarization.

### Phase 6 — Desktop Agent (v0.6)

Add safe tools for:

- launching applications;
- reading selected files;
- process/system information;
- clipboard;
- browser;
- Git/project operations.

Every mutating tool should be covered by explicit allow/ask/deny policy.

### Phase 7 — MCP and model routing (v0.7)

Add:

- MCP client/tool adapter;
- multiple LLM providers;
- AI Gateway/provider routing;
- fallback and rate-limit handling;
- provider-level telemetry.

### Phase 8 — Realtime speech-to-speech (v0.8)

Add a second Voice Engine implementation using a realtime audio model while keeping the same Agent Core and tool layer.

### Phase 9 — Wake word/background assistant (v0.9)

Only after the conversation stack is stable:

- wake-word detection;
- background process/service;
- tray application;
- sleep/wake states;
- microphone privacy indicator;
- explicit mute control.

---

## 8. Safety architecture for desktop expansion

The LLM must never directly execute arbitrary OS actions.

```text
LLM
 |
 | tool proposal
 v
Tool Registry
 |
 v
Policy Engine
 |       |       |
Allow    Ask     Deny
 |       |       |
 v       v       X
Executor
 |
 v
Verification
```

Example policy:

| Action | Default |
|---|---|
| read approved project file | allow |
| inspect process/system info | allow |
| run project test | allow |
| edit approved project | ask/allow by workspace policy |
| delete file | ask |
| git commit | ask |
| git push | ask |
| system-level destructive command | deny |

---

## 9. Observability

Later versions should trace one conversational turn as a single unit:

```text
turn_id
├── audio.capture
├── stt
├── model.response
├── tool.call(s)
├── tts
└── audio.playback
```

Recommended metrics:

- transcription latency;
- model latency;
- time to first model token;
- TTS time to first audio;
- total response latency;
- tool call count/failures;
- token usage;
- interruption count;
- VAD false-start/false-stop rate.

---

## 10. Why this architecture can grow into a Jarvis-style assistant

The key boundary is:

```text
                   +-------------+
                   | Voice Layer |
                   +------+------+ 
                          |
                   +------v------+
                   | Agent Core  |
                   +------^------+
                          |
        +-----------------+------------------+
        |                 |                  |
     Models             Memory              Tools
        |                                    |
   AI Gateway                               MCP
```

Voice is replaceable. Models are replaceable. Tools are replaceable. Memory can evolve independently. This prevents the initial Voice MVP from becoming a dead-end prototype.

The recommended rule for every future feature is: **extend a boundary before coupling two modules together**.
