"""Focused M26.2 tests for the provider-neutral capability registry."""
from __future__ import annotations

import unittest

from src.core.capability_registry import (
    CapabilityDefinition,
    CapabilityRegistry,
    CapabilityRegistryError,
)
from src.core.runtime_kernel import JarvisRuntime


class _Orchestration:
    def dispatch(self, request):
        from src.core.interface_backend import InterfaceResponseStatus, InterfaceResponse
        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={},
            metadata={"artifact_type": "TEST_STAGE"},
        )


class M26_2CapabilityRegistryTests(unittest.TestCase):
    def definition(self, **overrides):
        values = {
            "capability_id": "cap-1",
            "name": "Filesystem",
            "description": "Read and inspect files",
            "category": "system",
            "metadata": {"tags": ["files", "read"], "nested": {"safe": True}},
        }
        values.update(overrides)
        return CapabilityDefinition(**values)

    def test_definition_requires_non_empty_identity_and_metadata(self) -> None:
        for field in ("capability_id", "name", "description", "category"):
            with self.subTest(field=field):
                values = self.definition().__dict__.copy()
                values[field] = ""
                with self.assertRaises(ValueError):
                    CapabilityDefinition(**values)
        with self.assertRaises(TypeError):
            self.definition(metadata=[])

    def test_definition_metadata_is_recursively_immutable(self) -> None:
        definition = self.definition()
        with self.assertRaises(TypeError):
            definition.metadata["x"] = 1
        with self.assertRaises(TypeError):
            definition.metadata["nested"]["safe"] = False
        with self.assertRaises(TypeError):
            definition.metadata["tags"] += ("write",)

    def test_definition_name_normalization_is_deterministic(self) -> None:
        self.assertEqual(self.definition(name="  FileSystem  ").normalized_name, "filesystem")

    def test_register_and_snapshot_are_deterministic(self) -> None:
        registry = CapabilityRegistry()
        first = self.definition()
        second = self.definition(capability_id="cap-2", name="Python")
        registry.register(first)
        registry.register(second)
        self.assertEqual(registry.snapshot(), (first, second))
        self.assertEqual(len(registry), 2)

    def test_duplicate_id_is_rejected(self) -> None:
        registry = CapabilityRegistry()
        registry.register(self.definition())
        with self.assertRaises(CapabilityRegistryError):
            registry.register(self.definition(name="Different"))

    def test_duplicate_normalized_name_is_rejected(self) -> None:
        registry = CapabilityRegistry()
        registry.register(self.definition())
        with self.assertRaises(CapabilityRegistryError):
            registry.register(self.definition(capability_id="cap-2", name=" filesystem "))

    def test_lookup_by_id_and_name(self) -> None:
        registry = CapabilityRegistry()
        definition = self.definition()
        registry.register(definition)
        self.assertIs(registry.get("cap-1"), definition)
        self.assertIs(registry.find_by_name("FILESYSTEM"), definition)
        self.assertIsNone(registry.get("missing"))
        self.assertIsNone(registry.find_by_name("missing"))

    def test_remove_returns_definition_and_frees_name(self) -> None:
        registry = CapabilityRegistry()
        definition = self.definition()
        registry.register(definition)
        self.assertIs(registry.remove("cap-1"), definition)
        self.assertEqual(len(registry), 0)
        self.assertIsNone(registry.find_by_name("filesystem"))
        with self.assertRaises(KeyError):
            registry.remove("cap-1")

    def test_runtime_composes_a_capability_registry(self) -> None:
        runtime = JarvisRuntime(
            orchestration=_Orchestration(),
            session_id="session-runtime",
            actor_id="actor-runtime",
        )
        self.assertIsInstance(runtime.capability_registry, CapabilityRegistry)
        self.assertEqual(len(runtime.capability_registry), 0)

    def test_runtime_accepts_an_injected_registry(self) -> None:
        registry = CapabilityRegistry()
        runtime = JarvisRuntime(
            orchestration=_Orchestration(),
            session_id="session-runtime",
            actor_id="actor-runtime",
            capability_registry=registry,
        )
        self.assertIs(runtime.capability_registry, registry)

    def test_registry_does_not_execute_definitions(self) -> None:
        definition = self.definition(metadata={"execute": lambda: None})
        registry = CapabilityRegistry()
        registry.register(definition)
        self.assertIs(registry.get("cap-1"), definition)
        self.assertTrue(callable(registry.get("cap-1").metadata["execute"]))

    def test_registry_has_no_execution_or_authority_surface(self) -> None:
        registry = CapabilityRegistry()
        self.assertFalse(hasattr(registry, "invoke"))
        self.assertFalse(hasattr(registry, "authorize"))
        self.assertFalse(hasattr(registry, "execute"))


if __name__ == "__main__":
    unittest.main()
