import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_history import (
    EnvironmentWorldModelHistoryService,
)
from src.core.environment_world_model_rollback_decision import (
    EnvironmentWorldModelRollbackDecisionService,
)
from src.core.environment_world_model_rollback_application import (
    EnvironmentWorldModelRollbackApplication,
    EnvironmentWorldModelRollbackApplicationError,
    EnvironmentWorldModelRollbackApplicationService,
)


class EnvironmentWorldModelRollbackApplicationTests(unittest.TestCase):
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
        decision_service = EnvironmentWorldModelRollbackDecisionService()
        proposal = __import__(
            "src.core.environment_world_model_rollback_proposal",
            fromlist=["EnvironmentWorldModelRollbackProposalService"],
        ).EnvironmentWorldModelRollbackProposalService().propose(
            self.history, proposal_id="rb-1", target_model_id="model-1"
        )
        no_rollback_proposal = __import__(
            "src.core.environment_world_model_rollback_proposal",
            fromlist=["EnvironmentWorldModelRollbackProposalService"],
        ).EnvironmentWorldModelRollbackProposalService().propose(
            self.history, proposal_id="rb-2", target_model_id="model-2"
        )
        self.accept = decision_service.decide(proposal, decision_id="dec-1")
        self.reject = decision_service.decide(no_rollback_proposal, decision_id="dec-2")
        self.service = EnvironmentWorldModelRollbackApplicationService()

    def test_accept_returns_historical_target_and_applied_record(self) -> None:
        result, application = self.service.apply(
            self.history, self.accept, application_id="app-1"
        )
        self.assertIs(result, self.model1)
        self.assertIsInstance(application, EnvironmentWorldModelRollbackApplication)
        self.assertTrue(application.applied)
        self.assertEqual(application.previous_model_id, "model-2")
        self.assertEqual(application.target_model_id, "model-1")
        self.assertEqual(application.resulting_model_id, "model-1")

    def test_reject_retains_current_model(self) -> None:
        result, application = self.service.apply(
            self.history, self.reject, application_id="app-2"
        )
        self.assertIs(result, self.model2)
        self.assertFalse(application.applied)
        self.assertEqual(application.resulting_model_id, "model-2")

    def test_defer_retains_current_model(self) -> None:
        from src.core.environment_world_model_rollback_decision import EnvironmentWorldModelRollbackDecision
        decision = EnvironmentWorldModelRollbackDecision(
            decision_id="dec-defer",
            environment_id="env-1",
            current_model_id="model-2",
            target_model_id="model-1",
            proposal_id="rb-1",
            decision="DEFER",
        )
        result, application = self.service.apply(
            self.history, decision, application_id="app-3"
        )
        self.assertIs(result, self.model2)
        self.assertFalse(application.applied)

    def test_decision_current_identity_must_match_current_model(self) -> None:
        from src.core.environment_world_model_rollback_decision import EnvironmentWorldModelRollbackDecision
        decision = EnvironmentWorldModelRollbackDecision(
            decision_id="dec-mismatch",
            environment_id="env-1",
            current_model_id="model-1",
            target_model_id="model-2",
            proposal_id="rb-1",
            decision="ACCEPT",
        )
        with self.assertRaises(EnvironmentWorldModelRollbackApplicationError):
            self.service.apply(self.history, decision, application_id="app-4")

    def test_target_must_exist_in_history(self) -> None:
        from src.core.environment_world_model_rollback_decision import EnvironmentWorldModelRollbackDecision
        decision = EnvironmentWorldModelRollbackDecision(
            decision_id="dec-missing",
            environment_id="env-1",
            current_model_id="model-2",
            target_model_id="model-3",
            proposal_id="rb-1",
            decision="ACCEPT",
        )
        with self.assertRaises(EnvironmentWorldModelRollbackApplicationError):
            self.service.apply(self.history, decision, application_id="app-5")

    def test_environment_identity_must_match(self) -> None:
        from src.core.environment_world_model_rollback_decision import EnvironmentWorldModelRollbackDecision
        decision = EnvironmentWorldModelRollbackDecision(
            decision_id="dec-env",
            environment_id="env-2",
            current_model_id="model-2",
            target_model_id="model-1",
            proposal_id="rb-1",
            decision="ACCEPT",
        )
        with self.assertRaises(EnvironmentWorldModelRollbackApplicationError):
            self.service.apply(self.history, decision, application_id="app-6")

    def test_application_and_nested_data_are_immutable(self) -> None:
        _, application = self.service.apply(
            self.history,
            self.accept,
            application_id="app-7",
            reasons={"why": "validated rollback"},
            lineage={"source": {"decision_id": "dec-1"}},
        )
        with self.assertRaises(TypeError):
            application.reasons["why"] = "changed"
        with self.assertRaises(TypeError):
            application.lineage["source"]["decision_id"] = "changed"
        with self.assertRaises(AttributeError):
            application.application_id = "changed"

    def test_source_history_and_models_are_not_mutated(self) -> None:
        before_ids = self.history.model_ids
        before_latest = self.history.latest.model_id
        self.service.apply(self.history, self.accept, application_id="app-8")
        self.assertEqual(self.history.model_ids, before_ids)
        self.assertEqual(self.history.latest.model_id, before_latest)
        self.assertEqual(self.model1.model_id, "model-1")
        self.assertEqual(self.model2.model_id, "model-2")

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.apply(object(), self.accept, application_id="app-9")
        with self.assertRaises(TypeError):
            self.service.apply(self.history, object(), application_id="app-10")
        with self.assertRaises(TypeError):
            self.service.apply(self.history, self.accept, application_id="app-11", current_model=object())


if __name__ == "__main__":
    unittest.main()
