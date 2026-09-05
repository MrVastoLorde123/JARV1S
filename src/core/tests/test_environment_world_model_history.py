import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_history import (
    EnvironmentWorldModelHistory,
    EnvironmentWorldModelHistoryError,
    EnvironmentWorldModelHistoryService,
)


class EnvironmentWorldModelHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EnvironmentWorldModelHistoryService()
        self.model1 = EnvironmentWorldModel(
            model_id="model-1",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-1",),
            qualification_ids=("qual-1",),
            provenance_ids=("prov-1",),
            readiness_id="ready-1",
            source_bundle_id="bundle-1",
        )
        self.model2 = EnvironmentWorldModel(
            model_id="model-2",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "arm64"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-2",),
            qualification_ids=("qual-2",),
            provenance_ids=("prov-2",),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )

    def test_append_to_empty_history_creates_first_model(self) -> None:
        result = self.service.append(None, self.model1)
        self.assertIsInstance(result, EnvironmentWorldModelHistory)
        self.assertEqual(result.environment_id, "env-1")
        self.assertEqual(result.model_ids, ("model-1",))
        self.assertIs(result.latest, self.model1)

    def test_append_preserves_order(self) -> None:
        history = self.service.append(None, self.model1)
        history2 = self.service.append(history, self.model2)
        self.assertEqual(history2.model_ids, ("model-1", "model-2"))
        self.assertIs(history2.latest, self.model2)

    def test_history_is_immutable(self) -> None:
        history = self.service.append(None, self.model1, lineage={"source": {"stage": "m23.18"}})
        with self.assertRaises(AttributeError):
            history.environment_id = "env-2"
        with self.assertRaises(TypeError):
            history.lineage["source"]["stage"] = "changed"

    def test_models_must_share_environment(self) -> None:
        other = EnvironmentWorldModel(
            model_id="model-2",
            environment_id="env-2",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-2",),
            qualification_ids=("qual-2",),
            provenance_ids=("prov-2",),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )
        history = self.service.append(None, self.model1)
        with self.assertRaises(EnvironmentWorldModelHistoryError):
            self.service.append(history, other)

    def test_duplicate_model_identity_fails_closed(self) -> None:
        history = self.service.append(None, self.model1)
        with self.assertRaises(EnvironmentWorldModelHistoryError):
            self.service.append(history, self.model1)

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.append(object(), self.model1)
        with self.assertRaises(TypeError):
            self.service.append(None, object())

    def test_source_models_are_not_mutated(self) -> None:
        before1 = dict(self.model1.state_by_domain["hardware"])
        before2 = dict(self.model2.state_by_domain["hardware"])
        history = self.service.append(None, self.model1)
        self.service.append(history, self.model2)
        self.assertEqual(dict(self.model1.state_by_domain["hardware"]), before1)
        self.assertEqual(dict(self.model2.state_by_domain["hardware"]), before2)

    def test_lineage_is_preserved(self) -> None:
        history = self.service.append(None, self.model1, lineage={"source": {"stage": "application"}})
        self.assertEqual(history.lineage["source"]["stage"], "application")

    def test_duplicate_ids_in_constructed_history_are_rejected(self) -> None:
        with self.assertRaises(EnvironmentWorldModelHistoryError):
            EnvironmentWorldModelHistory(
                environment_id="env-1",
                models=(self.model1, self.model1),
            )

    def test_empty_history_has_no_latest(self) -> None:
        history = EnvironmentWorldModelHistory(environment_id="env-1", models=())
        self.assertIsNone(history.latest)
        self.assertEqual(history.model_ids, ())

    def test_history_scope_is_validated(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelHistory(environment_id="", models=())


if __name__ == "__main__":
    unittest.main()
