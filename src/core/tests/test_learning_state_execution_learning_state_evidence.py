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
)
from src.core.learning_state_execution_learning_proposal_application import (
    LearningStateExecutionLearningProposalApplicationService,
)
from src.core.learning_state_execution_learning_proposal_application_integrity import (
    LearningStateExecutionLearningProposalApplicationIntegrityService,
)
from src.core.learning_state_execution_learning_state_evidence import (
    LearningStateExecutionLearningStateEvidenceService,
    LearningStateExecutionLearningStateEvidenceStatus,
)
from src.core.learning_state_execution_outcome import LearningStateExecutionOutcomeStatus
from src.core.learning_state_execution_feedback import LearningStateExecutionFeedbackKind


class M23_132LearningStateEvidenceTests(unittest.TestCase):
    def _make_integrity(self, *, invalid=False):
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
        integrity = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(
            application, integrity_id="application-integrity-131"
        )
        if invalid:
            object.__setattr__(integrity, "application_id", "tampered-application")
        return integrity

    def _record(self, **kwargs):
        defaults = {
            "evidence_id": "evidence-132",
            "evidence_collector_id": "evidence-collector-A",
            "evidence_purpose": "record-candidate-state-effect",
            "evidence_rationale": {"basis": ["valid-integrity", {"scope": "bounded"}]},
            "evidence_payload": {"candidate_state": {"threshold": 0.95}, "observed": [1, 2]},
        }
        defaults.update(kwargs)
        return LearningStateExecutionLearningStateEvidenceService().record(
            self._make_integrity(), **defaults
        )

    def test_valid_integrity_produces_recorded_evidence(self):
        result = self._record()
        self.assertIs(result.status, LearningStateExecutionLearningStateEvidenceStatus.RECORDED)
        self.assertTrue(result.is_recorded)
        self.assertTrue(result.records_state_evidence)

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningStateEvidenceService().record(
                object(),
                evidence_id="evidence-132",
                evidence_collector_id="collector-A",
                evidence_purpose="record",
                evidence_rationale={"basis": "x"},
                evidence_payload={"x": 1},
            )

    def test_required_evidence_metadata_is_enforced(self):
        service = LearningStateExecutionLearningStateEvidenceService()
        integrity = self._make_integrity()
        with self.assertRaises(ValueError):
            service.record(
                integrity,
                evidence_id=" ",
                evidence_collector_id="collector-A",
                evidence_purpose="record",
                evidence_rationale={"basis": "x"},
                evidence_payload={"x": 1},
            )
        with self.assertRaises(ValueError):
            service.record(
                integrity,
                evidence_id="evidence-132",
                evidence_collector_id=" ",
                evidence_purpose="record",
                evidence_rationale={"basis": "x"},
                evidence_payload={"x": 1},
            )
        with self.assertRaises(ValueError):
            service.record(
                integrity,
                evidence_id="evidence-132",
                evidence_collector_id="collector-A",
                evidence_purpose="record",
                evidence_rationale=None,
                evidence_payload={"x": 1},
            )

    def test_invalid_integrity_fails_closed(self):
        result = LearningStateExecutionLearningStateEvidenceService().record(
            self._make_integrity(invalid=True),
            evidence_id="evidence-132",
            evidence_collector_id="collector-A",
            evidence_purpose="record",
            evidence_rationale={"basis": "invalid-source"},
            evidence_payload={"x": 1},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateEvidenceStatus.REJECTED)
        self.assertIn("application integrity is not VALID", result.reasons)

    def test_provenance_and_fingerprints_are_preserved(self):
        integrity = self._make_integrity()
        result = self._record()
        for field in (
            "integrity_id", "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id",
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "validation_id",
            "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "transition_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "confidence", "consumer_id",
            "execution_target_id", "execution_purpose", "objective", "evaluator_id", "evaluation_purpose", "signal_kind",
            "signal_purpose", "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose", "decision_maker_id",
            "decision_purpose", "applier_id", "application_purpose", "application_status",
        ):
            self.assertEqual(getattr(result, field), getattr(integrity, field))

    def test_evidence_metadata_is_recorded_explicitly(self):
        result = self._record()
        self.assertEqual(result.evidence_id, "evidence-132")
        self.assertEqual(result.evidence_collector_id, "evidence-collector-A")
        self.assertEqual(result.evidence_purpose, "record-candidate-state-effect")
        self.assertEqual(result.evidence_rationale["basis"][0], "valid-integrity")

    def test_nested_payload_and_lineage_are_recursively_frozen(self):
        result = self._record()
        self.assertIsInstance(result.evidence_payload, MappingProxyType)
        self.assertIsInstance(result.evidence_payload["candidate_state"], MappingProxyType)
        self.assertIsInstance(result.evidence_payload["observed"], tuple)
        self.assertIsInstance(result.lineage, MappingProxyType)

    def test_reasons_are_immutable_and_preserved(self):
        result = self._record(reasons=("caller-reason",))
        self.assertEqual(result.reasons, ("caller-reason",))
        with self.assertRaises(TypeError):
            self._record(reasons=("ok", " "))

    def test_source_integrity_is_not_mutated(self):
        integrity = self._make_integrity()
        before = integrity.status
        result = LearningStateExecutionLearningStateEvidenceService().record(
            integrity,
            evidence_id="evidence-132",
            evidence_collector_id="collector-A",
            evidence_purpose="record",
            evidence_rationale={"basis": "x"},
            evidence_payload={"x": 1},
        )
        self.assertIs(integrity.status, before)
        self.assertEqual(integrity.application_id, "application-130")
        self.assertEqual(result.integrity_id, integrity.integrity_id)

    def test_evidence_artifact_is_immutable(self):
        result = self._record()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateEvidenceStatus.REJECTED

    def test_evidence_is_deterministic_for_same_inputs(self):
        first = self._record()
        second = self._record()
        self.assertEqual(first, second)

    def test_state_evidence_does_not_transition_or_mutate_state(self):
        result = self._record()
        self.assertFalse(result.transitions_state)
        self.assertFalse(result.mutates_state)
        self.assertFalse(result.persists_state)

    def test_evidence_has_no_learning_or_authority_powers(self):
        result = self._record()
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "updates_model", "mutates_memory",
            "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness", "proposes_adaptation",
        ):
            self.assertFalse(getattr(result, name))

    def test_caller_lineage_is_preserved_without_source_mutation(self):
        custom_lineage = {"evidence_id": "evidence-132", "integrity_id": "application-integrity-131", "chain": {"step": 3}}
        result = self._record(lineage=custom_lineage)
        self.assertEqual(result.lineage["evidence_id"], "evidence-132")
        self.assertEqual(result.lineage["chain"]["step"], 3)


if __name__ == "__main__":
    unittest.main()
