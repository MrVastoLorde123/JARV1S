import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_authorization_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Error,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_validation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service,
)
from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)


class M23_63AdaptationAuthorizationV2Tests(unittest.TestCase):
    def _make_proposal(self, *, proposed=True):
        return EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2(
            proposal_id="proposal-1",
            eligibility_id="eligibility-1",
            integrity_id="integrity-1",
            signal_id="signal-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            outcome_id="outcome-1",
            execution_id="execution-1",
            preparation_id="preparation-1",
            decision_id="decision-1",
            source_proposal_id="proposal-1",
            assessment_id="assessment-1",
            environment_id="env-1",
            expected_model_id="model-expected",
            observed_model_id="model-observed",
            eligibility_status=(
                EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE
                if proposed else EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE
            ),
            signal_status=EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL,
            confidence=0.8,
            signal_fingerprint="a" * 64,
            proposal_kind="ADAPTATION_CANDIDATE" if proposed else "BLOCKED_ADAPTATION_CANDIDATE",
            proposal_status=(
                EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED
                if proposed else EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED
            ),
            proposal_payload={"operation": "adjust_threshold", "value": 0.7} if proposed else None,
            reasons={"origin": "test"},
            lineage={"chain": {"proposal": "proposal-1"}},
        )

    def _make_validation(self, *, proposed=True):
        proposal = self._make_proposal(proposed=proposed)
        return EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service().validate(
            proposal, validation_id="validation-1"
        )

    def _scope(self, validation):
        return {
            "proposal_id": validation.proposal_id,
            "proposal_fingerprint": validation.proposal_fingerprint,
        }

    def _authorize(self, validation):
        return EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service().authorize(
            validation,
            authorization_id="authorization-1",
            authority_principal_id="user:user-1",
            authority_kind=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER,
            authorization_scope=self._scope(validation),
        )

    def test_validated_proposal_requires_explicit_user_authority(self):
        result = self._authorize(self._make_validation())
        self.assertEqual(result.authorization_status, EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED)
        self.assertTrue(result.authorizes_adaptation)
        self.assertTrue(result.permits_adaptation)
        self.assertEqual(result.authority_principal_id, "user:user-1")

    def test_blocked_validation_can_never_receive_authorization(self):
        validation = self._make_validation(proposed=False)
        result = self._authorize(validation)
        self.assertEqual(result.authorization_status, EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED)
        self.assertFalse(result.authorizes_adaptation)
        self.assertIsNone(result.authority_principal_id)
        self.assertIsNone(result.authorization_scope)

    def test_authorization_scope_must_bind_exact_proposal_and_fingerprint(self):
        validation = self._make_validation()
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Error):
            EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service().authorize(
                validation,
                authorization_id="authorization-1",
                authority_principal_id="user:user-1",
                authority_kind=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER,
                authorization_scope={"proposal_id": validation.proposal_id, "proposal_fingerprint": "b" * 64},
            )

    def test_non_user_authority_kind_fails_closed(self):
        validation = self._make_validation()
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service().authorize(
                validation,
                authorization_id="authorization-1",
                authority_principal_id="system:jarvis",
                authority_kind="SYSTEM",
                authorization_scope=self._scope(validation),
            )

    def test_non_external_principal_namespace_fails_closed(self):
        validation = self._make_validation()
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Error):
            EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service().authorize(
                validation,
                authorization_id="authorization-1",
                authority_principal_id="jarvis",
                authority_kind=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER,
                authorization_scope=self._scope(validation),
            )

    def test_blank_authorization_id_is_rejected(self):
        validation = self._make_validation()
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service().authorize(
                validation,
                authorization_id=" ",
                authority_principal_id="user:user-1",
                authority_kind=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER,
                authorization_scope=self._scope(validation),
            )

    def test_blank_authority_principal_is_rejected(self):
        validation = self._make_validation()
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service().authorize(
                validation,
                authorization_id="authorization-1",
                authority_principal_id=" ",
                authority_kind=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER,
                authorization_scope=self._scope(validation),
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service().authorize(
                object(),
                authorization_id="authorization-1",
                authority_principal_id="user:user-1",
                authority_kind=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER,
                authorization_scope={"proposal_id": "proposal-1", "proposal_fingerprint": "a" * 64},
            )

    def test_authorization_is_immutable_proposal_scoped_and_non_executing(self):
        result = self._authorize(self._make_validation())
        self.assertTrue(result.is_external_user_authorized)
        self.assertFalse(result.grants_broader_authority)
        self.assertFalse(result.self_authorizes)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes)
        with self.assertRaises((AttributeError, TypeError)):
            result.authority_principal_id = "user:user-2"

    def test_payload_scope_and_lineage_are_recursive_immutable(self):
        validation = self._make_validation()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service().authorize(
            validation,
            authorization_id="authorization-1",
            authority_principal_id="user:user-1",
            authority_kind=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER,
            authorization_scope=self._scope(validation),
            lineage={"levels": [{"authorization": "authorization-1"}]},
        )
        with self.assertRaises(TypeError):
            result.authorization_scope["proposal_id"] = "other"
        with self.assertRaises(TypeError):
            result.proposal_payload["operation"] = "other"
        with self.assertRaises(TypeError):
            result.lineage["levels"] = []

    def test_provenance_and_exact_payload_are_preserved(self):
        validation = self._make_validation()
        result = self._authorize(validation)
        self.assertEqual(result.validation_id, validation.validation_id)
        self.assertEqual(result.proposal_id, validation.proposal_id)
        self.assertEqual(result.proposal_fingerprint, validation.proposal_fingerprint)
        self.assertEqual(result.proposal_payload, validation.proposal_payload)
        self.assertEqual(result.signal_fingerprint, validation.signal_fingerprint)
        self.assertEqual(dict(result.authorization_scope), self._scope(validation))

    def test_authorized_constructor_rejects_missing_external_authority(self):
        validation = self._make_validation()
        result = self._authorize(validation)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2(
                **{**result.__dict__, "authority_principal_id": None}
            )


if __name__ == "__main__":
    unittest.main()
