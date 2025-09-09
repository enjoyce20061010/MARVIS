import os
from typing import Any, List, Optional
from core.types import LLMClient, Message, ToolSchema


class OpenAIAdapter(LLMClient):
	def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, client: Optional[Any] = None):
		self.api_key = api_key or os.getenv("OPENAI_API_KEY")
		self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
		if client is not None:
			self.client = client
		else:
			# Lazy import to avoid dependency during offline runs
			from openai import OpenAI  # type: ignore
			self.client = OpenAI(api_key=self.api_key)

	def generate(self, messages: List[Message], tools: Optional[List[ToolSchema]] = None, tool_choice: Optional[str] = None) -> Message:
		openai_messages = [
			{"role": m.role, "content": m.content}
			for m in messages
		]
		openai_tools = None
		if tools:
			openai_tools = [{
				"type": "function",
				"function": {
					"name": t.name,
					"description": t.description,
					"parameters": t.parameters,
				},
			} for t in tools]

		resp = self.client.chat.completions.create(
			model=self.model,
			messages=openai_messages,
			tools=openai_tools,
			tool_choice=tool_choice or "auto" if openai_tools else None,
		)
		msg = resp.choices[0].message
		return Message(role="assistant", content=msg.content or "")
