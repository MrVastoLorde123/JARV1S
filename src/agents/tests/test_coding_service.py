from __future__ import annotations

import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentTask,
    CodingAgentVerification,
)


class FakePlanner:
    def __init__(self, plan):
        self.plan_value = plan
        self.seen_task = None

    def plan(self, task):
        self.seen_task = task
        return self.plan_value


class FakeWorker:
    def __init__(self, result):
        self.result = result
        self.seen_task = None

    def run(self, task):
        self.seen_task = task
        return self.result


class M28CodingAgentServiceTests(unittest.TestCase):
    def test_service_delegates_task_to_worker(self) -> None:
        task = CodingAgentTask(objective="Improve the interface")
        plan = CodingAgentPlan(
            edits=(),
            verification=CodingAgentVerification(runner="npm_build"),
        )
        planner = FakePlanner(plan)
        worker = FakeWorker(result="worker-result")
        service = CodingAgentService(planner, worker)

        result = service.execute(task)

        self.assertEqual(result, "worker-result")
        self.assertIs(worker.seen_task, task)

    def test_service_rejects_wrong_task_type(self) -> None:
        planner = FakePlanner(
            CodingAgentPlan(
                edits=(),
                verification=CodingAgentVerification(runner="npm_build"),
            )
        )
        worker = FakeWorker(result="unused")
        service = CodingAgentService(planner, worker)

        with self.assertRaises(TypeError):
            service.execute("not-a-task")

    def test_real_worker_composition_is_constructible(self) -> None:
        from src.agents.coding_worker import CodingAgentWorker

        planner = FakePlanner(
            CodingAgentPlan(
                edits=(CodingAgentEdit(path="ui/src/App.tsx", content="x"),),
                verification=CodingAgentVerification(runner="npm_build"),
            )
        )
        worker = CodingAgentWorker(planner, lambda request: None)
        service = CodingAgentService(planner, worker)

        self.assertIs(service._worker, worker)
        self.assertIs(service._planner, planner)


if __name__ == "__main__":
    unittest.main()
