import json

from adapters.fake_adapter import FakeAdapter
from core.controller import Controller
from core.trace import JsonlTracer
from modules.analyzer import SystemAnalyzer
from modules.code_agent import CodeAgent
from modules.supervisor import IndependentSupervisor
from modules.test_runner import TestRunner, TestResult


UTILS_CONTENT = """
def add(a: int, b: int) -> int:
    return a + b
""".strip()


TEST_CONTENT = """
def test_add():
    from modules import utils
    assert utils.add(2, 3) == 5
""".strip()


class _PlanAdapter(FakeAdapter):
    def __init__(self, plan_json: str):
        super().__init__()
        self._plan_json = plan_json

    def generate(self, messages, tools=None, tool_choice=None):
        from core.types import Message

        return Message(role="assistant", content=self._plan_json)


class _Runner(TestRunner):
    def run_tests(self, change) -> TestResult:
        # only run the specific new test to reduce flakiness
        code, out = self._run(["pytest", "-q", "-k", "test_add"])
        return TestResult(code == 0, out)


def test_utils_created_and_tests_pass(tmp_path):
    plan = {
        "description": "create utils and its test",
        "operations": [
            {"op": "write_file", "path": "modules/__init__.py", "content": ""},
            {"op": "write_file", "path": "modules/utils.py", "content": UTILS_CONTENT},
            {"op": "write_file", "path": "tests/test_utils_small.py", "content": TEST_CONTENT},
        ],
    }
    plan_json = json.dumps(plan)

    analyzer = SystemAnalyzer()
    llm = _PlanAdapter(plan_json)
    code_agent = CodeAgent(llm=llm)
    test_runner = _Runner()
    supervisor = IndependentSupervisor(max_retries=1)
    tracer = JsonlTracer(path=str(tmp_path / "trace.jsonl"))

    controller = Controller(analyzer, code_agent, test_runner, supervisor, tracer=tracer)
    result = controller.run(user_task="create utils")
    assert result == "Delivered"


