import unittest

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation_decision import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService,
)


def evaluation(**overrides):
    values = dict(
        evaluation_id="evaluation-1", feedback_id="feedback-1", integrity_id="integrity-1", execution_id="execution-1",
        preparation_id="preparation-1", admission_id="admission-1", proposal_id="proposal-1", decision_id="decision-1",
        evaluation_id_from_feedback="feedback-evaluation-1", decision_source_evaluation_id="decision-source-evaluation-1",
        source_feedback_id="source-feedback-1", candidate_id="candidate-1", source_candidate_id="source-candidate-1",
        execution_source_id="execution-source-1", source_execution_id="historical-execution-1",
        source_admission_id="source-admission-1", source_proposal_id="source-proposal-1", domain="learning",
        source_policy_id="source-policy-1", policy_id="policy-1",
        signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL,
        confidence=0.5, evidence={"feedback_kind": "integrity_success", "payload": {"ok": True}},
        provenance={"source": "m22.53"}, reason="observed evaluation",
    )
    values.update(overrides)
    return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(**values)


class M22_54_Tests(unittest.TestCase):
    def test_success_evaluates_to_accept(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation())
        )
        self.assertEqual(out.action, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.ACCEPT)
        self.assertEqual(out.confidence, 0.5)

    def test_failure_evaluates_to_defer(self):
        source = evaluation(
            signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_FAILURE_SIGNAL,
            reason="failed evaluation",
        )
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(source)
        )
        self.assertEqual(out.action, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.DEFER)

    def test_low_confidence_evaluates_to_defer(self):
        source = evaluation(confidence=0.4)
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(source)
        )
        self.assertEqual(out.action, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.DEFER)

    def test_context_rejects_wrong_evaluation_type(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(object())

    def test_service_rejects_wrong_context_type(self):
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(object())

    def test_full_lineage_is_preserved(self):
        source = evaluation()
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(source)
        )
        for field in (
            "evaluation_id", "feedback_id", "integrity_id", "execution_id", "preparation_id", "admission_id",
            "proposal_id", "evaluation_id_from_feedback", "source_feedback_id", "candidate_id",
            "source_candidate_id", "execution_source_id", "source_execution_id", "source_admission_id",
            "source_proposal_id", "domain", "source_policy_id", "policy_id",
        ):
            self.assertEqual(getattr(out, field), getattr(source, field))
        self.assertEqual(out.decision_source_evaluation_id, source.evaluation_id)

    def test_decision_id_is_deterministic_and_distinct(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService()
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation())
        first = service.decide(context)
        second = service.decide(context)
        self.assertEqual(first.decision_id, second.decision_id)
        self.assertNotEqual(first.decision_id, context.evaluation.evaluation_id)

    def test_decision_is_frozen(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation())
        )
        with self.assertRaises(AttributeError):
            out.reason = "changed"

    def test_metadata_is_recursively_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation())
        )
        with self.assertRaises((TypeError, AttributeError)):
            out.metadata["nested"] = {"changed": True}

    def test_authority_wall(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation())
        )
        self.assertFalse(out.execution_authorized)
        self.assertFalse(out.retry_requested)
        self.assertFalse(out.revocation_requested)
        self.assertFalse(out.memory_mutation_allowed)
        self.assertFalse(out.authority_granted)
        context = out.to_context()
        for key in (
            "execution_authorized", "authorization_granted", "execution_requested", "retry_requested",
            "revocation_requested", "memory_mutation_allowed", "adaptation_truth_proven", "authority_granted",
        ):
            self.assertFalse(context[key])

    def test_decision_does_not_establish_truth(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation())
        )
        self.assertFalse(out.to_context()["adaptation_truth_proven"])

    def test_proposal_lineage_uses_source_proposal_id(self):
        source = evaluation(source_proposal_id="canonical-source-proposal")
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(source)
        )
        self.assertEqual(out.source_proposal_id, "canonical-source-proposal")
        self.assertEqual(out.to_context()["learning_write_adaptation_evaluation_proposal_id"], "canonical-source-proposal")

    def test_invalid_confidence_is_rejected(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision(
                decision_id="decision", evaluation_id="evaluation", feedback_id="feedback", integrity_id="integrity",
                execution_id="execution", preparation_id="preparation", admission_id="admission", proposal_id="proposal",
                evaluation_id_from_feedback="feedback-evaluation", decision_source_evaluation_id="evaluation",
                source_feedback_id="source-feedback", candidate_id="candidate", source_candidate_id="source-candidate",
                execution_source_id="execution-source", source_execution_id="source-execution", source_admission_id="source-admission",
                source_proposal_id="source-proposal", domain="learning", source_policy_id="source-policy", policy_id="policy",
                action=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.ACCEPT,
                reason="reason", confidence=1.1, metadata={},
            )

    def test_context_related_data_is_immutable(self):
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
            evaluation(), related_context={"nested": {"value": 1}}
        )
        with self.assertRaises((TypeError, AttributeError)):
            context.related_context["nested"]["value"] = 2

    def test_provider_lineage_mismatch_is_rejected(self):
        class BadProvider:
            def decide(self, context):
                service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService()
                good = service._provider.decide(context)
                return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision(
                    **{**good.__dict__, "source_proposal_id": "wrong-source-proposal"}
                )

        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService(BadProvider()).decide(
                LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation())
            )


if __name__ == "__main__":
    unittest.main()
