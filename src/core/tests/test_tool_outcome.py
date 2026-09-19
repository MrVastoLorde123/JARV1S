"""OPS-17 execution/observation/verification separation tests."""
from __future__ import annotations

import unittest

from src.core.execution_plan_models import ExecutionPlan, PlanStep
from src.core.execution_executor_models import PlanExecutionStatus
from src.core.plan_executor import PlanExecutor
from src.core.execution_policy_models import ExecutionPolicyResult, PolicyDecision
from src.tools.models import ToolRequest, ToolResult, ToolDefinition, RiskLevel
from src.tools.outcome import (
    ExternalObservation,
    ExternalObservationState,
    ExternalVerification,
    ExternalVerificationState,
    ToolExecutionState,
    ToolOutcomeService,
)


class OutcomeTests(unittest.TestCase):
    def _result(self, *, success=True, invocation_id="invoke-1"):
        return ToolResult(
            success=success,
            tool_name="read_status",
            content={"status": "ok"} if success else None,
            invocation_id=invocation_id,
            error=None if success else __import__("src.tools.models", fromlist=["ToolError"]).ToolError(
                code="failed",
                message="handler failed",
            ),
        )

    def test_successful_tool_result_is_executed_but_not_observed_or_verified(self):
        request = ToolRequest(
            tool_name="read_status",
            invocation_id="invoke-1",
        )
        outcome = ToolOutcomeService.classify(
            request,
            self._result(),
        )

        self.assertEqual(outcome.execution_state, ToolExecutionState.EXECUTED)
        self.assertEqual(outcome.observation_state, ExternalObservationState.NOT_OBSERVED)
        self.assertEqual(outcome.verification_state, ExternalVerificationState.UNVERIFIED)
        self.assertTrue(outcome.executed)
        self.assertFalse(outcome.observed)
        self.assertFalse(outcome.verified)
        self.assertFalse(outcome.truth_established)

    def test_observation_does_not_become_verification(self):
        request = ToolRequest(
            tool_name="read_status",
            invocation_id="invoke-1",
        )
        outcome = ToolOutcomeService.classify(request, self._result())
        observed = ToolOutcomeService.observe(
            outcome,
            ExternalObservation(
                observation_id="observation-1",
                source="independent_status_reader",
                payload={"external_status": "ok"},
            ),
        )

        self.assertEqual(observed.observation_state, ExternalObservationState.OBSERVED)
        self.assertEqual(observed.verification_state, ExternalVerificationState.UNVERIFIED)
        self.assertTrue(observed.observed)
        self.assertFalse(observed.verified)
        self.assertFalse(observed.truth_established)

    def test_verification_requires_exact_observation_identity(self):
        request = ToolRequest(
            tool_name="read_status",
            invocation_id="invoke-1",
        )
        outcome = ToolOutcomeService.classify(request, self._result())
        observed = ToolOutcomeService.observe(
            outcome,
            ExternalObservation(
                observation_id="observation-1",
                source="independent_status_reader",
                payload={"external_status": "ok"},
            ),
        )

        with self.assertRaises(ValueError):
            ToolOutcomeService.verify(
                observed,
                ExternalVerification(
                    verification_id="verification-1",
                    observation_id="other-observation",
                    verifier="status_policy_check",
                    passed=True,
                ),
            )

        verified = ToolOutcomeService.verify(
            observed,
            ExternalVerification(
                verification_id="verification-1",
                observation_id="observation-1",
                verifier="status_policy_check",
                passed=True,
                evidence_refs=("observation-1",),
            ),
        )
        self.assertEqual(verified.verification_state, ExternalVerificationState.VERIFIED)
        self.assertTrue(verified.verified)
        self.assertFalse(verified.truth_established)

    def test_failed_handler_result_is_execution_failure_not_external_contradiction(self):
        request = ToolRequest(
            tool_name="read_status",
            invocation_id="invoke-1",
        )
        outcome = ToolOutcomeService.classify(
            request,
            self._result(success=False),
        )

        self.assertEqual(outcome.execution_state, ToolExecutionState.FAILED)
        self.assertEqual(outcome.observation_state, ExternalObservationState.NOT_OBSERVED)
        self.assertEqual(outcome.verification_state, ExternalVerificationState.UNVERIFIED)
        self.assertFalse(outcome.observed)
        self.assertFalse(outcome.verified)


class PlanExecutorOutcomeIntegrationTests(unittest.TestCase):
    def test_live_tool_step_surfaces_executed_observed_unverified_states(self):
        from src.core.tool_execution import ToolPlanStepHandler

        class Invoker:
            def invoke(self, request):
                return ToolResult(
                    success=True,
                    tool_name=request.tool_name,
                    content={"value": 42},
                    invocation_id=request.invocation_id,
                )

        plan = ExecutionPlan(
            plan_id="plan-outcome-1",
            task_description="Read status",
            steps=(
                PlanStep(
                    step_id="step-outcome-1",
                    description="Read status",
                    action="USE_TOOL",
                    order=0,
                    metadata={
                        "tool_name": "read_status",
                        "arguments": {},
                    },
                ),
            ),
        )
        policy = ExecutionPolicyResult(
            decision=PolicyDecision.ALLOW,
            plan=plan,
            issues=(),
        )
        execution = PlanExecutor(
            {
                "USE_TOOL": ToolPlanStepHandler(Invoker()),
            }
        ).execute(plan, policy)

        self.assertEqual(execution.status, PlanExecutionStatus.COMPLETED)
        context = execution.steps[0].metadata["tool_outcome"]
        self.assertEqual(context["execution_state"], "EXECUTED")
        self.assertEqual(context["observation_state"], "NOT_OBSERVED")
        self.assertEqual(context["verification_state"], "UNVERIFIED")
        self.assertFalse(context["truth_established"])

    def test_jarvis_response_surfaces_tool_outcome_without_claiming_verification(self):
        from src.ai.service import AIService
        from src.core.capability_argument_planner import CapabilityInvocationService
        from src.core.intelligent_request_router import IntelligentRequestRouter
        from src.core.jarvis import JARVIS
        from src.core.request_intent import IntentKind, RequestIntent
        from src.core.tool_execution import ToolCapabilityGateway

        class Classifier:
            def classify(self, text):
                return RequestIntent(
                    kind=IntentKind.TOOL,
                    content=text,
                    confidence=1.0,
                    reasoning="OPS-17 test",
                )

        class Planner:
            def propose(self, intent, capability):
                return {}

        class Gateway(ToolCapabilityGateway):
            def list_definitions(self):
                return (
                    ToolDefinition(
                        name="report_status",
                        description="Report runtime status",
                        version="1.0.0",
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        risk_level=RiskLevel.LOW,
                    ),
                )

            def invoke(self, request):
                return ToolResult(
                    success=True,
                    tool_name=request.tool_name,
                    content={"status": "ok"},
                    invocation_id=request.invocation_id,
                )

        jarvis = JARVIS(
            ai_service=AIService(default_provider="unused"),
            intelligent_request_router=IntelligentRequestRouter(Classifier()),
            tool_invoker=Gateway(),
            capability_invocation_service=CapabilityInvocationService(Planner()),
        )
        response = jarvis.ask("Report runtime status.")

        self.assertEqual(response.metadata["execution_status"], "COMPLETED")
        outcomes = response.metadata["tool_outcomes"]
        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0]["execution_state"], "EXECUTED")
        self.assertEqual(outcomes[0]["observation_state"], "NOT_OBSERVED")
        self.assertEqual(outcomes[0]["verification_state"], "UNVERIFIED")
        self.assertFalse(outcomes[0]["truth_established"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
