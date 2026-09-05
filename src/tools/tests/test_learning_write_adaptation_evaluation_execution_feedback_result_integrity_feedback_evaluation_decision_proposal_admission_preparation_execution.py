import unittest

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation_execution import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus,
)


class SuccessfulApplier:
    def __init__(self):
        self.request = None

    def apply(self, request):
        self.request = request
        return {"observed": True, "nested": {"value": 7}}


class FailingApplier:
    def apply(self, request):
        raise RuntimeError("boom")


def make_preparation(**overrides):
    values = dict(
        preparation_id="preparation-1", admission_id="admission-1", proposal_id="proposal-1",
        decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1",
        outcome_id="outcome-1", execution_id="historical-execution-1",
        source_admission_id="source-admission-1", source_proposal_id="source-proposal-1",
        decision_source_evaluation_id="decision-source-evaluation-1",
        evaluation_id_from_feedback="feedback-evaluation-1", source_feedback_id="source-feedback-1",
        candidate_id="candidate-1", source_candidate_id="source-candidate-1",
        execution_source_id="execution-source-1", source_execution_id="source-execution-1",
        domain="learning", source_policy_id="source-policy-1", policy_id="admission-policy-1",
        payload={"action": "apply", "nested": {"items": [1, 2]}},
        evidence={"basis": "observed-integrity-evidence"}, provenance={"source": "m22.49"},
    )
    values.update(overrides)
    return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation(**values)


def request_kwargs(preparation, **overrides):
    values = {
        "execution_id": "execution-x", "preparation_id": preparation.preparation_id, "admission_id": preparation.admission_id,
        "proposal_id": preparation.proposal_id, "decision_id": preparation.decision_id, "evaluation_id": preparation.evaluation_id,
        "feedback_id": preparation.feedback_id, "outcome_id": preparation.outcome_id,
        "source_admission_id": preparation.source_admission_id, "source_proposal_id": preparation.source_proposal_id,
        "decision_source_evaluation_id": preparation.decision_source_evaluation_id,
        "evaluation_id_from_feedback": preparation.evaluation_id_from_feedback, "source_feedback_id": preparation.source_feedback_id,
        "candidate_id": preparation.candidate_id, "source_candidate_id": preparation.source_candidate_id,
        "execution_source_id": preparation.execution_source_id, "source_execution_id": preparation.source_execution_id,
        "domain": preparation.domain, "source_policy_id": preparation.source_policy_id, "policy_id": preparation.policy_id,
        "payload": preparation.payload, "evidence": preparation.evidence, "provenance": preparation.provenance,
    }
    values.update(overrides)
    return values


def result_kwargs(preparation, **overrides):
    values = {
        "execution_id": "execution-x", "preparation_id": preparation.preparation_id, "admission_id": preparation.admission_id,
        "proposal_id": preparation.proposal_id, "decision_id": preparation.decision_id, "evaluation_id": preparation.evaluation_id,
        "feedback_id": preparation.feedback_id, "outcome_id": preparation.outcome_id,
        "source_admission_id": preparation.source_admission_id, "source_proposal_id": preparation.source_proposal_id,
        "decision_source_evaluation_id": preparation.decision_source_evaluation_id,
        "evaluation_id_from_feedback": preparation.evaluation_id_from_feedback, "source_feedback_id": preparation.source_feedback_id,
        "candidate_id": preparation.candidate_id, "source_candidate_id": preparation.source_candidate_id,
        "execution_source_id": preparation.execution_source_id, "source_execution_id": preparation.source_execution_id,
        "domain": preparation.domain, "source_policy_id": preparation.source_policy_id, "policy_id": preparation.policy_id,
        "status": LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.COMPLETED,
    }
    values.update(overrides)
    return values


class M22_50_Tests(unittest.TestCase):
    def test_executes_prepared_artifact(self):
        applier = SuccessfulApplier()
        result = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(applier).execute(make_preparation())
        self.assertEqual(result.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.COMPLETED)
        self.assertEqual(result.execution_result["observed"], True)
        self.assertIsNotNone(applier.request)

    def test_applier_failure_is_normalized(self):
        result = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(FailingApplier()).execute(make_preparation())
        self.assertEqual(result.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.FAILED)
        self.assertEqual(result.reason, "boom")

    def test_wrong_preparation_type_is_rejected(self):
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier()).execute(object())

    def test_full_lineage_is_preserved(self):
        preparation = make_preparation()
        result = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier()).execute(preparation)
        for field in ("preparation_id", "admission_id", "proposal_id", "decision_id", "evaluation_id", "feedback_id", "outcome_id", "execution_id", "source_admission_id", "source_proposal_id", "decision_source_evaluation_id", "evaluation_id_from_feedback", "source_feedback_id", "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id", "domain", "source_policy_id", "policy_id"):
            self.assertEqual(getattr(result, field), getattr(preparation, field))

    def test_execution_id_is_deterministic(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier())
        preparation = make_preparation()
        self.assertEqual(service._request(preparation).execution_id, service._request(preparation).execution_id)

    def test_execution_id_is_distinct_from_upstream(self):
        request = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier())._request(make_preparation())
        self.assertNotEqual(request.execution_id, "preparation-1")
        self.assertNotEqual(request.execution_id, "historical-execution-1")

    def test_request_payload_is_immutable(self):
        request = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier())._request(make_preparation())
        with self.assertRaises((AttributeError, TypeError)):
            request.payload["new"] = True

    def test_request_nested_payload_is_immutable(self):
        request = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier())._request(make_preparation())
        with self.assertRaises((AttributeError, TypeError)):
            request.payload["nested"]["items"][0] = 99

    def test_request_cannot_grant_authority(self):
        preparation = make_preparation()
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest(**request_kwargs(preparation, execution_authorized=True))

    def test_preparation_started_state_is_rejected(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier())
        bad = object.__new__(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation)
        source = make_preparation()
        for field_name, value in source.__dict__.items():
            object.__setattr__(bad, field_name, value)
        object.__setattr__(bad, "execution_started", True)
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError):
            service.execute(bad)

    def test_result_status_is_explicit(self):
        result = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier()).execute(make_preparation())
        self.assertIsInstance(result, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult)
        self.assertIsInstance(result.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus)

    def test_completed_result_cannot_have_failure_reason(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult(**result_kwargs(make_preparation(), reason="bad"))

    def test_failed_result_requires_reason(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult(**result_kwargs(make_preparation(), status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.FAILED))

    def test_result_nested_execution_observation_is_immutable(self):
        result = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier()).execute(make_preparation())
        with self.assertRaises((AttributeError, TypeError)):
            result.execution_result["nested"]["value"] = 99

    def test_provenance_is_immutable(self):
        request = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier())._request(make_preparation())
        with self.assertRaises((AttributeError, TypeError)):
            request.provenance["new"] = "x"

    def test_service_does_not_mutate_preparation(self):
        preparation = make_preparation()
        original_payload = preparation.payload
        LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService(SuccessfulApplier()).execute(preparation)
        self.assertEqual(preparation.payload, original_payload)


if __name__ == "__main__":
    unittest.main()
