import unittest

from src.plugins import CapabilityDescriptor, CapabilityRegistry, PluginRegistryError


class CapabilityRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = CapabilityRegistry()
        self.first = CapabilityDescriptor(
            capability_id="file.read",
            name="Read File",
            version="1.0.0",
            description="Read a file from an authorized workspace.",
            metadata={"category": "workspace", "risk": "medium"},
        )
        self.second = CapabilityDescriptor(
            capability_id="web.search",
            name="Web Search",
            version="2.0.0",
            description="Search the web through an external provider.",
        )

    def test_descriptor_is_immutable(self) -> None:
        with self.assertRaises(Exception):
            self.first.name = "Changed"

    def test_descriptor_requires_core_identity_fields(self) -> None:
        for kwargs in (
            {"capability_id": "", "name": "x", "version": "1", "description": "x"},
            {"capability_id": "id", "name": "", "version": "1", "description": "x"},
            {"capability_id": "id", "name": "x", "version": "", "description": "x"},
            {"capability_id": "id", "name": "x", "version": "1", "description": ""},
        ):
            with self.assertRaises(PluginRegistryError):
                CapabilityDescriptor(**kwargs)

    def test_registration_is_explicit_and_conflict_aware(self) -> None:
        self.registry.register(self.first)
        with self.assertRaises(PluginRegistryError):
            self.registry.register(
                CapabilityDescriptor(
                    capability_id="FILE.READ",
                    name="Other Read File",
                    version="9.0.0",
                    description="Conflicting identity.",
                )
            )

    def test_replace_requires_explicit_flag(self) -> None:
        self.registry.register(self.first)
        replacement = CapabilityDescriptor(
            capability_id="FILE.READ",
            name="Read File v2",
            version="2.0.0",
            description="Updated metadata.",
        )
        self.registry.register(replacement, replace=True)
        self.assertEqual(self.registry.get("file.read"), replacement)

    def test_discovery_is_deterministic_and_metadata_only(self) -> None:
        self.registry.register(self.second)
        self.registry.register(self.first)
        discovered = self.registry.discover()
        self.assertEqual(tuple(item.capability_id for item in discovered), ("file.read", "web.search"))
        self.assertFalse(any(item.to_context()["authority_granted"] for item in discovered))
        self.assertFalse(any(item.to_context()["execution_requested"] for item in discovered))

    def test_lookup_is_case_and_whitespace_insensitive(self) -> None:
        self.registry.register(self.first)
        self.assertEqual(self.registry.get(" FILE.READ "), self.first)

    def test_unregister_requires_existing_identity(self) -> None:
        with self.assertRaises(PluginRegistryError):
            self.registry.unregister("missing")
        self.registry.register(self.first)
        self.registry.unregister("FILE.READ")
        self.assertIsNone(self.registry.get("file.read"))

    def test_registry_never_implies_permission_or_execution(self) -> None:
        self.registry.register(self.first)
        descriptor = self.registry.get("file.read")
        assert descriptor is not None
        context = descriptor.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])


if __name__ == "__main__":
    unittest.main()
