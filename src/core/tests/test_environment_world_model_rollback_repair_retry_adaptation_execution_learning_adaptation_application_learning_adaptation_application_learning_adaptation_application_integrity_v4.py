import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4 as A,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status as AS,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Service as AService,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_integrity_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4 as I,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4Service as IS,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4Status as S,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Service,
)


class M23_96ApplicationIntegrityV4Tests(unittest.TestCase):
    def _application(self):
        return A(
            application_id="application-96", decision_id="decision-95", proposal_id="proposal-95", source_proposal_id="source-proposal-84",
            eligibility_id="eligibility-95", integrity_id="integrity-92", signal_id="signal-90", evaluation_id="evaluation-89",
            feedback_id="feedback-88", feedback_source_id="feedback-source-88", classification_id="classification-87",
            source_integrity_id="integrity-91", source_decision_id="decision-85", outcome_id="outcome-83",
            outcome_status="SUCCEEDED", feedback_status="VALID", confidence=0.91, signal_fingerprint="a"*64,
            source_signal_fingerprint="b"*64, result_fingerprint="c"*64, application_fingerprint="d"*64,
            failure_reason=None, evaluation_status="VALID", signal_status="VALID", integrity_status="VALID",
            eligibility_status="ELIGIBLE", proposal_status=__import__(
                "src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_proposal_v4",
                fromlist=["EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status"],
            ).EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.PROPOSED,
            proposal_kind="ADAPTATION_CANDIDATE",
            decision_status=__import__(
                "src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_decision_v4",
                fromlist=["EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status"],
            ).EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.ACCEPTED,
            application_status=AS.APPLIED,
            application_result={"nested": {"value": [1, 2]}},
            reasons={"reason": {"codes": ["R1", "R2"]}}, lineage={"chain": ["decision-95", "application-96"]},
        )

    def test_valid_integrity_is_emitted(self):
        result = IS().verify(self._application(), integrity_id="application-integrity-96")
        self.assertEqual(result.integrity_status, S.VALID)
        self.assertEqual(result.integrity_id, "application-integrity-96")

    def test_complete_provenance_is_preserved(self):
        source = self._application()
        result = IS().verify(source, integrity_id="application-integrity-96")
        for name in ("application_id", "decision_id", "proposal_id", "source_proposal_id", "eligibility_id", "integrity_source_id", "signal_id", "evaluation_id", "feedback_id", "classification_id", "source_integrity_id", "source_decision_id", "outcome_id"):
            expected = source.integrity_id if name == "integrity_source_id" else getattr(source, name)
            self.assertEqual(getattr(result, name), expected)
        self.assertEqual(result.application_status, source.application_status)
        self.assertEqual(result.confidence, source.confidence)

    def test_upstream_application_fingerprint_is_preserved(self):
        source = self._application()
        result = IS().verify(source, integrity_id="application-integrity-96")
        self.assertEqual(result.source_application_fingerprint, source.application_fingerprint)
        self.assertEqual(len(result.computed_application_fingerprint), 64)

    def test_fingerprint_is_deterministic_for_mapping_key_order(self):
        left = self._application()
        right = A(
            **{**{name: getattr(left, name) for name in left.__dataclass_fields__ if name not in {"application_result", "reasons", "lineage"}},
               "application_result": {"nested": {"value": [1, 2]}},
               "reasons": {"reason": {"codes": ["R1", "R2"]}},
               "lineage": {"chain": ["decision-95", "application-96"]},}
        )
        a = IS().verify(left, integrity_id="application-integrity-a")
        b = IS().verify(right, integrity_id="application-integrity-b")
        self.assertEqual(a.computed_application_fingerprint, b.computed_application_fingerprint)

    def test_nested_reasons_and_lineage_are_immutable(self):
        result = IS().verify(self._application(), integrity_id="application-integrity-96", reasons={"x": {"items": [1]}}, lineage={"y": {"items": [2]}})
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["x"] = {}
        with self.assertRaises(TypeError):
            result.lineage["y"] = {}

    def test_source_is_not_mutated(self):
        source = self._application()
        before = source
        IS().verify(source, integrity_id="application-integrity-96")
        self.assertEqual(source, before)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            IS().verify(object(), integrity_id="application-integrity-96")

    def test_blank_integrity_id_fails_closed(self):
        with self.assertRaises(ValueError):
            IS().verify(self._application(), integrity_id=" ")

    def test_integrity_status_requires_enum(self):
        with self.assertRaises(TypeError):
            I(
                integrity_id="application-integrity-96", application_id="application-96", decision_id="decision-95", proposal_id="proposal-95", source_proposal_id="source-proposal-84", eligibility_id="eligibility-95", integrity_source_id="integrity-92", signal_id="signal-90", evaluation_id="evaluation-89", feedback_id="feedback-88", classification_id="classification-87", source_integrity_id="integrity-91", source_decision_id="decision-85", outcome_id="outcome-83", confidence=0.91, application_status=AS.APPLIED, source_application_fingerprint="d"*64, computed_application_fingerprint="e"*64, integrity_status="VALID", failure_reason=None, reasons={}, lineage={}
            )

    def test_fingerprint_shape_is_enforced(self):
        with self.assertRaises(ValueError):
            I(
                integrity_id="application-integrity-96", application_id="application-96", decision_id="decision-95", proposal_id="proposal-95", source_proposal_id="source-proposal-84", eligibility_id="eligibility-95", integrity_source_id="integrity-92", signal_id="signal-90", evaluation_id="evaluation-89", feedback_id="feedback-88", classification_id="classification-87", source_integrity_id="integrity-91", source_decision_id="decision-85", outcome_id="outcome-83", confidence=0.91, application_status=AS.APPLIED, source_application_fingerprint="bad", computed_application_fingerprint="e"*64, integrity_status=S.VALID, failure_reason=None, reasons={}, lineage={}
            )

    def test_invalid_integrity_requires_failure_reason(self):
        with self.assertRaises(ValueError):
            I(
                integrity_id="application-integrity-96", application_id="application-96", decision_id="decision-95", proposal_id="proposal-95", source_proposal_id="source-proposal-84", eligibility_id="eligibility-95", integrity_source_id="integrity-92", signal_id="signal-90", evaluation_id="evaluation-89", feedback_id="feedback-88", classification_id="classification-87", source_integrity_id="integrity-91", source_decision_id="decision-85", outcome_id="outcome-83", confidence=0.91, application_status=AS.APPLIED, source_application_fingerprint="d"*64, computed_application_fingerprint="e"*64, integrity_status=S.INVALID, failure_reason=None, reasons={}, lineage={}
            )

    def test_valid_integrity_cannot_carry_failure_reason(self):
        with self.assertRaises(ValueError):
            I(
                integrity_id="application-integrity-96", application_id="application-96", decision_id="decision-95", proposal_id="proposal-95", source_proposal_id="source-proposal-84", eligibility_id="eligibility-95", integrity_source_id="integrity-92", signal_id="signal-90", evaluation_id="evaluation-89", feedback_id="feedback-88", classification_id="classification-87", source_integrity_id="integrity-91", source_decision_id="decision-85", outcome_id="outcome-83", confidence=0.91, application_status=AS.APPLIED, source_application_fingerprint="d"*64, computed_application_fingerprint="e"*64, integrity_status=S.VALID, failure_reason="bad", reasons={}, lineage={}
            )

    def test_advisory_and_mutation_walls_are_closed(self):
        result = IS().verify(self._application(), integrity_id="application-integrity-96")
        self.assertTrue(result.is_advisory_only)
        self.assertTrue(result.observational)
        self.assertFalse(result.establishes_truth)
        for name in ("grants_authority", "updates_model", "mutates_memory", "mutates_policy", "mutates_persistence", "schedules_work", "executes_action"):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
