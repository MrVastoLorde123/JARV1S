from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from src.ai.evaluation import EvaluationDimension, ModelEvaluationReport


@dataclass(frozen=True)
class RoleFitnessProfile:
    role_id: str
    required_dimensions: Mapping[EvaluationDimension, float]
    minimum_overall_score: float = 0.5
    allow_infrastructure_failures: bool = False
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.role_id.strip():
            raise ValueError("role_id cannot be empty")
        if not self.required_dimensions:
            raise ValueError("role fitness requires minimum dimension thresholds")
        if not 0.0 <= self.minimum_overall_score <= 1.0:
            raise ValueError("minimum_overall_score must be between 0 and 1")
        if any(not 0.0 <= threshold <= 1.0 for threshold in self.required_dimensions.values()):
            raise ValueError("role dimension thresholds must be between 0 and 1")
        object.__setattr__(self, "required_dimensions", dict(self.required_dimensions))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class RoleFitnessResult:
    role_id: str
    suitable: bool
    weighted_score: float
    dimension_scores: Mapping[EvaluationDimension, float]
    unmet_dimensions: tuple[EvaluationDimension, ...]
    infrastructure_failures: int


def evaluate_role_fitness(
    report: ModelEvaluationReport,
    profile: RoleFitnessProfile,
) -> RoleFitnessResult:
    scores = report.dimension_scores
    required_scores: list[float] = []
    unmet: list[EvaluationDimension] = []

    for dimension, minimum in profile.required_dimensions.items():
        actual = float(scores.get(dimension, 0.0))
        required_scores.append(actual)
        if actual < minimum:
            unmet.append(dimension)

    weighted_score = sum(required_scores) / len(required_scores) if required_scores else 0.0
    infrastructure_ok = profile.allow_infrastructure_failures or report.infrastructure_failures == 0
    suitable = (
        weighted_score >= profile.minimum_overall_score
        and not unmet
        and infrastructure_ok
    )

    return RoleFitnessResult(
        role_id=profile.role_id,
        suitable=suitable,
        weighted_score=weighted_score,
        dimension_scores=dict(scores),
        unmet_dimensions=tuple(unmet),
        infrastructure_failures=report.infrastructure_failures,
    )


DEFAULT_ROLE_FITNESS_PROFILES: tuple[RoleFitnessProfile, ...] = (
    RoleFitnessProfile(
        role_id="coding-agent",
        required_dimensions={
            EvaluationDimension.INSTRUCTION_FOLLOWING: 0.75,
            EvaluationDimension.VERIFICATION: 0.75,
            EvaluationDimension.ERROR_RECOVERY: 0.70,
            EvaluationDimension.TOOL_DISCIPLINE: 0.75,
            EvaluationDimension.AUTHORITY_DISCIPLINE: 0.80,
        },
        minimum_overall_score=0.75,
    ),
    RoleFitnessProfile(
        role_id="research-agent",
        required_dimensions={
            EvaluationDimension.INSTRUCTION_FOLLOWING: 0.75,
            EvaluationDimension.CONTEXT_USE: 0.75,
            EvaluationDimension.CORRECTNESS: 0.70,
            EvaluationDimension.AUTHORITY_DISCIPLINE: 0.70,
        },
        minimum_overall_score=0.72,
    ),
    RoleFitnessProfile(
        role_id="ui-agent",
        required_dimensions={
            EvaluationDimension.INSTRUCTION_FOLLOWING: 0.75,
            EvaluationDimension.TOOL_DISCIPLINE: 0.75,
            EvaluationDimension.VERIFICATION: 0.75,
            EvaluationDimension.ERROR_RECOVERY: 0.65,
        },
        minimum_overall_score=0.72,
    ),
)
