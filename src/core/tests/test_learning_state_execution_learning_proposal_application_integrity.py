import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_proposal_application import (
    LearningStateExecutionLearningProposalApplication,
    LearningStateExecutionLearningProposalApplicationStatus,
)
from src.core.learning_state_execution_learning_proposal_application_integrity import (
    LearningStateExecutionLearningProposalApplicationIntegrityService,
    LearningStateExecutionLearningProposalApplicationIntegrityStatus,
    _application_fingerprint,
)


class M23_163LearningProposalApplicationIntegrityTests(unittest.TestCase):
    def _make_application(self, *, malformed_lineage=False):
        lineage = {
            "application_id": "application-162",
            "decision_id": "decision-161",
        }
        if malformed_lineage:
            lineage["application_id"] = "wrong-application"
        return LearningStateExecutionLearningProposalApplication(
            application_id="application-162",
            decision_id="decision-161",
            proposal_id="proposal-160",
            eligibility_id="eligibility-159",
            integrity_id="integrity-158",
            signal_id="signal-157",
            evaluation_id="evaluation-156",
            feedback_id="feedback-155",
            outcome_id="outcome-154",
            attempt_id="attempt-153",
            admission_id="admission-152",
            eligibility_source_id="integrity-151",
            handling_id="handling-150",
            consumption_id="consumption-149",
            receipt_id="receipt-148",
            handoff_id="handoff-147",
            inherited_integrity_id="integrity-146",
            validation_id="validation-145",
            semantic_use_id="semantic-use-144",
            source_request_id="request-143",
            source_request_lineage_id="request-lineage-143",
            source_validation_id="source-validation-142",
            source_validation_lineage_id="source-validation-lineage-142",
            interpretation_id="interpretation-141",
            read_id="read-140",
            consumption_request_id="consumption-139",
            requester_id="requester-A",
            consumer_id="consumer-A",
            handoff_target_id="handoff-target-A",
            recipient_id="recipient-A",
            handling_target_id="handler-A",
            execution_target_id="executor-A",
            signal_kind="POSITIVE",
            signal_purpose="feed-learning",
            signal_context={"source": "feedback", "features": ["stable", {"score": 0.9}]},
            signal_status="RECORDED",
            source_signal_fingerprint="a" * 64,
            computed_signal_fingerprint="a" * 64,
            learner_id="learner-A",
            eligibility_purpose="future-learning",
            proposer_id="proposer-A",
            proposal_purpose="candidate-learning",
            proposed_change={"threshold": 0.95, "nested": ["stable"]},
            proposal_rationale={"why": {"score": 0.8}},
            decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate",
            decision_rationale={"basis": "bounded-review"},
            applier_id="applier-A",
            application_purpose="apply-approved-learning",
            application_rationale={"basis": ["approved", {"scope": "bounded"}]},
            application_evidence={"checks": [{"name": "decision"}]},
            status=LearningStateExecutionLearningProposalApplicationStatus.APPLIED,
            reasons=("learning proposal decision is APPROVED",),
            lineage=lineage,
        )

    def _verify(self, application=None, **kwargs):
        return LearningStateExecutionLearningProposalApplicationIntegrityService().verify(
            application or self._make_application(), integrity_id=kwargs.pop("integrity_id", "application-integrity-163"), **kwargs
        )

    def test_valid_application_produces_valid_integrity(self):
        result = self._verify()
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)
        self.assertTrue(result.validates_application)

    def test_exact_application_type_is_required(self):
        with self.assertRaises(TypeError):
            self._verify(object())

    def test_integrity_id_is_required(self):
        with self.assertRaises(ValueError):
            self._verify(integrity_id=" ")

    def test_integrity_identity_must_be_distinct(self):
        with self.assertRaises(ValueError):
            self._verify(integrity_id="application-162")

    def test_application_lineage_is_checked(self):
        result = self._verify(self._make_application(malformed_lineage=True))
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID)
        self.assertIn("application lineage mismatch", result.reasons)

    def test_decision_lineage_is_checked(self):
        application = self._make_application()
        object.__setattr__(application, "lineage", MappingProxyType({"application_id": application.application_id, "decision_id": "wrong-decision"}))
        result = self._verify(application)
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID)
        self.assertIn("decision lineage mismatch", result.reasons)

    def test_application_fingerprint_is_computed_and_preserved(self):
        application = self._make_application()
        result = self._verify(application)
        expected = _application_fingerprint(application)
        self.assertEqual(result.computed_application_fingerprint, expected)
        self.assertEqual(result.source_application_fingerprint, expected)
        self.assertEqual(len(expected), 64)

    def test_application_fingerprint_mismatch_is_reported_without_repair(self):
        application = self._make_application()
        lineage = MappingProxyType({"application_id": application.application_id, "decision_id": application.decision_id, "application_fingerprint": "b" * 64})
        object.__setattr__(application, "lineage", lineage)
        result = self._verify(application)
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID)
        self.assertIn("application fingerprint mismatch", result.reasons)
        self.assertEqual(result.source_application_fingerprint, "b" * 64)

    def test_integrity_id_is_new_and_application_provenance_is_preserved(self):
        application = self._make_application()
        result = self._verify(application)
        self.assertNotEqual(result.integrity_id, application.integrity_id)
        for field in (
            "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id", "signal_id", "evaluation_id",
            "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_source_id", "handling_id", "consumption_id",
            "receipt_id", "handoff_id", "inherited_integrity_id", "validation_id", "semantic_use_id", "source_request_id",
            "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id", "interpretation_id", "read_id",
            "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id",
            "execution_target_id", "signal_kind", "signal_purpose", "signal_context", "signal_status", "learner_id",
            "eligibility_purpose", "proposer_id", "proposal_purpose", "proposed_change", "proposal_rationale", "decision_maker_id",
            "decision_purpose", "decision_rationale", "applier_id", "application_purpose", "application_rationale", "application_evidence",
        ):
            expected = application.integrity_id if field == "source_integrity_id" else getattr(application, field)
            self.assertEqual(getattr(result, field), expected)
        self.assertIs(result.application_status, application.status)

    def test_nested_evidence_and_lineage_are_recursively_frozen(self):
        result = self._verify()
        self.assertIsInstance(result.signal_context, MappingProxyType)
        self.assertIsInstance(result.signal_context["features"], tuple)
        self.assertIsInstance(result.proposed_change, MappingProxyType)
        self.assertIsInstance(result.application_evidence, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)

    def test_reasons_are_immutable_and_preserved(self):
        result = self._verify(reasons=("caller-reason",))
        self.assertEqual(result.reasons, ("caller-reason",))
        with self.assertRaises(TypeError):
            self._verify(reasons=("ok", " "))

    def test_source_application_is_not_mutated(self):
        application = self._make_application()
        before = application.status
        self._verify(application)
        self.assertIs(application.status, before)

    def test_integrity_artifact_is_immutable(self):
        result = self._verify()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_integrity_is_deterministic_for_same_inputs(self):
        first = self._verify()
        second = self._verify()
        self.assertEqual(first, second)

    def test_integrity_has_no_learning_authority_or_execution_power(self):
        result = self._verify()
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "updates_model", "mutates_memory", "mutates_policy", "invokes_executor", "schedules_work",
            "plans_work", "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "proposes_adaptation",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
