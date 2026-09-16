from unittest import TestCase

from src.agency.task_orchestration import (
    CoordinationAction,
    OrchestratedStep,
    OrchestrationStatus,
    StepExecutionState,
    begin_task_orchestration,
    choose_next_coordination,
    update_orchestration,
)
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus


class M33TaskOrchestrationTests(TestCase):
    def _plan(self):
        work = WorkState(
            work_id="work-33",
            objective="coordinate bounded work",
            stage=WorkStage.PLANNING,
            status=WorkStatus.ACTIVE,
            role=WorkRole.TECHNICAL_LEAD,
        )
        return build_work_plan(
            work,
            (
                WorkPlanStep("research", "Research", PlanStepKind.RESEARCH, WorkRole.RESEARCHER),
                WorkPlanStep("implement", "Implement", PlanStepKind.IMPLEMENT, WorkRole.TECHNICAL_LEAD, depends_on=("research",)),
                WorkPlanStep("verify", "Verify", PlanStepKind.VERIFY, WorkRole.REVIEWER, depends_on=("implement",)),
            ),
        )

    def test_orchestration_preserves_plan_order_and_selects_first_ready_step(self):
        orchestration = begin_task_orchestration(self._plan())
        decision = choose_next_coordination(orchestration)
        self.assertIs(CoordinationAction.START_STEP, decision.action)
        self.assertEqual("research", decision.step.step_id)
        self.assertEqual(("research", "implement", "verify"), tuple(item.step_id for item in orchestration.steps))
        self.assertEqual(OrchestrationStatus.READY, orchestration.status)

    def test_completed_step_unlocks_dependent_step_deterministically(self):
        orchestration = begin_task_orchestration(self._plan())
        orchestration = update_orchestration(orchestration, "research", StepExecutionState.COMPLETE)
        decision = choose_next_coordination(orchestration)
        self.assertIs(CoordinationAction.START_STEP, decision.action)
        self.assertEqual("implement", decision.step.step_id)
        self.assertEqual(("research",), orchestration.completed_step_ids)

    def test_dependency_gate_rejects_premature_step_progression(self):
        orchestration = begin_task_orchestration(self._plan())
        with self.assertRaises(ValueError):
            update_orchestration(orchestration, "implement", StepExecutionState.ACTIVE)
        with self.assertRaises(ValueError):
            update_orchestration(orchestration, "implement", StepExecutionState.COMPLETE)

    def test_active_blocked_and_failed_states_never_execute_actions(self):
        orchestration = begin_task_orchestration(self._plan())
        active = update_orchestration(orchestration, "research", StepExecutionState.ACTIVE)
        self.assertEqual(CoordinationAction.WAIT, choose_next_coordination(active).action)
        blocked = update_orchestration(active, "research", StepExecutionState.BLOCKED, message="needs evidence")
        self.assertEqual(OrchestrationStatus.BLOCKED, blocked.status)
        self.assertEqual(CoordinationAction.BLOCKED, choose_next_coordination(blocked).action)
        failed = update_orchestration(orchestration, "research", StepExecutionState.FAILED, message="failed")
        self.assertEqual(OrchestrationStatus.FAILED, failed.status)
        self.assertEqual(CoordinationAction.BLOCKED, choose_next_coordination(failed).action)

    def test_all_completed_steps_produce_terminal_completion(self):
        orchestration = begin_task_orchestration(self._plan())
        for step_id in ("research", "implement", "verify"):
            orchestration = update_orchestration(orchestration, step_id, StepExecutionState.COMPLETE)
        self.assertEqual(OrchestrationStatus.COMPLETE, orchestration.status)
        self.assertTrue(orchestration.terminal)
        self.assertEqual(CoordinationAction.COMPLETE, choose_next_coordination(orchestration).action)

    def test_invalid_step_and_state_contracts_are_rejected(self):
        orchestration = begin_task_orchestration(self._plan())
        with self.assertRaises(ValueError):
            update_orchestration(orchestration, "missing", StepExecutionState.COMPLETE)
        with self.assertRaises(TypeError):
            update_orchestration(orchestration, "research", "COMPLETE")
        with self.assertRaises(TypeError):
            OrchestratedStep("research", StepExecutionState.PENDING, metadata=[])
