from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable, Mapping, Sequence
from time import monotonic
from uuid import uuid4

from src.ai.errors import (
    CapabilityError,
    GenerationError,
    InvalidRequestError,
    ProviderUnavailableError,
    TimeoutError,
)
from src.ai.models import AIRequest, AIResponse
from src.ai.observability import EvaluationOutcome, ExecutionTrace, TraceEventKind
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
    """A locally available model that may be benchmarked."""

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
    """Evidence for one benchmark case."""

    case_id: str
    model_id: str
    response: AIResponse | None
    scores: Mapping[EvaluationDimension, float]
    passed: bool
    outcome: EvaluationOutcome = EvaluationOutcome.MODEL_FAILURE
    error: str | None = None
    trace: ExecutionTrace | None = None
    latency_ms: float | None = None
    response_preview: str | None = None

    def __post_init__(self) -> None:
        for dimension, score in self.scores.items():
            if not isinstance(score, (int, float)) or not 0.0 <= float(score) <= 1.0:
                raise ValueError(f"score for {dimension.value} must be between 0 and 1")
        if self.latency_ms is not None and self.latency_ms < 0.0:
            raise ValueError("latency_ms cannot be negative")
        if self.response_preview is not None and not isinstance(self.response_preview, str):
            raise ValueError("response_preview must be a string or None")
        object.__setattr__(self, "scores", dict(self.scores))


@dataclass(frozen=True)
class ModelEvaluationReport:
    """Aggregate evidence for a single candidate model."""

    candidate: ModelCandidate
    observations: tuple[EvaluationObservation, ...]
    trace: ExecutionTrace | None = None

    @property
    def dimension_scores(self) -> Mapping[EvaluationDimension, float]:
        totals: dict[EvaluationDimension, list[float]] = {}
        for observation in self.observations:
            if observation.response is None:
                continue
            for dimension, score in observation.scores.items():
                totals.setdefault(dimension, []).append(float(score))
        return {dimension: sum(values) / len(values) for dimension, values in totals.items() if values}

    @property
    def overall_score(self) -> float:
        scores = tuple(self.dimension_scores.values())
        return sum(scores) / len(scores) if scores else 0.0

    @property
    def passed(self) -> bool:
        return bool(self.observations) and all(item.outcome is EvaluationOutcome.PASS for item in self.observations)

    @property
    def infrastructure_failures(self) -> int:
        infrastructure_outcomes = {
            EvaluationOutcome.INFRASTRUCTURE_ERROR,
            EvaluationOutcome.TIMEOUT,
            EvaluationOutcome.INVALID_PROVIDER_RESPONSE,
            EvaluationOutcome.REQUEST_ERROR,
        }
        return sum(observation.outcome in infrastructure_outcomes for observation in self.observations)

    @property
    def model_failures(self) -> int:
        return sum(observation.outcome is EvaluationOutcome.MODEL_FAILURE for observation in self.observations)

    @property
    def total_latency_ms(self) -> float:
        return round(sum(observation.latency_ms or 0.0 for observation in self.observations), 3)

    @property
    def average_latency_ms(self) -> float | None:
        measured = [observation.latency_ms for observation in self.observations if observation.latency_ms is not None]
        if not measured:
            return None
        return round(sum(measured) / len(measured), 3)


ScoreFunction = Callable[[EvaluationCase, AIResponse], Mapping[EvaluationDimension, float]]


def _classify_exception(exc: Exception) -> EvaluationOutcome:
    if isinstance(exc, ProviderUnavailableError):
        return EvaluationOutcome.INFRASTRUCTURE_ERROR
    if isinstance(exc, TimeoutError):
        return EvaluationOutcome.TIMEOUT
    if isinstance(exc, GenerationError):
        return EvaluationOutcome.INVALID_PROVIDER_RESPONSE
    if isinstance(exc, (InvalidRequestError, CapabilityError)):
        return EvaluationOutcome.REQUEST_ERROR
    return EvaluationOutcome.EVALUATION_ERROR


