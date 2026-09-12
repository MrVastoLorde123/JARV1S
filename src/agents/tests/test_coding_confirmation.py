from __future__ import annotations

import unittest

from src.agents.coding_confirmation import (
    CodingAgentConfirmationService,
    coding_plan_fingerprint,
)
from src.agents.coding_confirmation_models import CodingConfirmationStatus
from src.agents.coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentTask,
    CodingAgentVerification,
)


class M28CodingAgentConfirmationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = CodingAgentTask(
            objective="Improve the interface",
            task_id="coding-test-001",
            metadata={"scope": "ui"},
        )
        self.plan = CodingAgentPlan(
            edits=(
                CodingAgentEdit(
                    path="ui/src/App.tsx",
                    content="approved",
                    overwrite=True,
                ),
            ),
            verification=CodingAgentVerification(
                runner="npm_build",
            ),
            rationale="Make the smallest safe interface change.",
        )
        self.service = CodingAgentConfirmationService()

    def test_stage_preserves_exact_task_and_plan(self) -> None:
        operation = self.service.stage(self.task, self.plan)
        self.assertIs(operation.task, self.task)
        self.assertIs(operation.plan, self.plan)
        self.assertEqual(operation.status, CodingConfirmationStatus.PENDING)

    def test_stage_records_deterministic_plan_fingerprint(self) -> None:
        operation = self.service.stage(self.task, self.plan)
        self.assertEqual(
            operation.metadata["plan_fingerprint"],
            coding_plan_fingerprint(self.task, self.plan),
        )
        self.assertEqual(
            coding_plan_fingerprint(self.task, self.plan),
            coding_plan_fingerprint(self.task, self.plan),
        )

    def test_confirmation_preserves_exact_approved_plan(self) -> None:
        operation = self.service.stage(self.task, self.plan)
        confirmed = self.service.confirm(operation.operation_id)
        self.assertIsNotNone(confirmed)
        self.assertEqual(confirmed.status, CodingConfirmationStatus.CONFIRMED)
        self.assertIs(confirmed.task, self.task)
        self.assertIs(confirmed.plan, self.plan)
        self.assertFalse(confirmed.is_pending)

    def test_cancelled_operation_cannot_be_confirmed(self) -> None:
        operation = self.service.stage(self.task, self.plan)
        cancelled = self.service.cancel(operation.operation_id)
        self.assertIsNotNone(cancelled)
        self.assertEqual(cancelled.status, CodingConfirmationStatus.CANCELLED)
        self.assertIsNone(self.service.confirm(operation.operation_id))

    def test_confirmation_service_does_not_execute_tools(self) -> None:
        operation = self.service.stage(self.task, self.plan)
        confirmed = self.service.confirm(operation.operation_id)
        self.assertEqual(confirmed.status, CodingConfirmationStatus.CONFIRMED)
        self.assertIsNone(self.service.get_pending())

    def test_unknown_operation_cannot_be_confirmed_or_cancelled(self) -> None:
        self.assertIsNone(self.service.confirm("missing"))
        self.assertIsNone(self.service.cancel("missing"))


if __name__ == "__main__":
    unittest.main()
