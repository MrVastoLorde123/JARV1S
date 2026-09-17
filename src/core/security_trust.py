"""M78: deterministic trust and risk assessment from explicit evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _score(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if result < 0.0 or result > 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return result


@dataclass(frozen=True)
class TrustEvidence:
    evidence_id: str
    subject_id: str
    source: str
    score: float
    reliable: bool = True
    description: str = ""
    metadata: Mapping[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        for name in ("evidence_id", "subject_id", "source"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(self, "score", _score(self.score, "score"))
        if not isinstance(self.reliable, bool):
            raise TypeError("reliable must be a bool")
        if not isinstance(self.description, str):
            raise TypeError("description must be a string")
        metadata = {} if self.metadata is None else self.metadata
        if not isinstance(metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(metadata)))


@dataclass(frozen=True)
class TrustPolicy:
    minimum_score: float = 0.7
    maximum_risk: RiskLevel = RiskLevel.MEDIUM

    def __post_init__(self) -> None:
        object.__setattr__(self, "minimum_score", _score(self.minimum_score, "minimum_score"))
        if not isinstance(self.maximum_risk, RiskLevel):
            raise TypeError("maximum_risk must be a RiskLevel")


@dataclass(frozen=True)
class TrustAssessment:
    subject_id: str
    score: float
    risk_level: RiskLevel
    trusted: bool
    evidence_count: int
    reason: str
    evidence: tuple[TrustEvidence, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "subject_id", _text(self.subject_id, "subject_id"))
        object.__setattr__(self, "score", _score(self.score, "score"))
        if not isinstance(self.risk_level, RiskLevel):
            raise TypeError("risk_level must be a RiskLevel")
        if not isinstance(self.trusted, bool):
            raise TypeError("trusted must be a bool")
        if not isinstance(self.evidence_count, int) or isinstance(self.evidence_count, bool) or self.evidence_count < 0:
            raise ValueError("evidence_count must be a non-negative integer")
        object.__setattr__(self, "reason", _text(self.reason, "reason"))
        if not isinstance(self.evidence, tuple) or any(not isinstance(item, TrustEvidence) for item in self.evidence):
            raise TypeError("evidence must contain TrustEvidence values")

    def to_context(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "score": self.score,
            "risk_level": self.risk_level.value,
            "trusted": self.trusted,
            "evidence_count": self.evidence_count,
            "reason": self.reason,
            "evidence_ids": tuple(item.evidence_id for item in self.evidence),
            "authority_granted": False,
        }


class TrustModel:
    def __init__(self, evidence: Sequence[TrustEvidence] = (), policy: TrustPolicy | None = None) -> None:
        values = tuple(evidence)
        if any(not isinstance(item, TrustEvidence) for item in values):
            raise TypeError("evidence must contain TrustEvidence values")
        ids = [item.evidence_id for item in values]
        if len(ids) != len(set(ids)):
            raise ValueError("trust evidence IDs must be unique")
        self._evidence = values
        self._policy = policy or TrustPolicy()

    @property
    def policy(self) -> TrustPolicy:
        return self._policy

    def assess(self, subject_id: str) -> TrustAssessment:
        subject_id = _text(subject_id, "subject_id")
        relevant = tuple(item for item in self._evidence if item.subject_id == subject_id and item.reliable)
        score = 0.0 if not relevant else sum(item.score for item in relevant) / len(relevant)
        if score >= self._policy.minimum_score and relevant:
            risk = RiskLevel.LOW
        elif score >= 0.5:
            risk = RiskLevel.MEDIUM
        elif score > 0.0:
            risk = RiskLevel.HIGH
        else:
            risk = RiskLevel.CRITICAL
        allowed_risk = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2, RiskLevel.CRITICAL: 3}
        trusted = bool(relevant) and score >= self._policy.minimum_score and allowed_risk[risk] <= allowed_risk[self._policy.maximum_risk]
        reason = "trust threshold satisfied" if trusted else "trust evidence is insufficient for the security policy"
        return TrustAssessment(subject_id, score, risk, trusted, len(relevant), reason, relevant)

    def snapshot(self) -> tuple[TrustEvidence, ...]:
        return self._evidence


__all__ = ["RiskLevel", "TrustEvidence", "TrustPolicy", "TrustAssessment", "TrustModel"]
