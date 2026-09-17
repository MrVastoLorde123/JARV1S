from unittest import TestCase

from src.agency.recovery_state import reconcile_recovery
from src.agency.driveability import ContinuationCycle, DriveabilityController, Objective, ObjectiveState
from src.agency.execution_outcome import VerificationDecision, VerificationDisposition
from src.agency.task_orchestration import begin_task_orchestration
from src.agency.verification_recovery import derive_recovery_decision
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkStage, WorkState, WorkStatus
from src.agency.lifecycle_state import AgencyLifecycleState, build_agency_lifecycle_state


class M40AgencyLifecycleStateTests(TestCase):
    def _work(self):
        return WorkState("work-1", "finish bounded work", WorkStage.VERIFYING, WorkStatus.ACTIVE)

    def _plan(self):
        return build_work_plan(
            self._work(),
            (WorkPlanStep("step-1", "verify result", PlanStepKind.VERIFY),),
            "bounded lifecycle test",
        )

    def _recovery(self):
        objective = Objective("objective-1", "finish bounded work", ObjectiveState.ACTIVE)
        cycle = ContinuationCycle("cycle-1", "objective-1", 0, observation_ids=("obs-1",), max_cycles=3)
        verification = VerificationDecision("exec-1", VerificationDisposition.VERIFIED, "verified", evidence_id="e1")
        decision = derive_recovery_decision(verification, objective, cycle, observation_ids=("obs-1",))
        return reconcile_recovery(self._work(), decision)

    def test_aggregate_requires_matching_identities(self):
        work = self._work()
        plan = self._plan()
        orchestration = begin_task_orchestration(plan)
        state = build_agency_lifecycle_state(work, plan, orchestration)
        self.assertIsInstance(state, AgencyLifecycleState)
        self.assertEqual("work-1", state.work.work_id)
        self.assertEqual("step-1", state.plan.steps[0].step_id)
        self.assertFalse(state.terminal)
        self.assertFalse(state.authorization_granted if hasattr(state, "authorization_granted") else True)

    def test_recovery_can_be_attached_without_becoming_authority(self):
        work = self._work()
        plan = self._plan()
        state = build_agency_lifecycle_state(work, plan, begin_task_orchestration(plan), recovery=self._recovery())
        context = state.to_context()
        self.assertIsNotNone(state.recovery)
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertIn("recovery", context)

    def test_plan_and_orchestration_identity_is_required(self):
        work = self._work()
        plan = self._plan()
        orchestration = begin_task_orchestration(plan)
        mismatched = build_work_plan(work, (WorkPlanStep("step-2", "other", PlanStepKind.REVIEW),), "other")
        with self.assertRaises(ValueError):
            build_agency_lifecycle_state(work, mismatched, orchestration)
