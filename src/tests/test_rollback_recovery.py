"""Focused tests for the M16.6 rollback and recovery boundary."""

import unittest

from src.change_impact import ChangeImpactAssessment, ImpactLevel
from src.modification_planning import ControlledModificationPlan, ModificationStep, ModificationStepKind
from src.rollback_recovery import RecoveryStatus, RollbackRecovery, RollbackRecoveryValidationError
from src.safe_modification import ExecutionHandoffStatus, SafeModificationExecution
from src.self_development import SelfDevelopmentProposal
from src.test_verification import TestVerificationGate, VerificationStatus


def build_verified_execution() -> SafeModificationExecution:
    proposal = SelfDevelopmentProposal(
        proposal_id="proposal-1", title="Improve module", description="A bounded self-development proposal.",
        target="src/example.py", rationale="Reduce complexity.", expected_change="Refactor one path.",
        rollback_plan="Restore prior commit.", reversible=True,
    )
    assessment = ChangeImpactAssessment(
        assessment_id="assessment-1", proposal=proposal, overall_impact=ImpactLevel.LOW,
    )
    step = ModificationStep(
        step_id="step-1", kind=ModificationStepKind.MODIFY,
        description="Apply the planned refactor.", validation_gate="target tests pass",
    )
    plan = ControlledModificationPlan(plan_id="plan-1", assessment=assessment, steps=(step,))
    verification = TestVerificationGate(
        gate_id="gate-1", plan=plan, status=VerificationStatus.PASSED,
        required_checks=("target tests",), completed_checks=("target tests",),
        evidence=("19 focused tests passed",),
    )
    return SafeModificationExecution(
        execution_id="execution-1", verification=verification,
        status=ExecutionHandoffStatus.READY, execution_scope=("src/example.py",),
    )


def build_recovery() -> RollbackRecovery:
    return RollbackRecovery(
        recovery_id="recovery-1",
        execution=build_verified_execution(),
        prior_state_reference="commit:abc123",
        rollback_strategy="Restore the prior known-good commit.",
        recovery_steps=("Restore prior commit",),
    )


class RollbackRecoveryTests(unittest.TestCase):
    def test_default_status_is_available(self):
        self.assertEqual(build_recovery().status, RecoveryStatus.AVAILABLE)

    def test_lineage_is_preserved(self):
        recovery = build_recovery()
        self.assertEqual(recovery.proposal_id, "proposal-1")
        self.assertEqual(recovery.assessment_id, "assessment-1")
        self.assertEqual(recovery.plan_id, "plan-1")
        self.assertEqual(recovery.execution_id, "execution-1")

    def test_requires_prior_state_reference(self):
        with self.assertRaises(RollbackRecoveryValidationError):
            RollbackRecovery(
                recovery_id="recovery-2", execution=build_verified_execution(),
                prior_state_reference="", rollback_strategy="Restore prior state.",
            )

    def test_requires_strategy(self):
        with self.assertRaises(RollbackRecoveryValidationError):
            RollbackRecovery(
                recovery_id="recovery-3", execution=build_verified_execution(),
                prior_state_reference="commit:abc123", rollback_strategy="",
            )

    def test_completed_requires_evidence(self):
        with self.assertRaises(RollbackRecoveryValidationError):
            build_recovery().with_status(RecoveryStatus.COMPLETED)

    def test_failed_requires_outcome_notes(self):
        with self.assertRaises(RollbackRecoveryValidationError):
            build_recovery().with_status(RecoveryStatus.FAILED)

    def test_active_recovery_requires_verified_execution(self):
        execution = build_verified_execution()
        failed_verification = TestVerificationGate(
            gate_id="gate-2", plan=execution.verification.plan, status=VerificationStatus.FAILED,
            required_checks=("target tests",), completed_checks=("target tests",),
            failed_checks=("target tests",),
        )
        unverified_execution = SafeModificationExecution(
            execution_id="execution-2", verification=failed_verification,
        )
        with self.assertRaises(RollbackRecoveryValidationError):
            RollbackRecovery(
                recovery_id="recovery-4", execution=unverified_execution,
                prior_state_reference="commit:abc123", rollback_strategy="Restore prior state.",
                status=RecoveryStatus.REQUESTED,
            )

    def test_completed_recovery_reports_recovered(self):
        recovery = build_recovery().with_evidence("Prior commit restored and checks passed.")
        completed = recovery.with_status(RecoveryStatus.COMPLETED)
        self.assertTrue(completed.recovered)

    def test_other_states_are_not_recovered(self):
        self.assertFalse(build_recovery().recovered)

    def test_never_grants_authorization(self):
        recovery = build_recovery()
        self.assertFalse(recovery.authorization_granted)
        self.assertFalse(recovery.execution_requested)
        self.assertFalse(recovery.authority_scope_change)

    def test_recovery_steps_are_functionally_immutable(self):
        recovery = build_recovery()
        updated = recovery.with_recovery_step("Run verification checks")
        self.assertEqual(recovery.recovery_steps, ("Restore prior commit",))
        self.assertEqual(updated.recovery_steps, ("Restore prior commit", "Run verification checks"))

    def test_evidence_is_functionally_immutable(self):
        recovery = build_recovery()
        updated = recovery.with_evidence("Checks passed after restore.")
        self.assertEqual(recovery.recovery_evidence, ())
        self.assertEqual(updated.recovery_evidence, ("Checks passed after restore.",))

    def test_outcome_notes_are_functionally_immutable(self):
        recovery = build_recovery()
        updated = recovery.with_outcome_note("Recovery completed cleanly.")
        self.assertEqual(recovery.outcome_notes, ())
        self.assertEqual(updated.outcome_notes, ("Recovery completed cleanly.",))

    def test_duplicate_recovery_step_rejected(self):
        with self.assertRaises(RollbackRecoveryValidationError):
            build_recovery().with_recovery_step("Restore prior commit")

    def test_duplicate_evidence_rejected(self):
        recovery = build_recovery().with_evidence("Checks passed after restore.")
        with self.assertRaises(RollbackRecoveryValidationError):
            recovery.with_evidence("Checks passed after restore.")

    def test_duplicate_outcome_note_rejected(self):
        recovery = build_recovery().with_outcome_note("Recovery completed cleanly.")
        with self.assertRaises(RollbackRecoveryValidationError):
            recovery.with_outcome_note("Recovery completed cleanly.")

    def test_invalid_status_rejected(self):
        with self.assertRaises(RollbackRecoveryValidationError):
            build_recovery().with_status("completed")

    def test_metadata_is_frozen(self):
        recovery = RollbackRecovery(
            recovery_id="recovery-5", execution=build_verified_execution(),
            prior_state_reference="commit:abc123", rollback_strategy="Restore prior state.",
            metadata={"source": {"kind": "test"}},
        )
        with self.assertRaises(TypeError):
            recovery.metadata["new"] = "value"

    def test_serialization_preserves_boundary(self):
        data = build_recovery().to_dict()
        self.assertTrue(data["rollback_recovery"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["execution_requested"])
        self.assertFalse(data["authority_scope_change"])
        self.assertFalse(data["policy_authority"])

    def test_recovery_does_not_request_new_execution(self):
        completed = build_recovery().with_evidence("Restore verified.").with_status(RecoveryStatus.COMPLETED)
        self.assertFalse(completed.execution_requested)

    def test_not_required_is_descriptive(self):
        recovery = build_recovery().with_status(RecoveryStatus.NOT_REQUIRED)
        self.assertFalse(recovery.recovered)


if __name__ == "__main__":
    unittest.main()
