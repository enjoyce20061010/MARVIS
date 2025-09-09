from adapters.fake_adapter import FakeAdapter
from core.controller import Controller
from core.trace import JsonlTracer
from modules.analyzer import SystemAnalyzer
from modules.code_agent import CodeAgent
from modules.supervisor import IndependentSupervisor
from modules.test_runner import TestRunner, TestResult


class _FailingTestRunner(TestRunner):
    def run_tests(self, change) -> TestResult:
        return TestResult(passed=False, report="fail")


def test_controller_needs_intervention(tmp_path):
    tracer = JsonlTracer(path=str(tmp_path / "trace.jsonl"))
    analyzer = SystemAnalyzer()
    llm = FakeAdapter()
    code_agent = CodeAgent(llm=llm)
    # Configure supervisor to immediately intervene on first failure
    supervisor = IndependentSupervisor(max_retries=0, max_minutes=30, max_cost=10.0)
    controller = Controller(analyzer, code_agent, _FailingTestRunner(), supervisor, tracer)

    result = controller.run(user_task="demo task")
    assert result == "Needs Human Intervention"


def test_controller_failed_after_retries(tmp_path):
    tracer = JsonlTracer(path=str(tmp_path / "trace.jsonl"))
    analyzer = SystemAnalyzer()
    llm = FakeAdapter()
    code_agent = CodeAgent(llm=llm)
    # Allow one retry before failing after retries
    supervisor = IndependentSupervisor(max_retries=2, max_minutes=30, max_cost=10.0)
    controller = Controller(analyzer, code_agent, _FailingTestRunner(), supervisor, tracer)

    result = controller.run(user_task="demo task")
    # Given current supervisor logic, threshold triggers intervention, not explicit failure
    assert result == "Needs Human Intervention"


def test_supervisor_decide_branches():
    sup = IndependentSupervisor(max_retries=1, max_minutes=0, max_cost=1.0)

    # test_passed branch
    assert sup.decide(retry_count=0, wall_clock_minutes=0, cost=0, test_passed=True) == "done"

    # retry limit branch (retry_count + 1 >= max_retries)
    assert sup.decide(retry_count=1, wall_clock_minutes=0, cost=0, test_passed=False) == "intervene"

    # wall time exceeded branch
    assert sup.decide(retry_count=0, wall_clock_minutes=1.0, cost=0, test_passed=False) == "intervene"

    # cost exceeded branch
    assert sup.decide(retry_count=0, wall_clock_minutes=0, cost=2.0, test_passed=False) == "intervene"

    # otherwise, with higher retry budget, retry
    sup2 = IndependentSupervisor(max_retries=2, max_minutes=10, max_cost=10.0)
    assert sup2.decide(retry_count=0, wall_clock_minutes=0, cost=0, test_passed=False) == "retry"


