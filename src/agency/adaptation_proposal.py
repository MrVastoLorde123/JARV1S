"""M64: adaptation proposals derived from adoptable learning."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .learning_evaluation import LearningEvaluation


@dataclass(frozen=True)
class AdaptationProposal:
    proposal_id: str
    evaluation: LearningEvaluation
    target: str
    change_type: str
    description: str
    expected_benefit: float
    risk: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.evaluation, LearningEvaluation):
            raise TypeError("evaluation must be a LearningEvaluation")
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        for name in ("target", "change_type", "description"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("expected_benefit", "risk"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")
        if not self.evaluation.adoptable:
            raise ValueError("adaptation proposals require adoptable learning")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def learning_signal_id(self) -> str:
        return self.evaluation.signal.signal_id

    def to_context(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "evaluation_id": self.evaluation.evaluation_id,
            "learning_signal_id": self.learning_signal_id,
            "target": self.target,
            "change_type": self.change_type,
            "description": self.description,
            "expected_benefit": float(self.expected_benefit),
            "risk": float(self.risk),
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
        }


def propose_adaptation(
    evaluation: LearningEvaluation,
    *,
    proposal_id: str,
    target: str,
    change_type: str,
    description: str,
    expected_benefit: float,
    risk: float,
    metadata: Mapping[str, Any] | None = None,
) -> AdaptationProposal:
    return AdaptationProposal(
        proposal_id=proposal_id,
        evaluation=evaluation,
        target=target,
        change_type=change_type,
        description=description,
        expected_benefit=expected_benefit,
        risk=risk,
        metadata=metadata or {},
    )


__all__ = ["AdaptationProposal", "propose_adaptation"]
