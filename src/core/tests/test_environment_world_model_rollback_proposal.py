import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_history import EnvironmentWorldModelHistory, EnvironmentWorldModelHistoryService
from src.core.environment_world_model_rollback_proposal import (
    EnvironmentWorldModelRollbackProposal,
    EnvironmentWorldModelRollbackProposalError,
    EnvironmentWorldModelRollbackProposalService,
)


class EnvironmentWorldModelRollbackProposalTests(unittest.TestCase):
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
        self.service = EnvironmentWorldModelRollbackProposalService()

    def test_historical_target_produces_rollback(self) -> None:
        result = self.service.propose(self.history, proposal_id="rb-1", target_model_id="model-1")
        self.assertIsInstance(result, EnvironmentWorldModelRollbackProposal)
        self.assertEqual(result.current_model_id, "model-2")
        self.assertEqual(result.target_model_id, "model-1")
        self.assertEqual(result.recommendation, "ROLLBACK")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.applies_rollback)

    def test_current_target_produces_no_rollback(self) -> None:
        result = self.service.propose(self.history, proposal_id="rb-2", target_model_id="model-2")
        self.assertEqual(result.recommendation, "NO_ROLLBACK")

    def test_target_must_exist_in_history(self) -> None:
        with self.assertRaises(EnvironmentWorldModelRollbackProposalError):
            self.service.propose(self.history, proposal_id="rb-3", target_model_id="missing")

    def test_current_model_environment_must_match_history(self) -> None:
        other = EnvironmentWorldModel(
            model_id="model-x", environment_id="env-2",
            state_by_domain={"network": {"status": "up"}},
            represented_domains=("network",), missing_domains=("hardware",),
            context_ids=("ctx-x",), qualification_ids=("qual-x",),
            provenance_ids=("prov-x",), readiness_id="ready-x", source_bundle_id="bundle-x",
        )
        with self.assertRaises(EnvironmentWorldModelRollbackProposalError):
            self.service.propose(self.history, proposal_id="rb-4", target_model_id="model-1", current_model=other)

    def test_empty_history_has_no_rollback_source(self) -> None:
        empty = EnvironmentWorldModelHistory(environment_id="env-1", models=())
        with self.assertRaises(EnvironmentWorldModelRollbackProposalError):
            self.service.propose(empty, proposal_id="rb-5", target_model_id="model-1")

    def test_lineage_and_reasons_are_immutable(self) -> None:
        result = self.service.propose(
            self.history,
            proposal_id="rb-6",
            target_model_id="model-1",
            reasons={"why": "candidate regressed"},
            lineage={"source": {"stage": "history"}},
        )
        with self.assertRaises(TypeError):
            result.reasons["why"] = "changed"
        with self.assertRaises(TypeError):
            result.lineage["source"]["stage"] = "changed"

    def test_source_history_and_models_are_not_mutated(self) -> None:
        before_ids = self.history.model_ids
        before_current = self.history.latest.model_id
        self.service.propose(self.history, proposal_id="rb-7", target_model_id="model-1")
        self.assertEqual(self.history.model_ids, before_ids)
        self.assertEqual(self.history.latest.model_id, before_current)

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.propose(object(), proposal_id="rb-8", target_model_id="model-1")
        with self.assertRaises(TypeError):
            self.service.propose(self.history, proposal_id="rb-9", target_model_id="model-1", current_model=object())


if __name__ == "__main__":
    unittest.main()
