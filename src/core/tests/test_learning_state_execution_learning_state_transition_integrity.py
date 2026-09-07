import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_feedback import LearningStateExecutionFeedbackKind
from src.core.learning_state_execution_learning_eligibility import LearningStateExecutionLearningEligibilityService
from src.core.learning_state_execution_learning_proposal import LearningStateExecutionLearningProposalService
from src.core.learning_state_execution_learning_proposal_application import LearningStateExecutionLearningProposalApplicationService
from src.core.learning_state_execution_learning_proposal_application_integrity import LearningStateExecutionLearningProposalApplicationIntegrityService
from src.core.learning_state_execution_learning_proposal_decision import LearningStateExecutionLearningProposalDecisionService
from src.core.learning_state_execution_learning_signal import LearningStateExecutionLearningSignalKind, LearningStateExecutionLearningSignalService
from src.core.learning_state_execution_learning_signal_integrity import LearningStateExecutionLearningSignalIntegrityService
from src.core.learning_state_execution_learning_state_evidence import LearningStateExecutionLearningStateEvidenceService
from src.core.learning_state_execution_learning_state_transition import LearningStateExecutionLearningStateTransitionService, LearningStateExecutionLearningStateTransitionStatus
from src.core.learning_state_execution_learning_state_transition_integrity import (
    LearningStateExecutionLearningStateTransitionIntegrityService,
    LearningStateExecutionLearningStateTransitionIntegrityStatus,
)
from src.core.learning_state_execution_outcome import LearningStateExecutionOutcomeStatus


