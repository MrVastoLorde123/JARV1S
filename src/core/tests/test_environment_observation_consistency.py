import unittest

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_consistency import (
    EnvironmentObservationConsistency,
    EnvironmentObservationConsistencyService,
    ObservationConsistency,
)


class EnvironmentObservationConsistencyTests(unittest.TestCase):
    @staticmethod
    def observation(
        observation_id: str,
        adapter_id: str,
        domain: str = "hardware",
        payload: dict | None = None,
        environment_id: str = "env-1",
    ) -> EnvironmentObservation:
        return EnvironmentObservation(
            observation_id=observation_id,
            adapter_id=adapter_id,
            environment_id=environment_id,
            domain=domain,
            payload=payload or {"cpu": {"cores": 8}},
        )

    def test_equal_payloads_are_consistent(self):
        result = EnvironmentObservationConsistencyService().compare(
            self.observation("obs-1", "adapter-a"),
            self.observation("obs-2", "adapter-b"),
        )
        self.assertIsInstance(result, EnvironmentObservationConsistency)
        self.assertIs(result.consistency, ObservationConsistency.CONSISTENT)
        self.assertFalse(result.is_conflict)

    def test_different_payloads_are_conflicting(self):
        result = EnvironmentObservationConsistencyService().compare(
            self.observation("obs-1", "adapter-a", payload={"cpu": {"cores": 8}}),
            self.observation("obs-2", "adapter-b", payload={"cpu": {"cores": 16}}),
        )
        self.assertIs(result.consistency, ObservationConsistency.CONFLICTING)
        self.assertTrue(result.is_conflict)

    def test_mapping_key_order_does_not_create_false_conflict(self):
        result = EnvironmentObservationConsistencyService().compare(
            self.observation("obs-1", "adapter-a", payload={"b": 2, "a": 1}),
            self.observation("obs-2", "adapter-b", payload={"a": 1, "b": 2}),
        )
        self.assertIs(result.consistency, ObservationConsistency.CONSISTENT)

    def test_pair_identity_and_scope_are_preserved(self):
        result = EnvironmentObservationConsistencyService().compare(
            self.observation("obs-1", "adapter-a", domain="network"),
            self.observation("obs-2", "adapter-b", domain="network"),
        )
        self.assertEqual(result.left_observation_id, "obs-1")
        self.assertEqual(result.right_observation_id, "obs-2")
        self.assertEqual(result.left_adapter_id, "adapter-a")
        self.assertEqual(result.right_adapter_id, "adapter-b")
        self.assertEqual(result.environment_id, "env-1")
        self.assertEqual(result.domain, "network")

    def test_different_environment_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentObservationConsistencyService().compare(
                self.observation("obs-1", "adapter-a", environment_id="env-1"),
                self.observation("obs-2", "adapter-b", environment_id="env-2"),
            )

    def test_different_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentObservationConsistencyService().compare(
                self.observation("obs-1", "adapter-a", domain="hardware"),
                self.observation("obs-2", "adapter-b", domain="software"),
            )

    def test_duplicate_observation_id_is_rejected(self):
        observation = self.observation("obs-1", "adapter-a")
        with self.assertRaises(ValueError):
            EnvironmentObservationConsistencyService().compare(observation, observation)

    def test_wrong_input_type_is_rejected(self):
        with self.assertRaises(TypeError):
            EnvironmentObservationConsistencyService().compare(
                {"cpu": 1},  # type: ignore[arg-type]
                self.observation("obs-2", "adapter-b"),
            )

    def test_compare_many_preserves_pair_order(self):
        observations = (
            self.observation("obs-1", "adapter-a"),
            self.observation("obs-2", "adapter-b"),
            self.observation("obs-3", "adapter-c"),
        )
        results = EnvironmentObservationConsistencyService().compare_many(observations)
        self.assertEqual(
            [(item.left_observation_id, item.right_observation_id) for item in results],
            [("obs-1", "obs-2"), ("obs-1", "obs-3"), ("obs-2", "obs-3")],
        )

    def test_compare_many_skips_unrelated_domains(self):
        observations = (
            self.observation("obs-1", "adapter-a", domain="hardware"),
            self.observation("obs-2", "adapter-b", domain="software"),
        )
        self.assertEqual(EnvironmentObservationConsistencyService().compare_many(observations), ())

    def test_compare_many_skips_unrelated_environments(self):
        observations = (
            self.observation("obs-1", "adapter-a", environment_id="env-1"),
            self.observation("obs-2", "adapter-b", environment_id="env-2"),
        )
        self.assertEqual(EnvironmentObservationConsistencyService().compare_many(observations), ())

    def test_compare_many_rejects_wrong_input_type(self):
        with self.assertRaises(TypeError):
            EnvironmentObservationConsistencyService().compare_many(
                [self.observation("obs-1", "adapter-a"), {"bad": True}]  # type: ignore[list-item]
            )

    def test_consistency_result_is_immutable(self):
        result = EnvironmentObservationConsistencyService().compare(
            self.observation("obs-1", "adapter-a"),
            self.observation("obs-2", "adapter-b"),
        )
        with self.assertRaises((AttributeError, TypeError)):
            result.domain = "software"  # type: ignore[misc]

    def test_consistency_does_not_select_a_winner(self):
        result = EnvironmentObservationConsistencyService().compare(
            self.observation("obs-1", "adapter-a", payload={"value": 1}),
            self.observation("obs-2", "adapter-b", payload={"value": 2}),
        )
        self.assertIs(result.consistency, ObservationConsistency.CONFLICTING)
        self.assertTrue(hasattr(result, "left_observation_id"))
        self.assertTrue(hasattr(result, "right_observation_id"))


if __name__ == "__main__":
    unittest.main()
