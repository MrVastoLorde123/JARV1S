import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_authorization_decision import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision,
)
from src.core.environment_world_model_rollback_repair_retry_authorization_integrity import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity,
)
from src.core.environment_world_model_rollback_repair_retry_execution_preparation import (
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparation,
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError,
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparationService,
)


class EnvironmentWorldModelRollbackRepairRetryExecutionPreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluated_at = datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc)
        self.next_eligible_at = datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc)
        self.decision = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision(
            decision_id="decision1",
            environment_id="env1",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            eligible=True,
            evaluated_at=self.evaluated_at,
            next_eligible_at=self.next_eligible_at,
            decision="ACCEPT",
            reasons={"status": "accepted"},
            lineage={"source": "proposal"},
        )
        self.integrity = EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity(
            integrity_id="integrity1",
            environment_id="env1",
            authorization_decision_id="decision1",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            proposal_eligible=True,
            integrity_status="VALID",
            reasons={"status": "valid"},
            lineage={"source": "integrity"},
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryExecutionPreparationService()

    def prepare(self, **kwargs):
        return self.service.prepare(
            self.decision,
            self.integrity,
            preparation_id=kwargs.pop("preparation_id", "preparation1"),
            **kwargs,
        )

    def test_valid_accepted_integrity_produces_inert_preparation(self) -> None:
        result = self.prepare()
        self.assertEqual(result.preparation_id, "preparation1")
        self.assertEqual(result.authorization_decision_id, "decision1")
        self.assertEqual(result.authorization_integrity_id, "integrity1")
        self.assertTrue(result.is_non_executing)
        self.assertFalse(result.execution_started)
        self.assertFalse(result.grants_execution_authority)
        self.assertFalse(result.schedules_retry)
        self.assertFalse(result.authorizes_retry)

    def test_invalid_integrity_is_rejected(self) -> None:
        invalid = self.integrity.__class__(
            integrity_id="integrity2",
            environment_id="env1",
            authorization_decision_id="decision1",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            proposal_eligible=True,
            integrity_status="INVALID",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError):
            self.service.prepare(self.decision, invalid, preparation_id="preparation2")

    def test_deferred_integrity_is_rejected(self) -> None:
        deferred = self.integrity.__class__(
            integrity_id="integrity3",
            environment_id="env1",
            authorization_decision_id="decision1",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            requested_action="RETRY_REPAIR",
            decision="DEFER",
            proposal_eligible=True,
            integrity_status="DEFER",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError):
            self.service.prepare(self.decision, deferred, preparation_id="preparation3")

    def test_rejected_decision_is_rejected(self) -> None:
        rejected = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision(
            decision_id="decision4",
            environment_id="env1",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            eligible=True,
            evaluated_at=self.evaluated_at,
            next_eligible_at=self.next_eligible_at,
            decision="REJECT",
            reasons={},
            lineage={},
        )
        integrity = self.integrity.__class__(
            integrity_id="integrity4",
            environment_id="env1",
            authorization_decision_id="decision4",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            requested_action="RETRY_REPAIR",
            decision="REJECT",
            proposal_eligible=True,
            integrity_status="VALID",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError):
            self.service.prepare(rejected, integrity, preparation_id="preparation4")

    def test_ineligible_retry_is_rejected(self) -> None:
        ineligible = self.decision.__class__(
            decision_id="decision5",
            environment_id="env1",
            proposal_id="auth-proposal2",
            eligibility_id="eligibility2",
            action_decision_id="action-decision2",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            eligible=False,
            evaluated_at=self.evaluated_at,
            next_eligible_at=None,
            decision="REJECT",
            reasons={},
            lineage={},
        )
        integrity = self.integrity.__class__(
            integrity_id="integrity5",
            environment_id="env1",
            authorization_decision_id="decision5",
            proposal_id="auth-proposal2",
            eligibility_id="eligibility2",
            action_decision_id="action-decision2",
            requested_action="RETRY_REPAIR",
            decision="REJECT",
            proposal_eligible=False,
            integrity_status="VALID",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError):
            self.service.prepare(ineligible, integrity, preparation_id="preparation5")

    def test_identity_mismatch_fails_closed(self) -> None:
        mismatched = self.integrity.__class__(
            integrity_id="integrity6",
            environment_id="env1",
            authorization_decision_id="other-decision",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            proposal_eligible=True,
            integrity_status="VALID",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError):
            self.service.prepare(self.decision, mismatched, preparation_id="preparation6")

    def test_wrong_upstream_types_fail_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.prepare(object(), self.integrity, preparation_id="preparation7")
        with self.assertRaises(TypeError):
            self.service.prepare(self.decision, object(), preparation_id="preparation8")

    def test_preparation_id_must_be_non_empty(self) -> None:
        with self.assertRaises(ValueError):
            self.prepare(preparation_id=" ")

    def test_result_is_immutable_and_nested_evidence_is_frozen(self) -> None:
        result = self.prepare(
            preparation_id="preparation9",
            reasons={"cause": "validated"},
            lineage={"nested": {"source": "integrity"}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"
        with self.assertRaises(AttributeError):
            result.preparation_id = "changed"

    def test_source_artifacts_are_not_mutated(self) -> None:
        self.prepare(preparation_id="preparation10")
        self.assertEqual(self.decision.decision, "ACCEPT")
        self.assertEqual(self.integrity.integrity_status, "VALID")
        self.assertEqual(self.decision.requested_action, "RETRY_REPAIR")

    def test_snapshot_fields_preserve_exact_authority_lineage(self) -> None:
        result = self.prepare(preparation_id="preparation11")
        self.assertEqual(result.environment_id, self.decision.environment_id)
        self.assertEqual(result.proposal_id, self.decision.proposal_id)
        self.assertEqual(result.eligibility_id, self.decision.eligibility_id)
        self.assertEqual(result.action_decision_id, self.decision.action_decision_id)
        self.assertEqual(result.expected_model_id, self.decision.expected_model_id)
        self.assertEqual(result.observed_model_id, self.decision.observed_model_id)
        self.assertEqual(result.evaluated_at, self.decision.evaluated_at)
        self.assertEqual(result.next_eligible_at, self.decision.next_eligible_at)

    def test_custom_reasons_and_lineage_are_preserved(self) -> None:
        result = self.prepare(
            preparation_id="preparation12",
            reasons={"status": "ready-for-downstream-handoff"},
            lineage={"upstream": {"decision": "decision1", "integrity": "integrity1"}},
        )
        self.assertEqual(result.reasons["status"], "ready-for-downstream-handoff")
        self.assertEqual(result.lineage["upstream"]["decision"], "decision1")
        self.assertEqual(result.lineage["upstream"]["integrity"], "integrity1")

    def test_artifact_type_contract_is_explicit(self) -> None:
        result = self.prepare(preparation_id="preparation13")
        self.assertIsInstance(result, EnvironmentWorldModelRollbackRepairRetryExecutionPreparation)


if __name__ == "__main__":
    unittest.main()
