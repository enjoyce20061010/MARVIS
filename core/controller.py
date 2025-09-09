from __future__ import annotations
from typing import List, Optional
from core.types import Message, ToolSchema
from core.trace import JsonlTracer
from core.tools import EditPlan
from core.file_editor import FileEditor



class Controller:
	def __init__(self, analyzer, code_agent, test_runner, supervisor, tracer: JsonlTracer | None = None, editor: FileEditor | None = None):
		self.analyzer = analyzer
		self.code_agent = code_agent
		self.test_runner = test_runner
		self.supervisor = supervisor
		self.tracer = tracer or JsonlTracer()
		self.editor = editor or FileEditor()

	def run(self, user_task: str, max_retries: int = 3) -> str:
		self.tracer.log("controller.start", {"user_task": user_task})
		context = self.analyzer.summarize_context(user_task)
		enhanced_task = f"Task: {user_task}\n\nSystem Context:\n{context}"

		retry_count = 0
		while True:
			self.tracer.log("controller.iteration", {"retry": retry_count})
			change = self.code_agent.implement(enhanced_task)
			self.tracer.log("code_agent.change", {"summary_len": len(change.summary)})

			# If change.summary looks like an EditPlan JSON, try to apply it before tests
			try:
				plan = EditPlan.model_validate_json(change.summary)
				self.tracer.log("apply.edit_plan", {"ops": len(plan.operations)})
				for op in plan.operations:
					if op.op == "write_file" and op.content is not None:
						self.editor.write_file(op.path, op.content)
					elif op.op == "replace_text" and op.find is not None and op.replace is not None:
						self.editor.replace_text(op.path, op.find, op.replace)
					elif op.op == "delete_file":
						self.editor.delete_file(op.path)
					else:
						self.tracer.log("apply.edit_plan.skip", {"op": op.op, "path": op.path})
			except Exception:
				# Not a valid edit plan; proceed with tests as-is
				pass
			test_result = self.test_runner.run_tests(change)
			self.tracer.log("tests.result", {"passed": test_result.passed})

			decision = self.supervisor.decide(
				retry_count=retry_count,
				wall_clock_minutes=self.supervisor.wall_time_minutes(),
				cost=self.supervisor.estimated_cost(),
				test_passed=test_result.passed,
			)
			self.tracer.log("supervisor.decision", {"decision": decision})

			if test_result.passed:
				self.tracer.log("controller.done", {"status": "Delivered"})
				return "Delivered"

			if decision == "intervene":
				self.tracer.log("controller.done", {"status": "Needs Human Intervention"})
				return "Needs Human Intervention"

			retry_count += 1
			if retry_count >= max_retries:
				self.tracer.log("controller.done", {"status": "Failed after retries"})
				return "Failed after retries"

			# continue loop for retry
