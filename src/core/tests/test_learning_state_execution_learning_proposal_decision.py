import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignalKind,
    LearningStateExecutionLearningSignalService,
)
from src.core.learning_state_execution_learning_signal_integrity import (
    LearningStateExecutionLearningSignalIntegrityService,
)
from src.core.learning_state_execution_learning_eligibility import (
    LearningStateExecutionLearningEligibilityService,
)
from src.core.learning_state_execution_learning_proposal import (
    LearningStateExecutionLearningProposalService,
    LearningStateExecutionLearningProposalStatus,
)
from src.core.learning_state_execution_learning_proposal_decision import (
    LearningStateExecutionLearningProposalDecisionService,
    LearningStateExecutionLearningProposalDecisionStatus,
)


class M23_129LearningProposalDecisionTests(unittest.TestCase):
    def _make_proposal(self, *, status=None):
        evaluation = __import__(
            "src.core.learning_state_execution_evaluation", fromlist=["LearningStateExecutionEvaluation"]
        ).LearningStateExecutionEvaluation(
            evaluation_id="evaluation-124", feedback_id="feedback-123", outcome_id="outcome-122",
            attempt_id="attempt-121", admission_id="admission-120", eligibility_id="eligibility-119",
            handling_id="handling-118", consumption_id="consumption-117", receipt_id="receipt-116",
            handoff_id="handoff-115", integrity_id="integrity-114", validation_id="validation-113",
            use_id="use-112", request_id="semantic-use-111", interpretation_id="interpretation-108",
            source_request_id="request-107", read_validation_id="read-validation-106", read_id="read-105",
            consumption_request_id="consumption-104", source_validation_id="source-validation-103",
            source_integrity_id="source-integrity-102", transition_id="transition-98", evidence_id="evidence-97",
            application_id="application-96", state_key="demo.state", transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64, computed_application_fingerprint="c" * 64, confidence=0.91,
            consumer_id="consumer-A", use_purpose="semantic-use", downstream_recipient_id="receiver-X",
            downstream_handler_id="handler-X", handling_purpose="route", execution_target_id="executor-X",
            execution_purpose="perform", outcome_status=__import__(
                "src.core.learning_state_execution_outcome", fromlist=["LearningStateExecutionOutcomeStatus"]
            ).LearningStateExecutionOutcomeStatus.SUCCESS,
            feedback_kind=__import__(
                "src.core.learning_state_execution_feedback", fromlist=["LearningStateExecutionFeedbackKind"]
            ).LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK,
            observed_consequence={"state": "changed"}, executor_output={"raw": "result"},
            failure_type=None, failure_message=None, objective="reach-target", evaluator_id="evaluator-A",
            evaluation_purpose="assess", evaluation_judgment={"score": 0.8},
            evaluation_context={"objective": "reach-target"}, reasons={"source": "m23.124"},
            lineage={"evaluation_id": "evaluation-124"},
        )
        signal = LearningStateExecutionLearningSignalService().create(
            evaluation, signal_id="signal-125", signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE,
            signal_purpose="feed-learning",
        )
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(
            signal, integrity_id="integrity-126"
        )
        eligibility = LearningStateExecutionLearningEligibilityService().evaluate(
            integrity, eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning"
        )
        proposal = LearningStateExecutionLearningProposalService().propose(
            eligibility, proposal_id="proposal-128", proposer_id="proposer-A", proposal_purpose="candidate-learning",
            proposed_change={"threshold": 0.95}, rationale={"why": {"score": 0.8}},
        )
        if status is LearningStateExecutionLearningProposalStatus.REJECTED:
            object.__setattr__(proposal, "status", LearningStateExecutionLearningProposalStatus.REJECTED)
        return proposal

    def test_proposed_input_is_approved(self):
        result = LearningStateExecutionLearningProposalDecisionService().decide(
            self._make_proposal(), decision_id="decision-129", decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningProposalDecisionStatus.APPROVED)
        self.assertTrue(result.is_approved)
        self.assertTrue(result.decides_learning)
        self.assertFalse(result.authorizes_learning)

    def test_rejected_proposal_fails_closed(self):
        result = LearningStateExecutionLearningProposalDecisionService().decide(
            self._make_proposal(status=LearningStateExecutionLearningProposalStatus.REJECTED),
            decision_id="decision-129", decision_maker_id="decision-maker-A", decision_purpose="review-candidate",
            decision_rationale={"basis": "rejected-source"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningProposalDecisionStatus.REJECTED)
        self.assertTrue(result.is_rejected)
        self.assertFalse(result.is_approved)

    def test_exact_proposal_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningProposalDecisionService().decide(
                object(), decision_id="decision-129", decision_maker_id="decision-maker-A",
                decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
            )

    def test_required_decision_metadata_is_enforced(self):
        service = LearningStateExecutionLearningProposalDecisionService()
        proposal = self._make_proposal()
        for field, value in (("decision_id", " "), ("decision_maker_id", " "), ("decision_purpose", " ")):
            kwargs = dict(
                decision_id="decision-129", decision_maker_id="decision-maker-A", decision_purpose="review-candidate",
                decision_rationale={"basis": "bounded-review"},
            )
            kwargs[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                service.decide(proposal, **kwargs)
        with self.assertRaises(ValueError):
            service.decide(
                proposal, decision_id="decision-129", decision_maker_id="decision-maker-A",
                decision_purpose="review-candidate", decision_rationale=None,
            )

    def test_upstream_provenance_is_preserved(self):
        proposal = self._make_proposal()
        result = LearningStateExecutionLearningProposalDecisionService().decide(
            proposal, decision_id="decision-129", decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
        )
        for field in (
            "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id",
            "attempt_id", "admission_id", "eligibility_source_id", "source_integrity_id", "validation_id", "use_id",
            "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id", "consumption_request_id",
            "source_validation_id", "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "confidence", "consumer_id", "execution_target_id",
            "execution_purpose", "objective", "evaluator_id", "evaluation_purpose", "signal_kind", "signal_purpose", "learner_id",
            "eligibility_purpose", "proposer_id", "proposal_purpose",
        ):
            self.assertEqual(getattr(result, field), getattr(proposal, field))
        self.assertEqual(result.proposed_change, proposal.proposed_change)
        self.assertEqual(result.proposal_rationale, proposal.rationale)

    def test_decision_rationale_and_lineage_are_recursively_frozen(self):
        result = LearningStateExecutionLearningProposalDecisionService().decide(
            self._make_proposal(), decision_id="decision-129", decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": ["reviewed", {"score": 0.9}]},
            lineage={"chain": ["proposal-128", {"source": "eligibility-127"}]},
        )
        self.assertIsInstance(result.decision_rationale, MappingProxyType)
        self.assertEqual(result.decision_rationale["basis"], ("reviewed", MappingProxyType({"score": 0.9})))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertEqual(result.lineage["chain"][1]["source"], "eligibility-127")

    def test_source_is_not_mutated_and_artifact_is_immutable(self):
        proposal = self._make_proposal()
        before = proposal.status
        result = LearningStateExecutionLearningProposalDecisionService().decide(
            proposal, decision_id="decision-129", decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
        )
        self.assertIs(proposal.status, before)
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningProposalDecisionStatus.REJECTED

    def test_decision_is_deterministic_for_same_inputs(self):
        service = LearningStateExecutionLearningProposalDecisionService()
        first = service.decide(
            self._make_proposal(), decision_id="decision-129", decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
        )
        second = service.decide(
            self._make_proposal(), decision_id="decision-129", decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
        )
        self.assertEqual(first, second)

    def test_reasons_are_validated_and_preserved(self):
        result = LearningStateExecutionLearningProposalDecisionService().decide(
            self._make_proposal(), decision_id="decision-129", decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
            reasons=("human-review-complete",),
        )
        self.assertEqual(result.reasons, ("human-review-complete",))
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningProposalDecisionService().decide(
                self._make_proposal(), decision_id="decision-129", decision_maker_id="decision-maker-A",
                decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"}, reasons=("ok", " "),
            )

    def test_decision_has_no_application_learning_or_authority_powers(self):
        result = LearningStateExecutionLearningProposalDecisionService().decide(
            self._make_proposal(), decision_id="decision-129", decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
        )
        for name in (
            "is_learning", "authorizes_learning", "applies_learning", "establishes_truth", "establishes_correctness",
            "establishes_certainty", "establishes_usefulness", "proposes_adaptation", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "updates_model", "mutates_memory", "mutates_policy", "invokes_executor", "schedules_work", "plans_work",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
