import unittest

from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.request_intent import IntentKind, RequestIntent
from src.core.task_models import RequestType, TaskType


class FakeClassifier:
    def __init__(self, intent):
        self.intent = intent
        self.calls = []

    def classify(self, text):
        self.calls.append(text)
        return self.intent


class IntelligentRequestRouterTests(unittest.TestCase):
    def test_question_remains_conversation_with_intent_metadata(self):
        classifier = FakeClassifier(RequestIntent(IntentKind.QUESTION, "What is JARVIS?", confidence=0.9))
        router = IntelligentRequestRouter(classifier)
        result = router.route("What is JARVIS?")
        self.assertEqual(RequestType.CONVERSATION, result.request_type)
        self.assertEqual("question", result.metadata["intent_kind"])
        self.assertEqual(0.9, result.metadata["intent_confidence"])

    def test_task_becomes_explicit_task_request(self):
        classifier = FakeClassifier(RequestIntent(IntentKind.TASK, "Refactor the planner"))
        router = IntelligentRequestRouter(classifier)
        result = router.route("Refactor the planner")
        self.assertEqual(RequestType.TASK, result.request_type)
        self.assertEqual(TaskType.ACTION, result.task.task_type)
        self.assertEqual("Refactor the planner", result.task.content)

    def test_tool_becomes_tool_task(self):
        classifier = FakeClassifier(RequestIntent(IntentKind.TOOL, "Find the planner file"))
        router = IntelligentRequestRouter(classifier)
        result = router.route("Find the planner file")
        self.assertEqual(RequestType.TASK, result.request_type)
        self.assertEqual(TaskType.TOOL, result.task.task_type)

    def test_explicit_command_bypasses_classifier(self):
        classifier = FakeClassifier(RequestIntent(IntentKind.TASK, "never used"))
        router = IntelligentRequestRouter(classifier)
        result = router.route("/HELP")
        self.assertEqual(RequestType.COMMAND, result.request_type)
        self.assertEqual([], classifier.calls)

    def test_non_string_input_is_rejected(self):
        classifier = FakeClassifier(RequestIntent(IntentKind.CONVERSATION, "hello"))
        router = IntelligentRequestRouter(classifier)
        with self.assertRaises(TypeError):
            router.route(None)

    def test_empty_input_is_rejected(self):
        classifier = FakeClassifier(RequestIntent(IntentKind.CONVERSATION, "hello"))
        router = IntelligentRequestRouter(classifier)
        with self.assertRaises(ValueError):
            router.route(" ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
