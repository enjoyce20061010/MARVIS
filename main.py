import os
from modules.analyzer import SystemAnalyzer
from modules.code_agent import CodeAgent
from modules.test_runner import TestRunner
from modules.supervisor import IndependentSupervisor
from core.controller import Controller
from adapters.fake_adapter import FakeAdapter


def main():
	analyzer = SystemAnalyzer()
	# Default to FakeAdapter (offline). Set USE_OPENAI=1 to use OpenAIAdapter.
	use_openai = os.getenv("USE_OPENAI", "0") == "1"
	if use_openai:
		from adapters.openai_adapter import OpenAIAdapter  # lazy import to avoid dependency when offline
		llm = OpenAIAdapter()
	else:
		llm = FakeAdapter()
	code_agent = CodeAgent(llm=llm)
	test_runner = TestRunner()
	supervisor = IndependentSupervisor(max_retries=3, max_minutes=30, max_cost=10.0)

	controller = Controller(
		analyzer=analyzer,
		code_agent=code_agent,
		test_runner=test_runner,
		supervisor=supervisor,
	)

	result = controller.run(user_task="Refactor module X to improve readability")
	print("Result:", result)


if __name__ == "__main__":
	main()
