import unittest
from unittest.mock import Mock

from src.ai.models import AIResponse
from src.ai.service import AIService
from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
)
from src.core.execution_loop import ExecutionObservation
from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.model_continuation import ModelContinuationPlanner
from src.core.task_models import TaskRequest, TaskType


class ModelContinuationPlannerTests(unittest.TestCase):
    def setUp(self):
        self.ai_service = Mock(spec=AIService)
        self.planner = ModelContinuationPlanner(self.ai_service)
        self.plan = ExecutionPlan(
            plan_id="plan-1",
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
        self.observation = ExecutionObservation(
            self.plan,
            PlanExecutionResult(
                plan_id="plan-1",
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
        )

    def test_model_proposal_becomes_task_request(self):
        self.ai_service.generate.return_value = AIResponse(
            content='{"task":"retry carefully","task_type":"ACTION"}',
            provider="fake",
            model="fake-model",
        )

        result = self.planner.propose(
            TaskRequest("do it", TaskType.ACTION),
            self.observation,
        )

        self.assertEqual(result, TaskRequest("retry carefully", TaskType.ACTION))
        request = self.ai_service.generate.call_args.args[0]
        self.assertEqual(request.metadata["purpose"], "execution_correction")

    def test_no_task_stops_correction(self):
        self.ai_service.generate.return_value = AIResponse(
            content='{"task":null,"task_type":"UNKNOWN"}',
            provider="fake",
            model="fake-model",
        )

        result = self.planner.propose(TaskRequest("do it", TaskType.ACTION), self.observation)
        self.assertIsNone(result)

    def test_invalid_json_is_rejected(self):
        self.ai_service.generate.return_value = AIResponse(
            content="not json",
            provider="fake",
            model="fake-model",
        )
        with self.assertRaises(ValueError):
            self.planner.propose(TaskRequest("do it", TaskType.ACTION), self.observation)

    def test_invalid_task_type_is_rejected(self):
        self.ai_service.generate.return_value = AIResponse(
            content='{"task":"retry","task_type":"MAGIC"}',
            provider="fake",
            model="fake-model",
        )
        with self.assertRaises(ValueError):
            self.planner.propose(TaskRequest("do it", TaskType.ACTION), self.observation)

    def test_boundary_does_not_execute_tools(self):
        self.ai_service.generate.return_value = AIResponse(
            content='{"task":"retry","task_type":"TOOL"}',
            provider="fake",
            model="fake-model",
        )
        result = self.planner.propose(TaskRequest("do it", TaskType.ACTION), self.observation)
        self.assertEqual(result.task_type, TaskType.TOOL)
        # The continuation planner only returns a TaskRequest; execution remains
        # the responsibility of GuardedExecutionLoop and PlanExecutor.
        self.assertEqual(self.ai_service.generate.call_count, 1)

    def test_requires_real_ai_service(self):
        with self.assertRaises(TypeError):
            ModelContinuationPlanner(Mock())


if __name__ == "__main__":
    unittest.main()
