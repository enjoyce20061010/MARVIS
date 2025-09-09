from adapters.fake_adapter import FakeAdapter
from modules.code_agent import CodeAgent


def test_code_agent_prompt_requests_json_schema():
    class _SpyAdapter(FakeAdapter):
        def __init__(self):
            super().__init__()
            self.seen = []

        def generate(self, messages, tools=None, tool_choice=None):
            self.seen = messages
            return super().generate(messages, tools, tool_choice)

    spy = _SpyAdapter()
    agent = CodeAgent(spy)
    _ = agent.implement("Task: demo")

    joined = "\n".join(m.content for m in spy.seen if hasattr(m, "content"))
    assert "Schema:" in joined and "operations" in joined and "write_file" in joined

