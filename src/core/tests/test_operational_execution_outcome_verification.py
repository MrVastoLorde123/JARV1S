"""OPS-17 acceptance tests for execution versus external outcome verification."""
from __future__ import annotations

import unittest

from src.ai.service import AIService
from src.core.capability_argument_planner import CapabilityInvocationService
from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_plan_models import ExecutionPlan, PlanStep
from src.core.execution_policy_models import ExecutionPolicyResult, PolicyDecision
from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.jarvis import JARVIS
from src.core.tool_execution import ToolCapabilityGateway, ToolPlanStepHandler
from src.core.request_intent import IntentKind, RequestIntent
from src.tools.models import RiskLevel, ToolRequest, ToolResult
from src.tools.outcome import (
    ExternalObservation,
    ExternalOutcomeState,
    ExternalVerification,
    ToolOutcomeService,
)


class StaticToolIntentClassifier:
    def classify(self, text):
        return RequestIntent(
            kind=IntentKind.TOOL,
            content=text,
            confidence=1.0,
            reasoning="OPS-17 semantic boundary fixture",
        )


class EmptyArgumentPlanner:
    def propose(self, intent, capability):
        return {}


class OutcomeGateway(ToolCapabilityGateway):
    def list_definitions(self):
        return (
            self.definition(),
        )

    @staticmethod
    def definition():
        from src.tools.models import ToolDefinition

        return ToolDefinition(
            name="report_status",
            description="Report runtime status.",
            version="1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            risk_level=RiskLevel.LOW,
        )

    def invoke(self, request):
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"status": "ok"},
            invocation_id=request.invocation_id,
        )


class OPS17OutcomeAggregationTests(unittest.TestCase):
    def _verified(self):
        request = ToolRequest(tool_name="report_status", invocation_id="invoke-1")
        raw = ToolOutcomeService.classify(
            request,
            ToolResult(
                success=True,
                tool_name="report_status",
                content={"status": "ok"},
                invocation_id="invoke-1",
            ),
        )
        observed = ToolOutcomeService.observe(
            raw,
            ExternalObservation(
                observation_id="obs-1",
                source="independent-reader",
                subject_ref=raw.target_ref,
                payload={"status": "ok"},
            ),
        )
        return ToolOutcomeService.verify(
            observed,
            ExternalVerification(
                verification_id="verification-1",
                observation_id="obs-1",
                verifier="independent-reader",
                passed=True,
            ),
        )

    def test_execution_success_is_not_verified(self):
        request = ToolRequest(tool_name="report_status", invocation_id="invoke-1")
        raw = ToolOutcomeService.classify(
            request,
            ToolResult(
                success=True,
                tool_name="report_status",
                content={"status": "ok"},
                invocation_id="invoke-1",
            ),
        )

        self.assertEqual(
            ToolOutcomeService.aggregate((raw,)),
            ExternalOutcomeState.EXECUTED_UNVERIFIED,
        )
        self.assertFalse(raw.verified)
        self.assertFalse(raw.truth_established)

    def test_observation_without_verification_is_explicitly_distinct(self):
        request = ToolRequest(tool_name="report_status", invocation_id="invoke-2")
        raw = ToolOutcomeService.classify(
            request,
            ToolResult(
                success=True,
                tool_name="report_status",
                content={"status": "ok"},
                invocation_id="invoke-2",
            ),
        )
        observed = ToolOutcomeService.observe(
            raw,
            ExternalObservation(
                observation_id="obs-2",
                source="independent-reader",
                subject_ref=raw.target_ref,
                payload={"status": "ok"},
            ),
        )

        self.assertEqual(
            ToolOutcomeService.aggregate((observed,)),
            ExternalOutcomeState.OBSERVED_UNVERIFIED,
        )
        self.assertFalse(observed.verified)

    def test_only_external_verification_reaches_verified_state(self):
        verified = self._verified()

        self.assertEqual(
            ToolOutcomeService.aggregate((verified,)),
            ExternalOutcomeState.VERIFIED,
        )
        self.assertTrue(verified.verified)
        self.assertFalse(verified.truth_established)

    def test_contradiction_dominates_aggregate_claim(self):
        verified = self._verified()
        request = ToolRequest(tool_name="report_status", invocation_id="invoke-3")
        raw = ToolOutcomeService.classify(
            request,
            ToolResult(
                success=True,
                tool_name="report_status",
                content={"status": "ok"},
                invocation_id="invoke-3",
            ),
        )
        observed = ToolOutcomeService.observe(
            raw,
            ExternalObservation(
                observation_id="obs-3",
                source="independent-reader",
                subject_ref=raw.target_ref,
                payload={"status": "different"},
            ),
        )
        contradicted = ToolOutcomeService.verify(
            observed,
            ExternalVerification(
                verification_id="verification-3",
                observation_id="obs-3",
                verifier="independent-reader",
                passed=False,
            ),
        )

        self.assertEqual(
            ToolOutcomeService.aggregate((verified, contradicted)),
            ExternalOutcomeState.CONTRADICTED,
        )


class OPS17LiveJARVISOutcomeTests(unittest.TestCase):
    def test_live_jarvis_does_not_describe_handler_success_as_external_verification(self):
        jarvis = JARVIS(
            ai_service=AIService(default_provider="unused"),
            intelligent_request_router=IntelligentRequestRouter(
                StaticToolIntentClassifier()
            ),
            tool_invoker=OutcomeGateway(),
            capability_invocation_service=CapabilityInvocationService(
                EmptyArgumentPlanner()
            ),
        )

        response = jarvis.ask("Report runtime status.")

        self.assertEqual(
            response.metadata["execution_status"],
            PlanExecutionStatus.COMPLETED.value,
        )
        self.assertEqual(
            response.metadata["external_outcome_state"],
            ExternalOutcomeState.EXECUTED_UNVERIFIED.value,
        )
        self.assertFalse(response.metadata["external_outcome_verified"])
        self.assertFalse(response.metadata["truth_established"])
        self.assertIn("external outcome is not verified", response.content.lower())


class OPS17PlanExecutorOutcomeTests(unittest.TestCase):
    def test_plan_executor_preserves_the_semantic_outcome_context(self):
        class Invoker:
            def invoke(self, request):
                return ToolResult(
                    success=True,
                    tool_name=request.tool_name,
                    content={"value": 42},
                    invocation_id=request.invocation_id,
                )

        plan = ExecutionPlan(
            plan_id="ops-17-plan",
            task_description="Report status",
            steps=(
                PlanStep(
                    step_id="ops-17-step",
                    description="Report status",
                    action="USE_TOOL",
                    order=0,
                    metadata={
                        "tool_name": "report_status",
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

        execution = __import__(
            "src.core.plan_executor",
            fromlist=["PlanExecutor"],
        ).PlanExecutor(
            {"USE_TOOL": ToolPlanStepHandler(Invoker())}
        ).execute(plan, policy)

        self.assertEqual(
            execution.steps[0].metadata["tool_outcome"]["external_outcome_state"],
            ExternalOutcomeState.EXECUTED_UNVERIFIED.value,
        )
        self.assertFalse(
            execution.steps[0].metadata["tool_outcome"]["truth_established"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
