import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_rollback_application import (
    EnvironmentWorldModelRollbackApplication,
)
from src.core.environment_world_model_rollback_persistence import (
    EnvironmentWorldModelRollbackPersistenceError,
    EnvironmentWorldModelRollbackPersistenceService,
)
from src.core.environment_world_model_store import InMemoryEnvironmentWorldModelStore


class EnvironmentWorldModelRollbackPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous = EnvironmentWorldModel(
            model_id="m1",
            environment_id="env1",
            state_by_domain={"hardware": {"cpu": 4}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx1",),
            qualification_ids=("q1",),
            provenance_ids=("p1",),
            readiness_id="r1",
            source_bundle_id="b1",
            lineage={"source": "previous"},
        )
        self.target = EnvironmentWorldModel(
            model_id="m0",
            environment_id="env1",
            state_by_domain={"hardware": {"cpu": 2}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx0",),
            qualification_ids=("q0",),
            provenance_ids=("p0",),
            readiness_id="r0",
            source_bundle_id="b0",
            lineage={"source": "target"},
        )
        self.store = InMemoryEnvironmentWorldModelStore({"env1": self.previous})
        self.service = EnvironmentWorldModelRollbackPersistenceService()

    def _application(self, applied: bool, resulting: EnvironmentWorldModel) -> EnvironmentWorldModelRollbackApplication:
        return EnvironmentWorldModelRollbackApplication(
            application_id="app1",
            environment_id="env1",
            previous_model_id=self.previous.model_id,
            target_model_id=self.target.model_id,
            decision_id="decision1",
            applied=applied,
            resulting_model_id=resulting.model_id,
            reasons={"status": "test"},
            lineage={"source": "test"},
        )

    def test_applied_result_is_persisted_with_compare_and_swap(self) -> None:
        result = self.service.persist(
            self._application(True, self.target),
            self.target,
            self.store,
            persistence_id="persist1",
        )
        self.assertTrue(result.persisted)
        self.assertEqual(self.store.get("env1"), self.target)
        self.assertEqual(result.previous_model_id, "m1")
        self.assertEqual(result.resulting_model_id, "m0")

    def test_unapplied_result_leaves_store_unchanged(self) -> None:
        result = self.service.persist(
            self._application(False, self.previous),
            self.previous,
            self.store,
            persistence_id="persist1",
        )
        self.assertFalse(result.persisted)
        self.assertEqual(self.store.get("env1"), self.previous)

    def test_compare_and_swap_rejects_stale_store(self) -> None:
        different_current = EnvironmentWorldModel(
            model_id="m-other",
            environment_id="env1",
            state_by_domain={},
            represented_domains=(),
            missing_domains=("hardware", "software"),
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
            readiness_id="r-other",
            source_bundle_id="b-other",
            lineage={},
        )
        self.store.put(different_current)
        with self.assertRaises(EnvironmentWorldModelRollbackPersistenceError):
            self.service.persist(
                self._application(True, self.target),
                self.target,
                self.store,
                persistence_id="persist1",
            )

    def test_application_and_resulting_identity_must_match(self) -> None:
        with self.assertRaises(EnvironmentWorldModelRollbackPersistenceError):
            self.service.persist(
                self._application(True, self.target),
                self.previous,
                self.store,
                persistence_id="persist1",
            )

    def test_environment_identity_must_match(self) -> None:
        foreign = EnvironmentWorldModel(
            model_id="m-foreign",
            environment_id="env2",
            state_by_domain={},
            represented_domains=(),
            missing_domains=(),
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
            readiness_id="r2",
            source_bundle_id="b2",
            lineage={},
        )
        application = EnvironmentWorldModelRollbackApplication(
            application_id="app1",
            environment_id="env1",
            previous_model_id="m1",
            target_model_id="m0",
            decision_id="decision1",
            applied=True,
            resulting_model_id="m-foreign",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackPersistenceError):
            self.service.persist(application, foreign, self.store, persistence_id="persist1")

    def test_stored_current_identity_must_match_application(self) -> None:
        foreign_previous = EnvironmentWorldModel(
            model_id="m2",
            environment_id="env1",
            state_by_domain={},
            represented_domains=(),
            missing_domains=(),
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
            readiness_id="r2",
            source_bundle_id="b2",
            lineage={},
        )
        self.store.put(foreign_previous)
        with self.assertRaises(EnvironmentWorldModelRollbackPersistenceError):
            self.service.persist(
                self._application(True, self.target),
                self.target,
                self.store,
                persistence_id="persist1",
            )

    def test_nested_data_is_immutable(self) -> None:
        result = self.service.persist(
            self._application(True, self.target),
            self.target,
            self.store,
            persistence_id="persist1",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_source_application_and_models_are_not_mutated(self) -> None:
        application = self._application(True, self.target)
        previous = self.previous
        target = self.target
        self.service.persist(application, target, self.store, persistence_id="persist1")
        self.assertEqual(application.resulting_model_id, "m0")
        self.assertEqual(self.store.get("env1"), target)
        self.assertEqual(previous.model_id, "m1")

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.persist(object(), self.target, self.store, persistence_id="persist1")
        with self.assertRaises(TypeError):
            self.service.persist(self._application(True, self.target), object(), self.store, persistence_id="persist1")
        with self.assertRaises(TypeError):
            self.service.persist(self._application(True, self.target), self.target, object(), persistence_id="persist1")


if __name__ == "__main__":
    unittest.main()
