from __future__ import annotations

import argparse
import os

from core.controller import Controller
from core.trace import JsonlTracer
from modules.analyzer import SystemAnalyzer
from modules.code_agent import CodeAgent
from modules.supervisor import IndependentSupervisor
from modules.test_runner import TestRunner
from adapters.fake_adapter import FakeAdapter


def build_llm(use_openai: bool):
    if use_openai:
        from adapters.openai_adapter import OpenAIAdapter  # lazy import

        return OpenAIAdapter()
    return FakeAdapter()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the agent controller interactively.")
    parser.add_argument("--task", type=str, default="Refactor module X to improve readability", help="User task to execute")
    parser.add_argument("--online", action="store_true", help="Use OpenAI online adapter (requires OPENAI_API_KEY)")
    parser.add_argument("--trace", type=str, default="trace.jsonl", help="Path to JSONL trace output")
    args = parser.parse_args()

    analyzer = SystemAnalyzer()
    llm = build_llm(use_openai=args.online or os.getenv("USE_OPENAI", "0") == "1")
    code_agent = CodeAgent(llm=llm)
    test_runner = TestRunner()
    supervisor = IndependentSupervisor(max_retries=3, max_minutes=30, max_cost=10.0)
    tracer = JsonlTracer(path=args.trace)

    controller = Controller(
        analyzer=analyzer,
        code_agent=code_agent,
        test_runner=test_runner,
        supervisor=supervisor,
        tracer=tracer,
    )

    result = controller.run(user_task=args.task)
    print(f"Result: {result}")
    print(f"Trace written to: {args.trace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


