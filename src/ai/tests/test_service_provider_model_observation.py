import unittest

from src.ai.errors import InvalidRequestError
from src.ai.model_role_policy import ModelRolePolicy, ModelRolePolicyRule
from src.ai.model_routing import ModelRole
from src.ai.model_routing_runtime import ModelRoutingRuntime
from src.ai.service import AIService


class _ObservableProvider:
    def __init__(self, model_ids):
        self.model_ids = tuple(model_ids)

    def provider_name(self):
        return "observable"

    def list_models(self):
        return self.model_ids


class _NonObservableProvider:
    def provider_name(self):
        return "plain"


class AIServiceProviderModelObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        runtime = ModelRoutingRuntime(
            ModelRolePolicy(
                [
                    ModelRolePolicyRule(
                        "granite-8b",
                        frozenset({ModelRole.GENERAL}),
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
        self.service = AIService(default_provider="observable", model_routing_runtime=runtime)
        self.service.register_provider(_ObservableProvider(["qwen3-coder:30b", "unknown-model"]))

    def test_provider_inventory_is_observed_without_generation(self) -> None:
        observed = self.service.observe_provider_models()
        self.assertEqual(observed, ("qwen3-coder:30b", "unknown-model"))
        self.assertEqual(self.service.route_model(ModelRole.CODING).model_id, "qwen3-coder:30b")

    def test_unknown_provider_model_does_not_become_routeable(self) -> None:
        self.service.observe_provider_models()
        with self.assertRaisesRegex(LookupError, "no model available"):
            self.service.route_model(ModelRole.GENERAL)

    def test_non_observable_provider_is_rejected(self) -> None:
        service = AIService(default_provider="plain", model_routing_runtime=self.service._model_routing_runtime)
        service.register_provider(_NonObservableProvider())
        with self.assertRaisesRegex(InvalidRequestError, "does not expose model observation"):
            service.observe_provider_models()


if __name__ == "__main__":
    unittest.main()
