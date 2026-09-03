"""M10.2 deterministic evidence and outcome evaluation boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.learning.experience import Experience


class EvaluationState(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    MIXED = "MIXED"
    INCOMPLETE = "INCOMPLETE"
    INCONCLUSIVE = "INCONCLUSIVE"


class EvaluationConflictError(ValueError):
    """Raised when an evaluation identity conflicts with stored state."""


@dataclass(frozen=True)
class Evidence:
    """Explicit evidence signal used by evaluation; it is not truth."""

    evidence_id: str
    signal: str
    supports_success: bool | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_id, str) or not self.evidence_id.strip():
            raise ValueError("evidence_id must be a non-empty string")
        if not isinstance(self.signal, str) or not self.signal.strip():
            raise ValueError("signal must be a non-empty string")
        if self.supports_success is not None and not isinstance(self.supports_success, bool):
            raise TypeError("supports_success must be bool or None")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "signal": self.signal,
            "supports_success": self.supports_success,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "authority_granted": False,
        }


@dataclass(frozen=True)
class OutcomeAssessment:
    """Bounded assessment of explicit evidence against an observed outcome."""

    outcome: str
    evidence: tuple[Evidence, ...] = ()
    complete: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, str):
            raise TypeError("outcome must be a string")
        if not isinstance(self.evidence, tuple):
            raise TypeError("evidence must be a tuple")
        if not all(isinstance(item, Evidence) for item in self.evidence):
            raise TypeError("evidence must contain Evidence values")
        ids = [item.evidence_id for item in self.evidence]
        if len(set(ids)) != len(ids):
            raise ValueError("evidence identities must be unique")
        if not isinstance(self.complete, bool):
            raise TypeError("complete must be a bool")


@dataclass(frozen=True)
class Evaluation:
    """Immutable, inspectable evaluation result; never a truth claim."""

    evaluation_id: str
    experience_id: str
    state: EvaluationState
    evidence_ids: tuple[str, ...]
    rationale: str
    confidence: float | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("evaluation_id", "experience_id", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.state, EvaluationState):
            try:
                object.__setattr__(self, "state", EvaluationState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be an EvaluationState") from exc
        if not isinstance(self.evidence_ids, tuple):
            raise TypeError("evidence_ids must be a tuple")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids must be unique")
        if not all(isinstance(item, str) and item.strip() for item in self.evidence_ids):
            raise ValueError("evidence_ids must contain non-empty strings")
        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
                raise TypeError("confidence must be a number or None")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "experience_id": self.experience_id,
            "state": self.state.value,
            "evidence_ids": self.evidence_ids,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "policy_authority": False,
            "authorization_granted": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class OutcomeEvaluator:
    """Deterministic evaluator using only explicit evidence and outcome completeness."""

    def evaluate(
        self,
        experience: Experience,
        assessment: OutcomeAssessment,
        *,
        evaluation_id: str | None = None,
        confidence: float | None = None,
        provenance: Mapping[str, Any] | None = None,
    ) -> Evaluation:
        if not isinstance(experience, Experience):
            raise TypeError("experience must be an Experience")
        if not isinstance(assessment, OutcomeAssessment):
            raise TypeError("assessment must be an OutcomeAssessment")
        if not assessment.outcome.strip():
            state = EvaluationState.INCOMPLETE
            rationale = "outcome is missing"
        else:
            signals = {item.supports_success for item in assessment.evidence}
            if not assessment.complete:
                state = EvaluationState.INCOMPLETE
                rationale = "evidence set is explicitly incomplete"
            elif not assessment.evidence or signals == {None}:
                state = EvaluationState.INCONCLUSIVE
                rationale = "insufficient explicit directional evidence"
            elif True in signals and False in signals:
                state = EvaluationState.MIXED
                rationale = "explicit evidence contains conflicting outcome signals"
            elif True in signals:
                state = EvaluationState.SUCCESS
                rationale = "explicit evidence supports successful outcome"
            elif False in signals:
                state = EvaluationState.FAILURE
                rationale = "explicit evidence supports unsuccessful outcome"
            else:
                state = EvaluationState.INCONCLUSIVE
                rationale = "evaluation cannot establish a directional outcome"

        return Evaluation(
            evaluation_id=evaluation_id or f"{experience.experience_id}:evaluation",
            experience_id=experience.experience_id,
            state=state,
            evidence_ids=tuple(item.evidence_id for item in assessment.evidence),
            rationale=rationale,
            confidence=confidence,
            provenance=provenance or {"source": "m10.2", "experience_id": experience.experience_id},
        )


@dataclass(frozen=True)
class EvaluationStore:
    evaluations: tuple[Evaluation, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.evaluations, tuple):
            raise TypeError("evaluations must be a tuple")
        seen: set[str] = set()
        for evaluation in self.evaluations:
            if not isinstance(evaluation, Evaluation):
                raise TypeError("evaluations must contain Evaluation values")
            if evaluation.evaluation_id in seen:
                raise EvaluationConflictError(f"evaluation '{evaluation.evaluation_id}' is already stored")
            seen.add(evaluation.evaluation_id)

    def append(self, evaluation: Evaluation) -> "EvaluationStore":
        if not isinstance(evaluation, Evaluation):
            raise TypeError("evaluation must be an Evaluation")
        if any(item.evaluation_id == evaluation.evaluation_id for item in self.evaluations):
            raise EvaluationConflictError(f"evaluation '{evaluation.evaluation_id}' is already stored")
        return EvaluationStore(self.evaluations + (evaluation,))

    def get(self, evaluation_id: str) -> Evaluation | None:
        return next((item for item in self.evaluations if item.evaluation_id == evaluation_id), None)

    def list(self) -> tuple[Evaluation, ...]:
        return self.evaluations
