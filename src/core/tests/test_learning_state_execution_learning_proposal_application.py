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
)
from src.core.learning_state_execution_learning_proposal_decision import (
    LearningStateExecutionLearningProposalDecisionService,
    LearningStateExecutionLearningProposalDecisionStatus,
)
from src.core.learning_state_execution_learning_proposal_application import (
    LearningStateExecutionLearningProposalApplicationService,
    LearningStateExecutionLearningProposalApplicationStatus,
)


class M23_130LearningProposalApplicationTests(unittest.TestCase):
    def _make_decision(self, *, rejected=False):
        from src.core.learning_state_execution_evaluation import LearningStateExecutionEvaluation
        from src.core.learning_state_execution_outcome import LearningStateExecutionOutcomeStatus
        from src.core.learning_state_execution_feedback import LearningStateExecutionFeedbackKind
        from src.core.learning_state_execution_learning_proposal import LearningStateExecutionLearningProposalStatus

        evaluation = LearningStateExecutionEvaluation(
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
            execution_purpose="perform", outcome_status=LearningStateExecutionOutcomeStatus.SUCCESS,
            feedback_kind=LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK,
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
            integrity, eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning",
        )
        proposal = LearningStateExecutionLearningProposalService().propose(
            eligibility, proposal_id="proposal-128", proposer_id="proposer-A", proposal_purpose="candidate-learning",
            proposed_change={"threshold": 0.95}, rationale={"why": {"score": 0.8}},
        )
        if rejected:
            object.__setattr__(proposal, "status", LearningStateExecutionLearningProposalStatus.REJECTED)
        return LearningStateExecutionLearningProposalDecisionService().decide(
            proposal, decision_id="decision-129", decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"},
        )

    def test_approved_decision_enters_application_attempt(self):
        result = LearningStateExecutionLearningProposalApplicationService().apply(
            self._make_decision(), application_id="application-130", applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": "approved-decision"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationStatus.ATTEMPTED)
        self.assertTrue(result.is_attempted)
        self.assertTrue(result.applies_learning)

    def test_rejected_decision_fails_closed(self):
        result = LearningStateExecutionLearningProposalApplicationService().apply(
            self._make_decision(rejected=True), application_id="application-130", applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": "rejected-decision"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationStatus.REJECTED)
        self.assertTrue(result.is_rejected)
        self.assertFalse(result.applies_learning)

    def test_exact_decision_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningProposalApplicationService().apply(
                object(), application_id="application-130", applier_id="applier-A",
                application_purpose="apply-approved-learning", application_rationale={"basis": "bounded"},
            )

    def test_required_application_metadata_is_enforced(self):
        service = LearningStateExecutionLearningProposalApplicationService()
        decision = self._make_decision()
        for field, value in (("application_id", " "), ("applier_id", " "), ("application_purpose", " ")):
            kwargs = dict(
                application_id="application-130", applier_id="applier-A", application_purpose="apply-approved-learning",
                application_rationale={"basis": "bounded"},
            )
            kwargs[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                service.apply(decision, **kwargs)
        with self.assertRaises(ValueError):
            service.apply(
                decision, application_id="application-130", applier_id="applier-A",
                application_purpose="apply-approved-learning", application_rationale=None,
            )

    def test_provenance_and_fingerprints_are_preserved(self):
        decision = self._make_decision()
        result = LearningStateExecutionLearningProposalApplicationService().apply(
            decision, application_id="application-130", applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": "approved"},
        )
        for field in (
            "decision_id", "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id",
            "outcome_id", "attempt_id", "admission_id", "eligibility_source_id", "source_integrity_id", "validation_id",
            "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "transition_id", "evidence_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint", "confidence",
            "consumer_id", "execution_target_id", "execution_purpose", "objective", "evaluator_id", "evaluation_purpose",
            "signal_kind", "signal_purpose", "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose",
            "decision_maker_id", "decision_purpose", "decision_rationale", "proposed_change", "proposal_rationale",
        ):
            self.assertEqual(getattr(result, field), getattr(decision, field))

    def test_application_evidence_and_lineage_are_recursively_frozen(self):
        result = LearningStateExecutionLearningProposalApplicationService().apply(
            self._make_decision(), application_id="application-130", applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": ["approved", {"score": 0.9}]},
            application_evidence={"result": [{"state": "candidate"}]},
            lineage={"chain": ["decision-129", {"source": "proposal-128"}]},
        )
        self.assertIsInstance(result.application_rationale, MappingProxyType)
        self.assertEqual(result.application_rationale["basis"][1]["score"], 0.9)
        self.assertIsInstance(result.application_evidence, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)

    def test_source_decision_is_not_mutated_and_artifact_is_immutable(self):
        decision = self._make_decision()
        before = decision.status
        result = LearningStateExecutionLearningProposalApplicationService().apply(
            decision, application_id="application-130", applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": "approved"},
        )
        self.assertIs(decision.status, before)
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningProposalApplicationStatus.REJECTED

    def test_application_is_deterministic_for_same_inputs(self):
        service = LearningStateExecutionLearningProposalApplicationService()
        first = service.apply(
            self._make_decision(), application_id="application-130", applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": "approved"},
        )
        second = service.apply(
            self._make_decision(), application_id="application-130", applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": "approved"},
        )
        self.assertEqual(first, second)

    def test_reasons_are_validated_and_preserved(self):
        result = LearningStateExecutionLearningProposalApplicationService().apply(
            self._make_decision(), application_id="application-130", applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": "approved"},
            reasons=("approval-present",),
        )
        self.assertEqual(result.reasons, ("approval-present",))
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningProposalApplicationService().apply(
                self._make_decision(), application_id="application-130", applier_id="applier-A",
                application_purpose="apply-approved-learning", application_rationale={"basis": "approved"},
                reasons=("ok", " "),
            )

    def test_application_has_no_execution_or_external_authority_powers(self):
        result = LearningStateExecutionLearningProposalApplicationService().apply(
            self._make_decision(), application_id="application-130", applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": "approved"},
        )
        for name in (
            "authorizes_execution", "authorizes_retry", "invokes_executor", "schedules_work", "plans_work",
            "authorizes_learning", "invokes_learner", "updates_model", "mutates_memory", "mutates_policy",
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "proposes_adaptation",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
