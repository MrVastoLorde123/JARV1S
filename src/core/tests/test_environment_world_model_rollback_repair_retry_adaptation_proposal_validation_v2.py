import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_validation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status,
)


class M23_62AdaptationProposalValidationV2Tests(unittest.TestCase):
    def _make_proposal(self, *, proposed: bool = True, payload=None):
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
                if proposed
                else EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE
            ),
            signal_status=EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL,
            confidence=0.8,
            signal_fingerprint="a" * 64,
            proposal_kind="ADAPTATION_CANDIDATE" if proposed else "BLOCKED_ADAPTATION_CANDIDATE",
            proposal_status=(
                EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED
                if proposed
                else EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED
            ),
            proposal_payload=(
                {"operation": "adjust_threshold", "value": 0.7}
                if payload is None and proposed
                else payload
            ),
            reasons={"origin": "test"},
            lineage={"chain": {"proposal": "proposal-1"}},
        )

    def test_proposed_becomes_valid_with_deterministic_fingerprint(self):
        proposal = self._make_proposal()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service().validate(
            proposal, validation_id="validation-1"
        )
        self.assertEqual(result.validation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID)
        self.assertEqual(len(result.proposal_fingerprint), 64)

    def test_same_proposal_produces_same_fingerprint(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service()
        first = service.validate(self._make_proposal(), validation_id="validation-1")
        second = service.validate(self._make_proposal(), validation_id="validation-2")
        self.assertEqual(first.proposal_fingerprint, second.proposal_fingerprint)

    def test_blocked_proposal_remains_blocked(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service().validate(
            self._make_proposal(proposed=False), validation_id="validation-1"
        )
        self.assertEqual(result.validation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.BLOCKED)
        self.assertEqual(result.proposal_fingerprint, "0" * 64)
        self.assertIsNone(result.proposal_payload)

    def test_constructor_rejects_valid_inconsistent_status(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2(
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
                expected_model_id="expected",
                observed_model_id="observed",
                eligibility_status=EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE,
                signal_status=EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL,
                confidence=1.0,
                signal_fingerprint="a" * 64,
                proposal_kind="ADAPTATION_CANDIDATE",
                proposal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED,
                proposal_payload={"x": 1},
                proposal_fingerprint="a" * 64,
                validation_status=EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID,
            )

    def test_validation_id_is_required(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service().validate(
                self._make_proposal(), validation_id=" "
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service().validate(
                object(), validation_id="validation-1"
            )

    def test_payload_must_be_non_empty_mapping_for_proposed(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service()
        with self.assertRaises(ValueError):
            service.validate(self._make_proposal(payload={}), validation_id="validation-1")
        with self.assertRaises(ValueError):
            service.validate(self._make_proposal(payload=None), validation_id="validation-1")

    def test_nested_payload_reasons_and_lineage_are_frozen(self):
        payload = {"nested": {"inner": "value"}}
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service().validate(
            self._make_proposal(payload=payload),
            validation_id="validation-1",
            reasons={"nested": {"reason": "frozen"}},
            lineage={"levels": [{"id": "proposal-1"}]},
        )
        with self.assertRaises(TypeError):
            result.proposal_payload["nested"] = {}
        with self.assertRaises(TypeError):
            result.reasons["nested"] = {}
        with self.assertRaises(TypeError):
            result.lineage["levels"] = []

    def test_validation_is_immutable_advisory_and_source_is_unchanged(self):
        proposal = self._make_proposal()
        before = proposal
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service().validate(
            proposal, validation_id="validation-1"
        )
        self.assertIs(result.proposal_payload.__class__.__name__ != "dict", True)
        self.assertTrue(result.is_advisory_only)
        self.assertTrue(result.validates_representation_only)
        self.assertFalse(result.authorizes_adaptation)
        self.assertFalse(result.permits_adaptation)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes)
        self.assertEqual(proposal.proposal_id, before.proposal_id)
        with self.assertRaises((AttributeError, TypeError)):
            result.confidence = 0.2

    def test_provenance_is_preserved(self):
        proposal = self._make_proposal()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service().validate(
            proposal, validation_id="validation-1"
        )
        self.assertEqual(result.eligibility_id, proposal.eligibility_id)
        self.assertEqual(result.integrity_id, proposal.integrity_id)
        self.assertEqual(result.signal_id, proposal.signal_id)
        self.assertEqual(result.signal_fingerprint, proposal.signal_fingerprint)
        self.assertEqual(result.lineage["proposal_id"], proposal.proposal_id)


if __name__ == "__main__":
    unittest.main()
