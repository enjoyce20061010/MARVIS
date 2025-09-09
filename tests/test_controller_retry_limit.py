from adapters.fake_adapter import FakeAdapter
from core.controller import Controller
from core.trace import JsonlTracer
from modules.analyzer import SystemAnalyzer
from modules.code_agent import CodeAgent
from modules.supervisor import IndependentSupervisor
from modules.test_runner import TestRunner, TestResult


class _AlwaysFailRunner(TestRunner):
    def run_tests(self, change) -> TestResult:
        return TestResult(False, "fail")


def test_controller_hits_retry_limit(tmp_path):
    tracer = JsonlTracer(path=str(tmp_path / "trace.jsonl"))
    analyzer = SystemAnalyzer()
    llm = FakeAdapter()
    code_agent = CodeAgent(llm=llm)
    test_runner = _AlwaysFailRunner()
    supervisor = IndependentSupervisor(max_retries=2)

    controller = Controller(analyzer, code_agent, test_runner, supervisor, tracer=tracer)
    result = controller.run(user_task="demo", max_retries=2)
    # Current supervisor returns intervention at threshold
    assert result == "Needs Human Intervention"


