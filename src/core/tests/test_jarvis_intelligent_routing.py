import unittest
from unittest.mock import Mock

from src.core.capability_realization import CapabilityRealization
from src.core.capability_selection import CapabilityCandidate, CapabilitySelection
from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.jarvis import JARVIS
from src.core.models import JARVISResponse
from src.core.request_intent import IntentKind, RequestIntent
from src.core.task_models import TaskRequest, TaskType
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest


class FakeClassifier:
    def __init__(self, intent):
        self.intent = intent

    def classify(self, text):
        return self.intent


class JARVISIntelligentRoutingTests(unittest.TestCase):
    def _build_jarvis(self, intent):
        classifier = FakeClassifier(intent)
        intelligent_router = IntelligentRequestRouter(classifier)
        jarvis = JARVIS(
            ai_service=Mock(),
            intelligent_request_router=intelligent_router,
        )
        return jarvis

    @staticmethod
    def _realization(tool_name="read_file", arguments=None):
        definition = ToolDefinition(
            name=tool_name,
            description="Read a file",
            version="1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "string"},
            risk_level=RiskLevel.LOW,
        )
        candidate = CapabilityCandidate(
            capability=definition,
            score=4.0,
            reason="matched",
        )
        return CapabilityRealization(
            intent="Find the planner file",
            selection=CapabilitySelection(
                query="Find the planner file",
                candidates=(candidate,),
            ),
            candidate=candidate,
            request=ToolRequest(
                tool_name=tool_name,
                arguments=arguments or {},
            ),
        )

    def test_natural_language_task_enters_existing_task_pipeline(self):
        jarvis = self._build_jarvis(
            RequestIntent(
                IntentKind.TASK,
                "Refactor the planner",
                confidence=0.95,
            )
        )

        expected_task = TaskRequest(
            content="Refactor the planner",
            task_type=TaskType.ACTION,
        )
        jarvis._handle_task = Mock(
            return_value=JARVISResponse(
                content="task handled",
                ai_response=None,
                context=None,
                metadata={},
            )
        )

        response = jarvis.ask("Refactor the planner")

        jarvis._handle_task.assert_called_once_with(expected_task)
        self.assertEqual("task handled", response.content)
        self.assertEqual("task", response.metadata["intent_kind"])
        self.assertEqual(0.95, response.metadata["intent_confidence"])

    def test_natural_language_tool_is_realized_before_task_pipeline(self):
        jarvis = self._build_jarvis(
            RequestIntent(
                IntentKind.TOOL,
                "Find the planner file",
                confidence=0.91,
            )
        )
        realization_service = Mock()
        realization_service.realize.return_value = self._realization(
            arguments={"path": "src/core/execution_planner.py"}
        )
        jarvis.capability_realization_service = realization_service
        jarvis._handle_task = Mock(
            return_value=JARVISResponse(
                content="tool handled",
                ai_response=None,
                context=None,
                metadata={},
            )
        )

        response = jarvis.ask("Find the planner file")

        expected_task = TaskRequest(
            content="Find the planner file",
            task_type=TaskType.TOOL,
            metadata={
                "tool_name": "read_file",
                "arguments": {"path": "src/core/execution_planner.py"},
            },
        )
        realization_service.realize.assert_called_once_with("Find the planner file")
        jarvis._handle_task.assert_called_once_with(expected_task)
        self.assertTrue(response.metadata["capability_realized"])
        self.assertEqual("read_file", response.metadata["capability"])
        self.assertEqual("tool", response.metadata["intent_kind"])
        self.assertEqual(0.91, response.metadata["intent_confidence"])

    def test_realization_failure_stops_before_task_pipeline(self):
        jarvis = self._build_jarvis(
            RequestIntent(
                IntentKind.TOOL,
                "Find the planner file",
                confidence=0.91,
            )
        )
        realization_service = Mock()
        realization_service.realize.side_effect = LookupError("no match")
        jarvis.capability_realization_service = realization_service
        jarvis._handle_task = Mock()

        response = jarvis.ask("Find the planner file")

        realization_service.realize.assert_called_once_with("Find the planner file")
        jarvis._handle_task.assert_not_called()
        self.assertEqual("CAPABILITY_SELECTION", response.metadata["stage"])
        self.assertFalse(response.metadata["success"])

    def test_existing_explicit_tool_task_does_not_re_realize(self):
        jarvis = self._build_jarvis(
            RequestIntent(
                IntentKind.TOOL,
                "unused",
            )
        )
        realization_service = Mock()
        jarvis.capability_realization_service = realization_service
        jarvis._handle_task = Mock(
            return_value=JARVISResponse(
                content="tool handled",
                ai_response=None,
                context={},
                metadata={},
            )
        )

        # The intelligent router normally creates the first TOOL task without
        # tool metadata. This test keeps the guard explicit at the task seam.
        router = Mock()
        router.route.return_value = Mock(
            request_type=type("RequestTypeValue", (), {"value": "TASK"})(),
            original_input="explicit",
            task=TaskRequest(
                content="explicit tool call",
                task_type=TaskType.TOOL,
                metadata={"tool_name": "read_file", "arguments": {"path": "x"}},
            ),
            metadata={"intent_kind": "tool"},
        )
        jarvis.intelligent_request_router = router

        response = jarvis.ask("explicit tool call")

        realization_service.realize.assert_not_called()
        jarvis._handle_task.assert_called_once_with(
            TaskRequest(
                content="explicit tool call",
                task_type=TaskType.TOOL,
                metadata={"tool_name": "read_file", "arguments": {"path": "x"}},
            )
        )
        self.assertEqual("tool handled", response.content)

    def test_existing_command_route_stays_on_command_path(self):
        jarvis = self._build_jarvis(
            RequestIntent(
                IntentKind.TASK,
                "must not be used",
            )
        )

        jarvis._handle_command = Mock(
            return_value=JARVISResponse(
                content="command handled",
                ai_response=None,
                context=None,
                metadata={},
            )
        )
        jarvis._handle_task = Mock()

        response = jarvis.ask("/HELP")

        jarvis._handle_command.assert_called_once_with("/HELP")
        jarvis._handle_task.assert_not_called()
        self.assertEqual("command handled", response.content)

    def test_conversation_route_stays_on_conversation_path(self):
        jarvis = self._build_jarvis(
            RequestIntent(
                IntentKind.QUESTION,
                "What is JARVIS?",
                confidence=0.88,
            )
        )

        jarvis._handle_conversation = Mock(
            return_value=JARVISResponse(
                content="conversation handled",
                ai_response=None,
                context=None,
                metadata={},
            )
        )
        jarvis._handle_task = Mock()

        response = jarvis.ask("What is JARVIS?")

        jarvis._handle_conversation.assert_called_once()
        jarvis._handle_task.assert_not_called()
        self.assertEqual("conversation handled", response.content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
