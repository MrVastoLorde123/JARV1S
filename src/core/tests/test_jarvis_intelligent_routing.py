import unittest
from unittest.mock import Mock

from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.jarvis import JARVIS
from src.core.models import JARVISResponse
from src.core.request_intent import IntentKind, RequestIntent
from src.core.task_models import RequestType, RouteDecision, TaskRequest, TaskType


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

    def test_natural_language_tool_enters_existing_task_pipeline(self):
        jarvis = self._build_jarvis(
            RequestIntent(
                IntentKind.TOOL,
                "Find the planner file",
                confidence=0.91,
            )
        )

        expected_task = TaskRequest(
            content="Find the planner file",
            task_type=TaskType.TOOL,
        )
        jarvis._handle_task = Mock(
            return_value=JARVISResponse(
                content="tool handled",
                ai_response=None,
                context=None,
                metadata={},
            )
        )

        response = jarvis.ask("Find the planner file")

        jarvis._handle_task.assert_called_once_with(expected_task)
        self.assertEqual("tool handled", response.content)
        self.assertEqual("tool", response.metadata["intent_kind"])
        self.assertEqual(0.91, response.metadata["intent_confidence"])

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
