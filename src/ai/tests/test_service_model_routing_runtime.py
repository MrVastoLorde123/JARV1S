import unittest

from src.ai.errors import InvalidRequestError
from src.ai.model_role_policy import ModelRolePolicy, ModelRolePolicyRule
from src.ai.model_routing import ModelRole
from src.ai.model_routing_runtime import ModelRoutingRuntime
from src.ai.service import AIService


class AIServiceModelRoutingRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        runtime = ModelRoutingRuntime(
            ModelRolePolicy(
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
        )
        self.runtime = runtime
        self.service = AIService(default_provider="local", model_routing_runtime=runtime)

    def test_service_uses_runtime_role_selection(self) -> None:
        self.service.observe_models(["qwen3-coder:30b"])
        decision = self.service.route_model(ModelRole.CODING)
        self.assertEqual(decision.model_id, "qwen3-coder:30b")

    def test_service_exposes_runtime_profiles_with_availability(self) -> None:
        self.service.observe_models(["granite-8b"])
        profiles = self.service.list_models()
        available = {profile.model_id: profile.available for profile in profiles}
        self.assertTrue(available["granite-8b"])
        self.assertFalse(available["qwen3-coder:30b"])

    def test_service_refreshes_runtime_from_openai_models_payload(self) -> None:
        observed = self.service.observe_openai_models(
            {"data": [{"id": "granite-8b"}, {"id": "unknown-model"}]}
        )
        self.assertEqual(observed, ("granite-8b", "unknown-model"))
        self.assertEqual(self.runtime.observed_model_ids(), ("granite-8b", "unknown-model"))
        self.assertEqual(self.service.route_model(ModelRole.GENERAL).model_id, "granite-8b")

    def test_register_model_is_rejected_when_runtime_policy_is_bound(self) -> None:
        with self.assertRaisesRegex(InvalidRequestError, "register_model\(\) is unavailable"):
            self.service.register_model(object())

    def test_runtime_policy_does_not_add_authority_fields(self) -> None:
        self.service.observe_models(["granite-8b"])
        decision = self.service.route_model(ModelRole.GENERAL)
        self.assertFalse(hasattr(decision, "authority"))
        self.assertFalse(hasattr(decision, "permissions"))
        self.assertFalse(hasattr(decision, "tools"))


if __name__ == "__main__":
    unittest.main()
