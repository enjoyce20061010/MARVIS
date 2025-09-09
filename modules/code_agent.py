from core.types import LLMClient, Message, ToolSchema


class ProposedChange:
	def __init__(self, summary: str):
		self.summary = summary


class CodeAgent:
	def __init__(self, llm: LLMClient):
		self.llm = llm

	def implement(self, enhanced_task: str) -> ProposedChange:
		schema_hint = (
			"Respond with a SINGLE JSON object only (no markdown fences, no prose). "
			"Schema: {description: string, operations: [{op: 'write_file'|'replace_text'|'delete_file', path: string, content?: string, find?: string, replace?: string}]}. "
			"All paths must be within 'modules' or 'tests'."
		)
		fewshot = (
			"Example 1:\n"
			"{\"description\": \"create helper\", \"operations\": ["
			"{\"op\": \"write_file\", \"path\": \"modules/__init__.py\", \"content\": \"\"},"
			"{\"op\": \"write_file\", \"path\": \"modules/helper.py\", \"content\": \"def ping():\n    return 'pong'\n\"}]}\n"
			"Example 2:\n"
			"{\"description\": \"add unit test\", \"operations\": ["
			"{\"op\": \"write_file\", \"path\": \"tests/test_helper.py\", \"content\": \"def test_ping():\n    from modules import helper\n    assert helper.ping() == 'pong'\n\"}]}"
		)
		messages = [
			Message(role="system", content="You are a code generator. Output valid JSON only."),
			Message(role="user", content=f"{enhanced_task}\n\n{schema_hint}\n\n{fewshot}"),
		]
		reply = self.llm.generate(messages)
		return ProposedChange(summary=reply.content or "")
