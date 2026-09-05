from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationService,
)


class M22_49_Tests(unittest.TestCase):
    def setUp(self) -> None:
        from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal import (
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService,
        )
        from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision import (
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService,
        )
        from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation import (
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
        )

        evaluation = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            outcome_id="outcome-1",
            execution_id="execution-1",
            preparation_id="preparation-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            evaluation_id_from_feedback="evaluation-from-feedback-1",
            decision_source_evaluation_id="decision-source-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            execution_source_id="execution-source-1",
            source_execution_id="source-execution-1",
            source_admission_id="source-admission-1",
            proposal_source_id="proposal-source-1",
            domain="semantic",
            source_policy_id="source-policy-1",
            policy_id="policy-1",
            signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL,
            confidence=0.8,
            evidence={"observed": True},
            provenance={"source": "test"},
            reason="success",
        )
        decision = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation=evaluation)
        )
        proposal = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision, {"change": "candidate"}, {"observed": True}, {"source": "test"}
        )
        assert proposal is not None
        self.admission = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService().admit(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=proposal)
        )
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationService()

    def _prepare(self):
        return self.service.prepare(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext(
                admission=self.admission
            )
        )

    def test_prepares_admitted_artifact(self) -> None:
        preparation = self._prepare()
        self.assertIsInstance(preparation, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation)

    def test_preparation_id_is_deterministic(self) -> None:
        first = self._prepare()
        second = self._prepare()
        self.assertEqual(first.preparation_id, second.preparation_id)

    def test_preparation_id_is_distinct(self) -> None:
        preparation = self._prepare()
        self.assertNotEqual(preparation.preparation_id, preparation.admission_id)
        self.assertNotEqual(preparation.preparation_id, preparation.proposal_id)
        self.assertNotEqual(preparation.preparation_id, preparation.execution_id)

    def test_admission_must_be_admitted(self) -> None:
        rejected = self.admission.__class__(**{
            **self.admission.__dict__,
            "admission_id": "rejected-admission",
            "status": LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED,
        })
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError):
            self.service.prepare(
                LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext(admission=rejected)
            )

    def test_full_lineage_is_preserved(self) -> None:
        preparation = self._prepare()
        for name in (
            "admission_id", "proposal_id", "decision_id", "evaluation_id", "feedback_id", "outcome_id", "execution_id",
            "source_admission_id", "source_proposal_id", "decision_source_evaluation_id", "evaluation_id_from_feedback",
            "source_feedback_id", "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id",
            "domain", "source_policy_id", "policy_id",
        ):
            self.assertEqual(getattr(preparation, name), getattr(self.admission, name))

    def test_payload_is_recursively_immutable(self) -> None:
        preparation = self._prepare()
        with self.assertRaises(TypeError):
            preparation.payload["new"] = True  # type: ignore[index]

    def test_evidence_is_recursively_immutable(self) -> None:
        preparation = self._prepare()
        with self.assertRaises(TypeError):
            preparation.evidence["new"] = True  # type: ignore[index]

    def test_provenance_is_immutable(self) -> None:
        preparation = self._prepare()
        with self.assertRaises(TypeError):
            preparation.provenance["new"] = "blocked"  # type: ignore[index]

    def test_preparation_is_immutable(self) -> None:
        preparation = self._prepare()
        with self.assertRaises(FrozenInstanceError):
            preparation.domain = "changed"  # type: ignore[misc]

    def test_context_freezes_related_context(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext(
            admission=self.admission, related_context={"nested": {"value": True}}
        )
        with self.assertRaises(TypeError):
            context.related_context["new"] = True  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            context.admission = self.admission  # type: ignore[misc]

    def test_context_rejects_wrong_admission_type(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext(admission={"bad": True})  # type: ignore[arg-type]

    def test_authority_wall(self) -> None:
        preparation = self._prepare()
        context = preparation.to_context()
        for key in (
            "execution_authorized", "execution_started", "retry_requested", "revocation_requested",
            "memory_mutation_allowed", "authority_granted",
        ):
            self.assertFalse(context[key])

    def test_forbidden_authority_flags_are_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation(
                **{**self._prepare().__dict__, "execution_authorized": True}
            )

    def test_empty_payload_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation(
                **{**self._prepare().__dict__, "payload": {}}
            )

    def test_empty_evidence_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation(
                **{**self._prepare().__dict__, "evidence": {}}
            )

    def test_context_authority_input_is_not_authorization(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext(
            admission=self.admission,
            related_context={"authorization_requested": True},
        )
        self.assertEqual(context.related_context["authorization_requested"], True)
        preparation = self.service.prepare(context)
        self.assertFalse(preparation.execution_authorized)
        self.assertFalse(preparation.authority_granted)


if __name__ == "__main__":
    unittest.main()
