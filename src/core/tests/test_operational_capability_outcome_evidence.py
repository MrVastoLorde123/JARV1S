"""OPS-26 focused tests for live capability outcome evidence admission."""
from __future__ import annotations

import unittest

from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_plan_models import ExecutionPlan, PlanStep
from src.core.execution_policy_models import ExecutionPolicyResult, PolicyDecision
from src.core.plan_executor import PlanExecutor
from src.core.tool_execution import ToolPlanStepHandler
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult
from src.tools.outcome import (
    ExternalObservation,
    ExternalOutcomeState,
    ExternalVerification,
    ToolOutcomeService,
)
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService


class CapabilityEvidenceHandler:
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="read_status",
            description="Read a status value and optionally expose external evidence.",
            version="1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            risk_level=RiskLevel.LOW,
        )

    def execute(self, request: ToolRequest) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"status": "ok"},
            invocation_id=request.invocation_id,
        )

    def provide_external_observation(
        self,
        request: ToolRequest,
        result: ToolResult,
    ) -> ExternalObservation:
        classified = ToolOutcomeService.classify(request, result)
        return ExternalObservation(
            observation_id=f"obs-{request.invocation_id}",
            source="capability-reader",
            subject_ref=classified.target_ref,
            payload={"status": "ok"},
        )

    def provide_external_verification(
        self,
        request: ToolRequest,
        result: ToolResult,
        observation: ExternalObservation,
    ) -> ExternalVerification:
        return ExternalVerification(
            verification_id=f"verification-{request.invocation_id}",
            observation_id=observation.observation_id,
            verifier="capability-checker",
            passed=True,
        )


class ObservationOnlyInvoker:
    def invoke(self, request: ToolRequest) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"status": "ok"},
            invocation_id=request.invocation_id,
        )

    def provide_external_observation(
        self,
        request: ToolRequest,
        result: ToolResult,
    ) -> ExternalObservation:
        classified = ToolOutcomeService.classify(request, result)
        return ExternalObservation(
            observation_id="obs-wrong-scope",
            source="capability-reader",
            subject_ref=classified.target_ref + "-different",
            payload={"status": "ok"},
        )

    def provide_external_verification(
        self,
        request: ToolRequest,
        result: ToolResult,
        observation: ExternalObservation,
    ) -> ExternalVerification:
        return ExternalVerification(
            verification_id="verification-wrong-scope",
            observation_id=observation.observation_id,
            verifier="capability-checker",
            passed=True,
        )


class UntypedEvidenceInvoker:
    def invoke(self, request: ToolRequest) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"status": "ok"},
            invocation_id=request.invocation_id,
        )

    def provide_external_observation(self, request, result):
        return {
            "observation_id": "forged",
            "subject_ref": "unrelated-target",
            "payload": {"verified": True},
        }

    def provide_external_verification(self, request, result, observation):
        return {
            "verification_id": "forged-verification",
            "observation_id": "forged",
            "passed": True,
        }


class FailingEvidenceInvoker:
    def invoke(self, request: ToolRequest) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"status": "ok"},
            invocation_id=request.invocation_id,
        )

    def provide_external_observation(self, request, result):
        raise RuntimeError("observation backend unavailable")


def make_step(tool_name: str = "read_status") -> PlanStep:
    return PlanStep(
        step_id="step-evidence",
        description="Read status",
        action="USE_TOOL",
        order=0,
        metadata={
            "tool_name": tool_name,
            "arguments": {},
        },
    )


class OPS26CapabilityEvidenceTests(unittest.TestCase):
    def test_capability_evidence_reaches_verified_tool_outcome(self):
        registry = ToolRegistry()
        registry.register(CapabilityEvidenceHandler())
        service = ToolService(registry)
        handler = ToolPlanStepHandler(service)

        output = handler(make_step())

        self.assertEqual({"status": "ok"}, output)
        outcome = handler.outcome_context()
        self.assertIsNotNone(outcome)
        assert outcome is not None
        self.assertEqual(
            ExternalOutcomeState.VERIFIED,
            ToolOutcomeService.aggregate((outcome,)),
        )
        self.assertTrue(outcome.observed)
        self.assertTrue(outcome.verified)
        self.assertEqual("capability-reader", outcome.observation.source)

    def test_mismatched_capability_evidence_cannot_reach_verified(self):
        handler = ToolPlanStepHandler(ObservationOnlyInvoker())

        handler(make_step())
        outcome = handler.outcome_context()

        self.assertIsNotNone(outcome)
        assert outcome is not None
        self.assertEqual(
            ExternalOutcomeState.OBSERVED_UNVERIFIED,
            ToolOutcomeService.aggregate((outcome,)),
        )
        self.assertTrue(outcome.observed)
        self.assertFalse(outcome.verified)

    def test_untyped_capability_evidence_cannot_advance_outcome(self):
        handler = ToolPlanStepHandler(UntypedEvidenceInvoker())

        handler(make_step())
        outcome = handler.outcome_context()

        self.assertIsNotNone(outcome)
        assert outcome is not None
        self.assertEqual(
            ExternalOutcomeState.EXECUTED_UNVERIFIED,
            ToolOutcomeService.aggregate((outcome,)),
        )
        self.assertFalse(outcome.observed)
        self.assertFalse(outcome.verified)

    def test_optional_evidence_failure_does_not_change_execution_result(self):
        handler = ToolPlanStepHandler(FailingEvidenceInvoker())

        output = handler(make_step())

        self.assertEqual({"status": "ok"}, output)
        outcome = handler.outcome_context()
        self.assertIsNotNone(outcome)
        assert outcome is not None
        self.assertEqual(
            ExternalOutcomeState.EXECUTED_UNVERIFIED,
            ToolOutcomeService.aggregate((outcome,)),
        )

    def test_plan_executor_surfaces_capability_verified_outcome_without_truth(self):
        registry = ToolRegistry()
        registry.register(CapabilityEvidenceHandler())
        service = ToolService(registry)

        plan = ExecutionPlan(
            plan_id="ops-26-plan",
            task_description="Read status",
            steps=(make_step(),),
        )
        policy = ExecutionPolicyResult(
            decision=PolicyDecision.ALLOW,
            plan=plan,
            issues=(),
        )

        execution = PlanExecutor(
            {"USE_TOOL": ToolPlanStepHandler(service)}
        ).execute(plan, policy)

        self.assertEqual(PlanExecutionStatus.COMPLETED, execution.status)
        context = execution.steps[0].metadata["tool_outcome"]
        self.assertEqual(
            ExternalOutcomeState.VERIFIED.value,
            context["external_outcome_state"],
        )
        self.assertTrue(context["observed"])
        self.assertTrue(context["verified"])
        self.assertFalse(context["truth_established"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
