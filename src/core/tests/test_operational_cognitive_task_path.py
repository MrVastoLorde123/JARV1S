import unittest
from datetime import datetime, timezone

from src.ai.service import AIService
from src.core.capability_argument_planner import CapabilityInvocationService
from src.core.canonical_cognitive_runtime import CanonicalCognitiveRuntime
from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.jarvis import JARVIS
from src.core.request_intent import IntentKind, RequestIntent
from src.core.tool_execution import ToolCapabilityGateway
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult


class StaticTaskIntentClassifier:
    def classify(self, text):
        return RequestIntent(
            kind=IntentKind.TOOL,
            content=text,
            confidence=0.99,
            reasoning="deterministic operational cognition test fixture",
        )


class EmptyArgumentPlanner:
    def propose(self, intent, capability):
        return {}


class CognitiveOperationalToolGateway(ToolCapabilityGateway):
    def __init__(self):
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
        self.requests = []

    def list_definitions(self):
        return self.definitions

    def invoke(self, request: ToolRequest):
        self.requests.append(request)
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"status": "cognitive-operational-test-ok"},
            invocation_id=request.invocation_id,
        )


class StaticActionIntentClassifier:
    def classify(self, text):
        return RequestIntent(
            kind=IntentKind.TASK,
            content=text,
            confidence=0.99,
            reasoning="deterministic operational action fixture",
        )


class OperationalCognitiveTaskPathTests(unittest.TestCase):
    def test_cognition_feeds_the_live_execution_plan_without_authorizing_execution(self):
        gateway = CognitiveOperationalToolGateway()
        cognition = CanonicalCognitiveRuntime(
            clock=lambda: datetime(2026, 9, 18, 14, 0, tzinfo=timezone.utc),
        )
        router = IntelligentRequestRouter(StaticTaskIntentClassifier())
        jarvis = JARVIS(
            ai_service=AIService(default_provider="unused"),
            intelligent_request_router=router,
            cognitive_runtime=cognition,
            tool_invoker=gateway,
            capability_invocation_service=CapabilityInvocationService(
                EmptyArgumentPlanner(),
            ),
        )

        response = jarvis.ask("Report the current runtime status.")

        self.assertEqual(response.metadata["route"], "TASK")
        self.assertEqual(response.metadata["stage"], "EXECUTION")
        self.assertEqual(response.metadata["execution_status"], "COMPLETED")
        self.assertEqual(response.metadata["capability"], "report_status")
        self.assertEqual(len(gateway.requests), 1)

        cognitive_context = response.metadata["cognitive_context"]
        self.assertEqual(cognitive_context["status"], "COMPLETED")
        self.assertIsNotNone(cognitive_context["goal"]["goal_id"])
        self.assertIsNotNone(cognitive_context["selected_plan"]["plan_id"])
        self.assertIsNotNone(cognitive_context["proposal"]["proposal_id"])
        self.assertFalse(cognitive_context["authority_granted"])
        self.assertFalse(cognitive_context["authorization_granted"])
        self.assertFalse(cognitive_context["execution_requested"])

        execution_context = response.metadata["execution_plan_cognitive_context"]
        self.assertEqual(
            execution_context["selected_plan"]["plan_id"],
            cognitive_context["selected_plan"]["plan_id"],
        )
        self.assertFalse(execution_context["authorization_granted"])
        self.assertFalse(execution_context["execution_requested"])

    def test_planned_action_is_realized_through_existing_capability_stack(self):
        gateway = CognitiveOperationalToolGateway()
        cognition = CanonicalCognitiveRuntime(
            clock=lambda: datetime(2026, 9, 18, 14, 0, tzinfo=timezone.utc),
        )
        router = IntelligentRequestRouter(StaticActionIntentClassifier())
        jarvis = JARVIS(
            ai_service=AIService(default_provider="unused"),
            intelligent_request_router=router,
            cognitive_runtime=cognition,
            tool_invoker=gateway,
            capability_invocation_service=CapabilityInvocationService(
                EmptyArgumentPlanner(),
            ),
        )

        response = jarvis.ask("Report the current runtime status.")

        self.assertEqual(response.metadata["route"], "TASK")
        self.assertEqual(response.metadata["stage"], "EXECUTION")
        self.assertEqual(response.metadata["capability"], "report_status")
        self.assertTrue(response.metadata["capability_realized"])
        self.assertEqual(
            response.metadata["capability_query"],
            "Report the current runtime status.",
        )
        self.assertEqual(len(gateway.requests), 1)

        cognitive_context = response.metadata["cognitive_context"]
        self.assertEqual(
            cognitive_context["goal"]["desired_outcome"],
            response.metadata["capability_query"],
        )
        self.assertFalse(cognitive_context["authorization_granted"])

    def test_planned_action_without_capability_stops_before_execution(self):
        gateway = CognitiveOperationalToolGateway()
        cognition = CanonicalCognitiveRuntime(
            clock=lambda: datetime(2026, 9, 18, 14, 0, tzinfo=timezone.utc),
        )
        router = IntelligentRequestRouter(StaticActionIntentClassifier())
        jarvis = JARVIS(
            ai_service=AIService(default_provider="unused"),
            intelligent_request_router=router,
            cognitive_runtime=cognition,
            tool_invoker=gateway,
            capability_invocation_service=CapabilityInvocationService(
                EmptyArgumentPlanner(),
            ),
        )

        response = jarvis.ask("Deploy the production database.")

        self.assertEqual(response.metadata["route"], "TASK")
        self.assertEqual(response.metadata["stage"], "CAPABILITY_SELECTION")
        self.assertFalse(response.metadata["success"])
        self.assertEqual(len(gateway.requests), 0)
        self.assertFalse(response.metadata["cognitive_context"]["authorization_granted"])

    def test_cognition_failure_does_not_become_execution_authority(self):
        class FailingCognitiveRuntime:
            def run(self, query, **kwargs):
                raise RuntimeError("cognition unavailable")

        gateway = CognitiveOperationalToolGateway()
        router = IntelligentRequestRouter(StaticTaskIntentClassifier())
        jarvis = JARVIS(
            ai_service=AIService(default_provider="unused"),
            intelligent_request_router=router,
            cognitive_runtime=FailingCognitiveRuntime(),
            tool_invoker=gateway,
            capability_invocation_service=CapabilityInvocationService(
                EmptyArgumentPlanner(),
            ),
        )

        response = jarvis.ask("Report the current runtime status.")

        self.assertEqual(response.metadata["execution_status"], "COMPLETED")
        self.assertEqual(len(gateway.requests), 1)
        self.assertEqual(
            response.metadata["cognitive_context"]["status"],
            "UNAVAILABLE",
        )
        self.assertFalse(response.metadata["cognitive_context"]["authorization_granted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
