import json

from adapters.fake_adapter import FakeAdapter
from core.controller import Controller
from core.trace import JsonlTracer
from modules.analyzer import SystemAnalyzer
from modules.code_agent import CodeAgent
from modules.supervisor import IndependentSupervisor
from modules.test_runner import TestRunner, TestResult


class _PlanAdapter(FakeAdapter):
    def __init__(self, plan_json: str):
        super().__init__()
        self._plan_json = plan_json

    def generate(self, messages, tools=None, tool_choice=None):
        from core.types import Message

        return Message(role="assistant", content=self._plan_json)


class _PassingTestRunner(TestRunner):
    def run_tests(self, change) -> TestResult:
        # Verify the file created by the plan exists, then pass
        with open("tests/tmp_generated.txt", "r", encoding="utf-8") as f:
            data = f.read()
        assert "hello" in data
        return TestResult(passed=True, report="ok")


def test_edit_plan_applied_and_tests_pass(tmp_path, monkeypatch):
    plan = {
        "description": "create tmp file",
        "operations": [
            {"op": "write_file", "path": "tests/tmp_generated.txt", "content": "hello world"}
        ],
    }
    plan_json = json.dumps(plan)

    analyzer = SystemAnalyzer()
    llm = _PlanAdapter(plan_json)
    code_agent = CodeAgent(llm=llm)
    test_runner = _PassingTestRunner()
    supervisor = IndependentSupervisor(max_retries=1)
    tracer = JsonlTracer(path=str(tmp_path / "trace.jsonl"))

    controller = Controller(analyzer, code_agent, test_runner, supervisor, tracer=tracer)
    result = controller.run(user_task="demo")
    assert result == "Delivered"


