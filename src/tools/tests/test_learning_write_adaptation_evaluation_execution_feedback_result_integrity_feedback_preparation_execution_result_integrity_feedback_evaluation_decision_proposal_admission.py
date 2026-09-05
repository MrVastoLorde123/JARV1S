import unittest

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation_decision import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation_decision_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation_decision_proposal_admission import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus,
)


def decision(**overrides):
    values = dict(
        decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1", integrity_id="integrity-1",
        execution_id="execution-1", preparation_id="preparation-1", admission_id="admission-1", proposal_id="proposal-1",
        evaluation_id_from_feedback="evaluation-from-feedback-1", decision_source_evaluation_id="evaluation-1",
        source_feedback_id="source-feedback-1", candidate_id="candidate-1", source_candidate_id="source-candidate-1",
        execution_source_id="execution-source-1", source_execution_id="source-execution-1", source_admission_id="source-admission-1",
        source_proposal_id="source-proposal-1", domain="learning", source_policy_id="source-policy-1", policy_id="policy-1",
        action=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.ACCEPT,
        reason="accepted", confidence=0.5, metadata={"source": "test"},
    )
    values.update(overrides)
    return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision(**values)


def proposal(**overrides):
    values = dict(decision=decision(), payload={"change": "candidate-adaptation"}, evidence={"observed": True}, provenance={"source": "test"})
    values.update(overrides)
    return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(**values)


class M22_56_Tests(unittest.TestCase):
    def context(self, source=None, related_context=None):
        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(
            proposal=source or proposal(), related_context=related_context or {}
        )

    def test_admitted_proposal(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(self.context())
        self.assertEqual(out.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.ADMITTED)

    def test_wrong_context_type_is_rejected(self):
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(object())

    def test_context_related_data_is_immutable(self):
        context = self.context(related_context={"nested": {"ok": True}})
        with self.assertRaises((TypeError, AttributeError)):
            context.related_context["nested"]["ok"] = False

    def test_full_lineage_is_preserved(self):
        source = proposal()
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(self.context(source))
        for field in (
            "proposal_id", "decision_id", "evaluation_id", "feedback_id", "integrity_id", "execution_id", "preparation_id",
            "proposal_source_id", "source_proposal_id", "decision_source_evaluation_id", "evaluation_id_from_feedback",
            "source_feedback_id", "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id",
            "domain",
        ):
            self.assertEqual(getattr(out, field), getattr(source, field))
        self.assertEqual(out.source_policy_id, source.policy_id)
        self.assertEqual(out.source_admission_id, source.admission_id)

    def test_policy_lineage_changes_at_admission(self):
        source = proposal()
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(self.context(source))
        self.assertEqual(out.source_policy_id, source.policy_id)
        self.assertNotEqual(out.policy_id, source.policy_id)

    def test_admission_id_is_deterministic_and_distinct(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService()
        first = service.admit(self.context())
        second = service.admit(self.context())
        self.assertEqual(first.admission_id, second.admission_id)
        self.assertNotEqual(first.admission_id, first.proposal_id)

    def test_admission_is_frozen(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(self.context())
        with self.assertRaises(AttributeError):
            out.reason = "changed"

    def test_payload_is_recursively_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(
            self.context(proposal(payload={"nested": {"ok": True}}))
        )
        with self.assertRaises((TypeError, AttributeError)):
            out.proposal["nested"]["ok"] = False

    def test_evidence_is_recursively_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(
            self.context(proposal(evidence={"nested": {"ok": True}}))
        )
        with self.assertRaises((TypeError, AttributeError)):
            out.evidence["nested"]["ok"] = False

    def test_metadata_is_recursively_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(self.context())
        with self.assertRaises((TypeError, AttributeError)):
            out.metadata["nested"] = "bad"

    def test_confidence_bounds_are_enforced(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission(
                admission_id="admission", proposal_id="proposal", decision_id="decision", evaluation_id="evaluation",
                feedback_id="feedback", integrity_id="integrity", execution_id="execution", preparation_id="preparation",
                proposal_source_id="proposal-source", source_proposal_id="source-proposal", decision_source_evaluation_id="decision-source",
                evaluation_id_from_feedback="evaluation-from-feedback", source_feedback_id="source-feedback", candidate_id="candidate",
                source_candidate_id="source-candidate", execution_source_id="execution-source", source_execution_id="source-execution",
                source_admission_id="source-admission", domain="learning", source_policy_id="source-policy", policy_id="policy",
                status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.ADMITTED,
                reason="reason", confidence=1.1, proposal={"change": "x"}, evidence={}, provenance={"source": "test"},
            )

    def test_authority_wall(self):
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(self.context()).to_context()
        for key in (
            "execution_authorized", "authorization_granted", "execution_requested", "retry_requested",
            "revocation_requested", "memory_mutation_allowed", "authority_granted",
        ):
            self.assertFalse(context[key])

    def test_admission_does_not_establish_truth(self):
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(self.context()).to_context()
        self.assertFalse(context["adaptation_truth_proven"])

    def test_wrong_provider_output_type_is_rejected(self):
        class BadProvider:
            def admit(self, context):
                return object()
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService(provider=BadProvider()).admit(self.context())

    def test_provider_lineage_mismatch_is_rejected(self):
        class BadProvider:
            def admit(self, context):
                source = context.proposal
                return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission(
                    admission_id="admission", proposal_id="wrong", decision_id=source.decision_id, evaluation_id=source.evaluation_id,
                    feedback_id=source.feedback_id, integrity_id=source.integrity_id, execution_id=source.execution_id,
                    preparation_id=source.preparation_id, proposal_source_id=source.proposal_source_id, source_proposal_id=source.source_proposal_id,
                    decision_source_evaluation_id=source.decision_source_evaluation_id, evaluation_id_from_feedback=source.evaluation_id_from_feedback,
                    source_feedback_id=source.source_feedback_id, candidate_id=source.candidate_id, source_candidate_id=source.source_candidate_id,
                    execution_source_id=source.execution_source_id, source_execution_id=source.source_execution_id, source_admission_id=source.admission_id,
                    domain=source.domain, source_policy_id=source.policy_id, policy_id="new-policy",
                    status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.ADMITTED,
                    reason="ok", confidence=source.confidence, proposal=source.payload, evidence=source.evidence, provenance=source.provenance,
                )
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService(provider=BadProvider()).admit(self.context())

    def test_rejected_status_is_non_authorizing(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService()
        source = proposal()
        rejected = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission(
            admission_id="rejected-admission", proposal_id=source.proposal_id, decision_id=source.decision_id, evaluation_id=source.evaluation_id,
            feedback_id=source.feedback_id, integrity_id=source.integrity_id, execution_id=source.execution_id, preparation_id=source.preparation_id,
            proposal_source_id=source.proposal_source_id, source_proposal_id=source.source_proposal_id, decision_source_evaluation_id=source.decision_source_evaluation_id,
            evaluation_id_from_feedback=source.evaluation_id_from_feedback, source_feedback_id=source.source_feedback_id, candidate_id=source.candidate_id,
            source_candidate_id=source.source_candidate_id, execution_source_id=source.execution_source_id, source_execution_id=source.source_execution_id,
            source_admission_id=source.admission_id, domain=source.domain, source_policy_id=source.policy_id, policy_id="new-policy",
            status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED,
            reason="rejected", confidence=source.confidence, proposal={}, evidence={}, provenance={"source": "test"},
        )
        self.assertFalse(rejected.authority_granted)
        self.assertEqual(rejected.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED)


if __name__ == "__main__":
    unittest.main()
