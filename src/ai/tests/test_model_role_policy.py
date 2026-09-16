import unittest

from src.ai.model_role_policy import ModelRolePolicy, ModelRolePolicyRule
from src.ai.model_routing import ModelRole


class ModelRolePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = ModelRolePolicy(
            [
                ModelRolePolicyRule(
                    "granite-8b",
                    frozenset({ModelRole.GENERAL, ModelRole.VERIFICATION}),
                    priority=100,
                    notes="small reliable general/verification model",
                ),
                ModelRolePolicyRule(
                    "qwen3-coder:30b",
                    frozenset({ModelRole.CODING}),
                    priority=120,
                    notes="coding-specialized model",
                ),
            ]
        )

    def test_rule_builds_profile_without_authority(self) -> None:
        profile = self.policy.rule("granite-8b").profile(available=True)
        self.assertEqual(profile.model_id, "granite-8b")
        self.assertEqual(profile.roles, frozenset({ModelRole.GENERAL, ModelRole.VERIFICATION}))
        self.assertTrue(profile.available)
        self.assertFalse(hasattr(profile, "authority"))
        self.assertFalse(hasattr(profile, "permissions"))
        self.assertFalse(hasattr(profile, "tools"))

    def test_unobserved_rule_does_not_become_available(self) -> None:
        profile = self.policy.rule("granite-8b").profile()
        self.assertFalse(profile.available)

    def test_observed_unknown_model_is_not_assigned_a_role(self) -> None:
        profiles = self.policy.profiles_for_observed(["unknown-model"])
        self.assertEqual(profiles, ())

    def test_observed_known_models_get_only_explicitly_declared_roles(self) -> None:
        profiles = self.policy.profiles_for_observed(
            ["qwen3-coder:30b", "granite-8b", "unknown-model"]
        )
        self.assertEqual(
            tuple(profile.model_id for profile in profiles),
            ("granite-8b", "qwen3-coder:30b"),
        )
        self.assertEqual(profiles[0].roles, frozenset({ModelRole.GENERAL, ModelRole.VERIFICATION}))
        self.assertEqual(profiles[1].roles, frozenset({ModelRole.CODING}))

    def test_duplicate_policy_rule_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate model_id"):
            self.policy.register(
                ModelRolePolicyRule(
                    "granite-8b",
                    frozenset({ModelRole.GENERAL}),
                )
            )

    def test_invalid_policy_rule_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "roles cannot be empty"):
            ModelRolePolicyRule("empty", frozenset())

    def test_policy_rule_requires_model_role_values(self) -> None:
        with self.assertRaisesRegex(TypeError, "roles must contain only ModelRole"):
            ModelRolePolicyRule("bad", frozenset({"GENERAL"}))


if __name__ == "__main__":
    unittest.main()
