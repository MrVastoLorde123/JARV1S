"""Focused M23.158 tests for the bounded learning-signal integrity boundary."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_execution_evaluation import LearningStateExecutionEvaluationStatus, LearningStateExecutionEvaluation
from src.core.learning_state_execution_learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignal,
    LearningStateExecutionLearningSignalKind,
    LearningStateExecutionLearningSignalService,
    LearningStateExecutionLearningSignalStatus,
)
from src.core.learning_state_execution_learning_state_execution_learning_signal_integrity import (
    LearningStateExecutionLearningSignalIntegrity,
    LearningStateExecutionLearningSignalIntegrityService,
    LearningStateExecutionLearningSignalIntegrityStatus,
    _signal_fingerprint,
)


class M23_158LearningSignalIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        evaluation = LearningStateExecutionEvaluation(
            evaluation_id="execution-evaluation-156",
            feedback_id="execution-feedback-155",
            outcome_id="execution-outcome-154",
            attempt_id="execution-attempt-153",
            admission_id="execution-admission-152",
            eligibility_id="execution-eligibility-151",
            handling_id="semantic-handling-150",
            consumption_id="semantic-consumption-149",
            receipt_id="semantic-receipt-148",
            handoff_id="semantic-handoff-147",
            integrity_id="semantic-use-integrity-146",
            validation_id="semantic-use-validation-145",
            semantic_use_id="semantic-use-144",
            source_request_id="consumption-request-136",
            source_request_lineage_id="semantic-use-request-143",
            source_validation_id="consumption-validation-138",
            source_validation_lineage_id="semantic-use-validation-145",
            interpretation_id="interpretation-140",
            read_id="durable-read-137",
            consumption_request_id="consumption-request-136",
            requester_id="user-1",
            consumer_id="semantic-consumer-1",
            handoff_target_id="downstream-consumer-1",
            recipient_id="semantic-recipient-1",
            handling_target_id="planning-context",
            execution_target_id="executor-1",
            authorization_scope={"actions": ["execute"], "target": "executor-1"},
            outcome_status="SUCCEEDED",
            outcome_observation={"result": "completed"},
            feedback_signal={"quality": "positive"},
            feedback_purpose="record bounded feedback for later evaluation",
            feedback_rationale={"reason": "observed terminal outcome"},
            objective="assess whether the observed execution consequence met the declared objective",
            evaluator_id="evaluator-1",
            evaluation_purpose="bounded post-execution evaluation",
            evaluation_judgment={"assessment": "meets-objective", "score": 0.9},
            evaluation_context={"objective_class": "terminal-execution", "comparison": "declared-objective"},
            payload={"feedback_id": "execution-feedback-155", "objective": "assess", "evaluation_judgment": {"assessment": "meets-objective"}},
            status=LearningStateExecutionEvaluationStatus.EVALUATED,
            reasons=("execution feedback evaluated against explicit objective",),
            lineage={
                "evaluation_id": "execution-evaluation-156",
                "feedback_id": "execution-feedback-155",
                "outcome_id": "execution-outcome-154",
                "attempt_id": "execution-attempt-153",
                "admission_id": "execution-admission-152",
                "eligibility_id": "execution-eligibility-151",
                "handling_id": "semantic-handling-150",
                "consumption_id": "semantic-consumption-149",
                "receipt_id": "semantic-receipt-148",
                "handoff_id": "semantic-handoff-147",
                "integrity_id": "semantic-use-integrity-146",
                "validation_id": "semantic-use-validation-145",
                "semantic_use_id": "semantic-use-144",
                "request_id": "semantic-use-request-143",
                "source_validation_id": "semantic-use-validation-145",
                "interpretation_id": "interpretation-140",
                "source_request_provenance_id": "consumption-request-136",
                "source_validation_provenance_id": "consumption-validation-138",
                "read_id": "durable-read-137",
                "consumption_request_id": "consumption-request-136",
            },
        )
        self.signal = LearningStateExecutionLearningSignalService().create(
            evaluation,
            signal_id="learning-signal-157",
            signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE,
            signal_purpose="represent evaluated execution evidence for a later learning mechanism",
            signal_context={"source": "execution-evaluation", "scope": "bounded"},
        )

    def _verify(self, signal=None, **kwargs):
        source = signal or self.signal
        if type(source) is not LearningStateExecutionLearningSignal:
            raise TypeError("signal must be a learning-signal artifact")
        params = {"integrity_id": "learning-signal-integrity-158", "signal_fingerprint": _signal_fingerprint(source)}
        params.update(kwargs)
        return LearningStateExecutionLearningSignalIntegrityService().verify(source, **params)

    def test_exact_signal_type_is_required(self):
        with self.assertRaises(TypeError):
            self._verify(object())

    def test_recorded_signal_produces_valid_integrity(self):
        result = self._verify()
        self.assertIsInstance(result, LearningStateExecutionLearningSignalIntegrity)
        self.assertEqual(result.status, LearningStateExecutionLearningSignalIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)

    def test_rejected_signal_fails_closed(self):
        rejected = self.signal.__class__(**{**self.signal.__dict__, "status": LearningStateExecutionLearningSignalStatus.REJECTED})
        result = self._verify(rejected, signal_fingerprint=_signal_fingerprint(rejected))
        self.assertTrue(result.is_invalid)
        self.assertIn("learning signal status must be RECORDED", result.reasons)

    def test_integrity_identity_must_be_distinct(self):
        result = self._verify(integrity_id=self.signal.signal_id)
        self.assertTrue(result.is_invalid)
        self.assertIn("integrity identity must be distinct", result.reasons)

    def test_fingerprint_must_be_sha256(self):
        with self.assertRaises(ValueError):
            self._verify(signal_fingerprint="abc")

    def test_fingerprint_mismatch_fails_closed(self):
        result = self._verify(signal_fingerprint="0" * 64)
        self.assertTrue(result.is_invalid)
        self.assertIn("learning signal fingerprint mismatch", result.reasons)
        self.assertNotEqual(result.source_signal_fingerprint, result.computed_signal_fingerprint)

    def test_fingerprint_is_deterministic(self):
        first = _signal_fingerprint(self.signal)
        second = _signal_fingerprint(self.signal)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_signal_lineage_is_checked(self):
        lineage = dict(self.signal.lineage)
        lineage["signal_id"] = "tampered-signal"
        source = self.signal.__class__(**{**self.signal.__dict__, "lineage": lineage})
        result = self._verify(source)
        self.assertIn("signal lineage mismatch", result.reasons)

    def test_evaluation_lineage_is_checked(self):
        lineage = dict(self.signal.lineage)
        lineage["evaluation_id"] = "tampered-evaluation"
        source = self.signal.__class__(**{**self.signal.__dict__, "lineage": lineage})
        result = self._verify(source)
        self.assertIn("evaluation lineage mismatch", result.reasons)

    def test_feedback_lineage_is_checked(self):
        lineage = dict(self.signal.lineage)
        lineage["feedback_id"] = "tampered-feedback"
        source = self.signal.__class__(**{**self.signal.__dict__, "lineage": lineage})
        result = self._verify(source)
        self.assertIn("feedback lineage mismatch", result.reasons)

    def test_inherited_integrity_lineage_is_checked(self):
        lineage = dict(self.signal.lineage)
        lineage["integrity_id"] = "tampered-upstream-integrity"
        source = self.signal.__class__(**{**self.signal.__dict__, "lineage": lineage})
        result = self._verify(source)
        self.assertIn("inherited integrity lineage mismatch", result.reasons)

    def test_source_request_provenance_is_checked(self):
        lineage = dict(self.signal.lineage)
        lineage["source_request_provenance_id"] = "tampered-request"
        source = self.signal.__class__(**{**self.signal.__dict__, "lineage": lineage})
        result = self._verify(source)
        self.assertIn("source request provenance mismatch", result.reasons)

    def test_source_validation_provenance_is_checked(self):
        lineage = dict(self.signal.lineage)
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        source = self.signal.__class__(**{**self.signal.__dict__, "lineage": lineage})
        result = self._verify(source)
        self.assertIn("source validation provenance mismatch", result.reasons)

    def test_upstream_evidence_is_preserved(self):
        result = self._verify()
        self.assertEqual(result.signal_id, self.signal.signal_id)
        self.assertEqual(result.evaluation_id, self.signal.evaluation_id)
        self.assertEqual(result.execution_target_id, self.signal.execution_target_id)
        self.assertEqual(result.signal_kind, self.signal.signal_kind)
        self.assertEqual(result.signal_purpose, self.signal.signal_purpose)
        self.assertEqual(result.inherited_integrity_id, self.signal.integrity_id)

    def test_signal_context_is_immutable(self):
        result = self._verify()
        self.assertIsInstance(result.signal_context, MappingProxyType)
        with self.assertRaises(TypeError):
            result.signal_context["source"] = "changed"

    def test_lineage_is_immutable(self):
        result = self._verify()
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["signal_id"] = "changed"

    def test_source_signal_is_not_mutated(self):
        before = dict(self.signal.lineage)
        self._verify()
        self.assertEqual(dict(self.signal.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._verify(reasons=("integrity evidence captured",))
        self.assertEqual(result.reasons, ("integrity evidence captured",))

    def test_integrity_has_no_learning_or_authority_power(self):
        result = self._verify()
        for name in (
            "mutates_state", "persists_state", "reads_durable_state", "rereads_durable_state",
            "interprets_state", "is_learning", "applies_learning", "authorizes_learning",
            "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor",
            "schedules_work", "plans_work", "updates_model", "mutates_memory", "mutates_policy",
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_distinct_integrity_identities_remain_distinct(self):
        first = self._verify(integrity_id="learning-signal-integrity-158-a")
        second = self._verify(integrity_id="learning-signal-integrity-158-b")
        self.assertNotEqual(first.integrity_id, second.integrity_id)
        self.assertEqual(first.signal_id, second.signal_id)

    def test_signal_fingerprint_changes_when_signal_changes(self):
        changed = self.signal.__class__(**{**self.signal.__dict__, "signal_purpose": "changed purpose"})
        self.assertNotEqual(_signal_fingerprint(self.signal), _signal_fingerprint(changed))

    def test_explicit_classification_is_preserved(self):
        result = self._verify()
        self.assertEqual(result.signal_kind, LearningStateExecutionLearningSignalKind.POSITIVE)


if __name__ == "__main__":
    unittest.main()
