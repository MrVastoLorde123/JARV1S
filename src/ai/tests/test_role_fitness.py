from __future__ import annotations

import unittest

from src.ai.evaluation import EvaluationDimension, EvaluationObservation, ModelCandidate, ModelEvaluationReport
from src.ai.observability import EvaluationOutcome
from src.ai.role_fitness import RoleFitnessProfile, evaluate_role_fitness


class RoleFitnessTests(unittest.TestCase):
    def _report(self, scores):
        return ModelEvaluationReport(
            candidate=ModelCandidate("model", "ollama"),
            observations=(
                EvaluationObservation(
                    case_id="case",
                    model_id="model",
                    response=object(),
                    scores=scores,
                    passed=True,
                    outcome=EvaluationOutcome.PASS,
                ),
            ),
        )

    def test_suitable_requires_all_required_dimensions(self) -> None:
        profile = RoleFitnessProfile(
            role_id="coding-agent",
            required_dimensions={
                EvaluationDimension.VERIFICATION: 0.75,
                EvaluationDimension.AUTHORITY_DISCIPLINE: 0.80,
            },
            minimum_overall_score=0.75,
        )
        result = evaluate_role_fitness(
            self._report(
                {
                    EvaluationDimension.VERIFICATION: 0.90,
                    EvaluationDimension.AUTHORITY_DISCIPLINE: 0.85,
                }
            ),
            profile,
        )
        self.assertTrue(result.suitable)
        self.assertEqual(result.unmet_dimensions, ())

    def test_missing_or_weak_dimension_blocks_assignment(self) -> None:
        profile = RoleFitnessProfile(
            role_id="coding-agent",
            required_dimensions={EvaluationDimension.AUTHORITY_DISCIPLINE: 0.80},
        )
        result = evaluate_role_fitness(
            self._report({EvaluationDimension.AUTHORITY_DISCIPLINE: 0.40}),
            profile,
        )
        self.assertFalse(result.suitable)
        self.assertEqual(result.unmet_dimensions, (EvaluationDimension.AUTHORITY_DISCIPLINE,))

    def test_infrastructure_failure_blocks_default_fitness(self) -> None:
        report = ModelEvaluationReport(
            candidate=ModelCandidate("model", "ollama"),
            observations=(
                EvaluationObservation(
                    case_id="case",
                    model_id="model",
                    response=None,
                    scores={},
                    passed=False,
                    outcome=EvaluationOutcome.INFRASTRUCTURE_ERROR,
                ),
            ),
        )
        profile = RoleFitnessProfile(
            role_id="coding-agent",
            required_dimensions={EvaluationDimension.AUTHORITY_DISCIPLINE: 0.50},
        )
        result = evaluate_role_fitness(report, profile)
        self.assertFalse(result.suitable)
        self.assertEqual(result.infrastructure_failures, 1)


if __name__ == "__main__":
    unittest.main()
