from __future__ import annotations

import unittest

from src.ai.errors import ProviderUnavailableError
from src.ai.evaluation import (
    EvaluationCase,
    EvaluationDimension,
    EvaluationOutcome,
    ModelCandidate,
    ModelEvaluator,
)
from src.ai.models import AIResponse, AICapabilities
from src.ai.observability import ExecutionTrace, TraceEventKind
from src.ai.provider import AIProvider
from src.ai.service import AIService


class _FakeProvider(AIProvider):
    def __init__(self, response: str | None = "ok", fail: bool = False) -> None:
        self.response = response
        self.fail = fail

    def generate(self, request):
        if self.fail:
            raise ProviderUnavailableError("server unavailable")
        return AIResponse(content=self.response, provider="fake", model=request.model or "fake")

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "fake"


class ObservabilityTests(unittest.TestCase):
    def _case(self):
        return EvaluationCase(
            case_id="trace-001",
            name="Trace case",
            task="Say ok.",
            dimensions=(EvaluationDimension.CORRECTNESS,),
        )

    def test_trace_records_execution_lifecycle(self) -> None:
        service = AIService()
        service.register_provider(_FakeProvider())
        evaluator = ModelEvaluator(service, lambda case, response: {EvaluationDimension.CORRECTNESS: 1.0})
        trace = ExecutionTrace("run-1")

        report = evaluator.evaluate(
            ModelCandidate("fake-model", "fake"),
            (self._case(),),
            trace=trace,
        )

        self.assertTrue(report.passed)
        kinds = [event.kind for event in trace.events]
        self.assertEqual(kinds[0], TraceEventKind.RUN_STARTED)
        self.assertIn(TraceEventKind.REQUEST_CREATED, kinds)
        self.assertIn(TraceEventKind.RESPONSE_RECEIVED, kinds)
        self.assertIn(TraceEventKind.SCORE_CALCULATED, kinds)
        self.assertEqual(kinds[-1], TraceEventKind.RUN_COMPLETED)

    def test_infrastructure_failure_is_not_scored_as_model_failure(self) -> None:
        service = AIService()
        service.register_provider(_FakeProvider(fail=True))
        evaluator = ModelEvaluator(service, lambda case, response: {EvaluationDimension.CORRECTNESS: 1.0})

        report = evaluator.evaluate(ModelCandidate("fake-model", "fake"), (self._case(),))
        observation = report.observations[0]

        self.assertEqual(observation.outcome, EvaluationOutcome.INFRASTRUCTURE_ERROR)
        self.assertEqual(observation.scores, {})
        self.assertEqual(report.infrastructure_failures, 1)
        self.assertEqual(report.overall_score, 0.0)
        self.assertFalse(report.passed)

    def test_trace_is_serializable_to_ui_friendly_mapping(self) -> None:
        trace = ExecutionTrace("run-2")
        trace.add(TraceEventKind.RUN_STARTED, "Started.", model_id="qwen3:4b", provider_name="ollama")
        payload = trace.as_dict()

        self.assertEqual(payload["run_id"], "run-2")
        self.assertEqual(payload["events"][0]["kind"], "run_started")
        self.assertEqual(payload["events"][0]["model_id"], "qwen3:4b")


if __name__ == "__main__":
    unittest.main(verbosity=2)
