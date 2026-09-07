import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_proposal_decision import (
    LearningStateExecutionLearningProposalDecisionService,
    LearningStateExecutionLearningProposalDecisionStatus,
)
from src.core.learning_state_execution_learning_proposal_application import (
    LearningStateExecutionLearningProposalApplicationService,
    LearningStateExecutionLearningProposalApplicationStatus,
)
from src.core.learning_state_execution_learning_proposal import (
    LearningStateExecutionLearningProposal,
    LearningStateExecutionLearningProposalStatus,
)


class M23_162LearningProposalApplicationTests(unittest.TestCase):
    def _make_proposal(self, *, status=LearningStateExecutionLearningProposalStatus.PROPOSED):
        return LearningStateExecutionLearningProposal(
            proposal_id="proposal-160", eligibility_id="learning-eligibility-159", integrity_id="integrity-158",
            signal_id="signal-157", evaluation_id="evaluation-156", feedback_id="feedback-155", outcome_id="outcome-154",
            attempt_id="attempt-153", admission_id="admission-152", eligibility_source_id="integrity-158",
            handling_id="handling-150", consumption_id="consumption-149", receipt_id="receipt-148", handoff_id="handoff-147",
            inherited_integrity_id="integrity-previous", validation_id="validation-145", semantic_use_id="semantic-use-144",
            source_request_id="request-143", source_request_lineage_id="request-lineage-143", source_validation_id="source-validation-142",
            source_validation_lineage_id="source-validation-lineage-142", interpretation_id="interpretation-141", read_id="read-140",
            consumption_request_id="consumption-139", requester_id="requester-A", consumer_id="consumer-A",
            handoff_target_id="handoff-target-A", recipient_id="recipient-A", handling_target_id="handler-A", execution_target_id="executor-A",
            signal_kind="POSITIVE", signal_purpose="feed-learning",
            signal_context={"source": "execution-feedback", "features": ["stable", {"score": 0.9}]}, signal_status="RECORDED",
            source_signal_fingerprint="a" * 64, computed_signal_fingerprint="a" * 64, learner_id="learner-A",
            eligibility_purpose="enter-future-learning", proposer_id="proposer-A", proposal_purpose="candidate-learning",
            proposed_change={"threshold": 0.95, "nested": ["stable"]}, rationale={"why": {"score": 0.8}}, status=status,
            reasons=("learning eligibility is ELIGIBLE",), lineage={"proposal_id": "proposal-160", "eligibility_id": "learning-eligibility-159"},
        )

    def _make_decision(self, *, proposal=None, status=None, decision_id="decision-161"):
        proposal = proposal or self._make_proposal()
        if status is not None:
            proposal = self._make_proposal(status=status)
        return LearningStateExecutionLearningProposalDecisionService().decide(
            proposal, decision_id=decision_id, decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
        )

    def _apply(self, decision=None, **kwargs):
        return LearningStateExecutionLearningProposalApplicationService().apply(
            decision or self._make_decision(), application_id=kwargs.pop("application_id", "application-162"),
            applier_id=kwargs.pop("applier_id", "applier-A"), application_purpose=kwargs.pop("application_purpose", "apply-candidate"),
            application_rationale=kwargs.pop("application_rationale", {"basis": "approved-decision"}), **kwargs,
        )

    def test_approved_decision_is_applied(self):
        result = self._apply()
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationStatus.APPLIED)
        self.assertTrue(result.is_applied)
        self.assertFalse(result.is_learning)
        self.assertFalse(result.authorizes_learning)

    def test_rejected_decision_fails_closed(self):
        decision = self._make_decision(status=LearningStateExecutionLearningProposalStatus.REJECTED)
        result = self._apply(decision)
        self.assertIs(decision.status, LearningStateExecutionLearningProposalDecisionStatus.REJECTED)
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationStatus.REJECTED)
        self.assertTrue(result.is_rejected)

    def test_exact_decision_type_is_required(self):
        with self.assertRaises(TypeError):
            self._apply(object())

    def test_application_identity_must_be_distinct(self):
        with self.assertRaises(ValueError):
            self._apply(application_id="decision-161")

    def test_required_application_metadata_is_enforced(self):
        service = LearningStateExecutionLearningProposalApplicationService()
        decision = self._make_decision()
        for field in ("application_id", "applier_id", "application_purpose"):
            kwargs = {"application_id": "application-162", "applier_id": "applier-A", "application_purpose": "apply-candidate", "application_rationale": {"basis": "approved"}}
            kwargs[field] = " "
            with self.subTest(field=field), self.assertRaises(ValueError):
                service.apply(decision, **kwargs)
        with self.assertRaises(ValueError):
            service.apply(decision, application_id="application-162", applier_id="applier-A", application_purpose="apply-candidate", application_rationale=None)

    def test_upstream_provenance_is_preserved(self):
        decision = self._make_decision()
        result = self._apply(decision)
        for field in (
            "decision_id", "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id",
            "attempt_id", "admission_id", "eligibility_source_id", "handling_id", "consumption_id", "receipt_id", "handoff_id",
            "inherited_integrity_id", "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id",
            "source_validation_id", "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id",
            "requester_id", "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id",
            "signal_kind", "signal_purpose", "signal_context", "signal_status", "source_signal_fingerprint", "computed_signal_fingerprint",
            "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose", "proposed_change", "proposal_rationale",
            "decision_maker_id", "decision_purpose", "decision_rationale",
        ):
            self.assertEqual(getattr(result, field), getattr(decision, field))

    def test_application_rationale_evidence_and_lineage_are_recursively_frozen(self):
        result = self._apply(application_rationale={"basis": ["approved", {"score": 0.9}]}, application_evidence={"checks": [{"name": "decision"}]}, lineage={"chain": ["decision-161", {"source": "proposal-160"}]})
        self.assertIsInstance(result.application_rationale, MappingProxyType)
        self.assertIsInstance(result.application_evidence, MappingProxyType)
        self.assertEqual(result.application_rationale["basis"], ("approved", MappingProxyType({"score": 0.9})))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)

    def test_source_is_not_mutated_and_artifact_is_immutable(self):
        decision = self._make_decision()
        before = decision.status
        result = self._apply(decision)
        self.assertIs(decision.status, before)
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningProposalApplicationStatus.REJECTED
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_application_is_deterministic_for_same_inputs(self):
        first = self._apply()
        second = self._apply()
        self.assertEqual(first, second)

    def test_application_has_no_learning_or_authority_powers(self):
        result = self._apply()
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "proposes_adaptation", "authorizes_execution",
            "authorizes_retry", "invokes_learner", "updates_model", "mutates_memory", "mutates_policy", "invokes_executor",
            "schedules_work", "plans_work", "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
