from __future__ import annotations

import unittest

from src.agency.work_planning import (
    PlanStepKind,
    WorkPlanStep,
    build_work_plan,
    next_ready_steps,
)
from src.agency.work_state import WorkRole, WorkStage, WorkState


class M32WorkPlanningTests(unittest.TestCase):
    def test_plan_is_anchored_to_work_state(self) -> None:
        work = WorkState(
            work_id="work-1",
            objective="Build a safe feature",
            stage=WorkStage.PLANNING,
            role=WorkRole.TECHNICAL_LEAD,
            source="user",
            evidence_cursor=4,
        )
        step = WorkPlanStep("inspect", "Inspect the repository", PlanStepKind.RESEARCH, WorkRole.RESEARCHER)
        plan = build_work_plan(work, (step,), rationale="start with evidence")

        self.assertEqual(plan.work_id, work.work_id)
        self.assertEqual(plan.objective, work.objective)
        self.assertEqual(plan.stage, work.stage)
        self.assertEqual(plan.metadata["evidence_cursor"], 4)

    def test_dependencies_define_deterministic_ready_steps(self) -> None:
        steps = (
            WorkPlanStep("inspect", "Inspect", PlanStepKind.RESEARCH, WorkRole.RESEARCHER),
            WorkPlanStep("implement", "Implement", PlanStepKind.IMPLEMENT, WorkRole.TECHNICAL_LEAD, depends_on=("inspect",)),
            WorkPlanStep("verify", "Verify", PlanStepKind.VERIFY, WorkRole.REVIEWER, depends_on=("implement",)),
        )
        work = WorkState(work_id="work-2", objective="Ship safely", stage=WorkStage.PLANNING)
        plan = build_work_plan(work, steps)

        self.assertEqual(tuple(step.step_id for step in next_ready_steps(plan)), ("inspect",))
        self.assertEqual(tuple(step.step_id for step in next_ready_steps(plan, ("inspect",))), ("implement",))
        self.assertEqual(tuple(step.step_id for step in next_ready_steps(plan, ("inspect", "implement"))), ("verify",))

    def test_planning_does_not_authorize_execution(self) -> None:
        work = WorkState(work_id="work-3", objective="Do controlled work", stage=WorkStage.PLANNING)
        step = WorkPlanStep("act", "Prepare action", PlanStepKind.IMPLEMENT, WorkRole.TECHNICAL_LEAD)
        plan = build_work_plan(work, (step,))

        self.assertFalse(hasattr(plan, "authorize"))
        self.assertFalse(hasattr(plan, "execute"))
        self.assertFalse(hasattr(plan.steps[0], "invoke"))

    def test_invalid_dependencies_are_rejected(self) -> None:
        work = WorkState(work_id="work-4", objective="Validate plan", stage=WorkStage.PLANNING)
        step = WorkPlanStep("verify", "Verify", PlanStepKind.VERIFY, WorkRole.REVIEWER, depends_on=("missing",))
        with self.assertRaises(ValueError):
            build_work_plan(work, (step,))


if __name__ == "__main__":
    unittest.main()
