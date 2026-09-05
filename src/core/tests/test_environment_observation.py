import unittest
from dataclasses import dataclass
from types import MappingProxyType

from src.core.environment_model import EnvironmentSnapshot
from src.core.environment_observation import (
    ENVIRONMENT_DOMAINS,
    EnvironmentObservation,
    EnvironmentObservationError,
    EnvironmentObservationService,
)


@dataclass
class StaticAdapter:
    adapter_id: str
    domain: str
    payload: dict
    observation_id: str = "obs-1"

    def observe(self, environment_id: str) -> EnvironmentObservation:
        return EnvironmentObservation(
            observation_id=self.observation_id,
            adapter_id=self.adapter_id,
            environment_id=environment_id,
            domain=self.domain,
            payload=self.payload,
        )


class FailingAdapter:
    adapter_id = "failing"
    domain = "network"

    def observe(self, environment_id: str) -> EnvironmentObservation:
        raise RuntimeError("probe failed")


class WrongTypeAdapter:
    adapter_id = "wrong-type"
    domain = "hardware"

    def observe(self, environment_id: str):
        return {"cpu": "unknown"}


class WrongIdentityAdapter:
    adapter_id = "identity"
    domain = "software"

    def observe(self, environment_id: str) -> EnvironmentObservation:
        return EnvironmentObservation(
            observation_id="obs-identity",
            adapter_id="different",
            environment_id=environment_id,
            domain="software",
            payload={"python": "3.x"},
        )


class WrongEnvironmentAdapter:
    adapter_id = "environment"
    domain = "models"

    def observe(self, environment_id: str) -> EnvironmentObservation:
        return EnvironmentObservation(
            observation_id="obs-env",
            adapter_id=self.adapter_id,
            environment_id="other-environment",
            domain="models",
            payload={"local": True},
        )


class WrongDomainAdapter:
    adapter_id = "domain"
    domain = "network"

    def observe(self, environment_id: str) -> EnvironmentObservation:
        return EnvironmentObservation(
            observation_id="obs-domain",
            adapter_id=self.adapter_id,
            environment_id=environment_id,
            domain="software",
            payload={"version": "x"},
        )


class EnvironmentObservationTests(unittest.TestCase):
    def test_observation_is_recursively_immutable(self):
        payload = {"cpu": {"cores": 8}, "devices": ["gpu"]}
        observation = EnvironmentObservation(
            observation_id="obs-1",
            adapter_id="hardware-reader",
            environment_id="env-1",
            domain="hardware",
            payload=payload,
        )

        self.assertIsInstance(observation.payload, MappingProxyType)
        self.assertIsInstance(observation.payload["cpu"], MappingProxyType)
        self.assertEqual(observation.payload["devices"], ("gpu",))
        with self.assertRaises(TypeError):
            observation.payload["cpu"]["cores"] = 16
        payload["cpu"]["cores"] = 16
        self.assertEqual(observation.payload["cpu"]["cores"], 8)

    def test_unknown_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentObservation(
                observation_id="obs-1",
                adapter_id="reader",
                environment_id="env-1",
                domain="unknown",
            )

    def test_service_composes_observations_into_snapshot(self):
        adapters = (
            StaticAdapter("hardware-reader", "hardware", {"cpu": {"cores": 8}}),
            StaticAdapter("model-reader", "models", {"qwen": {"available": True}}, "obs-2"),
        )
        snapshot = EnvironmentObservationService().snapshot("env-1", adapters)

        self.assertIsInstance(snapshot, EnvironmentSnapshot)
        self.assertEqual(snapshot.hardware["cpu"]["cores"], 8)
        self.assertEqual(snapshot.models["qwen"]["available"], True)
        self.assertEqual(
            snapshot.metadata["observation_sources"]["hardware"]["adapter_id"],
            "hardware-reader",
        )
        self.assertEqual(
            snapshot.metadata["observation_sources"]["models"]["observation_id"],
            "obs-2",
        )

    def test_service_allows_partial_observation_set(self):
        snapshot = EnvironmentObservationService().snapshot(
            "env-1",
            (StaticAdapter("network-reader", "network", {"online": True}),),
        )
        self.assertEqual(snapshot.network["online"], True)
        self.assertEqual(dict(snapshot.hardware), {})
        self.assertEqual(set(snapshot.metadata["observation_sources"]), {"network"})

    def test_duplicate_adapter_id_is_rejected(self):
        adapter = StaticAdapter("same", "hardware", {})
        with self.assertRaises(EnvironmentObservationError):
            EnvironmentObservationService().snapshot("env-1", (adapter, adapter))

    def test_duplicate_domain_is_rejected(self):
        adapters = (
            StaticAdapter("first", "hardware", {}),
            StaticAdapter("second", "hardware", {}),
        )
        with self.assertRaises(EnvironmentObservationError):
            EnvironmentObservationService().snapshot("env-1", adapters)

    def test_adapter_failure_is_wrapped_without_retry(self):
        with self.assertRaisesRegex(EnvironmentObservationError, "failing"):
            EnvironmentObservationService().snapshot("env-1", (FailingAdapter(),))

    def test_wrong_observation_type_is_rejected(self):
        with self.assertRaises(EnvironmentObservationError):
            EnvironmentObservationService().snapshot("env-1", (WrongTypeAdapter(),))

    def test_adapter_identity_must_match(self):
        with self.assertRaises(EnvironmentObservationError):
            EnvironmentObservationService().snapshot("env-1", (WrongIdentityAdapter(),))

    def test_observation_environment_must_match(self):
        with self.assertRaises(EnvironmentObservationError):
            EnvironmentObservationService().snapshot("env-1", (WrongEnvironmentAdapter(),))

    def test_observation_domain_must_match_adapter(self):
        with self.assertRaises(EnvironmentObservationError):
            EnvironmentObservationService().snapshot("env-1", (WrongDomainAdapter(),))

    def test_environment_domain_contract_is_explicit(self):
        self.assertEqual(
            ENVIRONMENT_DOMAINS,
            (
                "hardware",
                "software",
                "network",
                "models",
                "capabilities",
                "permissions",
                "performance",
                "costs",
                "resources",
                "metadata",
            ),
        )

    def test_observation_service_does_not_add_authority(self):
        snapshot = EnvironmentObservationService().snapshot(
            "env-1",
            (StaticAdapter("permissions-reader", "permissions", {"workspace": "read"}),),
        )
        context = snapshot.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["adaptation_truth_proven"])


if __name__ == "__main__":
    unittest.main()
