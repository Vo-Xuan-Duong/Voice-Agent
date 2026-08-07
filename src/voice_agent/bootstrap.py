from __future__ import annotations

from openai import AsyncOpenAI

from voice_agent.agent.runtime import AgentRuntime
from voice_agent.app import VoiceApplication
from voice_agent.audio.microphone import PushToTalkMicrophone
from voice_agent.audio.speaker import WavSpeaker
from voice_agent.config.settings import Settings
from voice_agent.memory.conversation import ConversationMemory
from voice_agent.models.openai_model import OpenAIResponsesModel
from voice_agent.prompts.voice import VOICE_SYSTEM_PROMPT
from voice_agent.stt.openai_stt import OpenAISpeechToText
from voice_agent.tools.builtin import register_builtin_tools
from voice_agent.tools.registry import ToolRegistry
from voice_agent.tts.openai_tts import OpenAITextToSpeech


def build_application(settings: Settings) -> VoiceApplication:
    settings.validate_for_openai()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    tools = ToolRegistry()
    register_builtin_tools(tools)
    memory = ConversationMemory(max_turns=settings.max_history_turns)
    model = OpenAIResponsesModel(client=client, model=settings.chat_model, instructions=VOICE_SYSTEM_PROMPT)
    agent = AgentRuntime(model=model, memory=memory, tools=tools, max_tool_rounds=settings.max_tool_rounds)
    return VoiceApplication(
        agent=agent,
        stt=OpenAISpeechToText(client=client, model=settings.stt_model, language=settings.language),
        tts=OpenAITextToSpeech(client=client, model=settings.tts_model, voice=settings.tts_voice),
        microphone=PushToTalkMicrophone(sample_rate=settings.sample_rate, channels=settings.channels),
        speaker=WavSpeaker(),
    )
