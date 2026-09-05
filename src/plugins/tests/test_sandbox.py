import unittest

from src.plugins.sandbox import (
    IsolationMode,
    PluginIsolationError,
    SandboxAdmissionEvaluator,
    SandboxAdmissionResult,
    SandboxAdmissionStatus,
    SandboxProfile,
    SandboxProfileRegistry,
)


class SandboxIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = SandboxProfile(profile_id="plugin-default")

    def test_profile_is_immutable(self) -> None:
        with self.assertRaises(Exception):
            self.profile.timeout_seconds = 60

    def test_profile_requires_valid_core_constraints(self) -> None:
        with self.assertRaises(PluginIsolationError):
            SandboxProfile(profile_id="")
        with self.assertRaises(PluginIsolationError):
            SandboxProfile(profile_id="p", timeout_seconds=0)
        with self.assertRaises(PluginIsolationError):
            SandboxProfile(profile_id="p", memory_limit_mb=0)
        with self.assertRaises(PluginIsolationError):
            SandboxProfile(profile_id="p", cpu_limit_percent=101)
        with self.assertRaises(PluginIsolationError):
            SandboxProfile(profile_id="p", writable_paths=("/tmp",))

    def test_profile_context_contains_isolation_without_authority(self) -> None:
        context = self.profile.to_context()
        self.assertTrue(context["sandbox_bound"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_started"])
        self.assertFalse(context["containment_active"])

    def test_admissible_result_is_deterministic_and_non_authorizing(self) -> None:
        result = SandboxAdmissionEvaluator().evaluate("file.read", self.profile)
        self.assertEqual(result.status, SandboxAdmissionStatus.ADMISSIBLE)
        self.assertTrue(result.admissible)
        self.assertEqual(result.reasons, ())
        context = result.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_started"])

    def test_unsupported_mode_is_rejected(self) -> None:
        result = SandboxAdmissionEvaluator().evaluate(
            "plugin.run", self.profile, supported_modes=()
        )
        self.assertEqual(result.status, SandboxAdmissionStatus.REJECTED)
        self.assertFalse(result.admissible)
        self.assertEqual(
            result.reasons,
            ("isolation mode PROCESS is unsupported",),
        )

    def test_evaluator_validates_contract_types(self) -> None:
        evaluator = SandboxAdmissionEvaluator()
        with self.assertRaises(PluginIsolationError):
            evaluator.evaluate("", self.profile)
        with self.assertRaises(TypeError):
            evaluator.evaluate("plugin.run", object())
        with self.assertRaises(PluginIsolationError):
            evaluator.evaluate(
                "plugin.run", self.profile, supported_modes=("PROCESS",)
            )

    def test_admission_result_rejects_inconsistent_reason_state(self) -> None:
        with self.assertRaises(PluginIsolationError):
            SandboxAdmissionResult(
                "plugin.run",
                "plugin-default",
                SandboxAdmissionStatus.ADMISSIBLE,
                ("unexpected",),
            )
        with self.assertRaises(PluginIsolationError):
            SandboxAdmissionResult(
                "plugin.run",
                "plugin-default",
                SandboxAdmissionStatus.REJECTED,
                (),
            )

    def test_registry_is_explicit_and_conflict_aware(self) -> None:
        registry = SandboxProfileRegistry()
        registry.register(self.profile)
        with self.assertRaises(PluginIsolationError):
            registry.register(self.profile)
        self.assertEqual(registry.get("plugin-default"), self.profile)
        self.assertEqual(len(registry), 1)

    def test_registry_listing_is_deterministic(self) -> None:
        registry = SandboxProfileRegistry()
        registry.register(SandboxProfile(profile_id="z-profile"))
        registry.register(SandboxProfile(profile_id="a-profile"))
        self.assertEqual(
            tuple(item.profile_id for item in registry.list_profiles()),
            ("a-profile", "z-profile"),
        )

    def test_sandbox_does_not_imply_permission(self) -> None:
        context = self.profile.to_context()
        self.assertNotIn("authorized", context)
        self.assertNotIn("execute", context)
        self.assertFalse(context["permission_granted"])


if __name__ == "__main__":
    unittest.main()
