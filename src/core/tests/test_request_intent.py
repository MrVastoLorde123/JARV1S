import json
import unittest

from src.ai.models import AICapabilities, AIResponse
from src.ai.service import AIService
from src.core.request_intent import AIRequestIntentClassifier, IntentKind, RequestIntent, RequestIntentClassifier


class FakeAIProvider:
    def __init__(self, content):
        self.content = content

    def provider_name(self):
        return "fake"

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def generate(self, request):
        return AIResponse(content=self.content, provider="fake", model="fake-model")


class RequestIntentTests(unittest.TestCase):
    def _classifier(self, payload):
        service = AIService(default_provider="fake")
        service.register_provider(FakeAIProvider(json.dumps(payload)))
        return AIRequestIntentClassifier(service)

    def test_classifier_implements_contract(self):
        classifier = self._classifier({"kind": "question", "content": "What is JARVIS?"})
        self.assertIsInstance(classifier, RequestIntentClassifier)

    def test_question_is_classified(self):
        classifier = self._classifier({"kind": "question", "content": "What is JARVIS?", "confidence": 0.9})
        result = classifier.classify("What is JARVIS?")
        self.assertEqual(IntentKind.QUESTION, result.kind)
        self.assertEqual("What is JARVIS?", result.content)
        self.assertEqual(0.9, result.confidence)

    def test_tool_is_classified(self):
        classifier = self._classifier({"kind": "tool", "content": "Find my README"})
        self.assertEqual(IntentKind.TOOL, classifier.classify("Find my README").kind)

    def test_invalid_json_is_rejected(self):
        service = AIService(default_provider="fake")
        service.register_provider(FakeAIProvider("not json"))
        classifier = AIRequestIntentClassifier(service)
        with self.assertRaises(ValueError):
            classifier.classify("hello")

    def test_unknown_kind_is_rejected(self):
        classifier = self._classifier({"kind": "magic", "content": "hello"})
        with self.assertRaises(ValueError):
            classifier.classify("hello")

    def test_invalid_confidence_is_rejected(self):
        classifier = self._classifier({"kind": "conversation", "content": "hello", "confidence": 2})
        with self.assertRaises(ValueError):
            classifier.classify("hello")

    def test_empty_text_is_rejected(self):
        classifier = self._classifier({"kind": "conversation", "content": "hello"})
        with self.assertRaises(ValueError):
            classifier.classify(" ")


class RequestIntentModelTests(unittest.TestCase):
    def test_model_is_immutable(self):
        intent = RequestIntent(IntentKind.CONVERSATION, "hello")
        with self.assertRaises(AttributeError):
            intent.kind = IntentKind.TASK


if __name__ == "__main__":
    unittest.main(verbosity=2)