class ModelEvaluator:
    """Run controlled benchmark cases through the existing AIService boundary."""

    def __init__(self, ai_service: AIService, score_function: ScoreFunction) -> None:
        self._ai_service = ai_service
        self._score_function = score_function

    def evaluate(
        self,
        candidate: ModelCandidate,
        cases: Iterable[EvaluationCase],
        trace: ExecutionTrace | None = None,
    ) -> ModelEvaluationReport:
        trace = trace or ExecutionTrace(f"eval-{uuid4().hex}")
        case_list = tuple(cases)
        observations: list[EvaluationObservation] = []
        trace.add(
            TraceEventKind.RUN_STARTED,
            "Model evaluation started.",
            model_id=candidate.model_id,
            provider_name=candidate.provider_name,
            data={"case_count": len(case_list)},
        )

        for case in case_list:
            trace.add(
                TraceEventKind.CASE_STARTED,
                f"Started benchmark case '{case.name}'.",
                case_id=case.case_id,
                model_id=candidate.model_id,
                provider_name=candidate.provider_name,
            )
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
            trace.add(
                TraceEventKind.REQUEST_CREATED,
                "Provider-neutral AI request created.",
                case_id=case.case_id,
                model_id=candidate.model_id,
                provider_name=candidate.provider_name,
                data={
                    "required_capabilities": case.required_capabilities,
                    "generation_options": dict(case.generation_options),
                },
            )
            trace.add(
                TraceEventKind.PROVIDER_SELECTED,
                "Selected provider for benchmark case.",
                case_id=case.case_id,
                model_id=candidate.model_id,
                provider_name=candidate.provider_name,
            )

            started = monotonic()
            try:
                response = self._ai_service.generate(
                    request,
                    provider_name=candidate.provider_name,
                    required_capabilities=case.required_capabilities,
                )
                latency_ms = round((monotonic() - started) * 1000.0, 3)
                content = str(response.content)
                response_preview = content[:2000]
                trace.add(
                    TraceEventKind.RESPONSE_RECEIVED,
                    "Provider response received.",
                    case_id=case.case_id,
                    model_id=candidate.model_id,
                    provider_name=candidate.provider_name,
                    data={
                        "finish_reason": response.finish_reason,
                        "content_length": len(content),
                        "usage": response.usage,
                        "latency_ms": latency_ms,
                        "response_preview": response_preview,
                    },
                )
                raw_scores = self._score_function(case, response)
                scores = {
                    dimension: float(raw_scores.get(dimension, 0.0))
                    for dimension in case.dimensions
                }
                passed = all(score >= 0.5 for score in scores.values())
                outcome = EvaluationOutcome.PASS if passed else EvaluationOutcome.MODEL_FAILURE
                trace.add(
                    TraceEventKind.SCORE_CALCULATED,
                    "Benchmark score calculated.",
                    case_id=case.case_id,
                    model_id=candidate.model_id,
                    provider_name=candidate.provider_name,
                    outcome=outcome,
                    data={dimension.value: score for dimension, score in scores.items()},
                )
                trace.add(
                    TraceEventKind.CASE_COMPLETED,
                    "Benchmark case completed.",
                    case_id=case.case_id,
                    model_id=candidate.model_id,
                    provider_name=candidate.provider_name,
                    outcome=outcome,
                    data={"latency_ms": latency_ms},
                )
                observation = EvaluationObservation(
                    case_id=case.case_id,
                    model_id=candidate.model_id,
                    response=response,
                    scores=scores,
                    passed=passed,
                    outcome=outcome,
                    trace=trace,
                    latency_ms=latency_ms,
                    response_preview=response_preview,
                )
            except Exception as exc:
                latency_ms = round((monotonic() - started) * 1000.0, 3)
                outcome = _classify_exception(exc)
                message = f"{type(exc).__name__}: {exc}"
                trace.add(
                    TraceEventKind.ERROR,
                    "Benchmark execution failed.",
                    case_id=case.case_id,
                    model_id=candidate.model_id,
                    provider_name=candidate.provider_name,
                    outcome=outcome,
                    data={"error": message, "latency_ms": latency_ms},
                )
                trace.add(
                    TraceEventKind.CASE_COMPLETED,
                    "Benchmark case completed with an error.",
                    case_id=case.case_id,
                    model_id=candidate.model_id,
                    provider_name=candidate.provider_name,
                    outcome=outcome,
                    data={"latency_ms": latency_ms},
                )
                observation = EvaluationObservation(
                    case_id=case.case_id,
                    model_id=candidate.model_id,
                    response=None,
                    scores={},
                    passed=False,
                    outcome=outcome,
                    error=message,
                    trace=trace,
                    latency_ms=latency_ms,
                )
            observations.append(observation)

        report = ModelEvaluationReport(
            candidate=candidate,
            observations=tuple(observations),
            trace=trace,
        )
        trace.add(
            TraceEventKind.RUN_COMPLETED,
            "Model evaluation completed.",
            model_id=candidate.model_id,
            provider_name=candidate.provider_name,
            data={
                "overall_score": report.overall_score,
                "passed": report.passed,
                "model_failures": report.model_failures,
                "infrastructure_failures": report.infrastructure_failures,
                "average_latency_ms": report.average_latency_ms,
                "total_latency_ms": report.total_latency_ms,
            },
        )
        return report


def threshold_score_function(
    expected_substrings: Mapping[str, Sequence[str]],
) -> ScoreFunction:
    """Create a deterministic evaluator for smoke tests and early benchmarks."""
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
