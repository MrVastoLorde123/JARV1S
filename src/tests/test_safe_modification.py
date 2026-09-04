"""Focused tests for the M16.5 safe modification execution boundary."""

import unittest

from src.change_impact import ChangeImpactAssessment, ImpactLevel
from src.modification_planning import (
    ControlledModificationPlan,
    ModificationStep,
    ModificationStepKind,
)
from src.safe_modification import (
    ExecutionHandoffStatus,
    SafeModificationExecution,
    SafeModificationValidationError,
)
from src.self_development import SelfDevelopmentProposal
from src.test_verification import TestVerificationGate, VerificationStatus


def build_verified_execution() -> SafeModificationExecution:
    proposal = SelfDevelopmentProposal(
        proposal_id="proposal-1",
        title="Improve module",
        description="A bounded self-development proposal.",
        target="src/example.py",
        rationale="Reduce complexity.",
        expected_change="Refactor one path.",
        rollback_plan="Restore prior commit.",
        reversible=True,
    )
    assessment = ChangeImpactAssessment(
        assessment_id="assessment-1",
        proposal=proposal,
        overall_impact=ImpactLevel.LOW,
    )
    step = ModificationStep(
        step_id="step-1",
        kind=ModificationStepKind.MODIFY,
        description="Apply the planned refactor.",
        validation_gate="target tests pass",
    )
    plan = ControlledModificationPlan(
        plan_id="plan-1",
        assessment=assessment,
        steps=(step,),
    )
    verification = TestVerificationGate(
        gate_id="gate-1",
        plan=plan,
        status=VerificationStatus.PASSED,
        required_checks=("target tests",),
        completed_checks=("target tests",),
        evidence=("17 focused tests passed",),
    )
    return SafeModificationExecution(
        execution_id="execution-1",
        verification=verification,
        status=ExecutionHandoffStatus.READY,
        execution_scope=("src/example.py",),
        preconditions=("working tree is clean",),
    )


class SafeModificationTests(unittest.TestCase):
    def test_requires_verification_for_ready(self):
        execution = build_verified_execution()
        self.assertTrue(execution.verified)
        self.assertEqual(execution.status, ExecutionHandoffStatus.READY)

    def test_failed_verification_cannot_be_ready(self):
        execution = build_verified_execution()
        failed = TestVerificationGate(
            gate_id="gate-2",
            plan=execution.verification.plan,
            status=VerificationStatus.FAILED,
            required_checks=("target tests",),
            completed_checks=("target tests",),
            failed_checks=("target tests",),
        )
        with self.assertRaises(SafeModificationValidationError):
            SafeModificationExecution(
                execution_id="execution-2",
                verification=failed,
                status=ExecutionHandoffStatus.READY,
            )

    def test_default_state_is_not_executed(self):
        execution = SafeModificationExecution(
            execution_id="execution-3",
            verification=build_verified_execution().verification,
        )
        self.assertEqual(execution.status, ExecutionHandoffStatus.NOT_EXECUTED)
        self.assertFalse(execution.executed)

    def test_handed_off_requires_verification(self):
        execution = build_verified_execution().with_status(ExecutionHandoffStatus.HANDED_OFF)
        self.assertTrue(execution.verified)
        self.assertFalse(execution.executed)

    def test_blocked_can_exist_without_verification(self):
        execution = SafeModificationExecution(
            execution_id="execution-4",
            verification=build_verified_execution().verification.with_status,
        )
        self.fail("unreachable")

    def test_lineage_preserved(self):
        execution = build_verified_execution()
        self.assertEqual(execution.proposal_id, "proposal-1")
        self.assertEqual(execution.assessment_id, "assessment-1")
        self.assertEqual(execution.plan_id, "plan-1")

    def test_never_grants_authorization(self):
        execution = build_verified_execution()
        self.assertFalse(execution.authorization_granted)
        self.assertFalse(execution.policy_authority)
        self.assertFalse(execution.authority_scope_change)
        self.assertFalse(execution.identity_change_authorized)

    def test_execution_not_implied_by_ready(self):
        execution = build_verified_execution()
        self.assertEqual(execution.status, ExecutionHandoffStatus.READY)
        self.assertFalse(execution.executed)

    def test_scope_is_immutable_functional_update(self):
        execution = build_verified_execution()
        updated = execution.with_scope("src/another.py")
        self.assertEqual(execution.execution_scope, ("src/example.py",))
        self.assertEqual(updated.execution_scope, ("src/example.py", "src/another.py"))

    def test_preconditions_are_immutable_functional_update(self):
        execution = build_verified_execution()
        updated = execution.with_precondition("focused tests pass")
        self.assertEqual(len(execution.preconditions), 1)
        self.assertEqual(len(updated.preconditions), 2)

    def test_handoff_notes_are_immutable_functional_update(self):
        execution = build_verified_execution()
        updated = execution.with_handoff_note("Explicit downstream handoff only.")
        self.assertEqual(execution.handoff_notes, ())
        self.assertEqual(updated.handoff_notes, ("Explicit downstream handoff only.",))

    def test_duplicate_scope_rejected(self):
        with self.assertRaises(SafeModificationValidationError):
            build_verified_execution().with_scope("src/example.py")

    def test_duplicate_precondition_rejected(self):
        with self.assertRaises(SafeModificationValidationError):
            build_verified_execution().with_precondition("working tree is clean")

    def test_invalid_status_rejected(self):
        with self.assertRaises(SafeModificationValidationError):
            build_verified_execution().with_status("ready")

    def test_metadata_is_frozen(self):
        execution = SafeModificationExecution(
            execution_id="execution-5",
            verification=build_verified_execution().verification,
            metadata={"source": {"kind": "test"}},
        )
        with self.assertRaises(TypeError):
            execution.metadata["new"] = "value"

    def test_serialization_preserves_boundary(self):
        data = build_verified_execution().to_dict()
        self.assertTrue(data["safe_modification_execution"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["executed"])
        self.assertFalse(data["execution_requested"])

    def test_constraints_do_not_create_permission(self):
        execution = build_verified_execution()
        data = execution.to_dict()
        self.assertNotIn("permission_granted", data)

    def test_not_executed_survives_handoff_note(self):
        updated = build_verified_execution().with_handoff_note("Ready for a separate executor boundary.")
        self.assertFalse(updated.executed)

    def test_blocked_state_is_descriptive(self):
        execution = build_verified_execution().with_status(ExecutionHandoffStatus.BLOCKED)
        self.assertEqual(execution.status, ExecutionHandoffStatus.BLOCKED)
        self.assertFalse(execution.authorization_granted)
        self.assertFalse(execution.executed)


if __name__ == "__main__":
    unittest.main()
