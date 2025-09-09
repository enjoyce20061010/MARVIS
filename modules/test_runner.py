from __future__ import annotations

import subprocess
from typing import List


class TestResult:
	def __init__(self, passed: bool, report: str = ""):
		self.passed = passed
		self.report = report


class TestRunner:
	def _run(self, cmd: List[str]) -> tuple[int, str]:
		try:
			out = subprocess.run(cmd, capture_output=True, text=True, check=False)
			code = out.returncode
			stdout = (out.stdout or "") + (out.stderr or "")
			return code, stdout
		except Exception as e:
			return 1, f"exec error: {e}"

	def run_tests(self, change) -> TestResult:
		steps = [
			(["ruff", "check", "."], "ruff"),
			(["black", "--check", "."], "black"),
			(["mypy", "."], "mypy"),
			# pytest as last step (may be slow)
			(["pytest", "-q"], "pytest"),
		]
		reports = []
		for cmd, name in steps:
			code, out = self._run(cmd)
			reports.append(f"[{name}] exit={code}\n{out}")
			if code != 0:
				return TestResult(False, "\n\n".join(reports))
		return TestResult(True, "\n\n".join(reports))
