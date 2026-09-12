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
    def __init__(self, result, plan_result=None):
        self.result = result
        self.plan_result = plan_result
        self.seen_task = None
        self.seen_plan = None

    def plan(self, task):
        self.seen_task = task
        return self.plan_result

    def execute(self, task, plan):
        self.seen_task = task
        self.seen_plan = plan
        return self.result


class M28CodingAgentServiceTests(unittest.TestCase):
    def test_service_plans_without_execution(self) -> None:
        task = CodingAgentTask(objective="Improve the interface")
        plan = CodingAgentPlan(
            edits=(),
            verification=CodingAgentVerification(runner="npm_build"),
        )
        worker = FakeWorker(result="unused", plan_result=plan)
        service = CodingAgentService(FakePlanner(plan), worker)

        result = service.plan(task)

        self.assertIs(result, plan)
        self.assertIs(worker.seen_task, task)
        self.assertIsNone(worker.seen_plan)

    def test_service_executes_exactly_the_supplied_plan(self) -> None:
        task = CodingAgentTask(objective="Execute approved interface change")
        approved_plan = CodingAgentPlan(
            edits=(CodingAgentEdit(path="ui/src/App.tsx", content="approved"),),
            verification=CodingAgentVerification(runner="npm_build"),
        )
        worker = FakeWorker(result="worker-result", plan_result="unused")
        service = CodingAgentService(FakePlanner(approved_plan), worker)

        result = service.execute(task, approved_plan)

        self.assertEqual(result, "worker-result")
        self.assertIs(worker.seen_task, task)
        self.assertIs(worker.seen_plan, approved_plan)

    def test_service_rejects_wrong_task_type(self) -> None:
        planner = FakePlanner(
            CodingAgentPlan(
                edits=(),
                verification=CodingAgentVerification(runner="npm_build"),
            )
        )
        worker = FakeWorker(result="unused", plan_result="unused")
        service = CodingAgentService(planner, worker)

        with self.assertRaises(TypeError):
            service.plan("not-a-task")
        with self.assertRaises(TypeError):
            service.execute("not-a-task", planner.plan_value)

    def test_service_rejects_wrong_plan_type(self) -> None:
        task = CodingAgentTask(objective="Execute approved change")
        worker = FakeWorker(result="unused", plan_result="unused")
        service = CodingAgentService(FakePlanner("unused"), worker)

        with self.assertRaises(TypeError):
            service.execute(task, "not-a-plan")

    def test_real_worker_composition_is_constructible(self) -> None:
        from src.agents.coding_worker import CodingAgentWorker

        planner = FakePlanner(
            CodingAgentPlan(
                edits=(CodingAgentEdit(path="ui/src/App.tsx", content="x"),),
                verification=CodingAgentVerification(runner="npm_build"),
            )
        )

        class NoopInvoker:
            def invoke(self, request):
                return None

        worker = CodingAgentWorker(planner, NoopInvoker())
        service = CodingAgentService(planner, worker)

        self.assertIs(service._worker, worker)
        self.assertIs(service._planner, planner)


if __name__ == "__main__":
    unittest.main()
