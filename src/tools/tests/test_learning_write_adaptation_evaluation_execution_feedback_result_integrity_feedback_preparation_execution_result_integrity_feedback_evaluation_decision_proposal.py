import unittest

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation_decision import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation_decision_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposal,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalKind,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService,
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


class M22_55_Tests(unittest.TestCase):
    def test_accept_decision_produces_proposal(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(), payload={"change": "candidate-adaptation"}, evidence={"observed": True}
        )
        self.assertIsInstance(out, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposal)
        self.assertEqual(out.kind, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalKind.ACCEPTED_EVALUATION_DECISION)

    def test_defer_decision_produces_no_proposal(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(action=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.DEFER),
            payload={"change": "candidate-adaptation"},
        )
        self.assertIsNone(out)

    def test_reject_decision_produces_no_proposal(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(action=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.REJECT),
            payload={"change": "candidate-adaptation"},
        )
        self.assertIsNone(out)

    def test_full_lineage_is_preserved(self):
        source = decision()
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            source, payload={"change": "candidate-adaptation"}, evidence={"observed": True}
        )
        for field in (
            "decision_id", "evaluation_id", "feedback_id", "integrity_id", "execution_id", "preparation_id", "admission_id",
            "evaluation_id_from_feedback", "decision_source_evaluation_id", "source_feedback_id", "candidate_id",
            "source_candidate_id", "execution_source_id", "source_execution_id", "source_admission_id", "source_proposal_id",
            "domain", "source_policy_id", "policy_id",
        ):
            self.assertEqual(getattr(out, field), getattr(source, field))
        self.assertEqual(out.proposal_source_id, source.proposal_id)

    def test_source_proposal_id_and_proposal_source_id_are_distinct_lineage_roles(self):
        source = decision()
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            source, payload={"change": "candidate-adaptation"}
        )
        self.assertEqual(out.proposal_source_id, source.proposal_id)
        self.assertEqual(out.source_proposal_id, source.source_proposal_id)

    def test_proposal_id_is_deterministic_and_distinct(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService()
        first = service.propose(decision(), payload={"change": "candidate-adaptation"})
        second = service.propose(decision(), payload={"change": "candidate-adaptation"})
        self.assertEqual(first.proposal_id, second.proposal_id)
        self.assertNotEqual(first.proposal_id, first.decision_id)

    def test_proposal_is_frozen(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(), payload={"nested": {"ok": True}}
        )
        with self.assertRaises(AttributeError):
            out.reason = "changed"

    def test_payload_is_recursively_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(), payload={"nested": {"ok": True}}
        )
        with self.assertRaises((TypeError, AttributeError)):
            out.payload["nested"]["ok"] = False

    def test_evidence_is_recursively_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(), payload={"change": "x"}, evidence={"nested": {"ok": True}}
        )
        with self.assertRaises((TypeError, AttributeError)):
            out.evidence["nested"]["ok"] = False

    def test_metadata_is_recursively_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(), payload={"change": "x"}
        )
        with self.assertRaises((TypeError, AttributeError)):
            out.metadata["extra"] = "bad"

    def test_provenance_is_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(), payload={"change": "x"}, provenance={"source": "test"}
        )
        with self.assertRaises((TypeError, AttributeError)):
            out.provenance["extra"] = "bad"

    def test_invalid_payload_is_rejected(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
                decision(), payload={}
            )

    def test_authority_wall(self):
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(), payload={"change": "x"}
        ).to_context()
        for key in (
            "execution_authorized", "authorization_granted", "execution_requested", "retry_requested",
            "revocation_requested", "memory_mutation_allowed", "authority_granted", "adaptation_truth_proven",
        ):
            self.assertFalse(context[key])

    def test_proposal_does_not_establish_truth(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision(), payload={"change": "x"}
        )
        self.assertFalse(out.to_context()["adaptation_truth_proven"])

    def test_wrong_decision_type_is_rejected(self):
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
                object(), payload={"change": "x"}
            )


if __name__ == "__main__":
    unittest.main()
