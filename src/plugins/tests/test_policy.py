import unittest

from src.plugins.policy import (
    CapabilityPermissionBinding,
    CapabilityPolicyBindingRegistry,
    CapabilityPolicyError,
    PermissionEffect,
)


class CapabilityPolicyBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.allow_read = CapabilityPermissionBinding(
            capability_id="file.read",
            permission=" READ ",
            effect=PermissionEffect.ALLOW,
            version="1.2.0",
            policy_id="workspace-default",
            rationale="Reading workspace files is allowed by policy.",
        )
        self.deny_write = CapabilityPermissionBinding(
            capability_id="file.read",
            permission="write",
            effect=PermissionEffect.DENY,
            version="1.2.0",
            policy_id="workspace-default",
        )

    def test_binding_is_immutable(self) -> None:
        with self.assertRaises(Exception):
            self.allow_read.permission = "write"

    def test_binding_requires_core_fields(self) -> None:
        for kwargs in (
            {"capability_id": "", "permission": "read", "effect": PermissionEffect.ALLOW},
            {"capability_id": "file.read", "permission": "", "effect": PermissionEffect.ALLOW},
            {"capability_id": "file.read", "permission": "read", "effect": "ALLOW"},
            {"capability_id": "file.read", "permission": "read", "effect": PermissionEffect.ALLOW, "policy_id": ""},
        ):
            with self.assertRaises(CapabilityPolicyError):
                CapabilityPermissionBinding(**kwargs)

    def test_version_is_normalized_and_validated(self) -> None:
        binding = CapabilityPermissionBinding(
            "file.read", "read", PermissionEffect.ALLOW, version=" 1.2.3 "
        )
        self.assertEqual(binding.version, "1.2.3")
        with self.assertRaises(CapabilityPolicyError):
            CapabilityPermissionBinding(
                "file.read", "read", PermissionEffect.ALLOW, version="1.2"
            )

    def test_registry_rejects_duplicate_binding_identity(self) -> None:
        registry = CapabilityPolicyBindingRegistry()
        registry.register(self.allow_read)
        with self.assertRaises(CapabilityPolicyError):
            registry.register(
                CapabilityPermissionBinding(
                    "FILE.READ", "read", PermissionEffect.DENY,
                    version="1.2.0", policy_id="workspace-default"
                )
            )

    def test_registry_lookup_is_normalization_stable(self) -> None:
        registry = CapabilityPolicyBindingRegistry()
        registry.register(self.allow_read)
        found = registry.get(
            " FILE.READ ", " READ ", version="1.2.0", policy_id="workspace-default"
        )
        self.assertEqual(found, self.allow_read)

    def test_version_specific_and_version_agnostic_bindings_are_distinct(self) -> None:
        registry = CapabilityPolicyBindingRegistry()
        registry.register(self.allow_read)
        wildcard = CapabilityPermissionBinding(
            "file.read", "read", PermissionEffect.ALLOW,
            policy_id="workspace-wide"
        )
        registry.register(wildcard)
        self.assertEqual(len(registry), 2)

    def test_listing_is_deterministic(self) -> None:
        registry = CapabilityPolicyBindingRegistry()
        registry.register(self.deny_write)
        registry.register(self.allow_read)
        bindings = registry.list_for_capability("FILE.READ")
        self.assertEqual(
            tuple((b.policy_id, b.permission, b.effect.value) for b in bindings),
            (("workspace-default", "read", "ALLOW"), ("workspace-default", "write", "DENY")),
        )

    def test_context_contains_permission_binding_but_no_authority(self) -> None:
        context = self.allow_read.to_context()
        self.assertTrue(context["permission_bound"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_binding_does_not_become_authorization(self) -> None:
        registry = CapabilityPolicyBindingRegistry()
        registry.register(self.allow_read)
        context = registry.get(
            "file.read", "read", version="1.2.0", policy_id="workspace-default"
        ).to_context()
        self.assertEqual(context["effect"], "ALLOW")
        self.assertNotIn("authorized", context)
        self.assertFalse(context["authorization_granted"])


if __name__ == "__main__":
    unittest.main()
