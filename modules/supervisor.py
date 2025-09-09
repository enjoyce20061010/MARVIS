import time


class IndependentSupervisor:
	def __init__(self, max_retries: int = 3, max_minutes: int = 30, max_cost: float = 10.0):
		self.max_retries = max_retries
		self.max_minutes = max_minutes
		self.max_cost = max_cost
		self._start = time.time()

	def wall_time_minutes(self) -> float:
		return (time.time() - self._start) / 60.0

	def estimated_cost(self) -> float:
		# TODO: wire to real token/accounting
		return 0.0

	def decide(self, retry_count: int, wall_clock_minutes: float, cost: float, test_passed: bool) -> str:
		if test_passed:
			return "done"
		if retry_count + 1 >= self.max_retries:
			return "intervene"
		if wall_clock_minutes >= self.max_minutes:
			return "intervene"
		if cost >= self.max_cost:
			return "intervene"
		return "retry"
