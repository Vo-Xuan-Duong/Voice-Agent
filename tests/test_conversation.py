from voice_agent.memory.conversation import ConversationMemory


def test_memory_keeps_only_configured_turns() -> None:
    memory = ConversationMemory(max_turns=2)
    memory.add_user("u1")
    memory.add_assistant("a1")
    memory.add_user("u2")
    memory.add_assistant("a2")
    memory.add_user("u3")
    memory.add_assistant("a3")
    snapshot = memory.snapshot()
    assert [m.content for m in snapshot] == ["u2", "a2", "u3", "a3"]


def test_memory_ignores_blank_messages() -> None:
    memory = ConversationMemory(max_turns=2)
    memory.add_user("   ")
    memory.add_assistant("")
    assert memory.snapshot() == []
