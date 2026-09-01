from src.core.ai import AICapabilities, AIProvider, AIRequest, AIResponse
from src.core.ai import AIService
from src.core.execution_loop import GuardedExecutionLoop
from src.core.execution_policy import ExecutionPolicy
from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.jarvis import JARVIS
from src.core.jarvis_execution_adapter import install_execution_loop
from src.core.models import JARVISResponse
from src.core.task_models import TaskRequest, TaskType
from unittest.mock import Mock
import unittest


class JARVISExecutionAdapterTests(unittest.TestCase):
    def test_ask_task_uses_guarded_loop_and_model_correction(self):
        ai_service = AIService(default_provider="test")
        provider = Mock()
        provider.provider_name.return_value = "test"
        provider.capabilities.return_value = AICapabilities(text_generation=True)
        ai_service.register_provider(provider)

        jarvis = JARVIS(ai_service=ai_service)
        loop = Mock()
        loop.run.return_value = Mock(
            status="COMPLETED",
            iterations=2,
            observations=(Mock(execution=Mock(steps=(), step_count=0)),),
            last_policy=None,
            pending_operation_id=None,
        )
        continuation_planner = Mock()

        adapter = install_execution_loop(
            jarvis,
            continuation_planner=continuation_planner,
        )
        adapter.loop = loop

        response = jarvis.ask_task(TaskRequest("act", TaskType.ACTION))

        self.assertIsInstance(response, JARVISResponse)
        loop.run.assert_called_once()
        self.assertTrue(response.metadata["execution_loop"])

    def test_confirmation_still_blocks_execution(self):
        ai_service = AIService(default_provider="test")
        provider = Mock()
        provider.provider_name.return_value = "test"
        provider.capabilities.return_value = AICapabilities(text_generation=True)
        ai_service.register_provider(provider)

        jarvis = JARVIS(ai_service=ai_service)
        planner = Mock()
        planner.plan.return_value = ExecutionPlan(
            plan_id="p1",
            task_description="act",
            status=PlanStatus.READY,
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="act",
                    action="PERFORM_ACTION",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
        )
        jarvis.execution_policy = ExecutionPolicy()
        executor = Mock()
        jarvis.plan_executor = executor
        install_execution_loop(jarvis)

        response = jarvis.ask_task(TaskRequest("act", TaskType.ACTION))

        self.assertEqual(response.metadata["status"], "AWAITING_CONFIRMATION")
        executor.execute.assert_not_called()

    def test_adapter_is_reversible(self):
        ai_service = AIService(default_provider="reversibility")

        class ReversibilityProvider(AIProvider):
            def generate(self, request: AIRequest) -> AIResponse:
                return AIResponse(
                    content='{"task":"noop","task_type":"INFORMATION"}',
                    provider="reversibility",
                    model="test-model",
                )

            def capabilities(self):
                return AICapabilities(text_generation=True)

            def provider_name(self):
                return "reversibility"

        ai_service.register_provider(ReversibilityProvider())
        jarvis = JARVIS(ai_service=ai_service)
        original = jarvis._handle_task
        adapter = install_execution_loop(jarvis)
        self.assertIs(jarvis.execution_adapter.jarvis, jarvis)
        jarvis.execution_adapter.uninstall()
        restored = jarvis._handle_task
        self.assertIs(restored.__self__, original.__self__)
        self.assertIs(restored.__func__, original.__func__)
        self.assertIsNotNone(adapter)


if __name__ == "__main__":
    unittest.main()
