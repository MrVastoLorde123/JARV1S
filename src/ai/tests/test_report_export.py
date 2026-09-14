from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.ai.evaluation import EvaluationDimension, EvaluationObservation, ModelCandidate, ModelEvaluationReport
from src.ai.models import AIResponse
from src.ai.observability import EvaluationOutcome
from src.ai.report_export import report_as_dict, write_report_json
from src.ai.role_fitness import RoleFitnessResult


class ReportExportTests(unittest.TestCase):
    def _report(self) -> ModelEvaluationReport:
        return ModelEvaluationReport(
            candidate=ModelCandidate("qwen3:4b", "ollama"),
            observations=(
                EvaluationObservation(
                    case_id="case-1",
                    model_id="qwen3:4b",
                    response=AIResponse(content="verified response", provider="ollama", model="qwen3:4b"),
                    scores={EvaluationDimension.VERIFICATION: 1.0},
                    passed=True,
                    outcome=EvaluationOutcome.PASS,
                    latency_ms=1234.5,
                ),
            ),
        )

    def test_report_contains_response_evidence_and_latency(self) -> None:
        payload = report_as_dict(self._report())
        observation = payload["observations"][0]
        self.assertEqual(observation["response"], "verified response")
        self.assertEqual(observation["latency_ms"], 1234.5)
        self.assertEqual(observation["outcome"], "pass")

    def test_report_json_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            write_report_json(self._report(), path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["model_id"], "qwen3:4b")
            self.assertEqual(payload["observations"][0]["response"], "verified response")

    def test_role_fitness_serializes_without_granting_assignment(self) -> None:
        fitness = RoleFitnessResult(
            role_id="coding-agent",
            suitable=False,
            weighted_score=0.42,
            dimension_scores={},
            unmet_dimensions=(EvaluationDimension.AUTHORITY_DISCIPLINE,),
            infrastructure_failures=0,
        )
        payload = report_as_dict(self._report(), {"coding-agent": fitness})
        self.assertFalse(payload["role_fitness"]["coding-agent"]["suitable"])
        self.assertEqual(payload["role_fitness"]["coding-agent"]["unmet_dimensions"], ["authority_discipline"])


if __name__ == "__main__":
    unittest.main()
