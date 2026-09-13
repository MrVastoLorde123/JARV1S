from __future__ import annotations

import unittest

from src.ai.evaluation import (
    EvaluationCase,
    EvaluationDimension,
    ModelCandidate,
    ModelEvaluator,
    threshold_score_function,
)
from src.ai.models import AIResponse


class _FakeProvider:
    def __init__(self) -> None:
        self.requests = []

    def provider_name(self):
        return "fake"

    def capabilities(self):
        from src.ai.models import AICapabilities
        return AICapabilities(text_generation=True)

    def generate(self, request):
        self.requests.append(request)
        return AIResponse(
            content="verified browser tool request approved",
            provider="fake",
            model=request.model or "fake-model",
            finish_reason="stop",
        )


class _FakeService:
    def __init__(self) -> None:
        self.provider = _FakeProvider()

    def generate(self, request, provider_name=None, required_capabilities=None):
        if provider_name != "fake":
            raise AssertionError("unexpected provider")
        if required_capabilities and "text_generation" not in required_capabilities:
            raise AssertionError("unexpected capability contract")
        return self.provider.generate(request)


class ModelEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = _FakeService()
        self.case = EvaluationCase(
            case_id="authority-smoke",
            name="Authority smoke test",
            task="Return the verification result.",
            dimensions=(
                EvaluationDimension.CORRECTNESS,
                EvaluationDimension.AUTHORITY_DISCIPLINE,
            ),
            required_capabilities=("text_generation",),
        )

    def test_candidate_requires_identity(self) -> None:
        with self.assertRaises(ValueError):
            ModelCandidate("", "fake")
        with self.assertRaises(ValueError):
            ModelCandidate("fake", "")

    def test_case_requires_dimensions(self) -> None:
        with self.assertRaises(ValueError):
            EvaluationCase("case", "Case", "Task", ())

    def test_evaluator_passes_provider_neutral_request_to_service(self) -> None:
        candidate = ModelCandidate("fake-model", "fake")
        scorer = threshold_score_function(
            {"authority-smoke": ("verified", "approved")}
        )

        report = ModelEvaluator(self.service, scorer).evaluate(
            candidate,
            (self.case,),
        )

        self.assertTrue(report.passed)
        self.assertEqual(report.overall_score, 1.0)
        self.assertEqual(
            report.dimension_scores[EvaluationDimension.CORRECTNESS],
            1.0,
        )
        self.assertEqual(self.service.provider.requests[0].model, "fake-model")
        self.assertTrue(self.service.provider.requests[0].metadata["evaluation"])

    def test_failed_provider_call_becomes_negative_evidence(self) -> None:
        class FailingService:
            def generate(self, *args, **kwargs):
                raise RuntimeError("model unavailable")

        report = ModelEvaluator(
            FailingService(),
            threshold_score_function({"authority-smoke": ("verified",)}),
        ).evaluate(
            ModelCandidate("offline", "fake"),
            (self.case,),
        )

        self.assertFalse(report.passed)
        self.assertEqual(report.overall_score, 0.0)
        self.assertIn("model unavailable", report.observations[0].error)

    def test_score_is_bounded(self) -> None:
        candidate = ModelCandidate("fake-model", "fake")
        report = ModelEvaluator(
            self.service,
            lambda case, response: {
                EvaluationDimension.CORRECTNESS: 1.0,
                EvaluationDimension.AUTHORITY_DISCIPLINE: 0.0,
            },
        ).evaluate(candidate, (self.case,))

        self.assertEqual(report.overall_score, 0.5)
        with self.assertRaises(ValueError):
            from src.ai.evaluation import EvaluationObservation
            EvaluationObservation(
                "case",
                "fake",
                None,
                {EvaluationDimension.CORRECTNESS: 2.0},
                False,
            )


if __name__ == "__main__":
    unittest.main()
