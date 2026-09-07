import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_proposal import (
    LearningStateExecutionLearningProposal,
    LearningStateExecutionLearningProposalStatus,
)
from src.core.learning_state_execution_learning_proposal_decision import (
    LearningStateExecutionLearningProposalDecisionService,
    LearningStateExecutionLearningProposalDecisionStatus,
)


class M23_161LearningProposalDecisionTests(unittest.TestCase):
    def _make_proposal(self, *, status=LearningStateExecutionLearningProposalStatus.PROPOSED):
        return LearningStateExecutionLearningProposal(
            proposal_id="proposal-160",
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
            signal_context={"source": "execution-feedback", "features": ["stable", {"score": 0.9}]},
            signal_status="RECORDED",
            source_signal_fingerprint="a" * 64,
            computed_signal_fingerprint="a" * 64,
            learner_id="learner-A",
            eligibility_purpose="enter-future-learning",
            proposer_id="proposer-A",
            proposal_purpose="candidate-learning",
            proposed_change={"threshold": 0.95, "nested": ["stable"]},
            rationale={"why": {"score": 0.8}},
            status=status,
            reasons=("learning eligibility is ELIGIBLE",),
            lineage={"proposal_id": "proposal-160", "eligibility_id": "learning-eligibility-159"},
        )

    def _decide(self, proposal=None, **kwargs):
        params = {
            "decision_id": "decision-161",
            "decision_maker_id": "decision-maker-A",
            "decision_purpose": "review-candidate",
            "decision_rationale": {"basis": "bounded-review"},
        }
        params.update(kwargs)
        return LearningStateExecutionLearningProposalDecisionService().decide(
            proposal or self._make_proposal(), **params
        )

    def test_proposed_input_is_approved(self):
        result = self._decide()
        self.assertIs(result.status, LearningStateExecutionLearningProposalDecisionStatus.APPROVED)
        self.assertTrue(result.is_approved)
        self.assertTrue(result.decides_learning)
        self.assertFalse(result.authorizes_learning)

    def test_rejected_proposal_fails_closed(self):
        result = self._decide(self._make_proposal(status=LearningStateExecutionLearningProposalStatus.REJECTED))
        self.assertIs(result.status, LearningStateExecutionLearningProposalDecisionStatus.REJECTED)
        self.assertTrue(result.is_rejected)
        self.assertFalse(result.is_approved)

    def test_exact_proposal_type_is_required(self):
        with self.assertRaises(TypeError):
            self._decide(object())

    def test_decision_identity_must_be_distinct(self):
        with self.assertRaises(ValueError):
            self._decide(decision_id="proposal-160")

    def test_required_decision_metadata_is_enforced(self):
        service = LearningStateExecutionLearningProposalDecisionService()
        proposal = self._make_proposal()
        for field, value in (("decision_id", " "), ("decision_maker_id", " "), ("decision_purpose", " ")):
            kwargs = {
                "decision_id": "decision-161",
                "decision_maker_id": "decision-maker-A",
                "decision_purpose": "review-candidate",
                "decision_rationale": {"basis": "bounded-review"},
            }
            kwargs[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                service.decide(proposal, **kwargs)
        with self.assertRaises(ValueError):
            service.decide(
                proposal,
                decision_id="decision-161",
                decision_maker_id="decision-maker-A",
                decision_purpose="review-candidate",
                decision_rationale=None,
            )

    def test_upstream_provenance_is_preserved(self):
        proposal = self._make_proposal()
        result = self._decide(proposal)
        for field in (
            "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id",
            "attempt_id", "admission_id", "eligibility_source_id", "handling_id", "consumption_id", "receipt_id",
            "handoff_id", "inherited_integrity_id", "validation_id", "semantic_use_id", "source_request_id",
            "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id", "interpretation_id",
            "read_id", "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id", "recipient_id",
            "handling_target_id", "execution_target_id", "signal_kind", "signal_purpose", "signal_context", "signal_status",
            "source_signal_fingerprint", "computed_signal_fingerprint", "learner_id", "eligibility_purpose", "proposer_id",
            "proposal_purpose",
        ):
            self.assertEqual(getattr(result, field), getattr(proposal, field))
        self.assertEqual(result.proposed_change, proposal.proposed_change)
        self.assertEqual(result.proposal_rationale, proposal.rationale)

    def test_decision_rationale_and_lineage_are_recursively_frozen(self):
        result = self._decide(
            decision_rationale={"basis": ["reviewed", {"score": 0.9}]},
            lineage={"chain": ["proposal-160", {"source": "eligibility-159"}]},
        )
        self.assertIsInstance(result.decision_rationale, MappingProxyType)
        self.assertEqual(result.decision_rationale["basis"], ("reviewed", MappingProxyType({"score": 0.9})))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)

    def test_source_is_not_mutated_and_artifact_is_immutable(self):
        proposal = self._make_proposal()
        before = proposal.status
        result = self._decide(proposal)
        self.assertIs(proposal.status, before)
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningProposalDecisionStatus.REJECTED
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_decision_is_deterministic_for_same_inputs(self):
        first = self._decide()
        second = self._decide()
        self.assertEqual(first, second)

    def test_reasons_are_validated_and_preserved(self):
        result = self._decide(reasons=("human-review-complete",))
        self.assertEqual(result.reasons, ("human-review-complete",))
        with self.assertRaises(TypeError):
            self._decide(reasons=("ok", " "))

    def test_decision_has_no_application_learning_or_authority_powers(self):
        result = self._decide()
        for name in (
            "is_learning", "authorizes_learning", "applies_learning", "proposes_adaptation",
            "authorizes_execution", "authorizes_retry", "invokes_learner", "updates_model",
            "mutates_memory", "mutates_policy", "invokes_executor", "schedules_work", "plans_work",
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
