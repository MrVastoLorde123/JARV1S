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
    VerificationFreshnessState,
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
                subject_ref=outcome.target_ref,
                payload={"external_status": "ok"},
            ),
        )

        self.assertEqual(observed.observation_state, ExternalObservationState.OBSERVED)
        self.assertEqual(observed.verification_state, ExternalVerificationState.UNVERIFIED)
        self.assertTrue(observed.observed)
        self.assertFalse(observed.verified)
        self.assertFalse(observed.truth_established)

    def test_verification_rejects_unrelated_observation_target(self):
        request = ToolRequest(
            tool_name="read_status",
            invocation_id="invoke-1",
            arguments={"host": "10.0.0.1"},
        )
        outcome = ToolOutcomeService.classify(request, self._result())
        unrelated = ToolOutcomeService.observe(
            outcome,
            ExternalObservation(
                observation_id="observation-unrelated",
                source="independent_status_reader",
                subject_ref="tool-target-unrelated",
                payload={"external_status": "ok"},
            ),
        )

        with self.assertRaises(ValueError):
            ToolOutcomeService.verify(
                unrelated,
                ExternalVerification(
                    verification_id="verification-unrelated",
                    observation_id="observation-unrelated",
                    verifier="status_policy_check",
                    passed=True,
                ),
            )

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
                subject_ref=outcome.target_ref,
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

    def test_verified_observation_can_be_fresh(self):
        request = ToolRequest(
            tool_name="read_status",
            invocation_id="invoke-fresh",
        )
        outcome = ToolOutcomeService.classify(request, self._result(invocation_id="invoke-fresh"))
        observed = ToolOutcomeService.observe(
            outcome,
            ExternalObservation(
                observation_id="observation-fresh",
                source="independent_status_reader",
                subject_ref=outcome.target_ref,
                payload={"external_status": "ok"},
                observed_at="2026-09-19T01:00:00+00:00",
            ),
        )
        verified = ToolOutcomeService.verify(
            observed,
            ExternalVerification(
                verification_id="verification-fresh",
                observation_id="observation-fresh",
                verifier="status_policy_check",
                passed=True,
            ),
        )

        fresh = ToolOutcomeService.assess_freshness(
            verified,
            as_of="2026-09-19T01:00:30+00:00",
            max_age_seconds=60,
        )

        self.assertEqual(fresh.verification_state, ExternalVerificationState.VERIFIED)
        self.assertEqual(fresh.freshness_state, VerificationFreshnessState.FRESH)
        self.assertTrue(fresh.verified)
        self.assertFalse(fresh.truth_established)

    def test_verified_observation_can_be_stale_without_becoming_false(self):
        request = ToolRequest(
            tool_name="read_status",
            invocation_id="invoke-stale",
        )
        outcome = ToolOutcomeService.classify(request, self._result(invocation_id="invoke-stale"))
        observed = ToolOutcomeService.observe(
            outcome,
            ExternalObservation(
                observation_id="observation-stale",
                source="independent_status_reader",
                subject_ref=outcome.target_ref,
                payload={"external_status": "ok"},
                observed_at="2026-09-18T23:00:00+00:00",
            ),
        )
        verified = ToolOutcomeService.verify(
            observed,
            ExternalVerification(
                verification_id="verification-stale",
                observation_id="observation-stale",
                verifier="status_policy_check",
                passed=True,
            ),
        )

        stale = ToolOutcomeService.assess_freshness(
            verified,
            as_of="2026-09-19T01:00:00+00:00",
            max_age_seconds=60,
        )

        self.assertEqual(stale.verification_state, ExternalVerificationState.VERIFIED)
        self.assertEqual(stale.freshness_state, VerificationFreshnessState.STALE)
        self.assertTrue(stale.verified)
        self.assertFalse(stale.truth_established)

    def test_missing_or_future_observation_timestamp_is_unknown_freshness(self):
        request = ToolRequest(
            tool_name="read_status",
            invocation_id="invoke-unknown",
        )
        outcome = ToolOutcomeService.classify(
            request,
            self._result(invocation_id="invoke-unknown"),
        )
        observed = ToolOutcomeService.observe(
            outcome,
            ExternalObservation(
                observation_id="observation-unknown",
                source="independent_status_reader",
                subject_ref=outcome.target_ref,
                payload={"external_status": "ok"},
            ),
        )
        verified = ToolOutcomeService.verify(
            observed,
            ExternalVerification(
                verification_id="verification-unknown",
                observation_id="observation-unknown",
                verifier="status_policy_check",
                passed=True,
            ),
        )

        unknown = ToolOutcomeService.assess_freshness(
            verified,
            as_of="2026-09-19T01:00:00+00:00",
            max_age_seconds=60,
        )
        self.assertEqual(unknown.freshness_state, VerificationFreshnessState.UNKNOWN)

        future_observed = ToolOutcomeService.observe(
            outcome,
            ExternalObservation(
                observation_id="observation-future",
                source="independent_status_reader",
                subject_ref=outcome.target_ref,
                payload={"external_status": "ok"},
                observed_at="2026-09-19T02:00:00+00:00",
            ),
        )
        future_verified = ToolOutcomeService.verify(
            future_observed,
            ExternalVerification(
                verification_id="verification-future",
                observation_id="observation-future",
                verifier="status_policy_check",
                passed=True,
            ),
        )
        future = ToolOutcomeService.assess_freshness(
            future_verified,
            as_of="2026-09-19T01:00:00+00:00",
            max_age_seconds=60,
        )
        self.assertEqual(future.freshness_state, VerificationFreshnessState.UNKNOWN)


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

    def test_untyped_handler_cannot_inject_verification_evidence(self):
        class ForgedOutcomeHandler:
            def __call__(self, step):
                return {"status": "ok"}

            def outcome_context(self):
                return {
                    "execution_state": "EXECUTED",
                    "observation_state": "OBSERVED",
                    "verification_state": "VERIFIED",
                    "verified": True,
                    "truth_established": False,
                }

        plan = ExecutionPlan(
            plan_id="plan-forged-outcome",
            task_description="Run an untrusted handler",
            steps=(
                PlanStep(
                    step_id="step-forged-outcome",
                    description="Run an untrusted handler",
                    action="FORGED",
                    order=0,
                ),
            ),
        )
        policy = ExecutionPolicyResult(
            decision=PolicyDecision.ALLOW,
            plan=plan,
            issues=(),
        )

        execution = PlanExecutor(
            {"FORGED": ForgedOutcomeHandler()}
        ).execute(plan, policy)

        self.assertEqual(execution.status, PlanExecutionStatus.COMPLETED)
        self.assertNotIn("tool_outcome", execution.steps[0].metadata)

    def test_failed_new_tool_step_cannot_reuse_previous_outcome(self):
        class Invoker:
            def invoke(self, request):
                return ToolResult(
                    success=True,
                    tool_name=request.tool_name,
                    content={"value": 1},
                    invocation_id=request.invocation_id,
                )

        handler = __import__(
            "src.core.tool_execution",
            fromlist=["ToolPlanStepHandler"],
        ).ToolPlanStepHandler(Invoker())

        plan = ExecutionPlan(
            plan_id="plan-stale-outcome",
            task_description="Do two tool steps",
            steps=(
                PlanStep(
                    step_id="step-valid",
                    description="Valid tool invocation",
                    action="USE_TOOL",
                    order=0,
                    metadata={
                        "tool_name": "read_status",
                        "arguments": {},
                    },
                ),
                PlanStep(
                    step_id="step-invalid",
                    description="Invalid tool invocation",
                    action="USE_TOOL",
                    order=1,
                    metadata={
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

        execution = PlanExecutor({"USE_TOOL": handler}).execute(plan, policy)

        self.assertEqual(execution.status, PlanExecutionStatus.FAILED)
        self.assertIn("tool_outcome", execution.steps[0].metadata)
        self.assertNotIn("tool_outcome", execution.steps[1].metadata)
        self.assertIn("tool plan step requires a non-empty 'tool_name'", execution.steps[1].error)

    def test_concurrent_tool_invocations_keep_outcomes_thread_local(self):
        import threading

        from src.core.tool_execution import ToolPlanStepHandler

        class Invoker:
            def invoke(self, request):
                return ToolResult(
                    success=True,
                    tool_name=request.tool_name,
                    content={"tool": request.tool_name},
                    invocation_id=request.invocation_id,
                )

        handler = ToolPlanStepHandler(Invoker())
        step_a = PlanStep(
            step_id="step-a",
            description="Read A",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": "read_a",
                "arguments": {},
            },
        )
        step_b = PlanStep(
            step_id="step-b",
            description="Read B",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": "read_b",
                "arguments": {},
            },
        )

        first_ready = threading.Event()
        release_first = threading.Event()
        observed = {}

        def first_worker():
            handler.invoke(step_a)
            first_ready.set()
            release_first.wait(timeout=2)
            outcome = handler.outcome_context()
            observed["first"] = None if outcome is None else outcome.tool_name

        def second_worker():
            first_ready.wait(timeout=2)
            handler.invoke(step_b)
            outcome = handler.outcome_context()
            observed["second"] = None if outcome is None else outcome.tool_name
            release_first.set()

        thread_a = threading.Thread(target=first_worker)
        thread_b = threading.Thread(target=second_worker)
        thread_a.start()
        thread_b.start()
        thread_a.join(timeout=3)
        thread_b.join(timeout=3)

        self.assertFalse(thread_a.is_alive())
        self.assertFalse(thread_b.is_alive())
        self.assertEqual(observed["first"], "read_a")
        self.assertEqual(observed["second"], "read_b")

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
