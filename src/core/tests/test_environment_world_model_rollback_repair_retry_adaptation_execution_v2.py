import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_authorization_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_handoff_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status,
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


class M23_65AdaptationExecutionV2Tests(unittest.TestCase):
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

    def _make_handoff(self, *, ready=True):
        authorization = self._make_authorization(authorized=ready)
        return EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service().prepare(
            authorization, handoff_id="handoff-1"
        )

    def test_ready_handoff_executes_exact_payload(self):
        calls = []
        def executor(payload, environment_id):
            calls.append((payload, environment_id))
            return {"applied": True, "environment_id": environment_id}

        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
            self._make_handoff(), execution_id="execution-1", executor_id="executor:core-test", executor=executor
        )
        self.assertEqual(result.execution_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED)
        self.assertEqual(len(calls), 1)
        self.assertEqual(dict(calls[0][0]), {"operation": "adjust_threshold", "value": 0.7})
        self.assertEqual(calls[0][1], "env-1")
        self.assertEqual(len(result.result_fingerprint), 64)

    def test_blocked_handoff_is_rejected_without_executor_call(self):
        calls = []
        def executor(payload, environment_id):
            calls.append((payload, environment_id))
            return {"unexpected": True}

        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
            self._make_handoff(ready=False), execution_id="execution-1", executor_id="executor:core-test", executor=executor
        )
        self.assertEqual(result.execution_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED)
        self.assertEqual(calls, [])
        self.assertEqual(result.result_fingerprint, "0" * 64)
        self.assertIsNone(result.executor_id)

    def test_executor_failure_becomes_failed_evidence(self):
        def executor(payload, environment_id):
            raise RuntimeError("device rejected change")

        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
            self._make_handoff(), execution_id="execution-1", executor_id="executor:device-plugin", executor=executor
        )
        self.assertEqual(result.execution_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED)
        self.assertIn("device rejected change", result.failure_reason)
        self.assertEqual(result.result_fingerprint, "0" * 64)
        self.assertIsNone(result.observed_result)

    def test_non_mapping_executor_result_is_rejected(self):
        def executor(payload, environment_id):
            return ["bad"]

        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
                self._make_handoff(), execution_id="execution-1", executor_id="executor:core-test", executor=executor
            )

    def test_executor_identity_namespace_is_required(self):
        with self.assertRaises(Exception):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
                self._make_handoff(), execution_id="execution-1", executor_id="user:mero", executor=lambda payload, env: {"ok": True}
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
                object(), execution_id="execution-1", executor_id="executor:test", executor=lambda payload, env: {"ok": True}
            )

    def test_blank_execution_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
                self._make_handoff(), execution_id=" ", executor_id="executor:test", executor=lambda payload, env: {"ok": True}
            )

    def test_non_callable_executor_is_rejected(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
                self._make_handoff(), execution_id="execution-1", executor_id="executor:test", executor=None
            )

    def test_scope_mismatch_fails_closed(self):
        handoff = self._make_handoff()
        object.__setattr__(handoff, "authorization_scope", {"proposal_id": "other", "proposal_fingerprint": "b" * 64})
        with self.assertRaises(Exception):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
                handoff, execution_id="execution-1", executor_id="executor:test", executor=lambda payload, env: {"ok": True}
            )

    def test_result_is_immutable_and_source_handoff_is_unchanged(self):
        handoff = self._make_handoff()
        before = dict(handoff.__dict__)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
            handoff, execution_id="execution-1", executor_id="executor:test", executor=lambda payload, env: {"nested": {"ok": True}}
        )
        self.assertEqual(dict(handoff.__dict__), before)
        with self.assertRaises(TypeError):
            result.observed_result["nested"] = {}
        with self.assertRaises((AttributeError, TypeError)):
            result.confidence = 0.1

    def test_completed_result_fingerprint_must_match_observed_result(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2(
                execution_id="execution-1",
                handoff_id="handoff-1",
                authorization_id="authorization-1",
                validation_id="validation-1",
                proposal_id="proposal-1",
                eligibility_id="eligibility-1",
                integrity_id="integrity-1",
                signal_id="signal-1",
                evaluation_id="evaluation-1",
                feedback_id="feedback-1",
                outcome_id="outcome-1",
                preparation_id="preparation-1",
                decision_id="decision-1",
                source_proposal_id="proposal-1",
                assessment_id="assessment-1",
                environment_id="env-1",
                expected_model_id="expected",
                observed_model_id="observed",
                eligibility_status=EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE,
                proposal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED,
                validation_status=EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID,
                authorization_status=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED,
                handoff_status=EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY,
                confidence=1.0,
                signal_fingerprint="a" * 64,
                proposal_kind="ADAPTATION_CANDIDATE",
                proposal_fingerprint="b" * 64,
                handoff_fingerprint="c" * 64,
                authority_principal_id="user:mero",
                authority_kind=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER,
                authorization_scope={"proposal_id": "proposal-1", "proposal_fingerprint": "b" * 64},
                executor_id="executor:test",
                observed_result={"ok": True},
                result_fingerprint="d" * 64,
                failure_reason=None,
                execution_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED,
            )

    def test_execution_does_not_grant_authority_or_schedule(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service().execute(
            self._make_handoff(), execution_id="execution-1", executor_id="executor:test", executor=lambda payload, env: {"ok": True}
        )
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)


if __name__ == "__main__":
    unittest.main()
