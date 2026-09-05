import unittest

from src.core.environment_model import EnvironmentSnapshot, EnvironmentSnapshotService


class EnvironmentModelTests(unittest.TestCase):
    def snapshot(self, **overrides):
        values = dict(
            environment_id="env-1",
            hardware={"gpu": {"name": "RTX 3060", "vram_gb": 12}},
            software={"os": "Windows"},
            network={"vpn": "offline"},
            models={"reasoning": {"name": "local-model"}},
            capabilities={"github": {"available": True}},
            permissions={"github": {"read": True, "write": False}},
            performance={"gpu_utilization": 0.25},
            costs={"cloud_inference": {"currency": "USD", "per_1k_tokens": 0.0}},
            resources={"ram_gb": 16, "storage_free_gb": 200},
            metadata={"source": "test"},
        )
        values.update(overrides)
        return EnvironmentSnapshot(**values)

    def test_snapshot_preserves_environment_domains(self):
        out = self.snapshot()
        self.assertEqual(out.hardware["gpu"]["vram_gb"], 12)
        self.assertEqual(out.software["os"], "Windows")
        self.assertTrue(out.capabilities["github"]["available"])
        self.assertFalse(out.permissions["github"]["write"])

    def test_snapshot_is_recursively_immutable(self):
        out = self.snapshot()
        with self.assertRaises((TypeError, AttributeError)):
            out.hardware["gpu"]["vram_gb"] = 24

    def test_context_is_non_authorizing(self):
        context = self.snapshot().to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["adaptation_truth_proven"])

    def test_empty_environment_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentSnapshot(environment_id="")

    def test_non_mapping_domain_is_rejected(self):
        with self.assertRaises(TypeError):
            EnvironmentSnapshot(environment_id="env-1", hardware=[])

    def test_service_constructs_snapshot(self):
        out = EnvironmentSnapshotService().snapshot(
            "env-2",
            hardware={"cpu": {"cores": 8}},
            resources={"ram_gb": 32},
        )
        self.assertEqual(out.environment_id, "env-2")
        self.assertEqual(out.hardware["cpu"]["cores"], 8)
        self.assertEqual(out.resources["ram_gb"], 32)

    def test_service_does_not_alias_mutable_input(self):
        hardware = {"gpu": {"name": "RTX"}}
        out = EnvironmentSnapshotService().snapshot("env-3", hardware=hardware)
        hardware["gpu"]["name"] = "changed"
        self.assertEqual(out.hardware["gpu"]["name"], "RTX")

    def test_environment_snapshot_is_frozen(self):
        out = self.snapshot()
        with self.assertRaises(AttributeError):
            out.environment_id = "changed"


if __name__ == "__main__":
    unittest.main()
