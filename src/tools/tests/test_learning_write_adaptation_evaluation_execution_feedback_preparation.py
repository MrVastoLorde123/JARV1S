from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_decision import (
    LearningWriteAdaptationEvaluationExecutionFeedbackAction,
    LearningWriteAdaptationEvaluationExecutionFeedbackDecision,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalService,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_proposal_admission import (
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionService,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_preparation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackPreparation,
    LearningWriteAdaptationEvaluationExecutionFeedbackPreparationContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError,
    LearningWriteAdaptationEvaluationExecutionFeedbackPreparationService,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackPreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        decision = LearningWriteAdaptationEvaluationExecutionFeedbackDecision(
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            preparation_id="historical-preparation-1",
            admission_id="historical-admission-1",
            proposal_id="proposal-source-1",
            decision_source_evaluation_id="historical-evaluation-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            execution_id="execution-1",
            source_execution_id="source-execution-1",
            domain="semantic",
            policy_id="policy-source-1",
            action=LearningWriteAdaptationEvaluationExecutionFeedbackAction.ACCEPT,
            reason="sufficient observed evidence",
            confidence=0.8,
        )
        proposal = LearningWriteAdaptationEvaluationExecutionFeedbackProposalService().propose(
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext(
                decision=decision,
                proposal={"strategy": {"mode": "retain"}},
            )
        )
        assert proposal is not None
        admission = LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionService().admit(
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext(
                proposal=proposal
            )
        )
        self.proposal = proposal
        self.admission = admission
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackPreparationService()

    def _prepare(self):
        return self.service.prepare(self.proposal, self.admission)

    def test_admitted_proposal_creates_preparation(self) -> None:
        preparation = self._prepare()
        self.assertIsInstance(
            preparation,
            LearningWriteAdaptationEvaluationExecutionFeedbackPreparation,
        )

    def test_non_admitted_proposal_is_rejected(self) -> None:
        rejected = self.admission.__class__(
            admission_id=self.admission.admission_id,
            proposal_id=self.admission.proposal_id,
            decision_id=self.admission.decision_id,
            evaluation_id=self.admission.evaluation_id,
            decision_source_evaluation_id=self.admission.decision_source_evaluation_id,
            feedback_id=self.admission.feedback_id,
            source_feedback_id=self.admission.source_feedback_id,
            candidate_id=self.admission.candidate_id,
            source_candidate_id=self.admission.source_candidate_id,
            execution_id=self.admission.execution_id,
            source_execution_id=self.admission.source_execution_id,
            preparation_id=self.admission.preparation_id,
            source_admission_id=self.admission.source_admission_id,
            proposal_source_id=self.admission.proposal_source_id,
            domain=self.admission.domain,
            source_policy_id=self.admission.source_policy_id,
            policy_id=self.admission.policy_id,
            status=LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.REJECTED,
            reason="rejected for test",
            confidence=self.admission.confidence,
            proposal=self.admission.proposal,
            evidence=self.admission.evidence,
            provenance=self.admission.provenance,
        )
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError):
            self.service.prepare(self.proposal, rejected)

    def test_full_lineage_is_preserved(self) -> None:
        preparation = self._prepare()
        for field in (
            "proposal_id", "decision_id", "evaluation_id", "decision_source_evaluation_id",
            "feedback_id", "source_feedback_id", "candidate_id", "source_candidate_id",
            "execution_id", "source_execution_id", "source_admission_id", "proposal_source_id",
            "domain", "source_policy_id",
        ):
            self.assertEqual(getattr(preparation, field), getattr(self.proposal, field if field != "source_admission_id" and field != "source_policy_id" else {"source_admission_id": "admission_id", "source_policy_id": "policy_id"}[field]))
        self.assertEqual(preparation.admission_id, self.admission.admission_id)
        self.assertEqual(preparation.policy_id, self.admission.policy_id)

    def test_preparation_id_is_deterministic(self) -> None:
        first = self._prepare()
        second = self._prepare()
        self.assertEqual(first.preparation_id, second.preparation_id)

    def test_preparation_id_differs_from_upstream_identities(self) -> None:
        preparation = self._prepare()
        self.assertNotEqual(preparation.preparation_id, self.proposal.proposal_id)
        self.assertNotEqual(preparation.preparation_id, self.admission.admission_id)

    def test_payload_evidence_and_provenance_are_recursively_immutable(self) -> None:
        preparation = self._prepare()
        with self.assertRaises(TypeError):
            preparation.payload["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            preparation.payload["strategy"]["mode"] = "change"  # type: ignore[index]
        with self.assertRaises(TypeError):
            preparation.evidence["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            preparation.provenance["new"] = "blocked"  # type: ignore[index]

    def test_context_is_immutable(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackPreparationContext(
            proposal=self.proposal,
            admission=self.admission,
        )
        with self.assertRaises(FrozenInstanceError):
            context.proposal = self.proposal  # type: ignore[misc]

    def test_authority_wall_is_preserved(self) -> None:
        preparation = self._prepare()
        context = preparation.to_context()
        self.assertTrue(context["execution_prepared"])
        self.assertFalse(context["execution_authorized"])
        self.assertFalse(context["execution_started"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["authority_granted"])

    def test_preparation_cannot_be_constructed_with_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackPreparation(
                preparation_id="prep-x",
                admission_id="admission-x",
                proposal_id="proposal-x",
                decision_id="decision-x",
                evaluation_id="evaluation-x",
                decision_source_evaluation_id="historical-evaluation-x",
                feedback_id="feedback-x",
                source_feedback_id="source-feedback-x",
                candidate_id="candidate-x",
                source_candidate_id="source-candidate-x",
                execution_id="execution-x",
                source_execution_id="source-execution-x",
                source_admission_id="source-admission-x",
                proposal_source_id="proposal-source-x",
                domain="semantic",
                source_policy_id="source-policy-x",
                policy_id="policy-x",
                payload={"x": 1},
                evidence={"x": 1},
                provenance={"source": "test"},
                execution_authorized=True,
            )

    def test_invalid_proposal_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.prepare({"bad": True}, self.admission)  # type: ignore[arg-type]

    def test_invalid_admission_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.prepare(self.proposal, {"bad": True})  # type: ignore[arg-type]

    def test_context_requires_exact_types(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackPreparationContext(
                proposal={"bad": True},  # type: ignore[arg-type]
                admission=self.admission,
            )
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackPreparationContext(
                proposal=self.proposal,
                admission={"bad": True},  # type: ignore[arg-type]
            )

    def test_identity_mismatch_is_rejected(self) -> None:
        bad_admission = self.admission.__class__(
            admission_id=self.admission.admission_id,
            proposal_id="wrong-proposal",
            decision_id=self.admission.decision_id,
            evaluation_id=self.admission.evaluation_id,
            decision_source_evaluation_id=self.admission.decision_source_evaluation_id,
            feedback_id=self.admission.feedback_id,
            source_feedback_id=self.admission.source_feedback_id,
            candidate_id=self.admission.candidate_id,
            source_candidate_id=self.admission.source_candidate_id,
            execution_id=self.admission.execution_id,
            source_execution_id=self.admission.source_execution_id,
            preparation_id=self.admission.preparation_id,
            source_admission_id=self.admission.source_admission_id,
            proposal_source_id=self.admission.proposal_source_id,
            domain=self.admission.domain,
            source_policy_id=self.admission.source_policy_id,
            policy_id=self.admission.policy_id,
            status=self.admission.status,
            reason=self.admission.reason,
            confidence=self.admission.confidence,
            proposal=self.admission.proposal,
            evidence=self.admission.evidence,
            provenance=self.admission.provenance,
        )
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError):
            self.service.prepare(self.proposal, bad_admission)

    def test_to_context_preserves_lineage_and_policy(self) -> None:
        preparation = self._prepare()
        context = preparation.to_context()
        self.assertEqual(
            context["learning_write_adaptation_evaluation_execution_feedback_proposal_admission_id"],
            self.admission.admission_id,
        )
        self.assertEqual(
            context["learning_write_adaptation_evaluation_execution_policy_id"],
            self.admission.policy_id,
        )
        self.assertEqual(
            context["learning_write_adaptation_source_policy_id"],
            self.proposal.policy_id,
        )


if __name__ == "__main__":
    unittest.main()
