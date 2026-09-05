import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_history import EnvironmentWorldModelHistoryService
from src.core.environment_world_model_rollback_proposal import EnvironmentWorldModelRollbackProposal
from src.core.environment_world_model_rollback_proposal import EnvironmentWorldModelRollbackProposalService
from src.core.environment_world_model_rollback_decision import (
    EnvironmentWorldModelRollbackDecision,
    EnvironmentWorldModelRollbackDecisionError,
    EnvironmentWorldModelRollbackDecisionService,
)


class EnvironmentWorldModelRollbackDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model1 = EnvironmentWorldModel(
            model_id="model-1", environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",), missing_domains=("software",),
            context_ids=("ctx-1",), qualification_ids=("qual-1",),
            provenance_ids=("prov-1",), readiness_id="ready-1", source_bundle_id="bundle-1",
        )
        self.model2 = EnvironmentWorldModel(
            model_id="model-2", environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "arm64"}},
            represented_domains=("hardware",), missing_domains=("software",),
            context_ids=("ctx-2",), qualification_ids=("qual-2",),
            provenance_ids=("prov-2",), readiness_id="ready-2", source_bundle_id="bundle-2",
        )
        self.history = EnvironmentWorldModelHistoryService().append(
            EnvironmentWorldModelHistoryService().append(None, self.model1), self.model2
        )
        proposal_service = EnvironmentWorldModelRollbackProposalService()
        self.rollback_proposal = proposal_service.propose(
            self.history, proposal_id="rb-1", target_model_id="model-1"
        )
        self.no_rollback_proposal = proposal_service.propose(
            self.history, proposal_id="rb-2", target_model_id="model-2"
        )
        self.service = EnvironmentWorldModelRollbackDecisionService()

    def test_rollback_proposal_produces_accept(self) -> None:
        result = self.service.decide(self.rollback_proposal, decision_id="dec-1")
        self.assertIsInstance(result, EnvironmentWorldModelRollbackDecision)
        self.assertEqual(result.decision, "ACCEPT")
        self.assertEqual(result.current_model_id, "model-2")
        self.assertEqual(result.target_model_id, "model-1")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.applies_rollback)

    def test_no_rollback_proposal_produces_reject(self) -> None:
        result = self.service.decide(self.no_rollback_proposal, decision_id="dec-2")
        self.assertEqual(result.decision, "REJECT")
        self.assertEqual(result.current_model_id, "model-2")
        self.assertEqual(result.target_model_id, "model-2")

    def test_decision_identity_and_lineage_are_preserved(self) -> None:
        result = self.service.decide(
            self.rollback_proposal,
            decision_id="dec-3",
            lineage={"source": {"proposal_id": "rb-1"}},
        )
        self.assertEqual(result.proposal_id, "rb-1")
        self.assertEqual(result.lineage["source"]["proposal_id"], "rb-1")

    def test_reasons_are_preserved(self) -> None:
        result = self.service.decide(
            self.rollback_proposal,
            decision_id="dec-4",
            reasons={"why": "validated historical target"},
        )
        self.assertEqual(result.reasons["why"], "validated historical target")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.decide(
            self.rollback_proposal,
            decision_id="dec-5",
            reasons={"why": "validated historical target"},
            lineage={"source": {"proposal_id": "rb-1"}},
        )
        with self.assertRaises(TypeError):
            result.reasons["why"] = "changed"
        with self.assertRaises(TypeError):
            result.lineage["source"]["proposal_id"] = "changed"
        with self.assertRaises(AttributeError):
            result.decision_id = "changed"

    def test_source_proposal_is_not_mutated(self) -> None:
        before = vars(self.rollback_proposal).copy()
        self.service.decide(self.rollback_proposal, decision_id="dec-6")
        self.assertEqual(vars(self.rollback_proposal), before)

    def test_unsupported_recommendation_fails_closed(self) -> None:
        invalid = EnvironmentWorldModelRollbackProposal(
            proposal_id="rb-invalid",
            environment_id="env-1",
            current_model_id="model-2",
            target_model_id="model-1",
            recommendation="ROLLBACK",
        )
        object.__setattr__(invalid, "recommendation", "REVIEW")
        with self.assertRaises(EnvironmentWorldModelRollbackDecisionError):
            self.service.decide(invalid, decision_id="dec-7")

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide(object(), decision_id="dec-8")


if __name__ == "__main__":
    unittest.main()
