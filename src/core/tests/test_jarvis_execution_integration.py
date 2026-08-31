import unittest
from unittest.mock import Mock

from src.ai.models import (
    AICapabilities,
    AIRequest,
    AIResponse,
)
from src.ai.provider import AIProvider
from src.ai.service import AIService

from src.commands.models import CommandResult
from src.commands.handler import CommandHandler
from src.commands.registry import CommandRegistry
from src.commands.service import CommandService

from src.context.models import ContextOptions

from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
)
from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStatus,
    PlanStep,
    StepStatus,
)
from src.core.execution_policy_models import (
    ExecutionPolicyResult,
    PolicyDecision,
)
from src.core.execution_planner import ExecutionPlanner
from src.core.jarvis import JARVIS
from src.core.plan_validator import PlanValidator
from src.core.plan_validation_models import (
    PlanValidationIssue,
    PlanValidationResult,
)
from src.core.task_models import TaskRequest, TaskType


class IntegrationAIProvider(AIProvider):
    """Deterministic provider for orchestration tests."""

    def __init__(self):
        self.calls = 0

    def generate(self, request: AIRequest) -> AIResponse:
        self.calls += 1
        return AIResponse(
            content="Integration response.",
            provider="integration",
            model="integration-model",
            finish_reason="completed",
        )

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "integration"


class IntegrationCommandHandler(CommandHandler):
    def command_name(self):
        return "TEST"

    def execute(self, request):
        return CommandResult(
            success=True,
            command=request.name,
            message="Command executed.",
        )


class JARVISExecutionIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.provider = IntegrationAIProvider()
        self.ai_service = AIService(default_provider="integration")
        self.ai_service.register_provider(self.provider)

        self.router = Mock()
        self.router.route.side_effect = self._route
        self.router.route_task.side_effect = self._route_task

        self.command_registry = CommandRegistry()
        self.command_registry.register(
            IntegrationCommandHandler(),
        )
        self.command_service = CommandService(
            registry=self.command_registry,
        )

        self.planner = Mock(spec=ExecutionPlanner)
        self.validator = Mock(spec=PlanValidator)
        self.policy = Mock()
        self.executor = Mock()
        self.plan = self._plan()

        self.task = TaskRequest(
            content="Allowed task.",
            task_type=TaskType.ACTION,
        )
        self.confirmation_task = TaskRequest(
            content="Confirm task.",
            task_type=TaskType.TOOL,
        )

        self.allowed_policy = ExecutionPolicyResult(
            decision=PolicyDecision.ALLOW,
            plan=self.plan,
        )

        self.planner.plan.return_value = self.plan
        self.validator.validate.return_value = PlanValidationResult(
            valid=True,
            plan=self.plan,
        )
        self.policy.evaluate.return_value = ExecutionPolicyResult(
            decision=PolicyDecision.REQUIRE_CONFIRMATION,
            plan=self.plan,
        )
        self.policy.authorize_confirmed.return_value = self.allowed_policy
        self.executor.execute.return_value = PlanExecutionResult(
            plan_id=self.plan.plan_id,
            status=PlanExecutionStatus.COMPLETED,
            steps=(),
        )

        self.jarvis = JARVIS(
            ai_service=self.ai_service,
            request_router=self.router,
            command_service=self.command_service,
            execution_planner=self.planner,
            plan_validator=self.validator,
            execution_policy=self.policy,
            plan_executor=self.executor,
            context_options=ContextOptions(
                include_memories=False,
                include_evidence=False,
            ),
        )

    def _plan(self):
        return ExecutionPlan(
            plan_id="plan-integration",
            task_description="Test execution.",
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="Test execution.",
                    action="TEST",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
            status=PlanStatus.READY,
        )

    @staticmethod
    def _route(text):
        from src.core.task_models import RequestType, RouteDecision

        if text.startswith("/"):
            return RouteDecision(
                request_type=RequestType.COMMAND,
                original_input=text,
                command_name="TEST",
            )

        return RouteDecision(
            request_type=RequestType.CONVERSATION,
            original_input=text,
        )

    @staticmethod
    def _route_task(task):
        from src.core.task_models import RequestType, RouteDecision

        return RouteDecision(
            request_type=RequestType.TASK,
            original_input=task.content,
            task=task,
            reason="Test task.",
        )

    def _prepare_allowed_execution(self):
        self.planner.plan.return_value = self.plan
        self.validator.validate.return_value = PlanValidationResult(
            valid=True,
            plan=self.plan,
        )
        self.policy.evaluate.return_value = ExecutionPolicyResult(
            decision=PolicyDecision.ALLOW,
            plan=self.plan,
        )
        self.executor.execute.return_value = PlanExecutionResult(
            plan_id=self.plan.plan_id,
            status=PlanExecutionStatus.COMPLETED,
            steps=(),
        )

    def test_normal_conversation_uses_ai_path(self):
        response = self.jarvis.ask("Hello JARVIS.")
        self.assertEqual(response.metadata["route"], "CONVERSATION")
        self.assertEqual(response.content, "Integration response.")
        self.assertEqual(self.provider.calls, 1)
        self.planner.plan.assert_not_called()
        self.validator.validate.assert_not_called()
        self.policy.evaluate.assert_not_called()
        self.executor.execute.assert_not_called()

    def test_command_uses_command_service_path(self):
        response = self.jarvis.ask("/TEST")
        self.assertEqual(response.metadata["route"], "COMMAND")
        self.assertTrue(response.metadata["success"])
        self.assertEqual(response.content, "Command executed.")
        self.assertIsNone(response.ai_response)
        self.assertIsNone(response.context)
        self.assertEqual(self.provider.calls, 0)
        self.planner.plan.assert_not_called()

    def test_task_reaches_planner(self):
        self._prepare_allowed_execution()
        task = TaskRequest(
            content="Test execution.",
            task_type=TaskType.TOOL,
        )
        self.jarvis.ask_task(task)
        self.planner.plan.assert_called_once_with(task)

    def test_plan_reaches_validator(self):
        self._prepare_allowed_execution()
        task = TaskRequest(
            content="Test execution.",
            task_type=TaskType.TOOL,
        )
        self.jarvis.ask_task(task)
        self.validator.validate.assert_called_once_with(self.plan)

    def test_invalid_plan_stops_before_policy(self):
        self.planner.plan.return_value = self.plan
        self.validator.validate.return_value = PlanValidationResult(
            valid=False,
            plan=self.plan,
            issues=(
                PlanValidationIssue(
                    code="INVALID",
                    message="Plan invalid.",
                ),
            ),
        )
        response = self.jarvis.ask_task(
            TaskRequest(
                content="Invalid task.",
                task_type=TaskType.TOOL,
            )
        )
        self.assertEqual(response.metadata["stage"], "VALIDATION")
        self.assertFalse(response.metadata["valid"])
        self.policy.evaluate.assert_not_called()
        self.executor.execute.assert_not_called()

    def test_denied_plan_stops_before_executor(self):
        self.planner.plan.return_value = self.plan
        self.validator.validate.return_value = PlanValidationResult(
            valid=True,
            plan=self.plan,
        )
        self.policy.evaluate.return_value = ExecutionPolicyResult(
            decision=PolicyDecision.DENY,
            plan=self.plan,
        )
        response = self.jarvis.ask_task(
            TaskRequest(
                content="Denied task.",
                task_type=TaskType.ACTION,
            )
        )
        self.assertEqual(response.metadata["policy_decision"], "DENY")
        self.executor.execute.assert_not_called()

    def test_confirmation_required_plan_stops_before_executor(self):
        self.planner.plan.return_value = self.plan
        self.validator.validate.return_value = PlanValidationResult(
            valid=True,
            plan=self.plan,
        )
        self.policy.evaluate.return_value = ExecutionPolicyResult(
            decision=PolicyDecision.REQUIRE_CONFIRMATION,
            plan=self.plan,
        )
        response = self.jarvis.ask_task(
            TaskRequest(
                content="Confirm task.",
                task_type=TaskType.TOOL,
            )
        )
        self.assertEqual(
            response.metadata["policy_decision"],
            "REQUIRE_CONFIRMATION",
        )
        self.executor.execute.assert_not_called()

    def test_allowed_plan_reaches_executor(self):
        self._prepare_allowed_execution()
        response = self.jarvis.ask_task(
            TaskRequest(
                content="Allowed task.",
                task_type=TaskType.ACTION,
            )
        )
        policy = self.policy.evaluate.return_value
        self.policy.evaluate.assert_called_once_with(self.plan)
        self.executor.execute.assert_called_once_with(
            self.plan,
            policy,
        )
        self.assertEqual(response.metadata["stage"], "EXECUTION")
        self.assertEqual(response.metadata["execution_status"], "COMPLETED")

    def test_execution_result_is_returned_through_jarvis(self):
        self.planner.plan.return_value = self.plan
        self.validator.validate.return_value = PlanValidationResult(
            valid=True,
            plan=self.plan,
        )
        self.policy.evaluate.return_value = ExecutionPolicyResult(
            decision=PolicyDecision.ALLOW,
            plan=self.plan,
        )
        self.executor.execute.return_value = PlanExecutionResult(
            plan_id=self.plan.plan_id,
            status=PlanExecutionStatus.FAILED,
            steps=(),
            error="Test failure.",
        )
        response = self.jarvis.ask_task(
            TaskRequest(
                content="Failing task.",
                task_type=TaskType.ACTION,
            )
        )
        self.assertEqual(response.metadata["execution_status"], "FAILED")
        self.assertIn("Test failure.", response.content)

    def test_task_response_has_no_fake_ai_response(self):
        self.planner.plan.return_value = self.plan
        self.validator.validate.return_value = PlanValidationResult(
            valid=True,
            plan=self.plan,
        )
        self.policy.evaluate.return_value = ExecutionPolicyResult(
            decision=PolicyDecision.DENY,
            plan=self.plan,
        )
        response = self.jarvis.ask_task(
            TaskRequest(
                content="Denied task.",
                task_type=TaskType.ACTION,
            )
        )
        self.assertIsNone(response.ai_response)
        self.assertIsNone(response.context)

    def test_command_does_not_modify_conversation(self):
        before = self.jarvis.conversation.snapshot()
        self.jarvis.ask("/TEST")
        after = self.jarvis.conversation.snapshot()
        self.assertEqual(before, after)

    def test_conversation_still_records_turns_after_integration(self):
        self.jarvis.ask("Hello JARVIS.")
        turns = self.jarvis.conversation.get_recent_turns()
        self.assertEqual(len(turns), 2)
        self.assertEqual(turns[0].role, "user")
        self.assertEqual(turns[1].role, "assistant")

    def test_memory_formation_remains_on_conversation_path(self):
        response = self.jarvis.ask("Remember this conversation.")
        self.assertEqual(response.metadata["route"], "CONVERSATION")
        self.assertEqual(self.provider.calls, 1)
        self.planner.plan.assert_not_called()
        self.validator.validate.assert_not_called()
        self.policy.evaluate.assert_not_called()
        self.executor.execute.assert_not_called()

    def test_confirmation_does_not_replan(self):
        self.jarvis.ask("/CONFIRM")
        self.planner.plan.assert_not_called()

    def test_confirmation_executes_exact_staged_plan(self):
        response = self.jarvis.ask_task(self.task)
        operation_id = response.metadata["operation_id"]
        self.planner.plan.assert_called_once()
        self.executor.execute.reset_mock()
        confirmation = self.jarvis.ask(f"/CONFIRM {operation_id}")
        self.executor.execute.assert_called_once_with(
            self.plan,
            self.allowed_policy,
        )
        self.assertTrue(confirmation.metadata["confirmation"])

    def test_confirmation_does_not_replan_after_pending_operation(self):
        self.jarvis.ask_task(self.task)
        self.planner.plan.reset_mock()
        self.jarvis.ask("/CONFIRM")
        self.planner.plan.assert_not_called()

    def test_confirmation_does_not_replan_when_no_pending_operation(self):
        self.jarvis.ask("/CONFIRM")
        self.planner.plan.assert_not_called()

    def test_cancelled_operation_never_reaches_executor(self):
        response = self.jarvis.ask_task(self.confirmation_task)
        operation_id = response.metadata["operation_id"]
        self.jarvis.ask(f"/CANCEL {operation_id}")
        self.executor.execute.assert_not_called()

    def test_confirmation_blocks_changed_plan(self):
        response = self.jarvis.ask_task(self.confirmation_task)
        operation_id = response.metadata["operation_id"]
        pending = (
            self.jarvis
            .execution_confirmation_service
            .get(operation_id)
        )
        pending.metadata["plan_fingerprint"] = "tampered"
        result = self.jarvis.ask(f"/CONFIRM {operation_id}")
        self.executor.execute.assert_not_called()
        self.assertIn("fingerprint", result.content.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
