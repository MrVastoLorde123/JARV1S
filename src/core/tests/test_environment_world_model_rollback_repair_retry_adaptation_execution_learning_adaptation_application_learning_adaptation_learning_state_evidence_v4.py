import unittest
from dataclasses import replace
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4 as A,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status as AS,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_decision_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status as DS,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_proposal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status as PS,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_integrity_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4 as I,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4Status as IS,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4Service as IIS,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_evidence_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4 as E,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Service as ES,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status as S,
)


class M23_97LearningStateEvidenceV4Tests(unittest.TestCase):
    def _application(self):
        return A(
            application_id="application-96", decision_id="decision-95", proposal_id="proposal-95", source_proposal_id="source-proposal-84",
            eligibility_id="eligibility-95", integrity_id="integrity-92", signal_id="signal-90", evaluation_id="evaluation-89",
            feedback_id="feedback-88", feedback_source_id="feedback-source-88", classification_id="classification-87",
            source_integrity_id="integrity-91", source_decision_id="decision-85", outcome_id="outcome-83",
            outcome_status="SUCCEEDED", feedback_status="VALID", confidence=0.91, signal_fingerprint="a"*64,
            source_signal_fingerprint="b"*64, result_fingerprint="c"*64, application_fingerprint="d"*64,
            failure_reason=None, evaluation_status="VALID", signal_status="VALID", integrity_status="VALID",
            eligibility_status="ELIGIBLE", proposal_status=PS.PROPOSED, proposal_kind="ADAPTATION_CANDIDATE",
            decision_status=DS.ACCEPTED, application_status=AS.APPLIED,
            application_result={"nested": {"value": [1, 2]}},
            reasons={"reason": {"codes": ["R1", "R2"]}}, lineage={"chain": ["decision-95", "application-96"]},
        )

    def _integrity(self):
        return IIS().verify(self._application(), integrity_id="application-integrity-96")

    def test_ready_evidence_is_emitted_for_valid_applied_integrity(self):
        result = ES().record(self._integrity(), evidence_id="learning-state-97")
        self.assertEqual(result.evidence_status, S.READY)
        self.assertEqual(result.evidence_id, "learning-state-97")

    def test_complete_provenance_is_preserved(self):
        source = self._integrity()
        result = ES().record(source, evidence_id="learning-state-97")
        for name in (
            "application_id", "integrity_id", "decision_id", "proposal_id", "source_proposal_id", "eligibility_id",
            "signal_id", "evaluation_id", "feedback_id", "classification_id", "source_integrity_id",
            "source_decision_id", "outcome_id", "confidence", "application_status", "integrity_status",
        ):
            self.assertEqual(getattr(result, name), getattr(source, name))

    def test_application_fingerprints_are_preserved(self):
        source = self._integrity()
        result = ES().record(source, evidence_id="learning-state-97")
        self.assertEqual(result.source_application_fingerprint, source.source_application_fingerprint)
        self.assertEqual(result.computed_application_fingerprint, source.computed_application_fingerprint)

    def test_nested_evidence_metadata_is_immutable(self):
        result = ES().record(self._integrity(), evidence_id="learning-state-97", evidence={"nested": {"items": [1, 2]}})
        self.assertIsInstance(result.evidence, MappingProxyType)
        self.assertIsInstance(result.evidence["nested"], MappingProxyType)
        self.assertIsInstance(result.evidence["nested"]["items"], tuple)
        with self.assertRaises(TypeError):
            result.evidence["nested"] = {}

    def test_nested_reasons_and_lineage_are_immutable(self):
        result = ES().record(self._integrity(), evidence_id="learning-state-97", reasons={"r": {"items": [1]}}, lineage={"l": {"items": [2]}})
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["r"] = {}
        with self.assertRaises(TypeError):
            result.lineage["l"] = {}

    def test_source_is_not_mutated(self):
        source = self._integrity()
        before = source
        ES().record(source, evidence_id="learning-state-97")
        self.assertEqual(source, before)

    def test_invalid_integrity_blocks_learning_state_evidence(self):
        source = replace(self._integrity(), integrity_status=IS.INVALID, failure_reason="integrity invalid")
        result = ES().record(source, evidence_id="learning-state-97")
        self.assertEqual(result.evidence_status, S.BLOCKED)
        self.assertIn("VALID integrity", result.failure_reason)

    def test_non_applied_application_blocks_learning_state_evidence(self):
        source = replace(self._integrity(), application_status=AS.NOT_APPLIED)
        result = ES().record(source, evidence_id="learning-state-97")
        self.assertEqual(result.evidence_status, S.BLOCKED)
        self.assertIn("APPLIED", result.failure_reason)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            ES().record(object(), evidence_id="learning-state-97")

    def test_blank_evidence_id_fails_closed(self):
        with self.assertRaises(ValueError):
            ES().record(self._integrity(), evidence_id=" ")

    def test_evidence_status_requires_enum(self):
        source = self._integrity()
        ready = ES().record(source, evidence_id="learning-state-97")
        with self.assertRaises(TypeError):
            replace(ready, evidence_status="READY")

    def test_blocked_evidence_requires_failure_reason(self):
        source = self._integrity()
        ready = ES().record(source, evidence_id="learning-state-97")
        with self.assertRaises(ValueError):
            replace(ready, evidence_status=S.BLOCKED, failure_reason=None)

    def test_ready_evidence_rejects_failure_reason(self):
        source = self._integrity()
        ready = ES().record(source, evidence_id="learning-state-97")
        with self.assertRaises(ValueError):
            replace(ready, failure_reason="should not exist")

    def test_advisory_and_mutation_walls_are_closed(self):
        result = ES().record(self._integrity(), evidence_id="learning-state-97")
        self.assertTrue(result.is_advisory_only)
        for name in (
            "establishes_truth", "grants_authority", "persists_state", "invokes_learner", "updates_model",
            "mutates_memory", "mutates_policy", "schedules_work", "executes_action",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
