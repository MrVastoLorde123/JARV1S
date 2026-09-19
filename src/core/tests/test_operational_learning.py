"""Acceptance tests for OPS-07 operational feedback → learning → adaptation."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.ai.service import AIService
from src.core.capability_argument_planner import CapabilityInvocationService
from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
)
from src.core.execution_plan_models import ExecutionPlan, PlanStep, PlanStatus, StepStatus
from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.jarvis import JARVIS
from src.core.persistent_intelligence import PersistentMemoryRepository
from src.core.operational_learning import (
    OperationalAdaptationHintStatus,
    OperationalLearningEvaluationStatus,
    OperationalLearningRuntime,
)
from src.core.request_intent import IntentKind, RequestIntent
from src.core.tool_execution import ToolCapabilityGateway
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult


class StaticTaskIntentClassifier:
    def classify(self, text):
        return RequestIntent(
            kind=IntentKind.TASK,
            content=text,
            confidence=0.99,
            reasoning="OPS-07 deterministic task fixture",
        )


class EmptyArgumentPlanner:
    def propose(self, intent, capability):
        return {}


class LearningToolGateway(ToolCapabilityGateway):
    def __init__(self, *, fail=False):
        self.fail = fail
        self.requests = []
        self.definitions = (
            ToolDefinition(
                name="report_status",
                description="Report the current runtime status.",
                version="1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_level=RiskLevel.LOW,
            ),
        )

    def list_definitions(self):
        return self.definitions

    def invoke(self, request: ToolRequest):
        self.requests.append(request)
        if self.fail:
            raise RuntimeError("simulated execution failure")
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"status": "ops-07-ok"},
            invocation_id=request.invocation_id,
        )


class OPS07OperationalLearningTests(unittest.TestCase):
    def _plan(self, plan_id="plan-persist"):
        return ExecutionPlan(
            plan_id=plan_id,
            task_description="Report runtime status",
            steps=(
                PlanStep(
                    step_id=f"{plan_id}-step",
                    description="Report runtime status",
                    action="USE_TOOL",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
            status=PlanStatus.READY,
        )

    def _failed_execution(self, plan_id):
        return PlanExecutionResult(
            plan_id=plan_id,
            status=PlanExecutionStatus.FAILED,
            steps=(
                StepExecutionResult(
                    step_id=f"{plan_id}-step",
                    action="USE_TOOL",
                    status=StepExecutionStatus.FAILED,
                    error="persisted operational failure",
                ),
            ),
            error="persisted operational failure",
        )

    def test_learning_record_survives_runtime_reconstruction(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = PersistentMemoryRepository(Path(directory) / "learning.db")
            first = OperationalLearningRuntime(repository=repository)
            plan = self._plan()
            record = first.record_execution(
                self._failed_execution(plan.plan_id),
                plan,
                capability="report_status",
            )

            self.assertTrue(record.persisted)
            second = OperationalLearningRuntime(repository=repository)

            context = second.context_for("Report runtime status")
            self.assertTrue(context["available"])
            self.assertEqual(len(context["matches"]), 1)
            self.assertEqual(
                context["matches"][0]["adaptation_hint_status"],
                "CORRECT_PATTERN",
            )
            self.assertFalse(context["authority_granted"])
            self.assertFalse(context["execution_requested"])

    def test_fresh_jarvis_instance_consumes_persisted_learning_without_authority_expansion(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = PersistentMemoryRepository(Path(directory) / "learning.db")
            gateway = LearningToolGateway(fail=True)

            first = JARVIS(
                ai_service=AIService(default_provider="unused"),
                intelligent_request_router=IntelligentRequestRouter(StaticTaskIntentClassifier()),
                tool_invoker=gateway,
                capability_invocation_service=CapabilityInvocationService(EmptyArgumentPlanner()),
                operational_learning_runtime=OperationalLearningRuntime(repository=repository),
            )
            first_response = first.ask("Report the current runtime status.")
            self.assertEqual(first_response.metadata["execution_status"], "FAILED")
            self.assertEqual(
                first_response.metadata["operational_learning"]["adaptation_hint_status"],
                "CORRECT_PATTERN",
            )

            gateway.fail = False
            second = JARVIS(
                ai_service=AIService(default_provider="unused"),
                intelligent_request_router=IntelligentRequestRouter(StaticTaskIntentClassifier()),
                tool_invoker=gateway,
                capability_invocation_service=CapabilityInvocationService(EmptyArgumentPlanner()),
                operational_learning_runtime=OperationalLearningRuntime(repository=repository),
            )
            second_response = second.ask("Report the current runtime status.")

            self.assertEqual(second_response.metadata["execution_status"], "COMPLETED")
            learning = second_response.metadata["cognitive_context"]["operational_learning"]
            self.assertTrue(learning["available"])
            self.assertGreaterEqual(len(learning["matches"]), 1)
            step_description = second_response.metadata["cognitive_context"]["selected_plan"]["steps"][0]["description"]
            self.assertIn("Prior operational learning guidance:", step_description)
            self.assertIn("consider correction before repeating", step_description)
            self.assertFalse(second_response.metadata["cognitive_context"]["authority_granted"])
            self.assertFalse(second_response.metadata["cognitive_context"]["authorization_granted"])
            self.assertFalse(second_response.metadata["cognitive_context"]["execution_requested"])


    def test_runtime_turns_execution_result_into_bounded_learning_and_future_hint(self):
        runtime = OperationalLearningRuntime()
        plan = ExecutionPlan(
            plan_id="plan-1",
            task_description="Report runtime status",
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="Report runtime status",
                    action="USE_TOOL",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
            status=PlanStatus.READY,
        )
        execution = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            steps=(
                StepExecutionResult(
                    step_id="step-1",
                    action="USE_TOOL",
                    status=StepExecutionStatus.COMPLETED,
                    output={"ok": True},
                ),
            ),
        )

        record = runtime.record_execution(
            execution,
            plan,
            capability="report_status",
        )

        self.assertEqual(
            record.evaluation.status,
            OperationalLearningEvaluationStatus.SUCCESS_PATTERN,
        )
        self.assertEqual(
            record.adaptation_hint.status,
            OperationalAdaptationHintStatus.REINFORCE_PATTERN,
        )
        self.assertFalse(record.experience.grants_authority)
        self.assertFalse(record.experience.authorizes_retry)
        self.assertFalse(record.evaluation.creates_authority)
        self.assertFalse(record.evaluation.authorizes_retry)
        self.assertFalse(record.adaptation_hint.changes_authority)
        self.assertFalse(record.adaptation_hint.changes_policy)
        context = runtime.context_for("Report runtime status")
        self.assertTrue(context["available"])
        self.assertEqual(len(context["matches"]), 1)
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["execution_requested"])

    def test_failed_execution_becomes_correction_evidence_without_retry(self):
        runtime = OperationalLearningRuntime()
        plan = ExecutionPlan(
            plan_id="plan-2",
            task_description="Report runtime status",
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="Report runtime status",
                    action="USE_TOOL",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
            status=PlanStatus.READY,
        )
        execution = PlanExecutionResult(
            plan_id="plan-2",
            status=PlanExecutionStatus.FAILED,
            steps=(
                StepExecutionResult(
                    step_id="step-1",
                    action="USE_TOOL",
                    status=StepExecutionStatus.FAILED,
                    error="simulated execution failure",
                ),
            ),
            error="simulated execution failure",
        )
        record = runtime.record_execution(execution, plan, capability="report_status")
        self.assertEqual(record.evaluation.status, OperationalLearningEvaluationStatus.FAILURE_PATTERN)
        self.assertEqual(record.adaptation_hint.status, OperationalAdaptationHintStatus.CORRECT_PATTERN)
        self.assertEqual(record.experience.failure_reason, "simulated execution failure")
        self.assertFalse(record.evaluation.authorizes_retry)

    def test_blocked_execution_preserves_the_authorization_boundary_without_retry(self):
        runtime = OperationalLearningRuntime()
        plan = ExecutionPlan(
            plan_id="plan-3",
            task_description="Perform a protected operation",
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="Perform a protected operation",
                    action="USE_TOOL",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
            status=PlanStatus.READY,
        )
        execution = PlanExecutionResult(
            plan_id="plan-3",
            status=PlanExecutionStatus.BLOCKED,
            steps=(),
            error="Execution is not authorized by policy.",
        )

        record = runtime.record_execution(execution, plan)

        self.assertEqual(
            record.evaluation.status,
            OperationalLearningEvaluationStatus.BOUNDED_BLOCK,
        )
        self.assertEqual(
            record.adaptation_hint.status,
            OperationalAdaptationHintStatus.PRESERVE_BOUNDARY,
        )
        self.assertFalse(record.experience.grants_authority)
        self.assertFalse(record.experience.authorizes_retry)
        self.assertFalse(record.evaluation.creates_authority)
        self.assertFalse(record.adaptation_hint.changes_policy)


    def test_live_jarvis_exposes_learning_after_execution_and_feeds_it_forward(self):
        gateway = LearningToolGateway()
        jarvis = JARVIS(
            ai_service=AIService(default_provider="unused"),
            intelligent_request_router=IntelligentRequestRouter(StaticTaskIntentClassifier()),
            tool_invoker=gateway,
            capability_invocation_service=CapabilityInvocationService(EmptyArgumentPlanner()),
        )

        first = jarvis.ask("Report the current runtime status.")
        self.assertEqual(first.metadata["execution_status"], "COMPLETED")
        learning = first.metadata["operational_learning"]
        self.assertEqual(learning["evaluation_status"], "SUCCESS_PATTERN")
        self.assertFalse(learning["authority_granted"])
        self.assertFalse(learning["execution_requested"])

        second = jarvis.ask("Report the current runtime status.")
        context = second.metadata["cognitive_context"]["operational_learning"]
        self.assertTrue(context["available"])
        self.assertGreaterEqual(len(context["matches"]), 1)
        self.assertEqual(
            context["matches"][0]["outcome_status"],
            "COMPLETED",
        )

    def test_live_failed_execution_creates_failure_learning_without_automatic_retry(self):
        gateway = LearningToolGateway(fail=True)
        jarvis = JARVIS(
            ai_service=AIService(default_provider="unused"),
            intelligent_request_router=IntelligentRequestRouter(StaticTaskIntentClassifier()),
            tool_invoker=gateway,
            capability_invocation_service=CapabilityInvocationService(EmptyArgumentPlanner()),
        )

        response = jarvis.ask("Report the current runtime status.")
        self.assertEqual(response.metadata["execution_status"], "FAILED")
        learning = response.metadata["operational_learning"]
        self.assertEqual(learning["evaluation_status"], "FAILURE_PATTERN")
        self.assertEqual(learning["adaptation_hint_status"], "CORRECT_PATTERN")
        self.assertFalse(learning["authorizes_retry"])
        self.assertEqual(len(gateway.requests), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
