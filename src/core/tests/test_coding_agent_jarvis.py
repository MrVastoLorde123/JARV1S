from __future__ import annotations

import unittest

from src.agents.coding_confirmation import CodingAgentConfirmationService
from src.agents.coding_service import CodingAgentService
from src.agents.coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentResult,
    CodingAgentTask,
    CodingAgentVerification,
)
from src.core.coding_agent_jarvis import CodingAgentJARVIS


class FakePlanner:
    def __init__(self, plan: CodingAgentPlan) -> None:
        self.plan_value = plan
        self.calls = 0

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        self.calls += 1
        return self.plan_value


class FakeWorker:
    def __init__(self, plan: CodingAgentPlan, result: CodingAgentResult) -> None:
        self.plan_value = plan
        self.result = result
        self.planned_tasks: list[CodingAgentTask] = []
        self.executed: list[tuple[CodingAgentTask, CodingAgentPlan]] = []

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        self.planned_tasks.append(task)
        return self.plan_value

    def execute(self, task: CodingAgentTask, plan: CodingAgentPlan) -> CodingAgentResult:
        self.executed.append((task, plan))
        return self.result


class DummyAIService:
    pass


class M28CodingAgentJARVISTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task_plan = CodingAgentPlan(
            edits=(
                CodingAgentEdit(
                    path="ui/src/App.tsx",
                    content="approved",
                    overwrite=True,
                ),
            ),
            verification=CodingAgentVerification(runner="npm_build"),
            rationale="Keep the interface change minimal.",
        )
        self.result = CodingAgentResult(
            task_id="coding-jarvis-001",
            status="verified",
            edits_attempted=1,
            edits_applied=1,
            verification=None,
            message="verification passed",
        )
        self.planner = FakePlanner(self.task_plan)
        self.worker = FakeWorker(self.task_plan, self.result)
        self.coding_service = CodingAgentService(self.planner, self.worker)
        self.confirmation = CodingAgentConfirmationService()
        self.jarvis = CodingAgentJARVIS(
            ai_service=DummyAIService(),
            coding_agent_service=self.coding_service,
            coding_confirmation_service=self.confirmation,
        )

    def test_code_request_stages_exact_plan_without_execution(self) -> None:
        response = self.jarvis.ask("code: Improve the interface")

        self.assertEqual(response.metadata["route"], "CODING_AGENT")
        self.assertEqual(response.metadata["stage"], "CONFIRMATION")
        self.assertTrue(response.metadata["success"])
        self.assertEqual(len(self.worker.executed), 0)
        self.assertEqual(len(self.worker.planned_tasks), 1)
        pending = self.confirmation.get_pending()
        self.assertIsNotNone(pending)
        self.assertIs(pending.plan, self.task_plan)
        self.assertEqual(pending.operation_id, response.metadata["operation_id"])

    def test_confirm_executes_the_exact_staged_plan(self) -> None:
        response = self.jarvis.ask("code: Improve the interface")
        operation_id = response.metadata["operation_id"]

        confirmed = self.jarvis.ask(f"/CONFIRM {operation_id}")

        self.assertEqual(confirmed.metadata["route"], "CODING_AGENT")
        self.assertEqual(confirmed.metadata["stage"], "EXECUTION")
        self.assertTrue(confirmed.metadata["success"])
        self.assertEqual(len(self.worker.executed), 1)
        executed_task, executed_plan = self.worker.executed[0]
        self.assertIs(executed_plan, self.task_plan)
        self.assertEqual(executed_task.task_id, response.metadata["task_id"])
        self.assertEqual(
            executed_task.metadata["coding_operation_id"],
            operation_id,
        )

    def test_cancel_discards_pending_coding_operation(self) -> None:
        response = self.jarvis.ask("code: Improve the interface")
        operation_id = response.metadata["operation_id"]

        cancelled = self.jarvis.ask(f"/CANCEL {operation_id}")

        self.assertTrue(cancelled.metadata["success"])
        self.assertIsNone(self.confirmation.get_pending())
        self.assertEqual(len(self.worker.executed), 0)

    def test_empty_code_objective_is_rejected(self) -> None:
        response = self.jarvis.ask("code:")
        self.assertFalse(response.metadata["success"])
        self.assertEqual(response.metadata["stage"], "REQUEST")


if __name__ == "__main__":
    unittest.main()
