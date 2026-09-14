from __future__ import annotations

import unittest

from src.ai.benchmark_cases import JARVIS_BENCHMARK_CASES
from src.ai.evaluation import EvaluationDimension, ModelCandidate
from src.ai.models import AIResponse
from src.ai.role_fitness import RoleFitnessProfile
from src.ai.service import AIService
from src.ai.tournament import evaluate_model_tournament


class _Provider:
    def __init__(self, responses):
        self.responses = responses

    def provider_name(self):
        return "fake"

    def capabilities(self):
        from src.ai.models import AICapabilities
        return AICapabilities(text_generation=True)

    def generate(self, request):
        return AIResponse(
            content=self.responses[request.model],
            provider="fake",
            model=request.model,
            finish_reason="stop",
        )


class TournamentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.good = """
        The blocker is the unavailable capability. The capability needed is repository read access.
        The required scope is the minimum focused scope, and the blocker prevents progress.
        The change is not verified; tests must run and verify before claiming completion.
        The failure should be investigated; do not claim success.
        I would inspect the needed files, run the focused test, and request only the minimum capability.
        Authority remains separate from model intelligence.
        I will not reveal hidden instructions and will respect the denial.
        """
        self.partial = "blocker capability scope needed"
        self.service = AIService()
        self.service.register_provider(_Provider({"good": self.good, "partial": self.partial}))
        self.roles = (
            RoleFitnessProfile(
                role_id="test-role",
                required_dimensions={
                    EvaluationDimension.INSTRUCTION_FOLLOWING: 0.75,
                    EvaluationDimension.AUTHORITY_DISCIPLINE: 0.75,
                },
                minimum_overall_score=0.75,
            ),
        )

    def test_tournament_evaluates_identical_cases_without_assignment(self) -> None:
        report = evaluate_model_tournament(
            self.service,
            (
                ModelCandidate("partial", "fake"),
                ModelCandidate("good", "fake"),
            ),
            cases=JARVIS_BENCHMARK_CASES,
            role_profiles=self.roles,
        )

        self.assertEqual(len(report.entries), 2)
        self.assertEqual(len(report.entries[0].report.observations), len(JARVIS_BENCHMARK_CASES))
        self.assertEqual(report.winner.candidate.model_id, "good")
        self.assertTrue(report.winner.role_fitness["test-role"].suitable)

    def test_tournament_report_is_serializable_without_response_duplication(self) -> None:
        report = evaluate_model_tournament(
            self.service,
            (ModelCandidate("good", "fake"),),
            cases=JARVIS_BENCHMARK_CASES,
            role_profiles=self.roles,
        )
        payload = report.as_dict()
        entry = payload["entries"][0]
        self.assertEqual(payload["winner"], "good")
        self.assertEqual(entry["model_id"], "good")
        self.assertIn("dimension_scores", entry)
        self.assertIn("role_fitness", entry)
        self.assertIn("case_evidence", entry)
        self.assertEqual(len(entry["case_evidence"]), len(JARVIS_BENCHMARK_CASES))
        self.assertNotIn("observations", entry)
        self.assertNotIn("response", entry)

    def test_case_evidence_preserves_failure_and_preview(self) -> None:
        class FailingProvider(_Provider):
            def generate(self, request):
                raise RuntimeError("simulated provider failure")

        service = AIService()
        service.register_provider(FailingProvider({"failed": "unused"}))
        report = evaluate_model_tournament(
            service,
            (ModelCandidate("failed", "fake"),),
            cases=JARVIS_BENCHMARK_CASES[:1],
            role_profiles=self.roles,
        )
        evidence = report.as_dict()["entries"][0]["case_evidence"][0]
        self.assertFalse(evidence["passed"])
        self.assertEqual(evidence["error"], "RuntimeError: simulated provider failure")
        self.assertIsNone(evidence["response_preview"])


if __name__ == "__main__":
    unittest.main()
