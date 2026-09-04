import unittest
from types import MappingProxyType

from src.change_impact import ChangeImpactAssessment, ImpactDomain, ImpactLevel
from src.modification_planning import (
    ControlledModificationPlan,
    ModificationStep,
    ModificationStepKind,
)
from src.self_development import SelfDevelopmentProposal
from src.test_verification import (
    TestVerificationGate,
    TestVerificationValidationError,
    VerificationStatus,
)


class TestVerificationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = SelfDevelopmentProposal(
            proposal_id="proposal-1",
            title="Improve planner",
            description="Refine planning behavior.",
            target="src/modification_planning.py",
            rationale="Reduce ambiguity in self-development plans.",
            expected_change="Add stronger planning constraints.",
            affected_paths=("src/modification_planning.py",),
            validation_requirements=("planner tests",),
            rollback_plan="Restore the prior implementation.",
            reversible=True,
        )
        self.assessment = ChangeImpactAssessment(
            assessment_id="assessment-1",
            proposal=self.proposal,
            overall_impact=ImpactLevel.MEDIUM,
            affected_domains=(ImpactDomain.CODE, ImpactDomain.RUNTIME),
            reasons=("Planner logic changes can affect runtime behavior.",),
            dependency_impact=ImpactLevel.LOW,
            compatibility_impact=ImpactLevel.MEDIUM,
            rollback_feasibility=ImpactLevel.HIGH,
            confidence=0.9,
        )
        self.plan = ControlledModificationPlan(
            plan_id="plan-1",
            assessment=self.assessment,
            steps=(
                ModificationStep(
                    step_id="step-1",
                    kind=ModificationStepKind.INSPECT,
                    description="Inspect existing planner behavior.",
                    validation_gate="inspection complete",
                ),
            ),
            validation_gates=("planner tests pass",),
            rollback_checkpoints=("before modification",),
            constraints=("do not alter authority semantics",),
        )
        self.gate = TestVerificationGate(gate_id="gate-1", plan=self.plan)

    def test_lineage(self) -> None:
        self.assertEqual(self.gate.proposal_id, "proposal-1")
        self.assertEqual(self.gate.assessment_id, "assessment-1")
        self.assertEqual(self.gate.plan_id, "plan-1")

    def test_pending_is_not_verified(self) -> None:
        self.assertEqual(self.gate.status, VerificationStatus.PENDING)
        self.assertFalse(self.gate.verified)

    def test_pass_requires_checks_and_evidence(self) -> None:
        ready = (
            self.gate.with_required_check("unit tests")
            .with_completed_check("unit tests")
            .with_evidence("20 tests passed")
            .with_status(VerificationStatus.PASSED)
        )
        self.assertTrue(ready.verified)

    def test_pass_requires_all_required_checks(self) -> None:
        partial = self.gate.with_required_check("unit tests")
        with self.assertRaises(TestVerificationValidationError):
            partial.with_status(VerificationStatus.PASSED)

    def test_pass_requires_evidence(self) -> None:
        partial = self.gate.with_required_check("unit tests").with_completed_check("unit tests")
        with self.assertRaises(TestVerificationValidationError):
            partial.with_status(VerificationStatus.PASSED)

    def test_pass_cannot_contain_failed_checks(self) -> None:
        checked = (
            self.gate.with_required_check("unit tests")
            .with_completed_check("unit tests")
            .with_failed_check("unit tests")
            .with_evidence("unit tests failed")
        )
        with self.assertRaises(TestVerificationValidationError):
            checked.with_status(VerificationStatus.PASSED)

    def test_failed_requires_failed_check(self) -> None:
        with self.assertRaises(TestVerificationValidationError):
            self.gate.with_required_check("unit tests").with_status(VerificationStatus.FAILED)

    def test_completed_check_must_be_required(self) -> None:
        with self.assertRaises(TestVerificationValidationError):
            self.gate.with_completed_check("unknown")

    def test_failed_check_must_be_completed(self) -> None:
        required = self.gate.with_required_check("unit tests")
        with self.assertRaises(TestVerificationValidationError):
            required.with_failed_check("unit tests")

    def test_duplicates_rejected(self) -> None:
        required = self.gate.with_required_check("unit tests")
        with self.assertRaises(TestVerificationValidationError):
            required.with_required_check("unit tests")

    def test_evidence_duplicate_rejected(self) -> None:
        with_evidence = self.gate.with_evidence("receipt")
        with self.assertRaises(TestVerificationValidationError):
            with_evidence.with_evidence("receipt")

    def test_immutable_addition(self) -> None:
        updated = self.gate.with_required_check("unit tests")
        self.assertEqual(self.gate.required_checks, ())
        self.assertEqual(updated.required_checks, ("unit tests",))

    def test_metadata_frozen(self) -> None:
        gate = TestVerificationGate(
            gate_id="gate-2",
            plan=self.plan,
            metadata={"source": {"type": "local"}},
        )
        self.assertIsInstance(gate.metadata, MappingProxyType)
        with self.assertRaises(TypeError):
            gate.metadata["source"] = "changed"

    def test_authorization_always_false(self) -> None:
        ready = (
            self.gate.with_required_check("unit tests")
            .with_completed_check("unit tests")
            .with_evidence("20 tests passed")
            .with_status(VerificationStatus.PASSED)
        )
        self.assertFalse(ready.authorization_granted)
        self.assertFalse(ready.execution_requested)

    def test_failed_status_not_verified(self) -> None:
        gate = (
            self.gate.with_required_check("unit tests")
            .with_completed_check("unit tests")
            .with_failed_check("unit tests")
            .with_evidence("unit tests failed")
            .with_status(VerificationStatus.FAILED)
        )
        self.assertFalse(gate.verified)

    def test_serialization_preserves_wall(self) -> None:
        ready = (
            self.gate.with_required_check("unit tests")
            .with_completed_check("unit tests")
            .with_evidence("20 tests passed")
            .with_status(VerificationStatus.PASSED)
        )
        data = ready.to_dict()
        self.assertTrue(data["verification_gate"])
        self.assertTrue(data["verified"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["execution_requested"])
        self.assertFalse(data["instruction_granted"])
        self.assertFalse(data["policy_authority"])

    def test_evidence_and_notes_are_bounded_text(self) -> None:
        with self.assertRaises(TestVerificationValidationError):
            TestVerificationGate(
                gate_id="gate-3",
                plan=self.plan,
                evidence=("x" * 2049,),
            )


if __name__ == "__main__":
    unittest.main()
