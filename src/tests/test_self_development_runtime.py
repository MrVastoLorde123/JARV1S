"""Focused tests for the M16.7 self-development integration boundary."""

import unittest

from src.change_impact import ChangeImpactAssessment, ImpactLevel
from src.modification_planning import ControlledModificationPlan, ModificationStep, ModificationStepKind
from src.rollback_recovery import RecoveryStatus, RollbackRecovery
from src.safe_modification import ExecutionHandoffStatus, SafeModificationExecution
from src.self_development import SelfDevelopmentProposal
from src.self_development_runtime import (
    SelfDevelopmentIntegration,
    SelfDevelopmentIntegrationValidationError,
)
from src.test_verification import TestVerificationGate, VerificationStatus


def build_integration() -> SelfDevelopmentIntegration:
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
        plan_id="plan-1", assessment=assessment, steps=(step,)
    )
    verification = TestVerificationGate(
        gate_id="gate-1",
        plan=plan,
        status=VerificationStatus.PASSED,
        required_checks=("target tests",),
        completed_checks=("target tests",),
        evidence=("focused tests passed",),
    )
    execution = SafeModificationExecution(
        execution_id="execution-1",
        verification=verification,
        status=ExecutionHandoffStatus.READY,
        execution_scope=("src/example.py",),
    )
    recovery = RollbackRecovery(
        recovery_id="recovery-1",
        execution=execution,
        prior_state_reference="commit:previous",
        rollback_strategy="Restore previous commit.",
        status=RecoveryStatus.AVAILABLE,
    )
    return SelfDevelopmentIntegration(
        proposal=proposal,
        assessment=assessment,
        plan=plan,
        verification=verification,
        execution=execution,
        recovery=recovery,
    )


class SelfDevelopmentIntegrationTests(unittest.TestCase):
    def test_full_lineage_is_preserved(self):
        integration = build_integration()
        self.assertEqual(integration.proposal_id, "proposal-1")
        self.assertEqual(integration.assessment_id, "assessment-1")
        self.assertEqual(integration.plan_id, "plan-1")
        self.assertEqual(integration.gate_id, "gate-1")
        self.assertEqual(integration.execution_id, "execution-1")
        self.assertEqual(integration.recovery_id, "recovery-1")

    def test_components_must_share_identity_chain(self):
        integration = build_integration()
        other = build_integration()
        with self.assertRaises(SelfDevelopmentIntegrationValidationError):
            SelfDevelopmentIntegration(
                proposal=integration.proposal,
                assessment=other.assessment,
                plan=integration.plan,
                verification=integration.verification,
                execution=integration.execution,
                recovery=integration.recovery,
            )

    def test_verified_state_is_descriptive(self):
        self.assertTrue(build_integration().verified)

    def test_integration_never_reports_execution(self):
        integration = build_integration()
        self.assertFalse(integration.executed)
        self.assertFalse(integration.execution_requested)

    def test_integration_never_grants_authority(self):
        integration = build_integration()
        self.assertFalse(integration.authorization_granted)
        self.assertFalse(integration.policy_authority)
        self.assertFalse(integration.authority_scope_change)
        self.assertFalse(integration.identity_change_authorized)

    def test_recovery_state_is_exposed_without_new_authority(self):
        integration = build_integration()
        self.assertFalse(integration.recovered)
        self.assertFalse(integration.authorization_granted)

    def test_serialization_preserves_chain(self):
        data = build_integration().to_dict()
        self.assertTrue(data["self_development_integration"])
        self.assertEqual(data["proposal_id"], "proposal-1")
        self.assertEqual(data["assessment_id"], "assessment-1")
        self.assertEqual(data["plan_id"], "plan-1")
        self.assertFalse(data["executed"])
        self.assertFalse(data["authorization_granted"])

    def test_metadata_is_frozen(self):
        integration = SelfDevelopmentIntegration(
            **{**build_integration().__dict__, "metadata": {"origin": {"kind": "test"}}}
        )
        with self.assertRaises(TypeError):
            integration.metadata["new"] = "value"

    def test_integration_is_immutable(self):
        integration = build_integration()
        with self.assertRaises(AttributeError):
            integration.execution = integration.execution

    def test_mismatched_plan_rejected(self):
        integration = build_integration()
        other = build_integration()
        with self.assertRaises(SelfDevelopmentIntegrationValidationError):
            SelfDevelopmentIntegration(
                proposal=integration.proposal,
                assessment=integration.assessment,
                plan=other.plan,
                verification=integration.verification,
                execution=integration.execution,
                recovery=integration.recovery,
            )

    def test_mismatched_verification_rejected(self):
        integration = build_integration()
        other = build_integration()
        with self.assertRaises(SelfDevelopmentIntegrationValidationError):
            SelfDevelopmentIntegration(
                proposal=integration.proposal,
                assessment=integration.assessment,
                plan=integration.plan,
                verification=other.verification,
                execution=integration.execution,
                recovery=integration.recovery,
            )

    def test_mismatched_execution_rejected(self):
        integration = build_integration()
        other = build_integration()
        with self.assertRaises(SelfDevelopmentIntegrationValidationError):
            SelfDevelopmentIntegration(
                proposal=integration.proposal,
                assessment=integration.assessment,
                plan=integration.plan,
                verification=integration.verification,
                execution=other.execution,
                recovery=integration.recovery,
            )

    def test_mismatched_recovery_rejected(self):
        integration = build_integration()
        other = build_integration()
        with self.assertRaises(SelfDevelopmentIntegrationValidationError):
            SelfDevelopmentIntegration(
                proposal=integration.proposal,
                assessment=integration.assessment,
                plan=integration.plan,
                verification=integration.verification,
                execution=integration.execution,
                recovery=other.recovery,
            )

    def test_json_serialization_is_available(self):
        payload = build_integration().to_json()
        self.assertIn('"self_development_integration": true', payload)
        self.assertIn('"authorization_granted": false', payload)


if __name__ == "__main__":
    unittest.main()
