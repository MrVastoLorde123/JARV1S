from unittest import TestCase

from src.agency.driveability import ContinuationCycle, Objective, ObjectiveState
from src.agency.execution_outcome import AgencyExecutionOutcome, AgencyOutcomeStatus, VerificationDecision, VerificationDisposition
from src.agency.lifecycle_integration import AgencyLifecycleIntegration, build_agency_lifecycle_integration
from src.agency.lifecycle_state import build_agency_lifecycle_state
from src.agency.recovery_state import reconcile_recovery
from src.agency.task_orchestration import begin_task_orchestration
from src.agency.verification_recovery import derive_recovery_decision
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus


class M41AgencyLifecycleIntegrationTests(TestCase):
    def _work(self):
        return WorkState("work-1", "finish bounded work", WorkStage.VERIFYING, WorkStatus.ACTIVE)

    def _lifecycle(self):
        work = self._work()
        plan = build_work_plan(
            work,
            (WorkPlanStep("step-1", "verify result", PlanStepKind.VERIFY, WorkRole.REVIEWER),),
            rationale="bounded integration test",
        )
        return build_agency_lifecycle_state(work, plan, begin_task_orchestration(plan))

    def _recovery(self):
        objective = Objective("objective-1", "finish bounded work", ObjectiveState.ACTIVE)
        cycle = ContinuationCycle("cycle-1", "objective-1", 0, observation_ids=("obs-1",), max_cycles=3)
        verification = VerificationDecision("exec-1", VerificationDisposition.VERIFIED, "verified", evidence_id="e1")
        decision = derive_recovery_decision(verification, objective, cycle, observation_ids=("obs-1",))
        return verification, decision, reconcile_recovery(self._work(), decision)

    def test_full_identity_chain_links_execution_verification_recovery_and_state(self):
        verification, recovery_decision, recovery = self._recovery()
        outcome = AgencyExecutionOutcome("exec-1", "verify result", AgencyOutcomeStatus.SUCCEEDED, 1, True)
        state = build_agency_lifecycle_integration(
            self._lifecycle(),
            outcome=outcome,
            verification=verification,
            recovery_decision=recovery_decision,
            recovery=recovery,
        )
        self.assertIsInstance(state, AgencyLifecycleIntegration)
        self.assertEqual("exec-1", state.execution_id)
        self.assertEqual("work-1", state.lifecycle.work.work_id)
        self.assertTrue(state.terminal)

    def test_identity_mismatch_fails_closed(self):
        _, recovery_decision, recovery = self._recovery()
        outcome = AgencyExecutionOutcome("other-exec", "verify result", AgencyOutcomeStatus.SUCCEEDED, 1, True)
        with self.assertRaises(ValueError):
            build_agency_lifecycle_integration(
                self._lifecycle(), outcome=outcome, recovery_decision=recovery_decision, recovery=recovery
            )

    def test_partial_observation_is_allowed_without_authority(self):
        state = build_agency_lifecycle_integration(
            self._lifecycle(),
            outcome=AgencyExecutionOutcome("exec-2", "verify result", AgencyOutcomeStatus.SUCCEEDED, 1, True),
        )
        context = state.to_context()
        self.assertFalse(state.authorization_granted)
        self.assertFalse(state.execution_requested)
        self.assertFalse(context["verification_present"])
        self.assertFalse(context["recovery_decision_present"])

    def test_context_is_explicitly_non_authoritative(self):
        context = build_agency_lifecycle_integration(self._lifecycle()).to_context()
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertIn("orchestration_status", context)
        self.assertIn("work_status", context)
