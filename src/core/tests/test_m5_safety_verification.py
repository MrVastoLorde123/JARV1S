import unittest
from unittest.mock import Mock

from src.ai.models import AICapabilities, AIRequest, AIResponse
from src.ai.provider import AIProvider
from src.ai.service import AIService
from src.core.assessment_aware_planning import AssessmentAwarePlanningService
from src.core.execution_assessment import ExecutionAssessment, ExecutionAssessmentService
from src.core.execution_assessment_validator import ExecutionAssessmentValidator
from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.execution_policy import ExecutionPolicy
from src.core.execution_policy_models import PolicyDecision
from src.core.execution_state import ExecutionState
from src.core.model_execution_assessment import ModelExecutionAssessmentService
from src.core.model_execution_planner import ModelExecutionPlanner
from src.core.remaining_work import RemainingWork
from src.core.task_models import TaskRequest, TaskType


class AssessmentProvider(AIProvider):
    def __init__(self, content):
        self.content = content
        self.requests = []

    def generate(self, request: AIRequest) -> AIResponse:
        self.requests.append(request)
        return AIResponse(content=self.content, provider="assessment", model="test-model")

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "assessment"


class PlannerProvider(AIProvider):
    def __init__(self, content):
        self.content = content
        self.requests = []

    def generate(self, request: AIRequest) -> AIResponse:
        self.requests.append(request)
        return AIResponse(content=self.content, provider="planner", model="test-model")

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "planner"


class M5SafetyVerificationTests(unittest.TestCase):
    def setUp(self):
        self.task = TaskRequest(
            "inspect project then modify identified file",
            TaskType.ACTION,
        )
        self.state = ExecutionState(
            goal=self.task.content,
            plan_id="attempt-1",
            status=PlanExecutionStatus.FAILED,
            completed_steps=("inspect",),
            failed_steps=("modify",),
            unresolved_requirements=(
                "Resolve failed step 'modify': permission denied",
            ),
            next_allowed_actions=("CORRECT", "STOP"),
        )
        self.assessment = ExecutionAssessment(
            goal=self.state.goal,
            situation="blocked",
            completed=("inspect project",),
            remaining=("modify identified file",),
            blockers=("permission denied",),
            recommended_next_action="address permissions",
            confidence=0.95,
        )

    def test_m5_chain_preserves_observed_failure_to_planning(self):
        planner = Mock()
        planner.plan.return_value = ExecutionPlan(
            plan_id="plan-next",
            task_description=self.task.content,
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="resolve modify permission issue",
                    action="PERFORM_ACTION",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
            status=PlanStatus.READY,
        )

        planning = AssessmentAwarePlanningService(planner)
        plan = planning.plan(self.task, self.state, self.assessment)

        remaining = planner.plan.call_args.kwargs["remaining_work"]
        self.assertIsInstance(remaining, RemainingWork)
        self.assertIn("Resolve failed step 'modify': permission denied", remaining.items)
        self.assertIn("modify identified file", remaining.items)
        self.assertEqual(plan.steps[0].action, "PERFORM_ACTION")

    def test_validation_rejects_model_reality_conflict_even_with_high_confidence(self):
        invalid = ExecutionAssessment(
            goal=self.state.goal,
            situation="partial_progress",
            completed=("modify authentication config",),
            remaining=("modify identified file",),
            blockers=("permission denied",),
            confidence=1.0,
        )

        with self.assertRaisesRegex(ValueError, "failed step 'modify'"):
            ExecutionAssessmentValidator().validate(self.state, invalid)

    def test_model_assessment_cannot_replace_verified_outputs(self):
        provider = AssessmentProvider(
            '{"situation":"blocked","completed":["inspect"],'
            '"remaining":["modify identified file"],'
            '"blockers":["permission denied"],'
            '"recommended_next_action":"address permissions",'
            '"confidence":0.99}'
        )
        ai = AIService(default_provider="assessment")
        ai.register_provider(provider)
        service = ModelExecutionAssessmentService(ai)

        state = ExecutionState(
            goal="inspect project then modify identified file",
            plan_id="attempt-1",
            status=PlanExecutionStatus.FAILED,
            completed_steps=("inspect",),
            failed_steps=("modify",),
            available_outputs=(),
            unresolved_requirements=(
                "Resolve failed step 'modify': permission denied",
            ),
            next_allowed_actions=("CORRECT", "STOP"),
        )

        assessment = service.assess(state)

        self.assertEqual(assessment.useful_outputs, ())
        self.assertNotIn("output", assessment.to_context()["useful_outputs"])

    def test_invalid_assessment_is_rejected_before_any_plan_is_generated(self):
        planner = Mock()
        planning = AssessmentAwarePlanningService(planner)
        invalid = ExecutionAssessment(
            goal=self.state.goal,
            situation="objective_completed",
            completed=("modify",),
        )

        with self.assertRaises(ValueError):
            planning.plan(self.task, self.state, invalid)

        planner.plan.assert_not_called()

    def test_completed_execution_requires_completed_assessment(self):
        state = ExecutionState(
            goal="inspect project",
            plan_id="attempt-2",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("inspect",),
            next_allowed_actions=("COMPLETE",),
        )
        assessment = ExecutionAssessment(
            goal=state.goal,
            situation="partial_progress",
            completed=("inspect",),
        )

        with self.assertRaisesRegex(ValueError, "observed completed execution"):
            ExecutionAssessmentValidator().validate(state, assessment)

    def test_model_planner_receives_only_grounded_remaining_work(self):
        provider = PlannerProvider(
            '{"steps":[{"task":"resolve permission issue","task_type":"ACTION"}]}'
        )
        ai = AIService(default_provider="planner")
        ai.register_provider(provider)
        planner = ModelExecutionPlanner(ai)

        remaining = RemainingWork(
            goal=self.state.goal,
            items=("Resolve failed step 'modify': permission denied",),
            blockers=("Resolve failed step 'modify': permission denied",),
            source_requirements=self.state.unresolved_requirements,
        )

        planner.plan(self.task, remaining_work=remaining)

        prompt = provider.requests[0].task
        self.assertIn("Resolve failed step 'modify': permission denied", prompt)
        self.assertIn("Grounded remaining work", prompt)
        self.assertIn("Do not assume unobserved work is complete", prompt)

    def test_assessment_aware_plan_does_not_bypass_policy(self):
        planner = Mock()
        planner.plan.return_value = ExecutionPlan(
            plan_id="plan-next",
            task_description=self.task.content,
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="resolve modify permission issue",
                    action="PERFORM_ACTION",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
            status=PlanStatus.READY,
        )

        plan = AssessmentAwarePlanningService(planner).plan(
            self.task,
            self.state,
            self.assessment,
        )
        policy = ExecutionPolicy().evaluate(plan)

        self.assertEqual(policy.decision, PolicyDecision.REQUIRE_CONFIRMATION)

    def test_assessment_is_immutable_and_state_remains_separate(self):
        deterministic = ExecutionAssessmentService().assess(self.state)
        self.assertEqual(deterministic.completed, ("inspect",))
        self.assertEqual(deterministic.blockers, self.state.unresolved_requirements)
        self.assertEqual(deterministic.useful_outputs, self.state.available_outputs)
        with self.assertRaises(AttributeError):
            deterministic.situation = "objective_completed"


if __name__ == "__main__":
    unittest.main()
