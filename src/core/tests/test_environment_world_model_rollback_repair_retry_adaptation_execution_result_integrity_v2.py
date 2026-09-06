import hashlib
import json
import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_authorization_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind as AuthorityKind,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status as AuthorizationStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status as ExecutionStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_handoff_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status as HandoffStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status as ProposalStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_validation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status as ValidationStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_result_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status as IntegrityStatus,
)
from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status as EligibilityStatus,
)


def _fingerprint(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class M23_66AdaptationExecutionResultIntegrityV2Tests(unittest.TestCase):
    def setUp(self):
        self.service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Service()

    def _completed(self):
        observed = {"changed": True, "version": 7}
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2(
            execution_id="execution:66",
            handoff_id="handoff:66",
            authorization_id="authorization:66",
            validation_id="validation:66",
            proposal_id="proposal:66",
            eligibility_id="eligibility:66",
            integrity_id="learning-integrity:66",
            signal_id="signal:66",
            evaluation_id="evaluation:66",
            feedback_id="feedback:66",
            outcome_id="outcome:66",
            preparation_id="preparation:66",
            decision_id="decision:66",
            source_proposal_id="source-proposal:66",
            assessment_id="assessment:66",
            environment_id="environment:66",
            expected_model_id="model:expected",
            observed_model_id="model:observed",
            eligibility_status=EligibilityStatus.ELIGIBLE,
            proposal_status=ProposalStatus.PROPOSED,
            validation_status=ValidationStatus.VALID,
            authorization_status=AuthorizationStatus.AUTHORIZED,
            handoff_status=HandoffStatus.READY,
            confidence=0.95,
            signal_fingerprint="a" * 64,
            proposal_kind="model_patch",
            proposal_fingerprint="b" * 64,
            handoff_fingerprint="c" * 64,
            authority_principal_id="user:mero",
            authority_kind=AuthorityKind.USER,
            authorization_scope={"proposal_id": "proposal:66", "proposal_fingerprint": "b" * 64},
            executor_id="executor:test",
            observed_result=observed,
            result_fingerprint=_fingerprint(observed),
            failure_reason=None,
            execution_status=ExecutionStatus.COMPLETED,
        )

    def _failed(self):
        base = self._completed()
        data = {field: getattr(base, field) for field in base.__dataclass_fields__}
        data.update(
            observed_result=None,
            result_fingerprint="0" * 64,
            failure_reason="executor exploded",
            execution_status=ExecutionStatus.FAILED,
        )
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2(**data)

    def _rejected(self):
        base = self._completed()
        data = {field: getattr(base, field) for field in base.__dataclass_fields__}
        data.update(
            proposal_status=ProposalStatus.BLOCKED,
            authorization_status=AuthorizationStatus.DENIED,
            handoff_status=HandoffStatus.BLOCKED,
            authority_principal_id=None,
            authority_kind=None,
            authorization_scope=None,
            executor_id=None,
            observed_result=None,
            result_fingerprint="0" * 64,
            handoff_fingerprint="0" * 64,
            failure_reason="authorization denied",
            execution_status=ExecutionStatus.REJECTED,
        )
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2(**data)

    def test_completed_execution_is_valid_and_fingerprint_is_preserved(self):
        execution = self._completed()
        result = self.service.verify(execution, integrity_id="result-integrity:66")
        self.assertEqual(result.integrity_status, IntegrityStatus.VALID)
        self.assertEqual(result.result_fingerprint, execution.result_fingerprint)
        self.assertTrue(result.observed_result_integrity)

    def test_failed_execution_is_valid_failure_evidence(self):
        result = self.service.verify(self._failed(), integrity_id="result-integrity:66")
        self.assertEqual(result.integrity_status, IntegrityStatus.VALID)
        self.assertEqual(result.result_fingerprint, "0" * 64)
        self.assertEqual(result.failure_reason, "executor exploded")

    def test_rejected_execution_is_valid_without_executor_authority(self):
        result = self.service.verify(self._rejected(), integrity_id="result-integrity:66")
        self.assertEqual(result.integrity_status, IntegrityStatus.VALID)
        self.assertIsNone(result.observed_result)
        self.assertIsNone(result.executor_id)
        self.assertIsNone(result.authority_principal_id)

    def test_tampered_completed_result_becomes_invalid(self):
        execution = self._completed()
        object.__setattr__(execution, "result_fingerprint", "d" * 64)
        result = self.service.verify(execution, integrity_id="result-integrity:66")
        self.assertEqual(result.integrity_status, IntegrityStatus.INVALID)

    def test_tampered_failure_evidence_becomes_invalid(self):
        execution = self._failed()
        object.__setattr__(execution, "observed_result", {"unexpected": True})
        result = self.service.verify(execution, integrity_id="result-integrity:66")
        self.assertEqual(result.integrity_status, IntegrityStatus.INVALID)

    def test_tampered_authorization_scope_becomes_invalid(self):
        execution = self._completed()
        object.__setattr__(
            execution,
            "authorization_scope",
            MappingProxyType({"proposal_id": "proposal:other", "proposal_fingerprint": "b" * 64}),
        )
        result = self.service.verify(execution, integrity_id="result-integrity:66")
        self.assertEqual(result.integrity_status, IntegrityStatus.INVALID)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            self.service.verify(object(), integrity_id="result-integrity:66")

    def test_blank_integrity_id_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.verify(self._completed(), integrity_id=" ")

    def test_result_and_lineage_are_immutable_and_source_is_unchanged(self):
        execution = self._completed()
        original = dict(execution.observed_result)
        result = self.service.verify(
            execution,
            integrity_id="result-integrity:66",
            reasons={"r": "ok"},
            lineage={"parent": {"id": "execution:66"}},
        )
        self.assertEqual(dict(execution.observed_result), original)
        with self.assertRaises(TypeError):
            result.observed_result["changed"] = False
        with self.assertRaises(TypeError):
            result.lineage["parent"] = {}

    def test_integrity_never_authorizes_retry_or_grants_authority(self):
        result = self.service.verify(self._completed(), integrity_id="result-integrity:66")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)


if __name__ == "__main__":
    unittest.main()
