from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from src.ai.benchmark_cases import JARVIS_BENCHMARK_CASES, benchmark_score_function
from src.ai.evaluation import EvaluationCase, ModelCandidate, ModelEvaluationReport, ModelEvaluator
from src.ai.role_fitness import (
    DEFAULT_ROLE_FITNESS_PROFILES,
    RoleFitnessProfile,
    RoleFitnessResult,
    evaluate_role_fitness,
)
from src.ai.service import AIService


@dataclass(frozen=True)
class TournamentEntry:
    candidate: ModelCandidate
    report: ModelEvaluationReport
    role_fitness: Mapping[str, RoleFitnessResult]

    @property
    def suitable_role_count(self) -> int:
        return sum(result.suitable for result in self.role_fitness.values())

    @property
    def passed_case_count(self) -> int:
        return sum(observation.passed for observation in self.report.observations)

    @property
    def total_case_count(self) -> int:
        return len(self.report.observations)

    @property
    def rank_key(self) -> tuple[float, float, float, float, float, str]:
        # Higher is better for the first three dimensions; lower is better for
        # infrastructure failures and latency. The model id makes ties stable.
        return (
            float(self.suitable_role_count),
            float(self.report.passed),
            float(self.report.overall_score),
            -float(self.report.infrastructure_failures),
            -float(self.report.average_latency_ms if self.report.average_latency_ms is not None else float("inf")),
            self.candidate.model_id,
        )

    @property
    def case_evidence(self) -> tuple[dict[str, object], ...]:
        return tuple(
            {
                "case_id": observation.case_id,
                "passed": observation.passed,
                "outcome": observation.outcome.value,
                "scores": {
                    dimension.value: score
                    for dimension, score in observation.scores.items()
                },
                "error": observation.error,
                "latency_ms": observation.latency_ms,
                "response_preview": observation.response_preview,
            }
            for observation in self.report.observations
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "model_id": self.candidate.model_id,
            "provider_name": self.candidate.provider_name,
            "display_name": self.candidate.display_name,
            "overall_score": self.report.overall_score,
            "passed": self.report.passed,
            "passed_case_count": self.passed_case_count,
            "total_case_count": self.total_case_count,
            "model_failures": self.report.model_failures,
            "infrastructure_failures": self.report.infrastructure_failures,
            "average_latency_ms": self.report.average_latency_ms,
            "total_latency_ms": self.report.total_latency_ms,
            "dimension_scores": {
                dimension.value: score
                for dimension, score in self.report.dimension_scores.items()
            },
            "case_evidence": list(self.case_evidence),
            "suitable_role_count": self.suitable_role_count,
            "role_fitness": {
                role_id: {
                    "suitable": result.suitable,
                    "weighted_score": result.weighted_score,
                    "unmet_dimensions": [dimension.value for dimension in result.unmet_dimensions],
                    "infrastructure_failures": result.infrastructure_failures,
                }
                for role_id, result in self.role_fitness.items()
            },
        }


@dataclass(frozen=True)
class TournamentReport:
    entries: tuple[TournamentEntry, ...]

    @property
    def leaderboard(self) -> tuple[TournamentEntry, ...]:
        return tuple(sorted(self.entries, key=lambda entry: entry.rank_key, reverse=True))

    @property
    def winner(self) -> TournamentEntry | None:
        ranked = self.leaderboard
        return ranked[0] if ranked else None

    def as_dict(self) -> dict[str, object]:
        ranked = self.leaderboard
        return {
            "entries": [entry.as_dict() for entry in ranked],
            "winner": ranked[0].candidate.model_id if ranked else None,
        }


def evaluate_model_tournament(
    ai_service: AIService,
    candidates: Iterable[ModelCandidate],
    *,
    cases: Sequence[EvaluationCase] = JARVIS_BENCHMARK_CASES,
    role_profiles: Sequence[RoleFitnessProfile] = DEFAULT_ROLE_FITNESS_PROFILES,
) -> TournamentReport:
    """Run identical benchmark cases against multiple model candidates.

    This function only evaluates evidence. It does not register, assign, or
    authorize any model for a JARVIS role.
    """
    evaluator = ModelEvaluator(ai_service, benchmark_score_function)
    entries: list[TournamentEntry] = []

    for candidate in candidates:
        report = evaluator.evaluate(candidate, cases)
        role_fitness = {
            profile.role_id: evaluate_role_fitness(report, profile)
            for profile in role_profiles
        }
        entries.append(
            TournamentEntry(
                candidate=candidate,
                report=report,
                role_fitness=role_fitness,
            )
        )

    return TournamentReport(entries=tuple(entries))
