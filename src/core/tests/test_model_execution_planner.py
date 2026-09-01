import unittest
from unittest.mock import Mock

from src.ai.models import AICapabilities, AIRequest, AIResponse
from src.ai.provider import AIProvider
from src.ai.service import AIService
from src.core.capability_realization import CapabilityRealizationService
from src.core.execution_plan_models import ExecutionPlan
from src.core.model_execution_planner import ModelExecutionPlanner
from src.core.task_models import TaskRequest, TaskType


class PlanningProvider(AIProvider):
    def __init__(self, content):
        self.content = content

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content=self.content,
            provider="planning",
            model="test-model",
        )

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "planning"


class ModelExecutionPlannerTests(unittest.TestCase):
    def _service(self, content, capability_realizer=None, max_steps=8):
        ai = AIService(default_provider="planning")
        ai.register_provider(PlanningProvider(content))
        return ModelExecutionPlanner(
            ai,
            capability_realization_service=capability_realizer,
            max_steps=max_steps,
        )

    def test_model_subtasks_become_ordered_execution_plan(self):
        planner = self._service(
            '{"steps":[{"task":"inspect workspace","task_type":"INFORMATION"},'
            '{"task":"report findings","task_type":"ACTION"}]}'
        )

        plan = planner.plan(TaskRequest("inspect then report", TaskType.ACTION))

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertEqual(plan.metadata["planner"], "multi_step_deterministic")
        self.assertEqual(plan.metadata["subtask_count"], 2)
        self.assertEqual(len(plan.steps), 2)
        self.assertEqual(plan.steps[0].order, 0)
        self.assertEqual(plan.steps[1].depends_on, ("step-1",))

    def test_invalid_model_json_is_rejected(self):
        planner = self._service("not json")
        with self.assertRaises(ValueError):
            planner.plan(TaskRequest("do it", TaskType.ACTION))

    def test_unknown_task_type_is_rejected(self):
        planner = self._service(
            '{"steps":[{"task":"do it","task_type":"UNKNOWN"}]}'
        )
        with self.assertRaises(ValueError):
            planner.plan(TaskRequest("do it", TaskType.ACTION))

    def test_model_step_count_is_bounded(self):
        planner = self._service(
            '{"steps":[{"task":"one","task_type":"ACTION"},'
            '{"task":"two","task_type":"ACTION"}]}'
            ,
            max_steps=1,
        )
        with self.assertRaises(ValueError):
            planner.plan(TaskRequest("do two things", TaskType.ACTION))

    def test_planner_does_not_execute(self):
        planner = self._service(
            '{"steps":[{"task":"do it","task_type":"ACTION"}]}'
        )
        plan = planner.plan(TaskRequest("do it", TaskType.ACTION))
        self.assertIsInstance(plan, ExecutionPlan)

    def test_tool_subtask_requires_capability_realization(self):
        planner = self._service(
            '{"steps":[{"task":"read README.md","task_type":"TOOL"}]}'
        )
        with self.assertRaises(ValueError):
            planner.plan(TaskRequest("read README.md", TaskType.ACTION))

    def test_tool_subtask_uses_capability_realization_boundary(self):
        realizer = Mock(spec=CapabilityRealizationService)
        request = Mock()
        request.tool_name = "read_file"
        request.arguments = {"path": "README.md"}
        request.invocation_id = "inv-1"
        candidate = Mock(score=1.0, reason="matched")
        realizer.realize.return_value = Mock(request=request, candidate=candidate)

        planner = self._service(
            '{"steps":[{"task":"read README.md","task_type":"TOOL"}]}'
            ,
            capability_realizer=realizer,
        )

        plan = planner.plan(TaskRequest("read README.md", TaskType.ACTION))

        self.assertEqual(plan.steps[0].metadata["tool_name"], "read_file")
        self.assertEqual(plan.steps[0].metadata["arguments"], {"path": "README.md"})
        self.assertEqual(plan.steps[0].metadata["invocation_id"], "inv-1")
        realizer.realize.assert_called_once_with("read README.md")


if __name__ == "__main__":
    unittest.main()
