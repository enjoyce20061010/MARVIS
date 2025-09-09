from adapters.fake_adapter import FakeAdapter
from core.controller import Controller
from core.trace import JsonlTracer
from modules.analyzer import SystemAnalyzer
from modules.code_agent import CodeAgent
from modules.supervisor import IndependentSupervisor
from modules.test_runner import TestRunner, TestResult


class _PassingTestRunner(TestRunner):
    def run_tests(self, change) -> TestResult:
        return TestResult(passed=True, report="ok")


def test_controller_delivers_with_fake_adapter(tmp_path):
    tracer = JsonlTracer(path=str(tmp_path / "trace.jsonl"))
    analyzer = SystemAnalyzer()
    llm = FakeAdapter()
    code_agent = CodeAgent(llm=llm)
    test_runner = _PassingTestRunner()
    supervisor = IndependentSupervisor(max_retries=1, max_minutes=5, max_cost=1.0)

    controller = Controller(
        analyzer=analyzer,
        code_agent=code_agent,
        test_runner=test_runner,
        supervisor=supervisor,
        tracer=tracer,
    )

    result = controller.run(user_task="demo task")
    assert result == "Delivered"


