import unittest

from src.ai.service import AIService
from src.core.capability_argument_planner import CapabilityArgumentPlanner, CapabilityInvocationService
from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.jarvis import JARVIS
from src.core.request_intent import IntentKind, RequestIntent
from src.core.tool_execution import ToolCapabilityGateway
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult


class StaticIntentClassifier:
    def classify(self, text):
        return RequestIntent(
            kind=IntentKind.TOOL,
            content=text,
            confidence=0.99,
            reasoning="deterministic operational test fixture",
        )


class EmptyArgumentPlanner:
    def propose(self, intent, capability):
        return {}


class OperationalToolGateway(ToolCapabilityGateway):
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
            content={"status": "operational-test-ok"},
            invocation_id=request.invocation_id,
        )


class OperationalNaturalLanguageToolPathTests(unittest.TestCase):
    def test_plain_language_tool_request_reaches_existing_execution_path(self):
        gateway = OperationalToolGateway()
        invocation_service = CapabilityInvocationService(
            EmptyArgumentPlanner(),
        )
        router = IntelligentRequestRouter(StaticIntentClassifier())
        jarvis = JARVIS(
            ai_service=AIService(default_provider="unused"),
            intelligent_request_router=router,
            tool_invoker=gateway,
            capability_invocation_service=invocation_service,
        )

        response = jarvis.ask("Report the current runtime status.")

        self.assertEqual(response.metadata["route"], "TASK")
        self.assertEqual(response.metadata["stage"], "EXECUTION")
        self.assertEqual(response.metadata["capability"], "report_status")
        self.assertEqual(response.metadata["execution_status"], "COMPLETED")
        self.assertEqual(len(gateway.requests), 1)
        self.assertEqual(gateway.requests[0].tool_name, "report_status")
        self.assertEqual(response.metadata["execution_outputs"], ({"status": "operational-test-ok"},))


if __name__ == "__main__":
    unittest.main(verbosity=2)
