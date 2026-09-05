from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, replace

from src.tools.learning_write_adaptation_evaluation_execution_feedback_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_proposal_admission import (
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionService,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = LearningWriteAdaptationEvaluationExecutionFeedbackProposal(
            proposal_id="future-proposal-1",
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            decision_source_evaluation_id="historical-evaluation-1",
            feedback_id="feedback-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            execution_id="execution-1",
            source_execution_id="source-execution-1",
            preparation_id="preparation-1",
            admission_id="source-admission-1",
            proposal_source_id="proposal-source-1",
            domain="semantic",
            policy_id="source-policy-1",
            proposal={"strategy": {"mode": "retain"}},
            evidence={"signal": "success"},
            provenance={"source": "decision"},
            confidence=0.8,
            reason="accepted observed evidence",
        )
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionService()

    def _context(self, proposal=None):
        return LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext(
            proposal=proposal or self.proposal,
        )

    def test_admitted_proposal_returns_admitted_result(self) -> None:
        admission = self.service.admit(self._context())
        self.assertEqual(
            admission.status,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.ADMITTED,
        )
        self.assertTrue(admission.reason)

    def test_low_confidence_proposal_is_rejected(self) -> None:
        low = replace(self.proposal, confidence=0.49)
        admission = self.service.admit(self._context(low))
        self.assertEqual(
            admission.status,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.REJECTED,
        )

    def test_exact_lineage_is_preserved(self) -> None:
        admission = self.service.admit(self._context())
        for field in (
            "proposal_id",
            "decision_id",
            "evaluation_id",
            "decision_source_evaluation_id",
            "feedback_id",
            "source_feedback_id",
            "candidate_id",
            "source_candidate_id",
            "execution_id",
            "source_execution_id",
            "preparation_id",
            "proposal_source_id",
            "domain",
            "source_policy_id",
        ):
            proposal_field = "policy_id" if field == "source_policy_id" else (
                "admission_id" if field == "source_admission_id" else field
            )
            if field == "source_policy_id":
                expected = self.proposal.policy_id
            else:
                expected = getattr(self.proposal, proposal_field)
            self.assertEqual(getattr(admission, field), expected)
        self.assertEqual(admission.source_admission_id, self.proposal.admission_id)
        self.assertNotEqual(admission.admission_id, self.proposal.proposal_id)

    def test_admission_policy_is_distinct_from_source_policy(self) -> None:
        admission = self.service.admit(self._context())
        self.assertEqual(
            admission.policy_id,
            "adaptation-evaluation-execution-feedback-proposal-admission-baseline-v1",
        )
        self.assertEqual(admission.source_policy_id, self.proposal.policy_id)

    def test_admission_id_is_deterministic(self) -> None:
        context = self._context()
        first = self.service.admit(context)
        second = self.service.admit(context)
        self.assertEqual(first.admission_id, second.admission_id)

    def test_admission_id_changes_with_status_reason_input(self) -> None:
        admitted = self.service.admit(self._context())
        low = self.service.admit(self._context(replace(self.proposal, confidence=0.49)))
        self.assertNotEqual(admitted.admission_id, low.admission_id)

    def test_admission_is_immutable(self) -> None:
        admission = self.service.admit(self._context())
        with self.assertRaises(FrozenInstanceError):
            admission.reason = "changed"  # type: ignore[misc]

    def test_snapshots_are_recursively_immutable(self) -> None:
        admission = self.service.admit(self._context())
        with self.assertRaises(TypeError):
            admission.proposal["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            admission.proposal["strategy"]["mode"] = "change"  # type: ignore[index]
        with self.assertRaises(TypeError):
            admission.evidence["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            admission.provenance["new"] = "blocked"  # type: ignore[index]

    def test_context_is_immutable_and_related_context_is_frozen(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext(
            proposal=self.proposal,
            related_context={"nested": {"value": 1}},
        )
        with self.assertRaises(FrozenInstanceError):
            context.proposal = None  # type: ignore[assignment]
        with self.assertRaises(TypeError):
            context.related_context["nested"]["value"] = 2  # type: ignore[index]

    def test_admission_cannot_grant_authority(self) -> None:
        with self.assertRaises(
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError
        ):
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission(
                admission_id="admission-x",
                proposal_id="proposal-x",
                decision_id="decision-x",
                evaluation_id="evaluation-x",
                decision_source_evaluation_id="historical-x",
                feedback_id="feedback-x",
                source_feedback_id="source-feedback-x",
                candidate_id="candidate-x",
                source_candidate_id="source-candidate-x",
                execution_id="execution-x",
                source_execution_id="source-execution-x",
                preparation_id="preparation-x",
                source_admission_id="source-admission-x",
                proposal_source_id="proposal-source-x",
                domain="semantic",
                source_policy_id="source-policy-x",
                policy_id="policy-x",
                status=LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.ADMITTED,
                reason="test",
                confidence=0.8,
                proposal={"x": 1},
                evidence={"x": 1},
                provenance={"source": "test"},
                authorization_granted=True,
            )

    def test_invalid_proposal_type_is_rejected(self) -> None:
        with self.assertRaises(
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError
        ):
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext(
                proposal={"bad": True},  # type: ignore[arg-type]
            )

    def test_provider_output_identity_is_validated(self) -> None:
        class BadProvider:
            def admit(self, context):
                result = self.service_result(context)
                return replace(result, proposal_id="wrong")

            @staticmethod
            def service_result(context):
                from src.tools.learning_write_adaptation_evaluation_execution_feedback_proposal_admission import (
                    DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionProvider,
                )

                return DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionProvider().admit(
                    context
                )

        bad_service = LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionService(
            BadProvider()
        )
        with self.assertRaises(
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError
        ):
            bad_service.admit(self._context())

    def test_invalid_confidence_is_rejected(self) -> None:
        with self.assertRaises(
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError
        ):
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission(
                admission_id="admission-x",
                proposal_id="proposal-x",
                decision_id="decision-x",
                evaluation_id="evaluation-x",
                decision_source_evaluation_id="historical-x",
                feedback_id="feedback-x",
                source_feedback_id="source-feedback-x",
                candidate_id="candidate-x",
                source_candidate_id="source-candidate-x",
                execution_id="execution-x",
                source_execution_id="source-execution-x",
                preparation_id="preparation-x",
                source_admission_id="source-admission-x",
                proposal_source_id="proposal-source-x",
                domain="semantic",
                source_policy_id="source-policy-x",
                policy_id="policy-x",
                status=LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.ADMITTED,
                reason="test",
                confidence=1.1,
                proposal={"x": 1},
                evidence={"x": 1},
                provenance={"source": "test"},
            )

    def test_to_context_preserves_authority_wall(self) -> None:
        admission = self.service.admit(self._context())
        context = admission.to_context()
        self.assertFalse(context["adaptation_authorized"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["authority_granted"])


if __name__ == "__main__":
    unittest.main()
