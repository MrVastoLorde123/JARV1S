import unittest

from src.ai.local_model_policy import build_local_model_role_policy
from src.ai.model_routing import ModelRole


class LocalModelRolePolicyTests(unittest.TestCase):
    def test_discovered_models_have_only_explicitly_declared_roles(self) -> None:
        policy = build_local_model_role_policy()
        rules = {rule.model_id: rule for rule in policy.list_rules()}
        self.assertIn("qwen3-coder:30b", rules)
        self.assertEqual(rules["qwen3-coder:30b"].roles, frozenset({ModelRole.CODING}))

    def test_unknown_model_has_no_policy(self) -> None:
        policy = build_local_model_role_policy()
        with self.assertRaisesRegex(KeyError, "no role policy"):
            policy.rule("unknown-model")

    def test_policy_is_not_authority(self) -> None:
        rule = build_local_model_role_policy().rule("qwen3-coder:30b")
        profile = rule.profile(available=True)
        self.assertFalse(hasattr(rule, "authority"))
        self.assertFalse(hasattr(profile, "permissions"))
        self.assertFalse(hasattr(profile, "tools"))


if __name__ == "__main__":
    unittest.main()
