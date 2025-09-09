from types import SimpleNamespace

from adapters.openai_adapter import OpenAIAdapter
from core.types import Message, ToolSchema


class _FakeOpenAIClient:
    def __init__(self):
        self.last_payload = None

        class _Chat:
            def __init__(self, outer):
                class _Completions:
                    def __init__(self, outer2):
                        self._outer2 = outer2

                    def create(self, **kwargs):
                        outer.last_payload = kwargs
                        # simulate openai response shape
                        message = SimpleNamespace(content="ok")
                        choice = SimpleNamespace(message=message)
                        return SimpleNamespace(choices=[choice])

                self.completions = _Completions(self)

        self.chat = _Chat(self)


def test_openai_adapter_builds_payload():
    fake = _FakeOpenAIClient()
    adapter = OpenAIAdapter(model="gpt-4o-mini", client=fake)

    messages = [Message(role="user", content="hi")]
    tools = [
        ToolSchema(name="t1", description="d", parameters={"type": "object", "properties": {}})
    ]
    _ = adapter.generate(messages=messages, tools=tools, tool_choice="auto")

    payload = fake.last_payload
    assert payload["model"] == "gpt-4o-mini"
    assert isinstance(payload["messages"], list) and payload["messages"][0]["role"] == "user"
    assert isinstance(payload["tools"], list) and payload["tools"][0]["type"] == "function"
    assert payload["tool_choice"] == "auto"


