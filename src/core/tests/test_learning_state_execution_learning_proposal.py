import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignalKind,
    LearningStateExecutionLearningSignalService,
)
from src.core.learning_state_execution_learning_signal_integrity import (
    LearningStateExecutionLearningSignalIntegrityService,
    LearningStateExecutionLearningSignalIntegrityStatus,
)
from src.core.learning_state_execution_learning_eligibility import (
    LearningStateExecutionLearningEligibilityService,
    LearningStateExecutionLearningEligibilityStatus,
)
from src.core.learning_state_execution_learning_proposal import (
    LearningStateExecutionLearningProposalService,
    LearningStateExecutionLearningProposalStatus,
)


class M23_128LearningProposalTests(unittest.TestCase):
    def _make_eligibility(self, *, status=None):
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
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        eligibility = LearningStateExecutionLearningEligibilityService().evaluate(
            integrity, eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning"
        )
        if status is LearningStateExecutionLearningEligibilityStatus.REJECTED:
            object.__setattr__(eligibility, "status", LearningStateExecutionLearningEligibilityStatus.REJECTED)
        return eligibility

    def test_eligible_input_produces_proposal(self):
        result = LearningStateExecutionLearningProposalService().propose(
            self._make_eligibility(), proposal_id="proposal-128", proposer_id="proposer-A",
            proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95},
        )
        self.assertIs(result.status, LearningStateExecutionLearningProposalStatus.PROPOSED)
        self.assertTrue(result.is_proposed)
        self.assertFalse(result.is_rejected)

    def test_rejected_eligibility_fails_closed(self):
        result = LearningStateExecutionLearningProposalService().propose(
            self._make_eligibility(status=LearningStateExecutionLearningEligibilityStatus.REJECTED),
            proposal_id="proposal-128", proposer_id="proposer-A", proposal_purpose="candidate-learning",
            proposed_change={"threshold": 0.95},
        )
        self.assertIs(result.status, LearningStateExecutionLearningProposalStatus.REJECTED)
        self.assertTrue(result.is_rejected)
        self.assertFalse(result.is_proposed)

    def test_exact_eligibility_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningProposalService().propose(
                object(), proposal_id="proposal-128", proposer_id="proposer-A",
                proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95},
            )

    def test_required_proposal_metadata_is_enforced(self):
        service = LearningStateExecutionLearningProposalService()
        eligibility = self._make_eligibility()
        cases = (
            ("proposal_id", " "), ("proposer_id", " "), ("proposal_purpose", " "),
        )
        for field, value in cases:
            kwargs = dict(proposal_id="proposal-128", proposer_id="proposer-A", proposal_purpose="candidate-learning", proposed_change={"x": 1})
            kwargs[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                service.propose(eligibility, **kwargs)
        with self.assertRaises(ValueError):
            service.propose(
                eligibility, proposal_id="proposal-128", proposer_id="proposer-A",
                proposal_purpose="candidate-learning", proposed_change=None,
            )

    def test_upstream_provenance_is_preserved(self):
        eligibility = self._make_eligibility()
        result = LearningStateExecutionLearningProposalService().propose(
            eligibility, proposal_id="proposal-128", proposer_id="proposer-A",
            proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95},
        )
        for field in (
            "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id",
            "attempt_id", "admission_id", "source_integrity_id", "validation_id", "use_id", "request_id",
            "interpretation_id", "source_request_id", "read_validation_id", "read_id", "consumption_request_id",
            "source_validation_id", "transition_id", "evidence_id", "application_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "confidence", "consumer_id", "execution_target_id", "execution_purpose", "objective",
            "evaluator_id", "evaluation_purpose", "signal_kind", "signal_purpose", "learner_id", "eligibility_purpose",
        ):
            self.assertEqual(getattr(result, field), getattr(eligibility, field))

    def test_rationale_and_lineage_are_recursively_frozen(self):
        result = LearningStateExecutionLearningProposalService().propose(
            self._make_eligibility(), proposal_id="proposal-128", proposer_id="proposer-A",
            proposal_purpose="candidate-learning", proposed_change={"nested": ["x"]},
            rationale={"why": {"score": 0.8}}, lineage={"chain": ["eligibility-127", {"source": "signal-125"}]},
        )
        self.assertIsInstance(result.proposed_change, MappingProxyType)
        self.assertEqual(result.proposed_change["nested"], ("x",))
        self.assertIsInstance(result.rationale, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertEqual(result.lineage["chain"][1]["source"], "signal-125")

    def test_source_is_not_mutated_and_artifact_is_immutable(self):
        eligibility = self._make_eligibility()
        before = eligibility.status
        result = LearningStateExecutionLearningProposalService().propose(
            eligibility, proposal_id="proposal-128", proposer_id="proposer-A",
            proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95},
        )
        self.assertIs(eligibility.status, before)
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningProposalStatus.REJECTED

    def test_proposal_is_deterministic_for_same_inputs(self):
        service = LearningStateExecutionLearningProposalService()
        first = service.propose(
            self._make_eligibility(), proposal_id="proposal-128", proposer_id="proposer-A",
            proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95},
        )
        second = service.propose(
            self._make_eligibility(), proposal_id="proposal-128", proposer_id="proposer-A",
            proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95},
        )
        self.assertEqual(first, second)

    def test_reasons_are_validated_and_preserved(self):
        result = LearningStateExecutionLearningProposalService().propose(
            self._make_eligibility(), proposal_id="proposal-128", proposer_id="proposer-A",
            proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95},
            reasons=("bounded-candidate",),
        )
        self.assertEqual(result.reasons, ("bounded-candidate",))
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningProposalService().propose(
                self._make_eligibility(), proposal_id="proposal-128", proposer_id="proposer-A",
                proposal_purpose="candidate-learning", proposed_change={"x": 1}, reasons=("ok", " "),
            )

    def test_proposal_has_no_decision_learning_or_authority_powers(self):
        result = LearningStateExecutionLearningProposalService().propose(
            self._make_eligibility(), proposal_id="proposal-128", proposer_id="proposer-A",
            proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95},
        )
        for name in (
            "is_learning", "decides_learning", "authorizes_learning", "applies_learning", "proposes_adaptation",
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "authorizes_execution", "authorizes_retry", "invokes_learner", "updates_model", "mutates_memory",
            "mutates_policy", "invokes_executor", "schedules_work", "plans_work",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
