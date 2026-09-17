"""M63: bounded evaluation of learning signals."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .learning_signal import LearningSignal


class LearningEvaluationDisposition(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNCERTAIN = "UNCERTAIN"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class LearningEvaluation:
    evaluation_id: str
    signal: LearningSignal
    disposition: LearningEvaluationDisposition
    confidence: float
    reason: str
    evidence_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.signal, LearningSignal):
            raise TypeError("signal must be a LearningSignal")
        if not isinstance(self.disposition, LearningEvaluationDisposition):
            raise TypeError("disposition must be a LearningEvaluationDisposition")
        if not isinstance(self.evaluation_id, str) or not self.evaluation_id.strip():
            raise ValueError("evaluation_id must be a non-empty string")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.evidence_ids, tuple) or any(not isinstance(v, str) or not v.strip() for v in self.evidence_ids):
            raise TypeError("evidence_ids must be a tuple of non-empty strings")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids must be unique")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def adoptable(self) -> bool:
        return self.disposition is LearningEvaluationDisposition.SUPPORTED and self.confidence >= 0.7

    def to_context(self) -> dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "signal_id": self.signal.signal_id,
            "disposition": self.disposition.value,
            "confidence": float(self.confidence),
            "reason": self.reason,
            "evidence_ids": self.evidence_ids,
            "adoptable": self.adoptable,
            "metadata": dict(self.metadata),
            "authority_created": False,
            "execution_requested": False,
        }


def evaluate_learning_signal(
    signal: LearningSignal,
    *,
    evaluation_id: str,
    disposition: LearningEvaluationDisposition,
    confidence: float,
    reason: str,
    evidence_ids: tuple[str, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> LearningEvaluation:
    return LearningEvaluation(
        evaluation_id=evaluation_id,
        signal=signal,
        disposition=disposition,
        confidence=confidence,
        reason=reason,
        evidence_ids=evidence_ids,
        metadata=metadata or {},
    )


__all__ = ["LearningEvaluation", "LearningEvaluationDisposition", "evaluate_learning_signal"]
