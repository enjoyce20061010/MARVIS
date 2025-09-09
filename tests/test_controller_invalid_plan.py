from adapters.fake_adapter import FakeAdapter
from core.controller import Controller
from core.trace import JsonlTracer
from modules.analyzer import SystemAnalyzer
from modules.code_agent import CodeAgent
from modules.supervisor import IndependentSupervisor
from modules.test_runner import TestRunner, TestResult


class _InvalidPlanAdapter(FakeAdapter):
    def generate(self, messages, tools=None, tool_choice=None):
        from core.types import Message

        # return invalid JSON so controller goes through exception path
        return Message(role="assistant", content="not a json plan")


class _PassingTestRunner(TestRunner):
    def run_tests(self, change) -> TestResult:
        return TestResult(True, "ok")


def test_controller_handles_invalid_edit_plan(tmp_path):
    tracer = JsonlTracer(path=str(tmp_path / "trace.jsonl"))
    analyzer = SystemAnalyzer()
    llm = _InvalidPlanAdapter()
    code_agent = CodeAgent(llm=llm)
    test_runner = _PassingTestRunner()
    supervisor = IndependentSupervisor(max_retries=1)

    controller = Controller(analyzer, code_agent, test_runner, supervisor, tracer=tracer)
    result = controller.run(user_task="demo")
    assert result == "Delivered"


