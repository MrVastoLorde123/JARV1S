"""M62: bounded learning signals extracted from structured experience."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .experience_record import ExperienceRecord


@dataclass(frozen=True)
class LearningSignal:
    signal_id: str
    experience: ExperienceRecord
    hypothesis: str
    strength: float
    generalization_scope: str
    value_relevance: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.experience, ExperienceRecord):
            raise TypeError("experience must be an ExperienceRecord")
        if not isinstance(self.signal_id, str) or not self.signal_id.strip():
            raise ValueError("signal_id must be a non-empty string")
        for name in ("hypothesis", "generalization_scope"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("strength", "value_relevance"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        if not self.experience.learning_candidate:
            raise ValueError("non-learning experience cannot produce a learning signal")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "experience_id": self.experience.experience_id,
            "execution_id": self.experience.execution_id,
            "hypothesis": self.hypothesis,
            "strength": float(self.strength),
            "generalization_scope": self.generalization_scope,
            "value_relevance": float(self.value_relevance),
            "experience": self.experience.to_context(),
            "metadata": dict(self.metadata),
            "authority_created": False,
            "execution_requested": False,
        }


def build_learning_signal(
    experience: ExperienceRecord,
    *,
    signal_id: str,
    hypothesis: str,
    strength: float,
    generalization_scope: str,
    value_relevance: float,
    metadata: Mapping[str, Any] | None = None,
) -> LearningSignal:
    return LearningSignal(
        signal_id=signal_id,
        experience=experience,
        hypothesis=hypothesis,
        strength=strength,
        generalization_scope=generalization_scope,
        value_relevance=value_relevance,
        metadata=metadata or {},
    )


__all__ = ["LearningSignal", "build_learning_signal"]
