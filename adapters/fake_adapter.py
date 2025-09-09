from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from core.types import LLMClient, Message, ToolSchema


@dataclass
class _DeterministicConfig:
    fixed_response: str = "CHANGE_SUMMARY: Deterministic response for testing"


class FakeAdapter(LLMClient):
    """Deterministic LLM adapter for offline and reproducible tests."""

    def __init__(self, config: Optional[_DeterministicConfig] = None):
        self.config = config or _DeterministicConfig()

    def generate(
        self,
        messages: List[Message],
        tools: Optional[List[ToolSchema]] = None,
        tool_choice: Optional[str] = None,
    ) -> Message:
        # Echo minimal context for traceability while staying deterministic.
        user_contents = [m.content for m in messages if m.role == "user"]
        suffix = f" | inputs={len(user_contents)}"
        return Message(role="assistant", content=self.config.fixed_response + suffix)


