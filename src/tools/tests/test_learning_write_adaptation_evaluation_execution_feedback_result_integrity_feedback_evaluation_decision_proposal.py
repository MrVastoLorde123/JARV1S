from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError,
)


class M22_47_Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluation = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
            evaluation_id="evaluation-1", feedback_id="feedback-1", outcome_id="outcome-1", execution_id="execution-1",
            preparation_id="preparation-1", admission_id="admission-1", proposal_id="proposal-1", decision_id="decision-1",
            evaluation_id_from_feedback="evaluation-from-feedback-1", decision_source_evaluation_id="decision-source-1",
            source_feedback_id="source-feedback-1", candidate_id="candidate-1", source_candidate_id="source-candidate-1",
            execution_source_id="execution-source-1", source_execution_id="source-execution-1", source_admission_id="source-admission-1",
            proposal_source_id="proposal-source-1", domain="semantic", source_policy_id="source-policy-1", policy_id="policy-1",
            signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL,
            confidence=0.8, evidence={"observed": True}, provenance={"source": "test"}, reason="success",
        )
        decision = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation=self.evaluation)
        )
        self.decision = decision
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService()

    def test_accept_creates_proposal(self):
        proposal = self.service.propose(self.decision, {"change": "candidate"})
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.action, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction.ACCEPT)

    def test_defer_creates_no_proposal(self):
        defer = self.decision.__class__(**{**self.decision.__dict__, "decision_id": "decision-f", "action": LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction.DEFER})
        self.assertIsNone(self.service.propose(defer, {"change": True}))

    def test_payload_must_be_nonempty_mapping(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError):
            self.service.propose(self.decision, {})

    def test_proposal_id_is_deterministic(self):
        first = self.service.propose(self.decision, {"change": "candidate"})
        second = self.service.propose(self.decision, {"change": "candidate"})
        self.assertEqual(first.proposal_id, second.proposal_id)

    def test_proposal_id_is_distinct(self):
        proposal = self.service.propose(self.decision, {"change": "candidate"})
        self.assertNotEqual(proposal.proposal_id, self.decision.decision_id)
        self.assertNotEqual(proposal.proposal_id, self.decision.evaluation_id)
        self.assertNotEqual(proposal.proposal_id, self.decision.feedback_id)
        self.assertNotEqual(proposal.proposal_id, self.decision.execution_id)

    def test_full_lineage_is_preserved(self):
        proposal = self.service.propose(self.decision, {"change": "candidate"})
        for name in ("decision_id", "evaluation_id", "feedback_id", "outcome_id", "execution_id", "preparation_id", "admission_id", "source_proposal_id", "decision_source_evaluation_id", "evaluation_id_from_feedback", "source_feedback_id", "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id", "source_admission_id", "proposal_source_id", "domain", "source_policy_id", "policy_id"):
            expected_name = "proposal_id" if name == "source_proposal_id" else name
            self.assertEqual(getattr(proposal, name), getattr(self.decision, expected_name))

    def test_proposal_is_immutable(self):
        proposal = self.service.propose(self.decision, {"change": "candidate"})
        with self.assertRaises(FrozenInstanceError):
            proposal.reason = "changed"  # type: ignore[misc]

    def test_payload_is_recursively_immutable(self):
        proposal = self.service.propose(self.decision, {"nested": {"value": True}, "items": [1, 2]})
        with self.assertRaises(TypeError):
            proposal.payload["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            proposal.payload["nested"]["value"] = False  # type: ignore[index]

    def test_evidence_is_recursively_immutable(self):
        proposal = self.service.propose(self.decision, {"x": 1}, {"nested": {"x": True}})
        with self.assertRaises(TypeError):
            proposal.evidence["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            proposal.evidence["nested"]["x"] = False  # type: ignore[index]

    def test_provenance_is_immutable(self):
        proposal = self.service.propose(self.decision, {"x": 1}, provenance={"source": "test"})
        with self.assertRaises(TypeError):
            proposal.provenance["new"] = "blocked"  # type: ignore[index]

    def test_context_preserves_authority_wall(self):
        proposal = self.service.propose(self.decision, {"change": "candidate"})
        context = proposal.to_context()
        for key in ("execution_authorized", "authorization_granted", "execution_requested", "retry_requested", "revocation_requested", "memory_mutation_allowed", "authority_granted", "adaptation_truth_proven"):
            self.assertFalse(context[key])

    def test_confidence_preserved_and_bounded(self):
        proposal = self.service.propose(self.decision, {"change": "candidate"})
        self.assertEqual(proposal.confidence, 0.8)
        self.assertGreaterEqual(proposal.confidence, 0.0)
        self.assertLessEqual(proposal.confidence, 1.0)

    def test_only_accept_can_be_proposed(self):
        reject = self.decision.__class__(**{**self.decision.__dict__, "decision_id": "decision-r", "action": LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction.REJECT})
        self.assertIsNone(self.service.propose(reject, {"change": True}))

    def test_proposal_kind_is_explicit(self):
        proposal = self.service.propose(self.decision, {"change": "candidate"})
        self.assertEqual(proposal.kind.value, "accepted_evaluation")

    def test_metadata_is_immutable(self):
        proposal = self.service.propose(self.decision, {"change": "candidate"})
        with self.assertRaises(TypeError):
            proposal.metadata["new"] = True  # type: ignore[index]

    def test_context_is_non_authorizing(self):
        proposal = self.service.propose(self.decision, {"change": "candidate"})
        self.assertFalse(proposal.to_context()["authority_granted"])


if __name__ == "__main__":
    unittest.main()
