"""M100-M108: bounded reasoning, uncertainty, and prediction contracts.

Reasoning consumes evidence and world context and produces inspectable hypotheses,
bounded belief revisions, advisory predictions, and deterministic traces. It does
not establish truth, grant authority, authorize execution, select providers, or
execute capabilities.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class EvidencePolarity(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    CONTEXT = "CONTEXT"


class ReasoningStepKind(str, Enum):
    CONTEXT = "CONTEXT"
    EVIDENCE = "EVIDENCE"
    HYPOTHESIS = "HYPOTHESIS"
    REVISION = "REVISION"
    PREDICTION = "PREDICTION"
    EVALUATION = "EVALUATION"


class RevisionStatus(str, Enum):
    UNCHANGED = "UNCHANGED"
    REVISED = "REVISED"
    CONFLICTED = "CONFLICTED"


def _parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a non-empty string")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone offset")
    return parsed


def _bounded_score(name: str, value: float) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be numeric")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _canonical(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


def _digest(value: Any) -> str:
    payload = json.dumps(
        _canonical(value),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _logit(probability: float) -> float:
    return math.log(probability / (1.0 - probability))


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


@dataclass(frozen=True)
class ReasoningContext:
    """Immutable provider-neutral context envelope for one reasoning request."""

    request_id: str
    created_at: str
    question: str
    world_snapshot_id: str
    world_version: int
    world_observation_ids: tuple[str, ...] = ()
    memory_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("request_id", "question", "world_snapshot_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        _parse_timestamp(self.created_at)
        if not isinstance(self.world_version, int) or self.world_version < 0:
            raise ValueError("world_version must be a non-negative integer")
        for name in ("world_observation_ids", "memory_ids", "assumptions"):
            value = getattr(self, name)
            if not isinstance(value, tuple) or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
            if len(set(value)) != len(value):
                raise ValueError(f"{name} must not contain duplicates")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "created_at": self.created_at,
            "question": self.question,
            "world_snapshot_id": self.world_snapshot_id,
            "world_version": self.world_version,
            "world_observation_ids": self.world_observation_ids,
            "memory_ids": self.memory_ids,
            "assumptions": self.assumptions,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class EvidenceSignal:
    """Bounded evidence assessment used by the reasoning kernel."""

    evidence_id: str
    source_id: str
    polarity: EvidencePolarity
    confidence: float
    relevance: float
    likelihood_ratio: float
    summary: str
    provenance_ids: tuple[str, ...]
    observed_at: str

    def __post_init__(self) -> None:
        for name in ("evidence_id", "source_id", "summary"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.polarity, EvidencePolarity):
            raise TypeError("polarity must be an EvidencePolarity")
        _bounded_score("confidence", self.confidence)
        _bounded_score("relevance", self.relevance)
        if not isinstance(self.likelihood_ratio, (int, float)) or isinstance(self.likelihood_ratio, bool):
            raise TypeError("likelihood_ratio must be numeric")
        if not 0.01 <= float(self.likelihood_ratio) <= 100.0:
            raise ValueError("likelihood_ratio must be between 0.01 and 100")
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise TypeError("provenance_ids must be a tuple of non-empty strings")
        if not self.provenance_ids:
            raise ValueError("evidence requires at least one provenance id")
        if len(set(self.provenance_ids)) != len(self.provenance_ids):
            raise ValueError("provenance_ids must not contain duplicates")
        _parse_timestamp(self.observed_at)

    @property
    def weighted_log_likelihood(self) -> float:
        magnitude = float(self.confidence) * float(self.relevance) * math.log(float(self.likelihood_ratio))
        if self.polarity is EvidencePolarity.CONTRADICTS:
            return -abs(magnitude)
        if self.polarity is EvidencePolarity.SUPPORTS:
            return abs(magnitude)
        return 0.0

    def to_context(self) -> dict[str, object]:
        return {
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
            "polarity": self.polarity.value,
            "confidence": float(self.confidence),
            "relevance": float(self.relevance),
            "likelihood_ratio": float(self.likelihood_ratio),
            "summary": self.summary,
            "provenance_ids": self.provenance_ids,
            "observed_at": self.observed_at,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class Hypothesis:
    """Immutable candidate interpretation; a hypothesis is not a fact."""

    hypothesis_id: str
    statement: str
    prior: float
    context: ReasoningContext
    provenance_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.hypothesis_id, str) or not self.hypothesis_id.strip():
            raise ValueError("hypothesis_id must be a non-empty string")
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError("statement must be a non-empty string")
        if not isinstance(self.context, ReasoningContext):
            raise TypeError("context must be a ReasoningContext")
        if not isinstance(self.prior, (int, float)) or isinstance(self.prior, bool):
            raise TypeError("prior must be numeric")
        if not 0.001 <= float(self.prior) <= 0.999:
            raise ValueError("prior must be between 0.001 and 0.999")
        for name, value in (("provenance_ids", self.provenance_ids), ("assumptions", self.assumptions)):
            if not isinstance(value, tuple) or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
            if len(set(value)) != len(value):
                raise ValueError(f"{name} must not contain duplicates")

    def to_context(self) -> dict[str, object]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "prior": float(self.prior),
            "context_request_id": self.context.request_id,
            "world_snapshot_id": self.context.world_snapshot_id,
            "provenance_ids": self.provenance_ids,
            "assumptions": self.assumptions,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class BeliefRevision:
    """Transparent bounded revision of a hypothesis under explicit evidence."""

    revision_id: str
    hypothesis_id: str
    prior: float
    posterior: float
    net_evidence: float
    support_weight: float
    contradiction_weight: float
    evidence_ids: tuple[str, ...]
    status: RevisionStatus
    update_method: str = "odds-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.revision_id, str) or not self.revision_id.strip():
            raise ValueError("revision_id must be a non-empty string")
        if not isinstance(self.hypothesis_id, str) or not self.hypothesis_id.strip():
            raise ValueError("hypothesis_id must be a non-empty string")
        for name, value in (("prior", self.prior), ("posterior", self.posterior)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 < float(value) < 1.0:
                raise ValueError(f"{name} must be strictly between 0 and 1")
        for name, value in (("support_weight", self.support_weight), ("contradiction_weight", self.contradiction_weight)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if float(value) < 0.0:
                raise ValueError(f"{name} cannot be negative")
        if not isinstance(self.net_evidence, (int, float)) or isinstance(self.net_evidence, bool):
            raise TypeError("net_evidence must be numeric")
        if not isinstance(self.evidence_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.evidence_ids
        ):
            raise TypeError("evidence_ids must be a tuple of non-empty strings")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids must not contain duplicates")
        if not isinstance(self.status, RevisionStatus):
            raise TypeError("status must be a RevisionStatus")
        if not isinstance(self.update_method, str) or not self.update_method.strip():
            raise ValueError("update_method must be non-empty")

    @property
    def uncertainty(self) -> float:
        return 1.0 - abs((float(self.posterior) * 2.0) - 1.0)

    def to_context(self) -> dict[str, object]:
        return {
            "revision_id": self.revision_id,
            "hypothesis_id": self.hypothesis_id,
            "prior": float(self.prior),
            "posterior": float(self.posterior),
            "uncertainty": float(self.uncertainty),
            "net_evidence": float(self.net_evidence),
            "support_weight": float(self.support_weight),
            "contradiction_weight": float(self.contradiction_weight),
            "evidence_ids": self.evidence_ids,
            "status": self.status.value,
            "update_method": self.update_method,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class Prediction:
    """Advisory forecast projection; score is not a calibrated certainty claim."""

    prediction_id: str
    revision_id: str
    outcome: str
    forecast_score: float
    uncertainty: float
    horizon_start: str
    horizon_end: str
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("prediction_id", self.prediction_id),
            ("revision_id", self.revision_id),
            ("outcome", self.outcome),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        _bounded_score("forecast_score", self.forecast_score)
        _bounded_score("uncertainty", self.uncertainty)
        start = _parse_timestamp(self.horizon_start)
        end = _parse_timestamp(self.horizon_end)
        if end <= start:
            raise ValueError("horizon_end must be later than horizon_start")
        if not isinstance(self.assumptions, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.assumptions
        ):
            raise TypeError("assumptions must be a tuple of non-empty strings")
        if len(set(self.assumptions)) != len(self.assumptions):
            raise ValueError("assumptions must not contain duplicates")

    def to_context(self) -> dict[str, object]:
        return {
            "prediction_id": self.prediction_id,
            "revision_id": self.revision_id,
            "outcome": self.outcome,
            "forecast_score": float(self.forecast_score),
            "uncertainty": float(self.uncertainty),
            "horizon_start": self.horizon_start,
            "horizon_end": self.horizon_end,
            "assumptions": self.assumptions,
            "is_advisory": True,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ReasoningTraceStep:
    """Immutable inspectable trace step for one reasoning operation."""

    step_id: str
    kind: ReasoningStepKind
    input_ids: tuple[str, ...]
    output_ids: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not self.step_id.strip():
            raise ValueError("step_id must be a non-empty string")
        if not isinstance(self.kind, ReasoningStepKind):
            raise TypeError("kind must be a ReasoningStepKind")
        for name, value in (("input_ids", self.input_ids), ("output_ids", self.output_ids)):
            if not isinstance(value, tuple) or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
            if len(set(value)) != len(value):
                raise ValueError(f"{name} must not contain duplicates")
        if not isinstance(self.summary, str) or not self.summary.strip():
            raise ValueError("summary must be a non-empty string")

    def to_context(self) -> dict[str, object]:
        return {
            "step_id": self.step_id,
            "kind": self.kind.value,
            "input_ids": self.input_ids,
            "output_ids": self.output_ids,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ReasoningEvaluation:
    """Bounded structural evaluation of a reasoning result."""

    context_id: str
    hypothesis_count: int
    revision_count: int
    conflicted_count: int
    prediction_count: int
    evidence_count: int
    trace_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, str) or not self.context_id.strip():
            raise ValueError("context_id must be a non-empty string")
        for name in (
            "hypothesis_count",
            "revision_count",
            "conflicted_count",
            "prediction_count",
            "evidence_count",
            "trace_count",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.conflicted_count > self.revision_count:
            raise ValueError("conflicted_count cannot exceed revision_count")

    def to_context(self) -> dict[str, object]:
        return {
            "context_id": self.context_id,
            "hypothesis_count": self.hypothesis_count,
            "revision_count": self.revision_count,
            "conflicted_count": self.conflicted_count,
            "prediction_count": self.prediction_count,
            "evidence_count": self.evidence_count,
            "trace_count": self.trace_count,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ReasoningResult:
    """Immutable complete output of one bounded reasoning pass."""

    context: ReasoningContext
    revisions: tuple[BeliefRevision, ...]
    predictions: tuple[Prediction, ...]
    trace: tuple[ReasoningTraceStep, ...]
    evaluation: ReasoningEvaluation

    def __post_init__(self) -> None:
        if not isinstance(self.context, ReasoningContext):
            raise TypeError("context must be a ReasoningContext")
        for name, expected in (
            ("revisions", BeliefRevision),
            ("predictions", Prediction),
            ("trace", ReasoningTraceStep),
        ):
            value = getattr(self, name)
            if not isinstance(value, tuple) or any(not isinstance(item, expected) for item in value):
                raise TypeError(f"{name} must be a tuple of {expected.__name__}")
        if not isinstance(self.evaluation, ReasoningEvaluation):
            raise TypeError("evaluation must be a ReasoningEvaluation")

    @property
    def is_ambiguous(self) -> bool:
        return any(item.status is RevisionStatus.CONFLICTED for item in self.revisions)

    def to_context(self) -> dict[str, object]:
        return {
            "context": self.context.to_context(),
            "revisions": tuple(item.to_context() for item in self.revisions),
            "predictions": tuple(item.to_context() for item in self.predictions),
            "trace": tuple(item.to_context() for item in self.trace),
            "evaluation": self.evaluation.to_context(),
            "ambiguous": self.is_ambiguous,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


class ReasoningSystem:
    """Provider-neutral reasoning kernel below the authority boundary."""

    def revise_belief(
        self,
        hypothesis: Hypothesis,
        evidence: tuple[EvidenceSignal, ...],
    ) -> BeliefRevision:
        if not isinstance(hypothesis, Hypothesis):
            raise TypeError("hypothesis must be a Hypothesis")
        if not isinstance(evidence, tuple) or any(not isinstance(item, EvidenceSignal) for item in evidence):
            raise TypeError("evidence must be a tuple of EvidenceSignal")
        if len({item.evidence_id for item in evidence}) != len(evidence):
            raise ValueError("evidence ids must be unique within a revision")

        weighted_values = [item.weighted_log_likelihood for item in evidence]
        net = sum(weighted_values)
        posterior = _sigmoid(_logit(float(hypothesis.prior)) + net)
        support_weight = sum(max(value, 0.0) for value in weighted_values)
        contradiction_weight = sum(max(-value, 0.0) for value in weighted_values)
        if not evidence:
            status = RevisionStatus.UNCHANGED
        elif support_weight > 0.0 and contradiction_weight > 0.0:
            status = RevisionStatus.CONFLICTED
        else:
            status = RevisionStatus.REVISED
        revision_id = _digest({
            "hypothesis_id": hypothesis.hypothesis_id,
            "prior": float(hypothesis.prior),
            "posterior": posterior,
            "evidence_ids": tuple(item.evidence_id for item in evidence),
            "update_method": "odds-v1",
        })
        return BeliefRevision(
            revision_id=revision_id,
            hypothesis_id=hypothesis.hypothesis_id,
            prior=float(hypothesis.prior),
            posterior=posterior,
            net_evidence=net,
            support_weight=support_weight,
            contradiction_weight=contradiction_weight,
            evidence_ids=tuple(item.evidence_id for item in evidence),
            status=status,
        )

    def predict(
        self,
        revision: BeliefRevision,
        *,
        prediction_id: str,
        outcome: str,
        horizon_start: str,
        horizon_end: str,
        assumptions: tuple[str, ...] = (),
        adjustment: float = 0.0,
    ) -> Prediction:
        if not isinstance(revision, BeliefRevision):
            raise TypeError("revision must be a BeliefRevision")
        if not isinstance(prediction_id, str) or not prediction_id.strip():
            raise ValueError("prediction_id must be a non-empty string")
        if not isinstance(outcome, str) or not outcome.strip():
            raise ValueError("outcome must be a non-empty string")
        if not isinstance(adjustment, (int, float)) or isinstance(adjustment, bool):
            raise TypeError("adjustment must be numeric")
        if not -0.25 <= float(adjustment) <= 0.25:
            raise ValueError("adjustment must be between -0.25 and 0.25")
        score = max(0.0, min(1.0, float(revision.posterior) + float(adjustment)))
        return Prediction(
            prediction_id=prediction_id,
            revision_id=revision.revision_id,
            outcome=outcome,
            forecast_score=score,
            uncertainty=revision.uncertainty,
            horizon_start=horizon_start,
            horizon_end=horizon_end,
            assumptions=assumptions,
        )

    def reason(
        self,
        context: ReasoningContext,
        hypotheses: tuple[Hypothesis, ...],
        evidence: tuple[EvidenceSignal, ...],
        predictions: tuple[Prediction, ...] = (),
    ) -> ReasoningResult:
        if not isinstance(context, ReasoningContext):
            raise TypeError("context must be a ReasoningContext")
        if not isinstance(hypotheses, tuple) or any(not isinstance(item, Hypothesis) for item in hypotheses):
            raise TypeError("hypotheses must be a tuple of Hypothesis")
        if not isinstance(evidence, tuple) or any(not isinstance(item, EvidenceSignal) for item in evidence):
            raise TypeError("evidence must be a tuple of EvidenceSignal")
        if not isinstance(predictions, tuple) or any(not isinstance(item, Prediction) for item in predictions):
            raise TypeError("predictions must be a tuple of Prediction")
        if len({item.hypothesis_id for item in hypotheses}) != len(hypotheses):
            raise ValueError("hypothesis ids must be unique")

        revisions: list[BeliefRevision] = []
        trace: list[ReasoningTraceStep] = [
            ReasoningTraceStep(
                step_id=_digest({"kind": "CONTEXT", "context": context.request_id}),
                kind=ReasoningStepKind.CONTEXT,
                input_ids=(context.world_snapshot_id,),
                output_ids=(context.request_id,),
                summary="reasoning context accepted as bounded input",
            )
        ]
        if evidence:
            trace.append(
                ReasoningTraceStep(
                    step_id=_digest({"kind": "EVIDENCE", "ids": tuple(item.evidence_id for item in evidence)}),
                    kind=ReasoningStepKind.EVIDENCE,
                    input_ids=tuple(item.evidence_id for item in evidence),
                    output_ids=tuple(item.evidence_id for item in evidence),
                    summary="evidence signals retained with explicit polarity and provenance",
                )
            )
        for hypothesis in hypotheses:
            if hypothesis.context.request_id != context.request_id:
                raise ValueError("hypothesis context must match reasoning context")
            revision = self.revise_belief(hypothesis, evidence)
            revisions.append(revision)
            trace.append(
                ReasoningTraceStep(
                    step_id=_digest({"kind": "REVISION", "revision": revision.revision_id}),
                    kind=ReasoningStepKind.REVISION,
                    input_ids=(hypothesis.hypothesis_id,) + revision.evidence_ids,
                    output_ids=(revision.revision_id,),
                    summary=f"belief revision completed with status {revision.status.value}",
                )
            )

        ordered_predictions = tuple(
            sorted(
                predictions,
                key=lambda item: (-float(item.forecast_score), item.prediction_id),
            )
        )
        for prediction in ordered_predictions:
            trace.append(
                ReasoningTraceStep(
                    step_id=_digest({"kind": "PREDICTION", "prediction": prediction.prediction_id}),
                    kind=ReasoningStepKind.PREDICTION,
                    input_ids=(prediction.revision_id,),
                    output_ids=(prediction.prediction_id,),
                    summary="advisory forecast retained with explicit uncertainty",
                )
            )

        evaluation = ReasoningEvaluation(
            context_id=context.request_id,
            hypothesis_count=len(hypotheses),
            revision_count=len(revisions),
            conflicted_count=sum(item.status is RevisionStatus.CONFLICTED for item in revisions),
            prediction_count=len(ordered_predictions),
            evidence_count=len(evidence),
            trace_count=len(trace),
        )
        trace.append(
            ReasoningTraceStep(
                step_id=_digest({"kind": "EVALUATION", "context": context.request_id, "counts": evaluation.to_context()}),
                kind=ReasoningStepKind.EVALUATION,
                input_ids=tuple(item.revision_id for item in revisions),
                output_ids=(context.request_id,),
                summary="reasoning result evaluated for coverage and ambiguity",
            )
        )
        return ReasoningResult(
            context=context,
            revisions=tuple(revisions),
            predictions=ordered_predictions,
            trace=tuple(trace),
            evaluation=evaluation,
        )

    def summary(self) -> Mapping[str, object]:
        return {
            "reasoning_method": "odds-v1",
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
            "provider_selected": False,
        }

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_external_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False

    @property
    def selects_provider(self) -> bool:
        return False


__all__ = [
    "BeliefRevision",
    "EvidencePolarity",
    "EvidenceSignal",
    "Hypothesis",
    "Prediction",
    "ReasoningContext",
    "ReasoningEvaluation",
    "ReasoningResult",
    "ReasoningStepKind",
    "ReasoningSystem",
    "RevisionStatus",
    "ReasoningTraceStep",
]