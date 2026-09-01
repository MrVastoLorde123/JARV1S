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
from src.core.execution_policy import ExecutionPolicy
from src.core.jarvis import JARVIS
from src.core.jarvis_execution_adapter import install_execution_loop
from src.core.model_execution_planner import ModelExecutionPlanner
from src.core.plan_executor import PlanExecutor
from src.core.plan_validator import PlanValidator
from src.core.request_router import RequestRouter
from src.core.task_models import TaskRequest, TaskType


class PlanningAIProvider(AIProvider):
    def __init__(self):
        self.calls = 0

    def generate(self, request: AIRequest) -> AIResponse:
        self.calls += 1
        return AIResponse(
            content=(
                '{"steps":['
                '{"task":"inspect the workspace","task_type":"INFORMATION"},'
                '{"task":"summarize the findings","task_type":"INFORMATION"}'
                ']}'
            ),
            provider="test",
            model="test-model",
        )

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "test"


class JARVISModelExecutionPlanningTests(unittest.TestCase):
    def test_model_planned_multi_step_task_uses_full_guarded_pipeline(self):
        provider = PlanningAIProvider()
        ai_service = AIService(default_provider="test")
        ai_service.register_provider(provider)

        executor = Mock(spec=PlanExecutor)
        executor.execute.return_value = PlanExecutionResult(
            plan_id="model-plan",
            status=PlanExecutionStatus.COMPLETED,
            steps=(
                StepExecutionResult(
                    step_id="step-1",
                    action="PROVIDE_INFORMATION",
                    status=StepExecutionStatus.COMPLETED,
                    output="inspected",
                ),
                StepExecutionResult(
                    step_id="step-2",
                    action="PROVIDE_INFORMATION",
                    status=StepExecutionStatus.COMPLETED,
                    output="summarized",
                ),
            ),
        )

        planner = ModelExecutionPlanner(ai_service)
        jarvis = JARVIS(
            ai_service=ai_service,
            request_router=RequestRouter(),
            plan_validator=PlanValidator(),
            execution_policy=ExecutionPolicy(),
            plan_executor=executor,
            execution_confirmation_service=ExecutionConfirmationService(),
        )
        install_execution_loop(jarvis, execution_planner=planner)

        response = jarvis.ask_task(
            TaskRequest("understand the workspace", TaskType.INFORMATION)
        )

        self.assertEqual(response.metadata["execution_loop"], True)
        self.assertEqual(response.metadata["status"], "COMPLETED")
        self.assertEqual(response.metadata["step_count"], 2)
        self.assertEqual(response.metadata["observation_count"], 1)
        self.assertEqual(response.metadata["planner"], "multi_step_deterministic")
        self.assertEqual(provider.calls, 1)
        executor.execute.assert_called_once()
        plan = executor.execute.call_args.args[0]
        self.assertEqual(len(plan.steps), 2)
        self.assertEqual(plan.steps[0].depends_on, ())
        self.assertEqual(plan.steps[1].depends_on, (plan.steps[0].step_id,))

    def test_confirmation_still_blocks_model_planned_action(self):
        provider = PlanningAIProvider()
        ai_service = AIService(default_provider="test")
        ai_service.register_provider(provider)

        class ActionPlanningProvider(PlanningAIProvider):
            def generate(self, request: AIRequest) -> AIResponse:
                self.calls += 1
                return AIResponse(
                    content=(
                        '{"steps":[{"task":"perform the action",'
                        '"task_type":"ACTION"}]}'
                    ),
                    provider="test",
                    model="test-model",
                )

        action_provider = ActionPlanningProvider()
        action_service = AIService(default_provider="test")
        action_service.register_provider(action_provider)
        executor = Mock(spec=PlanExecutor)

        jarvis = JARVIS(
            ai_service=action_service,
            request_router=RequestRouter(),
            plan_validator=PlanValidator(),
            execution_policy=ExecutionPolicy(),
            plan_executor=executor,
            execution_confirmation_service=ExecutionConfirmationService(),
        )
        install_execution_loop(
            jarvis,
            execution_planner=ModelExecutionPlanner(action_service),
        )

        response = jarvis.ask_task(TaskRequest("act", TaskType.ACTION))

        self.assertEqual(response.metadata["status"], "AWAITING_CONFIRMATION")
        executor.execute.assert_not_called()
        self.assertEqual(action_provider.calls, 1)


if __name__ == "__main__":
    unittest.main()
