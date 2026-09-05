import unittest

from src.plugins.lifecycle import (
    CapabilityLifecycleError,
    CapabilityLifecycleRegistry,
    CapabilityVersion,
    LifecycleStatus,
    SemanticVersion,
)


class CapabilityLifecycleTests(unittest.TestCase):
    def test_semantic_version_parsing_and_normalization(self) -> None:
        version = SemanticVersion.parse(" 1.2.3 ")
        self.assertEqual(str(version), "1.2.3")
        self.assertEqual(str(SemanticVersion.parse("1.2.3-rc.1+build.7")), "1.2.3-rc.1+build.7")

    def test_semantic_version_rejects_invalid_values(self) -> None:
        for value in ("1", "1.2", "v1.2.3", "01.2.3", "1.2.3-01"):
            with self.assertRaises(CapabilityLifecycleError):
                SemanticVersion.parse(value)

    def test_semantic_version_precedence_is_deterministic(self) -> None:
        ordered = [
            SemanticVersion.parse("1.0.0-alpha"),
            SemanticVersion.parse("1.0.0-alpha.1"),
            SemanticVersion.parse("1.0.0-beta"),
            SemanticVersion.parse("1.0.0"),
            SemanticVersion.parse("2.0.0"),
        ]
        self.assertEqual(ordered, sorted(ordered))

    def test_capability_version_is_immutable(self) -> None:
        version = CapabilityVersion("file.read", "1.0.0")
        with self.assertRaises(Exception):
            version.version = "2.0.0"

    def test_version_requires_semantic_version(self) -> None:
        with self.assertRaises(CapabilityLifecycleError):
            CapabilityVersion("file.read", "1.0")

    def test_supersedes_requires_older_version(self) -> None:
        CapabilityVersion("file.read", "2.0.0", supersedes="1.0.0")
        for older in ("2.0.0", "3.0.0"):
            with self.assertRaises(CapabilityLifecycleError):
                CapabilityVersion("file.read", "2.0.0", supersedes=older)

    def test_duplicate_versions_are_rejected(self) -> None:
        registry = CapabilityLifecycleRegistry()
        registry.register(CapabilityVersion("file.read", "1.0.0"))
        with self.assertRaises(CapabilityLifecycleError):
            registry.register(CapabilityVersion(" FILE.READ ", "1.0.0"))

    def test_versions_are_listed_newest_first(self) -> None:
        registry = CapabilityLifecycleRegistry()
        registry.register(CapabilityVersion("file.read", "1.0.0"))
        registry.register(CapabilityVersion("file.read", "1.2.0"))
        registry.register(CapabilityVersion("file.read", "1.1.0"))
        self.assertEqual(
            tuple(item.version for item in registry.list_versions("FILE.READ")),
            ("1.2.0", "1.1.0", "1.0.0"),
        )

    def test_lifecycle_transitions_are_forward_only(self) -> None:
        version = CapabilityVersion("file.read", "1.0.0")
        deprecated = version.transition(LifecycleStatus.DEPRECATED)
        retired = deprecated.transition(LifecycleStatus.RETIRED)
        self.assertEqual(deprecated.lifecycle, LifecycleStatus.DEPRECATED)
        self.assertEqual(retired.lifecycle, LifecycleStatus.RETIRED)
        with self.assertRaises(CapabilityLifecycleError):
            deprecated.transition(LifecycleStatus.ACTIVE)
        with self.assertRaises(CapabilityLifecycleError):
            retired.transition(LifecycleStatus.ACTIVE)

    def test_registry_transition_is_explicit_and_preserves_identity(self) -> None:
        registry = CapabilityLifecycleRegistry()
        registry.register(CapabilityVersion("file.read", "1.0.0"))
        updated = registry.transition("file.read", "1.0.0", LifecycleStatus.DEPRECATED)
        self.assertEqual(updated.version, "1.0.0")
        self.assertEqual(updated.lifecycle, LifecycleStatus.DEPRECATED)
        self.assertEqual(registry.get("FILE.READ", "1.0.0"), updated)

    def test_latest_excludes_retired_by_default(self) -> None:
        registry = CapabilityLifecycleRegistry()
        registry.register(CapabilityVersion("file.read", "1.0.0"))
        registry.register(CapabilityVersion("file.read", "2.0.0"))
        registry.transition("file.read", "2.0.0", LifecycleStatus.RETIRED)
        self.assertEqual(registry.latest("file.read").version, "1.0.0")
        self.assertEqual(registry.latest("file.read", include_retired=True).version, "2.0.0")

    def test_missing_version_transition_fails(self) -> None:
        registry = CapabilityLifecycleRegistry()
        with self.assertRaises(CapabilityLifecycleError):
            registry.transition("missing", "1.0.0", LifecycleStatus.RETIRED)

    def test_context_contains_no_authority_semantics(self) -> None:
        version = CapabilityVersion("file.read", "1.0.0")
        context = version.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])


if __name__ == "__main__":
    unittest.main()
