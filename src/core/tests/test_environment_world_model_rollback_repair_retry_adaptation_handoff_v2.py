import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_authorization_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_handoff_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_validation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)


class M23_64AdaptationHandoffV2Tests(unittest.TestCase):
    def _make_authorization(self, *, authorized=True):
        return EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2(
            authorization_id="authorization-1",
            validation_id="validation-1",
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
            eligibility_status=(EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE if authorized else EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE),
            proposal_status=(EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED if authorized else EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED),
            validation_status=(EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID if authorized else EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.BLOCKED),
            confidence=0.8,
            signal_fingerprint="a" * 64,
            proposal_kind="ADAPTATION_CANDIDATE" if authorized else "BLOCKED_ADAPTATION_CANDIDATE",
            proposal_payload={"operation": "adjust_threshold", "value": 0.7} if authorized else None,
            proposal_fingerprint="b" * 64 if authorized else "0" * 64,
            authority_principal_id="user:mero" if authorized else None,
            authority_kind=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER if authorized else None,
            authorization_scope={"proposal_id": "proposal-1", "proposal_fingerprint": "b" * 64} if authorized else None,
            authorization_status=(EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED if authorized else EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED),
            reasons={"origin": "test"},
            lineage={"chain": {"authorization": "authorization-1"}},
        )

    def test_authorized_becomes_ready(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(self._make_authorization(), handoff_id="handoff-1")
        self.assertEqual(result.handoff_status, EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY)
        self.assertTrue(result.is_execution_ready)
        self.assertEqual(result.handoff_payload["operation"], "adjust_threshold")
        self.assertEqual(len(result.handoff_fingerprint), 64)

    def test_denied_becomes_blocked(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(self._make_authorization(authorized=False), handoff_id="handoff-1")
        self.assertEqual(result.handoff_status, EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.BLOCKED)
        self.assertFalse(result.is_execution_ready)
        self.assertIsNone(result.handoff_payload)
        self.assertEqual(result.handoff_fingerprint, "0" * 64)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(object(), handoff_id="handoff-1")

    def test_blank_handoff_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(self._make_authorization(), handoff_id=" ")

    def test_ready_preserves_exact_authorization_scope(self):
        authorization = self._make_authorization()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(authorization, handoff_id="handoff-1")
        self.assertEqual(dict(result.authorization_scope), dict(authorization.authorization_scope))
        self.assertEqual(result.proposal_id, authorization.proposal_id)
        self.assertEqual(result.proposal_fingerprint, authorization.proposal_fingerprint)

    def test_exact_proposal_payload_is_preserved(self):
        authorization = self._make_authorization()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(authorization, handoff_id="handoff-1")
        self.assertEqual(result.handoff_payload, authorization.proposal_payload)
        self.assertEqual(result.proposal_payload, authorization.proposal_payload)

    def test_fingerprint_is_deterministic(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service()
        first = service.prepare(self._make_authorization(), handoff_id="handoff-1")
        second = service.prepare(self._make_authorization(), handoff_id="handoff-2")
        self.assertEqual(first.handoff_fingerprint, second.handoff_fingerprint)

    def test_handoff_payload_scope_and_lineage_are_frozen(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(
            self._make_authorization(), handoff_id="handoff-1", lineage={"nested": {"id": "handoff-1"}}
        )
        with self.assertRaises(TypeError):
            result.handoff_payload["operation"] = "x"
        with self.assertRaises(TypeError):
            result.authorization_scope["proposal_id"] = "x"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = {}

    def test_source_authorization_is_unchanged(self):
        authorization = self._make_authorization()
        before = dict(authorization.__dict__)
        EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(authorization, handoff_id="handoff-1")
        self.assertEqual(dict(authorization.__dict__), before)

    def test_handoff_is_advisory_and_non_executing(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(self._make_authorization(), handoff_id="handoff-1")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.executes)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)

    def test_ready_constructor_rejects_denied_authorization(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2(
                **{**self._make_authorization(authorized=False).__dict__,
                   "handoff_id": "handoff-1",
                   "authorization_status": EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED,
                   "handoff_payload": {"x": 1},
                   "handoff_fingerprint": "a" * 64,
                   "handoff_status": EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY}
            )

    def test_wrong_payload_shape_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(
                self._make_authorization(), handoff_id="handoff-1", lineage=["bad"]
            )

    def test_invalid_authorization_status_fails_closed(self):
        authorization = self._make_authorization()
        object.__setattr__(authorization, "authorization_status", "AUTHORIZED")
        with self.assertRaises(Exception):
            EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(authorization, handoff_id="handoff-1")


if __name__ == "__main__":
    unittest.main()
