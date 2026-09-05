import hashlib
import json
import unittest
from collections.abc import Mapping

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation_execution_result_integrity import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation_execution import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus,
)


def _json_ready(value):
    if isinstance(value, Mapping):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_json_ready(item) for item in value), key=repr)
    return value


def request(**overrides):
    values = dict(
        execution_id="execution-1", preparation_id="preparation-1", admission_id="admission-1", proposal_id="proposal-1",
        decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1", outcome_id="outcome-1",
        source_admission_id="source-admission-1", source_proposal_id="source-proposal-1", decision_source_evaluation_id="decision-source-evaluation-1",
        evaluation_id_from_feedback="feedback-evaluation-1", source_feedback_id="source-feedback-1", candidate_id="candidate-1",
        source_candidate_id="source-candidate-1", execution_source_id="execution-source-1", source_execution_id="historical-execution-1",
        domain="learning", source_policy_id="source-policy-1", policy_id="policy-1",
        payload={"action": "apply", "nested": {"items": [1, 2]}}, evidence={"basis": "observed"}, provenance={"source": "m22.50"},
    )
    values.update(overrides)
    return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest(**values)


def result(req, **overrides):
    values = dict(
        execution_id=req.execution_id, preparation_id=req.preparation_id, admission_id=req.admission_id, proposal_id=req.proposal_id,
        decision_id=req.decision_id, evaluation_id=req.evaluation_id, feedback_id=req.feedback_id, outcome_id=req.outcome_id,
        source_admission_id=req.source_admission_id, source_proposal_id=req.source_proposal_id,
        decision_source_evaluation_id=req.decision_source_evaluation_id, evaluation_id_from_feedback=req.evaluation_id_from_feedback,
        source_feedback_id=req.source_feedback_id, candidate_id=req.candidate_id, source_candidate_id=req.source_candidate_id,
        execution_source_id=req.execution_source_id, source_execution_id=req.source_execution_id, domain=req.domain,
        source_policy_id=req.source_policy_id, policy_id=req.policy_id,
        status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.COMPLETED,
        execution_result={"ok": True, "nested": {"value": 7}},
    )
    values.update(overrides)
    return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult(**values)


