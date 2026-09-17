from unittest import TestCase

from src.agency.driveability import ContinuationCycle, Objective, ObjectiveState
from src.agency.execution_outcome import VerificationDecision, VerificationDisposition
from src.agency.verification_recovery import RecoveryDisposition, derive_recovery_decision


class M38VerificationRecoveryTests(TestCase):
    def _objective(self):
        return Objective("objective-1", "finish bounded work", ObjectiveState.ACTIVE)

    def _cycle(self, observation_ids=()):
        return ContinuationCycle("cycle-1", "objective-1", 0, observation_ids=tuple(observation_ids), max_cycles=3)

    def test_verified_outcome_completes_objective_without_execution_authority(self):
        decision = derive_recovery_decision(
            VerificationDecision("exec-1", VerificationDisposition.VERIFIED, "independent verification passed", evidence_id="evidence-1"),
            self._objective(), self._cycle(("obs-1",)), observation_ids=("obs-1",),
        )
        self.assertEqual(RecoveryDisposition.COMPLETE, decision.disposition)
        self.assertEqual("COMPLETED", decision.continuation.stop_reason.value)
        self.assertFalse(decision.execution_requested)
        self.assertFalse(decision.authorization_granted)

    def test_rejected_verification_can_propose_bounded_continuation(self):
        decision = derive_recovery_decision(
            VerificationDecision("exec-2", VerificationDisposition.REJECTED, "verification rejected"),
            self._objective(), self._cycle(("obs-2",)), observation_ids=("obs-2",), next_step="inspect the failed result",
        )
        self.assertEqual(RecoveryDisposition.CONTINUE, decision.disposition)
        self.assertIsNotNone(decision.continuation.proposal)
        self.assertFalse(decision.continuation.proposal.execution_requested)

    def test_blocked_and_uncertain_verification_stop_without_execution_request(self):
        blocked = derive_recovery_decision(
            VerificationDecision("exec-3", VerificationDisposition.BLOCKED, "verification unavailable"),
            self._objective(), self._cycle(), observation_ids=(),
        )
        uncertain = derive_recovery_decision(
            VerificationDecision("exec-4", VerificationDisposition.PENDING, "verification pending"),
            self._objective(), self._cycle(), observation_ids=(),
        )
        self.assertEqual(RecoveryDisposition.STOP_BLOCKED, blocked.disposition)
        self.assertEqual(RecoveryDisposition.STOP_UNCERTAIN, uncertain.disposition)
        self.assertFalse(blocked.execution_requested)
        self.assertFalse(uncertain.authorization_granted)

    def test_identity_and_input_contracts_are_rejected(self):
        with self.assertRaises(ValueError):
            derive_recovery_decision(
                VerificationDecision("exec-5", VerificationDisposition.VERIFIED, "verified", evidence_id="evidence-5"),
                self._objective(),
                ContinuationCycle("cycle-2", "other-objective", 0, max_cycles=3),
            )
        with self.assertRaises(TypeError):
            derive_recovery_decision("not verification", self._objective(), self._cycle())
