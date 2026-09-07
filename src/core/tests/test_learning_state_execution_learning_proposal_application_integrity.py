import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_signal import LearningStateExecutionLearningSignalKind, LearningStateExecutionLearningSignalService
from src.core.learning_state_execution_learning_signal_integrity import LearningStateExecutionLearningSignalIntegrityService
from src.core.learning_state_execution_learning_eligibility import LearningStateExecutionLearningEligibilityService
from src.core.learning_state_execution_learning_proposal import LearningStateExecutionLearningProposalService
from src.core.learning_state_execution_learning_proposal_decision import LearningStateExecutionLearningProposalDecisionService
from src.core.learning_state_execution_learning_proposal_application import LearningStateExecutionLearningProposalApplicationService, LearningStateExecutionLearningProposalApplicationStatus
from src.core.learning_state_execution_learning_proposal_application_integrity import LearningStateExecutionLearningProposalApplicationIntegrityService, LearningStateExecutionLearningProposalApplicationIntegrityStatus


class M23_131LearningProposalApplicationIntegrityTests(unittest.TestCase):
    def _make_application(self, *, malformed_lineage=False):
        evaluation = __import__("src.core.learning_state_execution_evaluation", fromlist=["LearningStateExecutionEvaluation"]).LearningStateExecutionEvaluation(
            evaluation_id="evaluation-124", feedback_id="feedback-123", outcome_id="outcome-122", attempt_id="attempt-121", admission_id="admission-120", eligibility_id="eligibility-119",
            handling_id="handling-118", consumption_id="consumption-117", receipt_id="receipt-116", handoff_id="handoff-115", integrity_id="integrity-114", validation_id="validation-113",
            use_id="use-112", request_id="semantic-use-111", interpretation_id="interpretation-108", source_request_id="request-107", read_validation_id="read-validation-106", read_id="read-105",
            consumption_request_id="consumption-104", source_validation_id="source-validation-103", source_integrity_id="source-integrity-102", transition_id="transition-98", evidence_id="evidence-97",
            application_id="application-96", state_key="demo.state", transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64, computed_application_fingerprint="c" * 64,
            confidence=0.91, consumer_id="consumer-A", use_purpose="semantic-use", downstream_recipient_id="receiver-X", downstream_handler_id="handler-X", handling_purpose="route",
            execution_target_id="executor-X", execution_purpose="perform", outcome_status=__import__("src.core.learning_state_execution_outcome", fromlist=["LearningStateExecutionOutcomeStatus"]).LearningStateExecutionOutcomeStatus.SUCCESS,
            feedback_kind=__import__("src.core.learning_state_execution_feedback", fromlist=["LearningStateExecutionFeedbackKind"]).LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK,
            observed_consequence={"state": "changed"}, executor_output={"raw": "result"}, failure_type=None, failure_message=None, objective="reach-target", evaluator_id="evaluator-A",
            evaluation_purpose="assess", evaluation_judgment={"score": 0.8}, evaluation_context={"objective": "reach-target"}, reasons={"source": "m23.124"}, lineage={"evaluation_id": "evaluation-124"},
        )
        signal = LearningStateExecutionLearningSignalService().create(evaluation, signal_id="signal-125", signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE, signal_purpose="feed-learning")
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        eligibility = LearningStateExecutionLearningEligibilityService().evaluate(integrity, eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning")
        proposal = LearningStateExecutionLearningProposalService().propose(eligibility, proposal_id="proposal-128", proposer_id="proposer-A", proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95}, rationale={"why": {"score": 0.8}})
        decision = LearningStateExecutionLearningProposalDecisionService().decide(proposal, decision_id="decision-129", decision_maker_id="decision-maker-A", decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"})
        lineage = {"application_id": "wrong-id", "decision_id": decision.decision_id} if malformed_lineage else {"application_id": "application-130", "decision_id": decision.decision_id}
        return LearningStateExecutionLearningProposalApplicationService().apply(
            decision, application_id="application-130", applier_id="applier-A", application_purpose="apply-approved-learning", application_rationale={"basis": ["approved", {"scope": "bounded"}]},
            application_evidence={"attempt": [{"step": 1}, {"step": 2}]}, lineage=lineage,
        )

    def test_valid_application_produces_valid_integrity(self):
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(self._make_application(), integrity_id="application-integrity-131")
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)
        self.assertTrue(result.validates_application)

    def test_exact_application_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningProposalApplicationIntegrityService().validate(object(), integrity_id="application-integrity-131")

    def test_integrity_id_is_required(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionLearningProposalApplicationIntegrityService().validate(self._make_application(), integrity_id=" ")

    def test_application_lineage_is_checked(self):
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(self._make_application(malformed_lineage=True), integrity_id="application-integrity-131")
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID)
        self.assertIn("application lineage mismatch", result.reasons)

    def test_application_identity_and_provenance_are_preserved(self):
        application = self._make_application()
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(application, integrity_id="application-integrity-131")
        for field in (
            "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id",
            "attempt_id", "admission_id", "validation_id", "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id", "consumption_request_id",
            "source_validation_id", "transition_id", "evidence_id", "state_key", "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "consumer_id", "execution_target_id", "execution_purpose", "objective", "evaluator_id", "evaluation_purpose", "signal_kind", "signal_purpose", "learner_id",
            "eligibility_purpose", "proposer_id", "proposal_purpose", "decision_maker_id", "decision_purpose", "applier_id", "application_purpose",
        ):
            expected = application.integrity_id if field == "source_integrity_id" else getattr(application, field)
            self.assertEqual(getattr(result, field), expected)
        self.assertEqual(result.application_status, application.status)
        self.assertEqual(result.proposed_change, application.proposed_change)
        self.assertEqual(result.application_rationale, application.application_rationale)

    def test_integrity_id_is_new_and_source_integrity_is_preserved(self):
        application = self._make_application()
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(application, integrity_id="application-integrity-131")
        self.assertNotEqual(result.integrity_id, application.integrity_id)
        self.assertEqual(result.source_integrity_id, application.integrity_id)

    def test_fingerprints_and_confidence_are_preserved(self):
        application = self._make_application()
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(application, integrity_id="application-integrity-131")
        self.assertEqual(result.transition_fingerprint, application.transition_fingerprint)
        self.assertEqual(result.source_application_fingerprint, application.source_application_fingerprint)
        self.assertEqual(result.computed_application_fingerprint, application.computed_application_fingerprint)
        self.assertEqual(result.confidence, application.confidence)

    def test_nested_evidence_and_lineage_are_recursively_frozen(self):
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(self._make_application(), integrity_id="application-integrity-131")
        self.assertIsInstance(result.application_evidence["attempt"], tuple)
        self.assertIsInstance(result.application_evidence["attempt"][0], MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)

    def test_reasons_are_immutable_and_preserved(self):
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(self._make_application(), integrity_id="application-integrity-131", reasons=("caller-reason",))
        self.assertEqual(result.reasons, ("caller-reason",))
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningProposalApplicationIntegrityService().validate(self._make_application(), integrity_id="application-integrity-131", reasons=("ok", " "))

    def test_source_application_is_not_mutated(self):
        application = self._make_application()
        before = application.status
        LearningStateExecutionLearningProposalApplicationIntegrityService().validate(application, integrity_id="application-integrity-131")
        self.assertIs(application.status, before)

    def test_integrity_artifact_is_immutable(self):
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(self._make_application(), integrity_id="application-integrity-131")
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID

    def test_integrity_is_deterministic_for_same_inputs(self):
        service = LearningStateExecutionLearningProposalApplicationIntegrityService()
        first = service.validate(self._make_application(), integrity_id="application-integrity-131")
        second = service.validate(self._make_application(), integrity_id="application-integrity-131")
        self.assertEqual(first, second)

    def test_invalid_fingerprint_is_reported_without_repair(self):
        application = self._make_application()
        object.__setattr__(application, "source_application_fingerprint", "bad")
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(application, integrity_id="application-integrity-131")
        self.assertIs(result.status, LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID)
        self.assertIn("invalid source_application_fingerprint", result.reasons)
        self.assertEqual(result.source_application_fingerprint, "bad")

    def test_integrity_has_no_learning_authority_or_execution_power(self):
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(self._make_application(), integrity_id="application-integrity-131")
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry", "invokes_learner", "updates_model",
            "mutates_memory", "mutates_policy", "invokes_executor", "schedules_work", "plans_work", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness", "proposes_adaptation",
        ):
            self.assertFalse(getattr(result, name))

    def test_application_status_is_preserved_as_evidence(self):
        application = self._make_application()
        result = LearningStateExecutionLearningProposalApplicationIntegrityService().validate(application, integrity_id="application-integrity-131")
        self.assertIs(result.application_status, LearningStateExecutionLearningProposalApplicationStatus.ATTEMPTED)


if __name__ == "__main__":
    unittest.main()
