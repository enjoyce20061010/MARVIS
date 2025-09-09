from pathlib import Path

from adapters.fake_adapter import FakeAdapter
from modules.code_agent import CodeAgent


def test_code_agent_golden(tmp_path):
    llm = FakeAdapter()
    agent = CodeAgent(llm=llm)
    change = agent.implement("Task: demo\n\nSystem Context:\n<ctx>")

    golden_path = Path(__file__).parent / "golden" / "code_agent_output.txt"
    expected = golden_path.read_text(encoding="utf-8").strip()
    assert change.summary.strip().startswith(expected.split("| inputs=")[0])


