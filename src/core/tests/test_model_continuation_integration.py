import unittest
from unittest.mock import Mock

from src.ai.models import AIResponse
from src.ai.service import AIService
from src.core.execution_confirmation import ExecutionConfirmationService
from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
)
from src.core.execution_loop import GuardedExecutionLoop, ExecutionObservation
from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.execution_policy import ExecutionPolicy
from src.core.model_continuation import ModelContinuationPlanner
from src.core.plan_executor import PlanExecutor
from src.core.plan_validator import PlanValidator
from src.core.task_models import TaskRequest, TaskType


class ModelContinuationIntegrationTests(unittest.TestCase):
    def _plan(self, plan_id, action="PROVIDE_INFORMATION"):
        return ExecutionPlan(
            plan_id=plan_id,
            task_description="do it",
            status=PlanStatus.READY,
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="do it",
                    action=action,
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
        )

    def test_model_correction_reenters_guarded_loop(self):
        ai_service = Mock(spec=AIService)
        ai_service.generate.return_value = AIResponse(
            content='{"task":"retry","task_type":"INFORMATION"}',
            provider="fake",
            model="fake-model",
        )
        continuation = ModelContinuationPlanner(ai_service)

        plans = [self._plan("p1"), self._plan("p2")]
        planner = Mock()
        planner.plan.side_effect = plans

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
                        output="ok",
                    ),
                ),
            ),
        ]

        loop = GuardedExecutionLoop(
            planner,
            PlanValidator(),
            ExecutionPolicy(),
            executor,
            ExecutionConfirmationService(),
            max_iterations=2,
        )

        result = loop.run(
            TaskRequest("do it", TaskType.INFORMATION),
            corrective_planner=continuation.propose,
        )

        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(result.iterations, 2)
        self.assertEqual(planner.plan.call_count, 2)
        self.assertEqual(executor.execute.call_count, 2)
        self.assertEqual(ai_service.generate.call_count, 1)


if __name__ == "__main__":
    unittest.main()
