import unittest
from unittest.mock import Mock

from src.ai.models import AIResponse
from src.ai.service import AIService
from src.core.execution_assessment import ExecutionAssessmentService
from src.core.execution_executor_models import (
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
    PlanExecutionResult,
)
from src.core.execution_state import ExecutionOutput, ExecutionState
from src.core.model_execution_assessment import ModelExecutionAssessmentService


class ModelExecutionAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.ai_service = Mock(spec=AIService)
        self.service = ModelExecutionAssessmentService(self.ai_service)
        self.state = ExecutionState(
            goal="inspect project then modify identified file",
            plan_id="plan-1",
            status=PlanExecutionStatus.FAILED,
            completed_steps=("inspect",),
            failed_steps=("modify",),
            available_outputs=(ExecutionOutput("inspect", "auth/config.py"),),
            unresolved_requirements=("Resolve failed step 'modify': permission denied",),
            next_allowed_actions=("CORRECT", "STOP"),
        )

    def _response(self, content: str):
        self.ai_service.generate.return_value = AIResponse(
            content=content,
            provider="fake",
            model="fake-model",
        )

    def test_model_assessment_is_returned(self):
        self._response(
            '{"situation":"partial_progress","completed":["inspect project"],'
            '"remaining":["modify auth/config.py","verify the fix"],'
            '"blockers":["permission denied"],'
            '"recommended_next_action":"address permissions",'
            '"confidence":0.9}'
        )

        result = self.service.assess(self.state)

        self.assertEqual(result.goal, self.state.goal)
        self.assertEqual(result.situation, "partial_progress")
        self.assertEqual(result.completed, ("inspect project",))
        self.assertEqual(result.remaining, ("modify auth/config.py", "verify the fix"))
        self.assertEqual(result.blockers, ("permission denied",))
        self.assertEqual(result.recommended_next_action, "address permissions")
        self.assertEqual(result.confidence, 0.9)

    def test_verified_outputs_are_not_model_supplied(self):
        self._response(
            '{"situation":"partial_progress","completed":["inspect"],'
            '"remaining":["modify"],"blockers":[],'
            '"recommended_next_action":"continue","confidence":0.8}'
        )

        result = self.service.assess(self.state)

        self.assertEqual(result.useful_outputs, self.state.available_outputs)

    def test_model_receives_verified_state_and_deterministic_baseline(self):
        self._response(
            '{"situation":"blocked","completed":["inspect"],"remaining":["modify"],'
            '"blockers":["permission denied"],"recommended_next_action":"CORRECT",'
            '"confidence":0.7}'
        )

        self.service.assess(self.state)

        request = self.ai_service.generate.call_args.args[0]
        self.assertEqual(request.context["type"], "execution_assessment")
        self.assertIn("permission denied", str(request.task))
        self.assertIn("deterministic_assessment", request.context)
        self.assertEqual(request.metadata["purpose"], "execution_state_reasoning")

    def test_invalid_json_is_rejected(self):
        self._response("not json")
        with self.assertRaises(ValueError):
            self.service.assess(self.state)

    def test_missing_field_is_rejected(self):
        self._response(
            '{"situation":"blocked","completed":[],"remaining":[],"blockers":[],"confidence":0.8}'
        )
        with self.assertRaises(ValueError):
            self.service.assess(self.state)

    def test_invalid_confidence_is_rejected(self):
        self._response(
            '{"situation":"blocked","completed":[],"remaining":[],"blockers":[],'
            '"recommended_next_action":"STOP","confidence":2.0}'
        )
        with self.assertRaises(ValueError):
            self.service.assess(self.state)

    def test_non_state_input_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.assess("not state")

    def test_requires_real_ai_service(self):
        with self.assertRaises(TypeError):
            ModelExecutionAssessmentService(Mock())


if __name__ == "__main__":
    unittest.main()
