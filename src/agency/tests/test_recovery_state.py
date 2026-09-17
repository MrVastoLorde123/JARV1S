from unittest import TestCase

from src.agency.driveability import (
    ContinuationCycle,
    DriveabilityController,
    NextStepProposal,
    Objective,
    ObjectiveState,
)
from src.agency.execution_outcome import VerificationDecision, VerificationDisposition
from src.agency.recovery_state import RecoveryStateDisposition, reconcile_recovery
from src.agency.verification_recovery import derive_recovery_decision
from src.agency.work_state import WorkStage, WorkState, WorkStatus


class M39RecoveryStateTests(TestCase):
    def _objective(self):
        return Objective("objective-1", "finish bounded work", ObjectiveState.ACTIVE)

    def _cycle(self):
        return ContinuationCycle("cycle-1", "objective-1", 0, observation_ids=("obs-1",), max_cycles=3)

    def _work(self):
        return WorkState("work-1", "finish bounded work", stage=WorkStage.VERIFYING, status=WorkStatus.ACTIVE)

    def _decision(self, disposition, *, next_step=None):
        return derive_recovery_decision(
            VerificationDecision("exec-1", disposition, "verification result"),
            self._objective(),
            self._cycle(),
            observation_ids=("obs-1",),
            next_step=next_step,
        )

    def test_verified_recovery_closes_work_state(self):
        decision = derive_recovery_decision(
            VerificationDecision("exec-1", VerificationDisposition.VERIFIED, "verified", evidence_id="evidence-1"),
            self._objective(), self._cycle(), observation_ids=("obs-1",),
        )
        reconciliation = reconcile_recovery(self._work(), decision)
        self.assertEqual(RecoveryStateDisposition.COMPLETED, reconciliation.disposition)
        self.assertEqual(WorkStage.COMPLETE, reconciliation.after.stage)
        self.assertEqual(WorkStatus.COMPLETE, reconciliation.after.status)
        self.assertEqual(1.0, reconciliation.after.progress)
        self.assertFalse(reconciliation.after.metadata["authorization_granted"] if "authorization_granted" in reconciliation.after.metadata else False)

    def test_rejected_recovery_reopens_planning_without_execution_authority(self):
        decision = self._decision(VerificationDisposition.REJECTED, next_step="inspect the failed result")
        reconciliation = reconcile_recovery(self._work(), decision)
        self.assertEqual(RecoveryStateDisposition.CONTINUING, reconciliation.disposition)
        self.assertEqual(WorkStage.PLANNING, reconciliation.after.stage)
        self.assertEqual(WorkStatus.ACTIVE, reconciliation.after.status)
        self.assertEqual("inspect the failed result", reconciliation.after.current_step)
        self.assertEqual("exec-1", reconciliation.after.metadata["recovery_execution_id"])
        self.assertIsInstance(decision.continuation.proposal, NextStepProposal)
        self.assertFalse(decision.execution_requested)
        self.assertFalse(decision.authorization_granted)

    def test_blocked_and_uncertain_recovery_become_operational_blocks(self):
        blocked = self._decision(VerificationDisposition.BLOCKED)
        uncertain = self._decision(VerificationDisposition.PENDING)
        blocked_state = reconcile_recovery(self._work(), blocked).after
        uncertain_state = reconcile_recovery(self._work(), uncertain).after
        self.assertEqual((WorkStage.BLOCKED, WorkStatus.BLOCKED), (blocked_state.stage, blocked_state.status))
        self.assertEqual((WorkStage.VERIFYING, WorkStatus.BLOCKED), (uncertain_state.stage, uncertain_state.status))
        self.assertEqual("BLOCKING", blocked_state.blockers[-1].severity)
        self.assertEqual("UNCERTAIN", uncertain_state.blockers[-1].severity)

    def test_rejected_without_bounded_proposal_fails_closed(self):
        controller = DriveabilityController()
        decision = derive_recovery_decision(
            VerificationDecision("exec-2", VerificationDisposition.REJECTED, "verification rejected"),
            self._objective(),
            ContinuationCycle("cycle-2", "objective-1", 2, parent_cycle_id="cycle-1", observation_ids=(), max_cycles=3),
            observation_ids=(),
            controller=controller,
            next_step="cannot continue",
        )
        reconciliation = reconcile_recovery(self._work(), decision)
        self.assertEqual(RecoveryStateDisposition.FAILED, reconciliation.disposition)
        self.assertEqual(WorkStage.FAILED, reconciliation.after.stage)
        self.assertEqual(WorkStatus.FAILED, reconciliation.after.status)

    def test_identity_and_input_contracts_are_rejected(self):
        with self.assertRaises(TypeError):
            reconcile_recovery("not work state", self._decision(VerificationDisposition.PENDING))
        with self.assertRaises(TypeError):
            reconcile_recovery(self._work(), "not recovery")
        decision = self._decision(VerificationDisposition.REJECTED, next_step="continue")
        with self.assertRaises(ValueError):
            from src.agency.recovery_state import RecoveryReconciliation
            RecoveryReconciliation("other-work", decision.execution_id, decision, self._work(), self._work(), RecoveryStateDisposition.CONTINUING, {})
