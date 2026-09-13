from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable, Mapping, Sequence

from src.ai.models import AIRequest, AIResponse
from src.ai.service import AIService


class EvaluationDimension(str, Enum):
    CORRECTNESS = "correctness"
    INSTRUCTION_FOLLOWING = "instruction_following"
    TOOL_DISCIPLINE = "tool_discipline"
    AUTHORITY_DISCIPLINE = "authority_discipline"
    VERIFICATION = "verification"
    ERROR_RECOVERY = "error_recovery"
    CONTEXT_USE = "context_use"
    EFFICIENCY = "efficiency"


@dataclass(frozen=True)
class ModelCandidate:
    """A locally available model that may be benchmarked.

    A candidate is descriptive only. Registering or benchmarking a model
    never grants it an agent assignment or runtime authority.
    """

    model_id: str
    provider_name: str
    display_name: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id cannot be empty")
        if not self.provider_name.strip():
            raise ValueError("provider_name cannot be empty")

        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class EvaluationCase:
    """One controlled task used to measure a candidate model."""

    case_id: str
    name: str
    task: str
    dimensions: tuple[EvaluationDimension, ...]
    context: object = None
    generation_options: Mapping[str, object] = field(default_factory=dict)
    required_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("case_id cannot be empty")
        if not self.name.strip():
            raise ValueError("case name cannot be empty")
        if not self.task.strip():
            raise ValueError("evaluation task cannot be empty")
        if not self.dimensions:
            raise ValueError("evaluation case requires at least one dimension")

        object.__setattr__(self, "dimensions", tuple(self.dimensions))
        object.__setattr__(self, "generation_options", dict(self.generation_options))
        object.__setattr__(self, "required_capabilities", tuple(self.required_capabilities))


@dataclass(frozen=True)
class EvaluationObservation:
    """Provider response plus deterministic benchmark evidence."""

    case_id: str
    model_id: str
    response: AIResponse | None
    scores: Mapping[EvaluationDimension, float]
    passed: bool
    error: str | None = None

    def __post_init__(self) -> None:
        for dimension, score in self.scores.items():
            if not isinstance(score, (int, float)) or not 0.0 <= float(score) <= 1.0:
                raise ValueError(
                    f"score for {dimension.value} must be between 0 and 1"
                )
        object.__setattr__(self, "scores", dict(self.scores))


@dataclass(frozen=True)
class ModelEvaluationReport:
    """Aggregate evidence for a single candidate model."""

    candidate: ModelCandidate
    observations: tuple[EvaluationObservation, ...]

    @property
    def dimension_scores(self) -> Mapping[EvaluationDimension, float]:
        totals: dict[EvaluationDimension, list[float]] = {}
        for observation in self.observations:
            for dimension, score in observation.scores.items():
                totals.setdefault(dimension, []).append(float(score))
        return {
            dimension: sum(values) / len(values)
            for dimension, values in totals.items()
            if values
        }

    @property
    def overall_score(self) -> float:
        scores = tuple(self.dimension_scores.values())
        return sum(scores) / len(scores) if scores else 0.0

    @property
    def passed(self) -> bool:
        return bool(self.observations) and all(item.passed for item in self.observations)


ScoreFunction = Callable[[EvaluationCase, AIResponse], Mapping[EvaluationDimension, float]]


class ModelEvaluator:
    """Run controlled benchmark cases through the existing AIService boundary."""

    def __init__(self, ai_service: AIService, score_function: ScoreFunction) -> None:
        self._ai_service = ai_service
        self._score_function = score_function

    def evaluate(
        self,
        candidate: ModelCandidate,
        cases: Iterable[EvaluationCase],
    ) -> ModelEvaluationReport:
        observations: list[EvaluationObservation] = []

        for case in cases:
            request = AIRequest(
                task=case.task,
                context=case.context,
                model=candidate.model_id,
                generation_options=dict(case.generation_options),
                metadata={
                    "evaluation": True,
                    "case_id": case.case_id,
                    "candidate_model_id": candidate.model_id,
                },
            )

            try:
                response = self._ai_service.generate(
                    request,
                    provider_name=candidate.provider_name,
                    required_capabilities=case.required_capabilities,
                )
                raw_scores = self._score_function(case, response)
                scores = {
                    dimension: float(raw_scores.get(dimension, 0.0))
                    for dimension in case.dimensions
                }
                observation = EvaluationObservation(
                    case_id=case.case_id,
                    model_id=candidate.model_id,
                    response=response,
                    scores=scores,
                    passed=all(score >= 0.5 for score in scores.values()),
                )
            except Exception as exc:
                observation = EvaluationObservation(
                    case_id=case.case_id,
                    model_id=candidate.model_id,
                    response=None,
                    scores={dimension: 0.0 for dimension in case.dimensions},
                    passed=False,
                    error=f"{type(exc).__name__}: {exc}",
                )

            observations.append(observation)

        return ModelEvaluationReport(
            candidate=candidate,
            observations=tuple(observations),
        )


def threshold_score_function(
    expected_substrings: Mapping[str, Sequence[str]],
) -> ScoreFunction:
    """Create a deterministic evaluator for smoke tests and early benchmarks.

    The returned score is 1.0 when all configured substrings for a case are
    present in the model response and 0.0 otherwise. It is intentionally
    simple so initial model infrastructure can be validated before adding
    richer task-specific judges.
    """

    normalized = {
        case_id: tuple(item.casefold() for item in phrases)
        for case_id, phrases in expected_substrings.items()
    }

    def score(case: EvaluationCase, response: AIResponse) -> Mapping[EvaluationDimension, float]:
        content = str(response.content).casefold()
        expected = normalized.get(case.case_id, ())
        score = 1.0 if all(fragment in content for fragment in expected) else 0.0
        return {dimension: score for dimension in case.dimensions}

    return score
