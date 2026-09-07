import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_proposal_application_integrity import LearningStateExecutionLearningProposalApplicationIntegrityService
from src.core.learning_state_execution_learning_proposal_application import LearningStateExecutionLearningProposalApplicationService
from src.core.learning_state_execution_learning_proposal_decision import LearningStateExecutionLearningProposalDecisionService
from src.core.learning_state_execution_learning_proposal import LearningStateExecutionLearningProposalService
from src.core.learning_state_execution_learning_eligibility import LearningStateExecutionLearningEligibilityService
from src.core.learning_state_execution_learning_signal_integrity import LearningStateExecutionLearningSignalIntegrityService
from src.core.learning_state_execution_learning_signal import LearningStateExecutionLearningSignalKind, LearningStateExecutionLearningSignalService
from src.core.learning_state_execution_feedback import LearningStateExecutionFeedbackKind
from src.core.learning_state_execution_outcome import LearningStateExecutionOutcomeStatus
from src.core.learning_state_execution_learning_state_evidence import LearningStateExecutionLearningStateEvidenceService, LearningStateExecutionLearningStateEvidenceStatus
from src.core.learning_state_execution_learning_state_transition import LearningStateExecutionLearningStateTransitionService, LearningStateExecutionLearningStateTransitionStatus


class M23_133LearningStateTransitionTests(unittest.TestCase):
    def _make_evidence(self):
        evaluation = __import__("src.core.learning_state_execution_evaluation", fromlist=["LearningStateExecutionEvaluation"]).LearningStateExecutionEvaluation(
            evaluation_id="evaluation-124", feedback_id="feedback-123", outcome_id="outcome-122", attempt_id="attempt-121", admission_id="admission-120", eligibility_id="eligibility-119", handling_id="handling-118", consumption_id="consumption-117", receipt_id="receipt-116", handoff_id="handoff-115", integrity_id="integrity-114", validation_id="validation-113", use_id="use-112", request_id="semantic-use-111", interpretation_id="interpretation-108", source_request_id="request-107", read_validation_id="read-validation-106", read_id="read-105", consumption_request_id="consumption-104", source_validation_id="source-validation-103", source_integrity_id="source-integrity-102", transition_id="transition-98", evidence_id="evidence-97", application_id="application-96", state_key="demo.state", transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64, computed_application_fingerprint="c" * 64, confidence=0.91, consumer_id="consumer-A", use_purpose="semantic-use", downstream_recipient_id="receiver-X", downstream_handler_id="handler-X", handling_purpose="route", execution_target_id="executor-X", execution_purpose="perform", outcome_status=LearningStateExecutionOutcomeStatus.SUCCESS, feedback_kind=LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK, observed_consequence={"state": "changed"}, executor_output={"raw": "result"}, failure_type=None, failure_message=None, objective="reach-target", evaluator_id="evaluator-A", evaluation_purpose="assess", evaluation_judgment={"score": 0.8}, evaluation_context={"objective": "reach-target"}, reasons={"source": "m23.124"}, lineage={"evaluation_id": "evaluation-124"},
        )
        signal = LearningStateExecutionLearningSignalService().create(evaluation, signal_id="signal-125", signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE, signal_purpose="feed-learning")
        signal_integrity = LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        eligibility = LearningStateExecutionLearningEligibilityService().evaluate(signal_integrity, eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning")
        proposal = LearningStateExecutionLearningProposalService().propose(eligibility, proposal_id="proposal-128", proposer_id="proposer-A", proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95}, rationale={"why": {"score": 0.8}})
        decision = LearningStateExecutionLearningProposalDecisionService().decide(proposal, decision_id="decision-129", decision_maker_id="decision-maker-A", decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"})
        application = LearningStateExecutionLearningProposalApplicationService().apply(decision, application_id="application-130", applier_id="applier-A", application_purpose="apply-approved-learning", application_rationale={"basis": ["approved", {"scope": "bounded"}]}, application_evidence={"attempt": [{"step": 1}, {"step": 2}]}, lineage={"application_id": "application-130", "decision_id": decision.decision_id})
        integrity = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(application, integrity_id="application-integrity-131")
        return LearningStateExecutionLearningStateEvidenceService().record(integrity, evidence_id="evidence-132", evidence_collector_id="collector-A", evidence_purpose="record-state-effect", evidence_rationale={"basis": "integrity"}, evidence_payload={"candidate_state": {"threshold": 0.95}, "observed": [1, 2]})

    def _formulate(self, evidence=None, **kwargs):
        return LearningStateExecutionLearningStateTransitionService().formulate(evidence or self._make_evidence(), transition_id="transition-133", state_before={"threshold": 0.8}, state_after={"threshold": 0.95}, transition_actor_id="transition-actor-A", transition_purpose="apply-recorded-learning-state-change", transition_rationale={"basis": ["recorded-evidence", {"scope": "bounded"}]}, **kwargs)

    def test_recorded_evidence_produces_formulated_transition(self):
        result = self._formulate()
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionStatus.FORMULATED)
        self.assertTrue(result.is_formulated)
        self.assertTrue(result.represents_transition)

    def test_rejected_evidence_fails_closed(self):
        evidence = self._make_evidence()
        object.__setattr__(evidence, "status", LearningStateExecutionLearningStateEvidenceStatus.REJECTED)
        result = self._formulate(evidence)
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionStatus.REJECTED)
        self.assertIn("learning-state evidence is not RECORDED", result.reasons)

    def test_exact_evidence_type_is_required(self):
        with self.assertRaises(TypeError):
            self._formulate(object())

    def test_transition_metadata_and_states_are_explicit(self):
        result = self._formulate()
        self.assertEqual(result.transition_id, "transition-133")
        self.assertEqual(result.transition_actor_id, "transition-actor-A")
        self.assertEqual(result.transition_purpose, "apply-recorded-learning-state-change")
        self.assertEqual(result.state_before["threshold"], 0.8)
        self.assertEqual(result.state_after["threshold"], 0.95)

    def test_transition_fingerprint_is_deterministic(self):
        self.assertEqual(self._formulate(), self._formulate())
        self.assertEqual(len(self._formulate().transition_fingerprint), 64)

    def test_provenance_is_preserved(self):
        evidence = self._make_evidence()
        result = self._formulate(evidence)
        for field in ("evidence_id", "integrity_id", "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "validation_id", "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id", "consumption_request_id", "source_validation_id", "state_key", "proposed_change", "confidence", "consumer_id", "execution_target_id", "application_status"):
            self.assertEqual(getattr(result, field), getattr(evidence, field))

    def test_transition_artifact_is_immutable(self):
        result = self._formulate()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateTransitionStatus.REJECTED

    def test_nested_states_and_lineage_are_recursively_frozen(self):
        result = self._formulate(lineage={"transition_id": "transition-133", "chain": {"step": 4}}, reasons=("caller-reason",))
        self.assertIsInstance(result.state_before, MappingProxyType)
        self.assertIsInstance(result.state_after, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["chain"]["step"] = 5

    def test_reasons_and_lineage_are_preserved(self):
        result = self._formulate(reasons=("caller-reason",), lineage={"transition_id": "transition-133", "source": {"evidence_id": "evidence-132"}})
        self.assertEqual(result.reasons, ("caller-reason",))
        self.assertEqual(result.lineage["source"]["evidence_id"], "evidence-132")

    def test_source_evidence_is_not_mutated(self):
        evidence = self._make_evidence()
        before = evidence.status
        result = self._formulate(evidence)
        self.assertIs(evidence.status, before)
        self.assertEqual(evidence.state_key, "demo.state")
        self.assertEqual(result.evidence_id, evidence.evidence_id)

    def test_transition_does_not_mutate_or_persist_state(self):
        result = self._formulate()
        self.assertFalse(result.transitions_state)
        self.assertFalse(result.mutates_state)
        self.assertFalse(result.persists_state)

    def test_transition_has_no_execution_or_authority_powers(self):
        result = self._formulate()
        for name in ("is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "updates_model", "mutates_memory", "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness"):
            self.assertFalse(getattr(result, name))

    def test_transition_rationale_is_frozen(self):
        result = self._formulate()
        self.assertIsInstance(result.transition_rationale, MappingProxyType)
        self.assertIsInstance(result.transition_rationale["basis"], tuple)

    def test_before_and_after_are_distinct_explicit_values(self):
        result = self._formulate()
        self.assertNotEqual(result.state_before, result.state_after)


if __name__ == "__main__":
    unittest.main()
