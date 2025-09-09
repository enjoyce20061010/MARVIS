from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class Message:
	role: str  # system | user | assistant | tool
	content: str
	tool_call_id: Optional[str] = None
	name: Optional[str] = None


@dataclass
class ToolSchema:
	name: str
	description: str
	parameters: Dict[str, Any]  # JSON Schema


@dataclass
class ToolCall:
	name: str
	arguments_json: str  # raw JSON string
	id: Optional[str] = None


class LLMClient(Protocol):
	def generate(self, messages: List[Message], tools: Optional[List[ToolSchema]] = None, tool_choice: Optional[str] = None) -> Message:
		"""Return a single assistant Message. If tool calls are requested, embed them in Message via content or name fields as needed by adapter's convention, or attach in adapter-specific metadata (kept internal)."""
		...