class M22_51_Tests(unittest.TestCase):
    def test_success_normalizes_to_succeeded(self):
        req = request(); out = result(req)
        integrity = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(out, req)
        self.assertEqual(integrity.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.SUCCEEDED)

    def test_success_has_sha256_fingerprint(self):
        req = request(); out = result(req)
        integrity = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(out, req)
        expected = hashlib.sha256(json.dumps(_json_ready(out.execution_result), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(integrity.result_fingerprint, expected)

    def test_failed_normalizes_to_failed(self):
        req = request(); out = result(req, status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.FAILED, execution_result=None, reason="boom")
        integrity = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(out, req)
        self.assertEqual(integrity.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.FAILED)
        self.assertEqual(integrity.reason, "boom")
        self.assertIsNone(integrity.result_fingerprint)

    def test_full_lineage_is_preserved(self):
        req = request(); out = result(req)
        integrity = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(out, req)
        for field in ("execution_id", "preparation_id", "admission_id", "proposal_id", "decision_id", "evaluation_id", "feedback_id", "outcome_id", "source_admission_id", "source_proposal_id", "decision_source_evaluation_id", "evaluation_id_from_feedback", "source_feedback_id", "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id", "domain", "source_policy_id", "policy_id"):
            self.assertEqual(getattr(integrity, field), getattr(out, field))

    def test_execution_lineage_mismatch_is_rejected(self):
        req = request(); out = result(req, execution_id="other-execution")
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(out, req)

    def test_preparation_lineage_mismatch_is_rejected(self):
        req = request(); out = result(req, preparation_id="other-preparation")
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(out, req)

    def test_request_type_is_exact(self):
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(object(), request())

    def test_success_requires_fingerprint(self):
        req = request()
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity(
                integrity_id="integrity-1", execution_id=req.execution_id, preparation_id=req.preparation_id, admission_id=req.admission_id,
                proposal_id=req.proposal_id, decision_id=req.decision_id, evaluation_id=req.evaluation_id, feedback_id=req.feedback_id,
                outcome_id=req.outcome_id, source_admission_id=req.source_admission_id, source_proposal_id=req.source_proposal_id,
                decision_source_evaluation_id=req.decision_source_evaluation_id, evaluation_id_from_feedback=req.evaluation_id_from_feedback,
                source_feedback_id=req.source_feedback_id, candidate_id=req.candidate_id, source_candidate_id=req.source_candidate_id,
                execution_source_id=req.execution_source_id, source_execution_id=req.source_execution_id, domain=req.domain,
                source_policy_id=req.source_policy_id, policy_id=req.policy_id,
                status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.SUCCEEDED,
            )

    def test_failed_requires_reason(self):
        req = request()
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity(
                integrity_id="integrity-1", execution_id=req.execution_id, preparation_id=req.preparation_id, admission_id=req.admission_id,
                proposal_id=req.proposal_id, decision_id=req.decision_id, evaluation_id=req.evaluation_id, feedback_id=req.feedback_id,
                outcome_id=req.outcome_id, source_admission_id=req.source_admission_id, source_proposal_id=req.source_proposal_id,
                decision_source_evaluation_id=req.decision_source_evaluation_id, evaluation_id_from_feedback=req.evaluation_id_from_feedback,
                source_feedback_id=req.source_feedback_id, candidate_id=req.candidate_id, source_candidate_id=req.source_candidate_id,
                execution_source_id=req.execution_source_id, source_execution_id=req.source_execution_id, domain=req.domain,
                source_policy_id=req.source_policy_id, policy_id=req.policy_id,
                status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.FAILED,
            )

    def test_success_cannot_have_reason(self):
        req = request(); out = result(req)
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity(
                integrity_id="integrity-1", execution_id=req.execution_id, preparation_id=req.preparation_id, admission_id=req.admission_id,
                proposal_id=req.proposal_id, decision_id=req.decision_id, evaluation_id=req.evaluation_id, feedback_id=req.feedback_id,
                outcome_id=req.outcome_id, source_admission_id=req.source_admission_id, source_proposal_id=req.source_proposal_id,
                decision_source_evaluation_id=req.decision_source_evaluation_id, evaluation_id_from_feedback=req.evaluation_id_from_feedback,
                source_feedback_id=req.source_feedback_id, candidate_id=req.candidate_id, source_candidate_id=req.source_candidate_id,
                execution_source_id=req.execution_source_id, source_execution_id=req.source_execution_id, domain=req.domain,
                source_policy_id=req.source_policy_id, policy_id=req.policy_id,
                status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.SUCCEEDED,
                result_fingerprint="abc", reason="bad",
            )

    def test_failed_cannot_have_fingerprint(self):
        req = request()
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity(
                integrity_id="integrity-1", execution_id=req.execution_id, preparation_id=req.preparation_id, admission_id=req.admission_id,
                proposal_id=req.proposal_id, decision_id=req.decision_id, evaluation_id=req.evaluation_id, feedback_id=req.feedback_id,
                outcome_id=req.outcome_id, source_admission_id=req.source_admission_id, source_proposal_id=req.source_proposal_id,
                decision_source_evaluation_id=req.decision_source_evaluation_id, evaluation_id_from_feedback=req.evaluation_id_from_feedback,
                source_feedback_id=req.source_feedback_id, candidate_id=req.candidate_id, source_candidate_id=req.source_candidate_id,
                execution_source_id=req.execution_source_id, source_execution_id=req.source_execution_id, domain=req.domain,
                source_policy_id=req.source_policy_id, policy_id=req.policy_id,
                status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.FAILED,
                result_fingerprint="abc", reason="boom",
            )

    def test_observed_result_is_immutable(self):
        req = request(); integrity = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(result(req), req)
        with self.assertRaises((TypeError, AttributeError)):
            integrity.execution_result["new"] = True

    def test_nested_observed_result_is_immutable(self):
        req = request(); integrity = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(result(req), req)
        with self.assertRaises((TypeError, AttributeError)):
            integrity.execution_result["nested"]["value"] = 8

    def test_integrity_id_is_deterministic(self):
        req = request(); out = result(req); service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService()
        self.assertEqual(service.evaluate(out, req).integrity_id, service.evaluate(out, req).integrity_id)

    def test_integrity_id_is_distinct_from_execution(self):
        req = request(); out = result(req); integrity = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(out, req)
        self.assertNotEqual(integrity.integrity_id, integrity.execution_id)

    def test_result_is_frozen(self):
        req = request(); out = result(req); integrity = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(out, req)
        with self.assertRaises(AttributeError):
            integrity.status = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.FAILED

    def test_invalid_integrity_status_is_rejected(self):
        req = request()
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity(
                integrity_id="integrity-1", execution_id=req.execution_id, preparation_id=req.preparation_id, admission_id=req.admission_id,
                proposal_id=req.proposal_id, decision_id=req.decision_id, evaluation_id=req.evaluation_id, feedback_id=req.feedback_id,
                outcome_id=req.outcome_id, source_admission_id=req.source_admission_id, source_proposal_id=req.source_proposal_id,
                decision_source_evaluation_id=req.decision_source_evaluation_id, evaluation_id_from_feedback=req.evaluation_id_from_feedback,
                source_feedback_id=req.source_feedback_id, candidate_id=req.candidate_id, source_candidate_id=req.source_candidate_id,
                execution_source_id=req.execution_source_id, source_execution_id=req.source_execution_id, domain=req.domain,
                source_policy_id=req.source_policy_id, policy_id=req.policy_id, status="invalid", result_fingerprint="abc",
            )

    def test_integrity_does_not_grant_authority(self):
        req = request(); out = result(req); integrity = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService().evaluate(out, req)
        self.assertFalse(hasattr(integrity, "authorization_granted"))


if __name__ == "__main__":
    unittest.main()
