import unittest

from src.ai.local_model_policy import build_local_model_role_policy
from src.ai.model_routing_runtime import ModelRoutingRuntime
from src.ai.providers.local_provider import LocalProvider
from src.ai.service import AIService
from src.interface.control_host import _model_routing_projection


class ControlHostModelRoutingProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = AIService(
            default_provider="local",
            model_routing_runtime=ModelRoutingRuntime(build_local_model_role_policy()),
        )
        self.service.register_provider(
            LocalProvider(base_url="http://127.0.0.1:1", model="qwen3:30b", timeout=1)
        )

    def test_projection_refreshes_observation_and_exposes_role_selection(self) -> None:
        projection = _model_routing_projection(
            ai_service=self.service,
            observation={
                "observed_model_ids": ("qwen3:30b", "unknown-model"),
            },
        )
        self.assertEqual(
            projection["observed_model_ids"],
            ("qwen3:30b", "unknown-model"),
        )
        self.assertEqual(
            projection["role_selections"]["GENERAL"]["model_id"],
            "qwen3:30b",
        )
        self.assertEqual(
            projection["role_selections"]["CODING"]["state"],
            "NO_AVAILABLE_MODEL",
        )

    def test_projection_contains_no_authority_surface(self) -> None:
        projection = _model_routing_projection(
            ai_service=self.service,
            observation={"observed_model_ids": ("qwen3-coder:30b",)},
        )
        self.assertNotIn("authority", projection)
        self.assertNotIn("permissions", projection)
        self.assertTrue(projection["routing_read_only"])


if __name__ == "__main__":
    unittest.main()
