"""M10.5 bounded reasoning quality feedback boundary.

This module evaluates reasoning quality from explicit quality signals. It never
claims truth, grants authority, authorizes execution, or mutates policy.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class QualityDimension(str, Enum):
    OUTCOME_ALIGNMENT = "OUTCOME_ALIGNMENT"
    EVIDENCE_USE = "EVIDENCE_USE"
    CLARITY = "CLARITY"
    CONSISTENCY = "CONSISTENCY"
    EFFICIENCY = "EFFICIENCY"


class FeedbackSignal(str, Enum):
    RETAIN = "RETAIN"
    IMPROVE = "IMPROVE"
    CAUTION = "CAUTION"
    INSUFFICIENT = "INSUFFICIENT"


class ReasoningFeedbackConflictError(ValueError):
    """Raised when a reasoning assessment or feedback identity conflicts."""


@dataclass(frozen=True)
class QualitySignal:
    """Explicit bounded signal about one reasoning-quality dimension."""

    signal_id: str
    dimension: QualityDimension
    score: float
    rationale: str
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.signal_id, str) or not self.signal_id.strip():
            raise ValueError("signal_id must be a non-empty string")
        if not isinstance(self.dimension, QualityDimension):
            try:
                object.__setattr__(self, "dimension", QualityDimension(self.dimension))
            except (TypeError, ValueError) as exc:
                raise TypeError("dimension must be a QualityDimension") from exc
        if isinstance(self.score, bool) or not isinstance(self.score, (int, float)):
            raise TypeError("score must be a number")
        if not 0.0 <= float(self.score) <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")
        if not isinstance(self.rationale, str) or not self.rationale.strip():
            raise ValueError("rationale must be a non-empty string")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "dimension": self.dimension.value,
            "score": self.score,
            "rationale": self.rationale,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ReasoningQualityAssessment:
    """Immutable quality assessment of a reasoning trace; not a truth claim."""

    assessment_id: str
    reasoning_id: str
    evaluation_id: str | None
    signal_ids: tuple[str, ...]
    overall_score: float
    confidence: float | None
    rationale: str
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("assessment_id", "reasoning_id", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.evaluation_id is not None and (
            not isinstance(self.evaluation_id, str) or not self.evaluation_id.strip()
        ):
            raise ValueError("evaluation_id must be a non-empty string or None")
        if not isinstance(self.signal_ids, tuple):
            raise TypeError("signal_ids must be a tuple")
        if len(set(self.signal_ids)) != len(self.signal_ids):
            raise ValueError("signal_ids must be unique")
        if not self.signal_ids:
            raise ValueError("at least one quality signal is required")
        if not all(isinstance(item, str) and item.strip() for item in self.signal_ids):
            raise ValueError("signal_ids must contain non-empty strings")
        if isinstance(self.overall_score, bool) or not isinstance(self.overall_score, (int, float)):
            raise TypeError("overall_score must be a number")
        if not 0.0 <= float(self.overall_score) <= 1.0:
            raise ValueError("overall_score must be between 0.0 and 1.0")
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
            "assessment_id": self.assessment_id,
            "reasoning_id": self.reasoning_id,
            "evaluation_id": self.evaluation_id,
            "signal_ids": self.signal_ids,
            "overall_score": self.overall_score,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "policy_authority": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


@dataclass(frozen=True)
class ReasoningFeedback:
    """Immutable bounded learning signal derived from a quality assessment."""

    feedback_id: str
    assessment_id: str
    signal: FeedbackSignal
    target: str
    rationale: str
    confidence: float | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("feedback_id", "assessment_id", "target", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.signal, FeedbackSignal):
            try:
                object.__setattr__(self, "signal", FeedbackSignal(self.signal))
            except (TypeError, ValueError) as exc:
                raise TypeError("signal must be a FeedbackSignal") from exc
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
            "feedback_id": self.feedback_id,
            "assessment_id": self.assessment_id,
            "signal": self.signal.value,
            "target": self.target,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class ReasoningQualityEvaluator:
    """Deterministically turn explicit quality signals into an assessment."""

    def assess(
        self,
        *,
        reasoning_id: str,
        signals: tuple[QualitySignal, ...],
        evaluation_id: str | None = None,
        assessment_id: str | None = None,
        confidence: float | None = None,
        rationale: str | None = None,
        provenance: Mapping[str, Any] | None = None,
    ) -> ReasoningQualityAssessment:
        if not isinstance(signals, tuple):
            raise TypeError("signals must be a tuple")
        if not signals:
            raise ValueError("at least one quality signal is required")
        if not all(isinstance(item, QualitySignal) for item in signals):
            raise TypeError("signals must contain QualitySignal values")
        dimensions = [item.dimension for item in signals]
        if len(set(dimensions)) != len(dimensions):
            raise ValueError("quality dimensions must be unique")
        overall_score = sum(float(item.score) for item in signals) / len(signals)
        derived_rationale = rationale or self._derive_rationale(overall_score)
        return ReasoningQualityAssessment(
            assessment_id=assessment_id or f"{reasoning_id}:quality",
            reasoning_id=reasoning_id,
            evaluation_id=evaluation_id,
            signal_ids=tuple(item.signal_id for item in signals),
            overall_score=overall_score,
            confidence=confidence,
            rationale=derived_rationale,
            provenance=provenance or {"source": "m10.5", "reasoning_id": reasoning_id},
        )

    @staticmethod
    def _derive_rationale(score: float) -> str:
        if score >= 0.8:
            return "quality signals indicate strong reasoning quality"
        if score >= 0.6:
            return "quality signals indicate acceptable reasoning quality"
        if score >= 0.4:
            return "quality signals indicate reasoning quality needs improvement"
        return "quality signals indicate reasoning quality requires caution"


class ReasoningFeedbackController:
    """Generate non-authoritative feedback from an existing assessment."""

    def generate(
        self,
        assessment: ReasoningQualityAssessment,
        *,
        target: str,
        feedback_id: str | None = None,
        confidence: float | None = None,
        rationale: str | None = None,
        provenance: Mapping[str, Any] | None = None,
    ) -> ReasoningFeedback:
        if not isinstance(assessment, ReasoningQualityAssessment):
            raise TypeError("assessment must be a ReasoningQualityAssessment")
        if not isinstance(target, str) or not target.strip():
            raise ValueError("target must be a non-empty string")
        signal = self._signal_for(assessment.overall_score)
        return ReasoningFeedback(
            feedback_id=feedback_id or f"{assessment.assessment_id}:feedback",
            assessment_id=assessment.assessment_id,
            signal=signal,
            target=target,
            rationale=rationale or f"assessment score={assessment.overall_score:.3f}",
            confidence=confidence if confidence is not None else assessment.confidence,
            provenance=provenance or {"source": "m10.5", "assessment_id": assessment.assessment_id},
        )

    @staticmethod
    def _signal_for(score: float) -> FeedbackSignal:
        if score >= 0.8:
            return FeedbackSignal.RETAIN
        if score >= 0.6:
            return FeedbackSignal.IMPROVE
        if score >= 0.4:
            return FeedbackSignal.CAUTION
        return FeedbackSignal.INSUFFICIENT


@dataclass(frozen=True)
class ReasoningQualityStore:
    assessments: tuple[ReasoningQualityAssessment, ...] = ()
    feedback: tuple[ReasoningFeedback, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.assessments, tuple) or not isinstance(self.feedback, tuple):
            raise TypeError("assessments and feedback must be tuples")
        assessment_ids: set[str] = set()
        for item in self.assessments:
            if not isinstance(item, ReasoningQualityAssessment):
                raise TypeError("assessments must contain ReasoningQualityAssessment values")
            if item.assessment_id in assessment_ids:
                raise ReasoningFeedbackConflictError(
                    f"assessment '{item.assessment_id}' is already stored"
                )
            assessment_ids.add(item.assessment_id)
        feedback_ids: set[str] = set()
        for item in self.feedback:
            if not isinstance(item, ReasoningFeedback):
                raise TypeError("feedback must contain ReasoningFeedback values")
            if item.feedback_id in feedback_ids:
                raise ReasoningFeedbackConflictError(
                    f"feedback '{item.feedback_id}' is already stored"
                )
            if item.assessment_id not in assessment_ids:
                raise ValueError("feedback must reference a stored assessment")
            feedback_ids.add(item.feedback_id)

    def append_assessment(self, assessment: ReasoningQualityAssessment) -> "ReasoningQualityStore":
        if not isinstance(assessment, ReasoningQualityAssessment):
            raise TypeError("assessment must be a ReasoningQualityAssessment")
        if any(item.assessment_id == assessment.assessment_id for item in self.assessments):
            raise ReasoningFeedbackConflictError(
                f"assessment '{assessment.assessment_id}' is already stored"
            )
        return ReasoningQualityStore(self.assessments + (assessment,), self.feedback)

    def append_feedback(self, feedback: ReasoningFeedback) -> "ReasoningQualityStore":
        if not isinstance(feedback, ReasoningFeedback):
            raise TypeError("feedback must be a ReasoningFeedback")
        if any(item.feedback_id == feedback.feedback_id for item in self.feedback):
            raise ReasoningFeedbackConflictError(
                f"feedback '{feedback.feedback_id}' is already stored"
            )
        if not any(item.assessment_id == feedback.assessment_id for item in self.assessments):
            raise ValueError("feedback must reference a stored assessment")
        return ReasoningQualityStore(self.assessments, self.feedback + (feedback,))

    def get_assessment(self, assessment_id: str) -> ReasoningQualityAssessment | None:
        return next((item for item in self.assessments if item.assessment_id == assessment_id), None)

    def get_feedback(self, feedback_id: str) -> ReasoningFeedback | None:
        return next((item for item in self.feedback if item.feedback_id == feedback_id), None)

    def to_json(self) -> str:
        return json.dumps(
            {
                "assessments": [item.to_dict() for item in self.assessments],
                "feedback": [item.to_dict() for item in self.feedback],
            },
            sort_keys=True,
            default=str,
        )
