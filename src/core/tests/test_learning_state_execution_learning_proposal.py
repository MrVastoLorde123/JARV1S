import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_eligibility import (
    LearningStateExecutionLearningEligibility,
    LearningStateExecutionLearningEligibilityStatus,
)
from src.core.learning_state_execution_learning_proposal import (
    LearningStateExecutionLearningProposalService,
    LearningStateExecutionLearningProposalStatus,
)


class M23_160LearningProposalTests(unittest.TestCase):
    def _make_eligibility(self, *, status=LearningStateExecutionLearningEligibilityStatus.ELIGIBLE):
        return LearningStateExecutionLearningEligibility(
            eligibility_id="learning-eligibility-159",
            integrity_id="integrity-158",
            signal_id="signal-157",
            evaluation_id="evaluation-156",
            feedback_id="feedback-155",
            outcome_id="outcome-154",
            attempt_id="attempt-153",
            admission_id="admission-152",
            eligibility_source_id="integrity-158",
            handling_id="handling-150",
            consumption_id="consumption-149",
            receipt_id="receipt-148",
            handoff_id="handoff-147",
            inherited_integrity_id="integrity-previous",
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
            signal_context={"source": "execution-feedback", "features": ["stable"]},
            signal_status="RECORDED",
            source_signal_fingerprint="a" * 64,
            computed_signal_fingerprint="a" * 64,
            learner_id="learner-A",
            eligibility_purpose="enter-future-learning",
            status=status,
            reasons=("learning signal integrity is VALID",),
            lineage={"eligibility_id": "learning-eligibility-159", "integrity_id": "integrity-158"},
        )

    def _propose(self, eligibility=None, **kwargs):
        params = {
            "proposal_id": "proposal-160",
            "proposer_id": "proposer-A",
            "proposal_purpose": "candidate-learning",
            "proposed_change": {"threshold": 0.95},
        }
        params.update(kwargs)
        return LearningStateExecutionLearningProposalService().propose(
            eligibility or self._make_eligibility(), **params
        )

    def test_eligible_input_produces_proposal(self):
        result = self._propose()
        self.assertIs(result.status, LearningStateExecutionLearningProposalStatus.PROPOSED)
        self.assertTrue(result.is_proposed)
        self.assertFalse(result.is_rejected)

    def test_rejected_eligibility_fails_closed(self):
        result = self._propose(self._make_eligibility(status=LearningStateExecutionLearningEligibilityStatus.REJECTED))
        self.assertIs(result.status, LearningStateExecutionLearningProposalStatus.REJECTED)
        self.assertFalse(result.is_proposed)
        self.assertTrue(result.is_rejected)

    def test_exact_eligibility_type_is_required(self):
        with self.assertRaises(TypeError):
            self._propose(object())

    def test_proposal_identity_must_be_distinct(self):
        with self.assertRaises(ValueError):
            self._propose(proposal_id="learning-eligibility-159")

    def test_required_proposal_metadata_is_enforced(self):
        for kwargs in (
            {"proposal_id": " ", "proposer_id": "proposer-A", "proposal_purpose": "candidate-learning"},
            {"proposal_id": "proposal-160", "proposer_id": " ", "proposal_purpose": "candidate-learning"},
            {"proposal_id": "proposal-160", "proposer_id": "proposer-A", "proposal_purpose": " "},
        ):
            params = {"proposed_change": {"threshold": 0.95}}
            params.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self._propose(**params)
        with self.assertRaises(ValueError):
            self._propose(proposed_change=None)

    def test_upstream_provenance_is_preserved(self):
        eligibility = self._make_eligibility()
        result = self._propose(eligibility)
        for field in (
            "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id",
            "attempt_id", "admission_id", "eligibility_source_id", "handling_id", "consumption_id",
            "receipt_id", "handoff_id", "inherited_integrity_id", "validation_id", "semantic_use_id",
            "source_request_id", "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id",
            "interpretation_id", "read_id", "consumption_request_id", "requester_id", "consumer_id",
            "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id", "signal_kind",
            "signal_purpose", "signal_context", "signal_status", "source_signal_fingerprint",
            "computed_signal_fingerprint", "learner_id", "eligibility_purpose",
        ):
            self.assertEqual(getattr(result, field), getattr(eligibility, field))

    def test_proposed_change_rationale_and_lineage_are_recursively_frozen(self):
        result = self._propose(
            proposed_change={"nested": ["x", {"limit": 1}]},
            rationale={"why": {"score": 0.8}},
            lineage={"chain": ["eligibility-159", {"source": "integrity-158"}]},
        )
        self.assertIsInstance(result.proposed_change, MappingProxyType)
        self.assertEqual(result.proposed_change["nested"][1]["limit"], 1)
        self.assertIsInstance(result.rationale, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)
        self.assertIsInstance(result.lineage["chain"][1], MappingProxyType)

    def test_source_is_not_mutated_and_artifact_is_immutable(self):
        eligibility = self._make_eligibility()
        before = eligibility.status
        result = self._propose(eligibility)
        self.assertIs(eligibility.status, before)
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningProposalStatus.REJECTED
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_proposal_is_deterministic_for_same_inputs(self):
        first = self._propose()
        second = self._propose()
        self.assertEqual(first, second)

    def test_reasons_are_validated_and_preserved(self):
        result = self._propose(reasons=("bounded-candidate",))
        self.assertEqual(result.reasons, ("bounded-candidate",))
        with self.assertRaises(TypeError):
            self._propose(reasons=("ok", " "))

    def test_proposal_has_no_decision_learning_or_authority_powers(self):
        result = self._propose()
        for name in (
            "is_learning", "decides_learning", "authorizes_learning", "applies_learning", "proposes_adaptation",
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "authorizes_execution", "authorizes_retry", "invokes_learner", "updates_model", "mutates_memory",
            "mutates_policy", "invokes_executor", "schedules_work", "plans_work",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
