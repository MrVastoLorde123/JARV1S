import unittest
from unittest.mock import Mock

from src.ai.models import AICapabilities, AIRequest, AIResponse
from src.ai.provider import AIProvider
from src.ai.service import AIService
from src.core.execution_confirmation import ExecutionConfirmationService
from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
)
from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.execution_policy import ExecutionPolicy
from src.core.execution_planner import ExecutionPlanner
from src.core.jarvis import JARVIS
from src.core.jarvis_execution_adapter import install_execution_loop
from src.core.plan_executor import PlanExecutor
from src.core.plan_validator import PlanValidator
from src.core.request_router import RequestRouter
from src.core.task_models import TaskRequest, TaskType


class ContinuationAIProvider(AIProvider):
    def __init__(self):
        self.calls = 0

    def generate(self, request: AIRequest) -> AIResponse:
        self.calls += 1
        return AIResponse(
            content='{"task":"retry the task","task_type":"INFORMATION"}',
            provider="test",
            model="test-model",
        )

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "test"


def make_plan(plan_id: str):
    return ExecutionPlan(
        plan_id=plan_id,
        task_description="do it",
        status=PlanStatus.READY,
        steps=(
            PlanStep(
                step_id="step-1",
                description="do it",
                action="PROVIDE_INFORMATION",
                order=0,
                status=StepStatus.READY,
            ),
        ),
    )


class JARVISExecutionAdapterTests(unittest.TestCase):
    def test_ask_task_uses_guarded_loop_and_model_correction(self):
        provider = ContinuationAIProvider()
        ai_service = AIService(default_provider="test")
        ai_service.register_provider(provider)

        planner = Mock(spec=ExecutionPlanner)
        planner.plan.side_effect = [make_plan("p1"), make_plan("p2")]

        executor = Mock(spec=PlanExecutor)
        executor.execute.side_effect = [
            PlanExecutionResult(
                plan_id="p1",
                status=PlanExecutionStatus.FAILED,
                steps=(
                    StepExecutionResult(
                        step_id="step-1",
                        action="PROVIDE_INFORMATION",
                        status=StepExecutionStatus.FAILED,
                        error="boom",
                    ),
                ),
                error="boom",
            ),
            PlanExecutionResult(
                plan_id="p2",
                status=PlanExecutionStatus.COMPLETED,
                steps=(
                    StepExecutionResult(
                        step_id="step-1",
                        action="PROVIDE_INFORMATION",
                        status=StepExecutionStatus.COMPLETED,
                        output="fixed",
                    ),
                ),
            ),
        ]

        jarvis = JARVIS(
            ai_service=ai_service,
            request_router=RequestRouter(),
            execution_planner=planner,
            plan_validator=PlanValidator(),
            execution_policy=ExecutionPolicy(),
            plan_executor=executor,
            execution_confirmation_service=ExecutionConfirmationService(),
        )
        install_execution_loop(jarvis, max_iterations=2)

        response = jarvis.ask_task(TaskRequest("do it", TaskType.INFORMATION))

        self.assertEqual(response.metadata["execution_loop"], True)
        self.assertEqual(response.metadata["status"], "COMPLETED")
        self.assertEqual(response.metadata["iterations"], 2)
        self.assertEqual(response.metadata["observation_count"], 2)
        self.assertEqual(planner.plan.call_count, 2)
        self.assertEqual(executor.execute.call_count, 2)
        self.assertEqual(provider.calls, 1)

    def test_confirmation_still_blocks_execution(self):
        planner = Mock(spec=ExecutionPlanner)
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
        executor = Mock(spec=PlanExecutor)
        continuation = Mock()

        jarvis = JARVIS(
            ai_service=Mock(),
            request_router=RequestRouter(),
            execution_planner=planner,
            plan_validator=PlanValidator(),
            execution_policy=ExecutionPolicy(),
            plan_executor=executor,
            execution_confirmation_service=ExecutionConfirmationService(),
        )
        install_execution_loop(jarvis, continuation_planner=continuation)

        response = jarvis.ask_task(TaskRequest("act", TaskType.ACTION))

        self.assertEqual(response.metadata["status"], "AWAITING_CONFIRMATION")
        executor.execute.assert_not_called()
        continuation.propose.assert_not_called()

    def test_adapter_is_reversible(self):
        jarvis = JARVIS(ai_service=Mock())
        original = jarvis._handle_task
        install_execution_loop(jarvis)
        self.assertIs(jarvis.execution_adapter.jarvis, jarvis)
        jarvis.execution_adapter.uninstall()
        self.assertIs(jarvis._handle_task, original)


if __name__ == "__main__":
    unittest.main()
