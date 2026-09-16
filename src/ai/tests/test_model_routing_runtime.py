import unittest

from src.ai.model_role_policy import ModelRolePolicy, ModelRolePolicyRule
from src.ai.model_routing import ModelRole
from src.ai.model_routing_runtime import ModelRoutingRuntime


class ModelRoutingRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = ModelRolePolicy(
            [
                ModelRolePolicyRule(
                    "granite-8b",
                    frozenset({ModelRole.GENERAL, ModelRole.VERIFICATION}),
                    priority=100,
                ),
                ModelRolePolicyRule(
                    "qwen3-coder:30b",
                    frozenset({ModelRole.CODING}),
                    priority=120,
                ),
            ]
        )
        self.runtime = ModelRoutingRuntime(self.policy)

    def test_unobserved_policy_models_are_not_routeable(self) -> None:
        with self.assertRaisesRegex(LookupError, "no model available"):
            self.runtime.route(ModelRole.CODING)

    def test_observation_refreshes_role_routing(self) -> None:
        self.runtime.observe_models(["qwen3-coder:30b"])
        decision = self.runtime.route(ModelRole.CODING)
        self.assertEqual(decision.model_id, "qwen3-coder:30b")

    def test_unknown_observed_models_remain_unrouteable(self) -> None:
        self.runtime.observe_models(["unknown-model"])
        self.assertEqual(self.runtime.observed_model_ids(), ("unknown-model",))
        with self.assertRaisesRegex(LookupError, "no model available"):
            self.runtime.route(ModelRole.GENERAL)

    def test_latest_observation_can_make_a_previous_model_unavailable(self) -> None:
        self.runtime.observe_models(["granite-8b"])
        self.assertEqual(self.runtime.route(ModelRole.GENERAL).model_id, "granite-8b")
        self.runtime.observe_models(["qwen3-coder:30b"])
        with self.assertRaisesRegex(LookupError, "no model available"):
            self.runtime.route(ModelRole.GENERAL)

    def test_explicit_preference_cannot_escape_role_policy(self) -> None:
        self.runtime.observe_models(["granite-8b", "qwen3-coder:30b"])
        with self.assertRaisesRegex(ValueError, "does not serve role"):
            self.runtime.route(ModelRole.CODING, preferred_model="granite-8b")

    def test_new_policy_rule_becomes_routeable_without_reobservation(self) -> None:
        self.runtime.observe_models(["qwen3-coder:30b", "new-general"])
        self.policy.register(
            ModelRolePolicyRule(
                "new-general",
                frozenset({ModelRole.GENERAL}),
                priority=150,
            )
        )
        decision = self.runtime.route(ModelRole.GENERAL)
        self.assertEqual(decision.model_id, "new-general")

    def test_new_policy_rule_remains_unavailable_until_observed(self) -> None:
        self.policy.register(
            ModelRolePolicyRule(
                "new-general",
                frozenset({ModelRole.GENERAL}),
                priority=150,
            )
        )
        with self.assertRaisesRegex(LookupError, "no model available"):
            self.runtime.route(ModelRole.GENERAL)


if __name__ == "__main__":
    unittest.main()