class M23_134LearningStateTransitionIntegrityTests(unittest.TestCase):
    def _make_transition(self):
        evaluation = __import__(
            "src.core.learning_state_execution_evaluation",
            fromlist=["LearningStateExecutionEvaluation"],
        ).LearningStateExecutionEvaluation(
            evaluation_id="evaluation-124",
            feedback_id="feedback-123",
            outcome_id="outcome-122",
            attempt_id="attempt-121",
            admission_id="admission-120",
            eligibility_id="eligibility-119",
            handling_id="handling-118",
            consumption_id="consumption-117",
            receipt_id="receipt-116",
            handoff_id="handoff-115",
            integrity_id="integrity-114",
            validation_id="validation-113",
            use_id="use-112",
            request_id="semantic-use-111",
            interpretation_id="interpretation-108",
            source_request_id="request-107",
            read_validation_id="read-validation-106",
            read_id="read-105",
            consumption_request_id="consumption-104",
            source_validation_id="source-validation-103",
            source_integrity_id="source-integrity-102",
            transition_id="transition-98",
            evidence_id="evidence-97",
            application_id="application-96",
            state_key="demo.state",
            transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64,
            confidence=0.91,
            consumer_id="consumer-A",
            use_purpose="semantic-use",
            downstream_recipient_id="receiver-X",
            downstream_handler_id="handler-X",
            handling_purpose="route",
            execution_target_id="executor-X",
            execution_purpose="perform",
            outcome_status=LearningStateExecutionOutcomeStatus.SUCCESS,
            feedback_kind=LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK,
            observed_consequence={"state": "changed"},
            executor_output={"raw": "result"},
            failure_type=None,
            failure_message=None,
            objective="reach-target",
            evaluator_id="evaluator-A",
            evaluation_purpose="assess",
            evaluation_judgment={"score": 0.8},
            evaluation_context={"objective": "reach-target"},
            reasons={"source": "m23.124"},
            lineage={"evaluation_id": "evaluation-124"},
        )
        signal = LearningStateExecutionLearningSignalService().create(
            evaluation,
            signal_id="signal-125",
            signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE,
            signal_purpose="feed-learning",
        )
        signal_integrity = LearningStateExecutionLearningSignalIntegrityService().validate(
            signal, integrity_id="integrity-126"
        )
        eligibility = LearningStateExecutionLearningEligibilityService().evaluate(
            signal_integrity,
            eligibility_id="learning-eligibility-127",
            learner_id="learner-A",
            eligibility_purpose="future-learning",
        )
        proposal = LearningStateExecutionLearningProposalService().propose(
            eligibility,
            proposal_id="proposal-128",
            proposer_id="proposer-A",
            proposal_purpose="candidate-learning",
            proposed_change={"threshold": 0.95},
            rationale={"why": {"score": 0.8}},
        )
        decision = LearningStateExecutionLearningProposalDecisionService().decide(
            proposal,
            decision_id="decision-129",
            decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate",
            decision_rationale={"basis": "bounded-review"},
        )
        application = LearningStateExecutionLearningProposalApplicationService().apply(
            decision,
            application_id="application-130",
            applier_id="applier-A",
            application_purpose="apply-approved-learning",
            application_rationale={"basis": ["approved", {"scope": "bounded"}]},
            application_evidence={"attempt": [{"step": 1}, {"step": 2}]},
            lineage={"application_id": "application-130", "decision_id": decision.decision_id},
        )
        application_integrity = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(
            application,
            integrity_id="application-integrity-131",
        )
        evidence = LearningStateExecutionLearningStateEvidenceService().record(
            application_integrity,
            evidence_id="evidence-132",
            evidence_collector_id="collector-A",
            evidence_purpose="record-state-effect",
            evidence_rationale={"basis": "integrity"},
            evidence_payload={"candidate_state": {"threshold": 0.95}, "observed": [1, 2]},
        )
        return LearningStateExecutionLearningStateTransitionService().formulate(
            evidence,
            transition_id="transition-133",
            state_before={"threshold": 0.8},
            state_after={"threshold": 0.95},
            transition_actor_id="transition-actor-A",
            transition_purpose="apply-recorded-learning-state-change",
            transition_rationale={"basis": ["recorded-evidence", {"scope": "bounded"}]},
            lineage={"transition_id": "transition-133", "evidence_id": "evidence-132"},
        )

    def test_valid_formulated_transition_produces_valid_integrity(self):
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            self._make_transition(), integrity_id="transition-integrity-134"
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)
        self.assertTrue(result.validates_transition)

    def test_exact_transition_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningStateTransitionIntegrityService().validate(
                object(), integrity_id="transition-integrity-134"
            )

    def test_integrity_id_is_required_and_distinct(self):
        transition = self._make_transition()
        with self.assertRaises(ValueError):
            LearningStateExecutionLearningStateTransitionIntegrityService().validate(
                transition, integrity_id=" "
            )
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            transition, integrity_id="transition-integrity-134"
        )
        self.assertNotEqual(result.integrity_id, transition.transition_id)

    def test_formulated_transition_status_is_required(self):
        transition = self._make_transition()
        object.__setattr__(transition, "status", LearningStateExecutionLearningStateTransitionStatus.REJECTED)
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            transition, integrity_id="transition-integrity-134"
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID)
        self.assertIn("transition is not FORMULATED", result.reasons)

    def test_transition_fingerprint_is_recomputed(self):
        transition = self._make_transition()
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            transition, integrity_id="transition-integrity-134"
        )
        self.assertEqual(result.transition_fingerprint, result.computed_transition_fingerprint)
        self.assertEqual(len(result.computed_transition_fingerprint), 64)

    def test_tampered_transition_fingerprint_is_reported_without_repair(self):
        transition = self._make_transition()
        original = transition.transition_fingerprint
        object.__setattr__(transition, "transition_fingerprint", "tampered")
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            transition, integrity_id="transition-integrity-134"
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID)
        self.assertIn("transition fingerprint mismatch", result.reasons)
        self.assertEqual(result.transition_fingerprint, "tampered")
        self.assertNotEqual(result.computed_transition_fingerprint, "tampered")
        self.assertNotEqual(original, result.transition_fingerprint)

    def test_transition_lineage_is_checked(self):
        transition = self._make_transition()
        object.__setattr__(transition, "evidence_id", "tampered-evidence")
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            transition, integrity_id="transition-integrity-134"
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID)
        self.assertIn("evidence lineage mismatch", result.reasons)

    def test_identical_before_and_after_state_is_rejected(self):
        transition = self._make_transition()
        object.__setattr__(transition, "state_after", transition.state_before)
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            transition, integrity_id="transition-integrity-134"
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID)
        self.assertIn("state before and after are identical", result.reasons)

    def test_provenance_and_application_fingerprints_are_preserved(self):
        transition = self._make_transition()
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            transition, integrity_id="transition-integrity-134"
        )
        for field in (
            "transition_id", "evidence_id", "state_key", "application_id", "decision_id", "proposal_id",
            "eligibility_id", "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id",
            "attempt_id", "admission_id", "validation_id", "use_id", "request_id", "interpretation_id",
            "source_request_id", "read_validation_id", "read_id", "consumption_request_id", "source_validation_id",
            "source_application_fingerprint", "computed_application_fingerprint", "confidence", "application_status",
        ):
            self.assertEqual(getattr(result, field), getattr(transition, field))

    def test_nested_transition_data_are_recursively_frozen(self):
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            self._make_transition(), integrity_id="transition-integrity-134"
        )
        self.assertIsInstance(result.state_before, MappingProxyType)
        self.assertIsInstance(result.state_after, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)

    def test_caller_reasons_and_lineage_are_preserved(self):
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            self._make_transition(),
            integrity_id="transition-integrity-134",
            reasons=("caller-reason",),
            lineage={"integrity_id": "transition-integrity-134", "source": {"transition_id": "transition-133"}},
        )
        self.assertEqual(result.reasons, ("caller-reason",))
        self.assertEqual(result.lineage["source"]["transition_id"], "transition-133")

    def test_source_transition_is_not_mutated(self):
        transition = self._make_transition()
        before = transition.transition_id
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            transition, integrity_id="transition-integrity-134"
        )
        self.assertEqual(transition.transition_id, before)
        self.assertEqual(result.transition_id, transition.transition_id)

    def test_integrity_artifact_is_immutable(self):
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            self._make_transition(), integrity_id="transition-integrity-134"
        )
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID

    def test_validation_is_deterministic_for_same_inputs(self):
        first = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            self._make_transition(), integrity_id="transition-integrity-134"
        )
        second = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            self._make_transition(), integrity_id="transition-integrity-134"
        )
        self.assertEqual(first, second)

    def test_integrity_has_no_state_mutation_or_execution_powers(self):
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            self._make_transition(), integrity_id="transition-integrity-134"
        )
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "updates_model", "mutates_memory",
            "mutates_policy", "mutates_state", "persists_state", "executes_work", "establishes_truth",
            "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_nested_integrity_payload_is_immutable(self):
        result = LearningStateExecutionLearningStateTransitionIntegrityService().validate(
            self._make_transition(), integrity_id="transition-integrity-134"
        )
        self.assertIsInstance(result.proposal_rationale, MappingProxyType)
        self.assertIsInstance(result.application_evidence, MappingProxyType)
        self.assertIsInstance(result.evidence_payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.evidence_payload["x"] = 1


if __name__ == "__main__":
    unittest.main()
