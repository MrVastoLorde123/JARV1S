from __future__ import annotations

import unittest

from src.ai.evaluation import EvaluationDimension, EvaluationObservation, EvaluationOutcome, ModelCandidate, ModelEvaluationReport
from src.ai.models import AIResponse
from src.ai.observability import ExecutionTrace
from src.ai.repeatability import aggregate_reports, repeatability_as_dict


class RepeatabilityTests(unittest.TestCase):
    candidate = ModelCandidate("test-model", "fake", "Test Model")

    def _report(self, score: float, outcome: EvaluationOutcome, latency: float = 100.0) -> ModelEvaluationReport:
        is_infrastructure = outcome in {EvaluationOutcome.INFRASTRUCTURE_ERROR, EvaluationOutcome.TIMEOUT}
        observation = EvaluationObservation(
            case_id="case-001",
            model_id="test-model",
            response=AIResponse(content="ok", provider="fake", model="test-model") if not is_infrastructure else None,
            scores={EvaluationDimension.CORRECTNESS: score} if not is_infrastructure else {},
            passed=outcome is EvaluationOutcome.PASS,
            outcome=outcome,
            latency_ms=latency,
            trace=ExecutionTrace("test-run"),
        )
        return ModelEvaluationReport(candidate=self.candidate, observations=(observation,))

    def test_aggregate_preserves_variance_and_case_outcomes(self) -> None:
        summary = aggregate_reports(
            (
                self._report(1.0, EvaluationOutcome.PASS, 100.0),
                self._report(0.0, EvaluationOutcome.MODEL_FAILURE, 200.0),
                self._report(0.0, EvaluationOutcome.INFRASTRUCTURE_ERROR, 300.0),
            )
        )

        case = summary.cases["case-001"]
        self.assertEqual(summary.trial_count, 3)
        self.assertEqual(summary.trials_with_infrastructure_failures, 1)
        self.assertEqual(summary.evaluable_observation_count, 2)
        self.assertEqual(summary.model_failure_rate, 0.5)
        self.assertEqual(summary.infrastructure_failure_rate, 1 / 3)
        self.assertEqual(case.pass_count, 1)
        self.assertEqual(case.model_failure_count, 1)
        self.assertEqual(case.infrastructure_failure_count, 1)
        self.assertEqual(case.observed_scores, (1.0, 0.0))
        self.assertIsNotNone(case.score_stddev)

    def test_infrastructure_failures_do_not_inflate_model_failure_rate(self) -> None:
        summary = aggregate_reports(
            (
                self._report(0.0, EvaluationOutcome.MODEL_FAILURE),
                self._report(0.0, EvaluationOutcome.INFRASTRUCTURE_ERROR),
                self._report(0.0, EvaluationOutcome.INFRASTRUCTURE_ERROR),
            )
        )
        self.assertEqual(summary.model_failure_rate, 1.0)
        self.assertEqual(summary.infrastructure_failure_rate, 2 / 3)

    def test_mixed_models_are_rejected(self) -> None:
        other = ModelEvaluationReport(
            candidate=ModelCandidate("other-model", "fake"),
            observations=(),
        )
        with self.assertRaises(ValueError):
            aggregate_reports((self._report(1.0, EvaluationOutcome.PASS), other))

    def test_serialization_is_json_ready(self) -> None:
        summary = aggregate_reports((self._report(1.0, EvaluationOutcome.PASS),))
        payload = repeatability_as_dict(summary)
        self.assertEqual(payload["trial_count"], 1)
        self.assertEqual(payload["evaluable_observation_count"], 1)
        self.assertEqual(payload["cases"]["case-001"]["pass_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
