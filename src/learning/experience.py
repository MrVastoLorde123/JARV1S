"""M10.1 immutable learning and experience boundary.

An Experience records what happened around a decision, action, observation,
outcome, and feedback. It is evidence for later learning; it is not truth,
policy, authorization, permission, or execution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


class ExperienceConflictError(ValueError):
    """Raised when an experience identity conflicts with stored state."""


@dataclass(frozen=True)
class Experience:
    """Immutable record of one bounded experience event."""

    experience_id: str
    source: str
    objective_id: str | None = None
    action_reference: str | None = None
    decision_reference: str | None = None
    observations: tuple[str, ...] = ()
    outcome: str = ""
    user_feedback: str | None = None
    evaluation: str | None = None
    confidence: float | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("experience_id", "source"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        for name in ("objective_id", "action_reference", "decision_reference", "user_feedback", "evaluation"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")

        if not isinstance(self.observations, tuple):
            raise TypeError("observations must be a tuple")
        if len(set(self.observations)) != len(self.observations):
            raise ValueError("observations must be unique")
        for observation in self.observations:
            if not isinstance(observation, str) or not observation.strip():
                raise ValueError("observation ids must be non-empty strings")

        if not isinstance(self.outcome, str):
            raise TypeError("outcome must be a string")

        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
                raise TypeError("confidence must be a number or None")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0.0 and 1.0")

        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize the experience without turning evidence into authority."""
        return {
            "experience_id": self.experience_id,
            "source": self.source,
            "objective_id": self.objective_id,
            "action_reference": self.action_reference,
            "decision_reference": self.decision_reference,
            "observations": self.observations,
            "outcome": self.outcome,
            "user_feedback": self.user_feedback,
            "evaluation": self.evaluation,
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "policy_authority": False,
            "authorization_granted": False,
            "execution_requested": False,
        }

    def to_context(self) -> dict[str, Any]:
        """Return a provider-neutral, non-authoritative context projection."""
        return self.to_dict()

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


@dataclass(frozen=True)
class ExperienceStore:
    """Immutable deterministic store keyed by experience_id."""

    experiences: tuple[Experience, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.experiences, tuple):
            raise TypeError("experiences must be a tuple")
        seen: set[str] = set()
        for experience in self.experiences:
            if not isinstance(experience, Experience):
                raise TypeError("experiences must contain Experience values")
            if experience.experience_id in seen:
                raise ExperienceConflictError(
                    f"experience '{experience.experience_id}' is already stored"
                )
            seen.add(experience.experience_id)

    def append(self, experience: Experience) -> "ExperienceStore":
        if not isinstance(experience, Experience):
            raise TypeError("experience must be an Experience")
        if any(item.experience_id == experience.experience_id for item in self.experiences):
            raise ExperienceConflictError(
                f"experience '{experience.experience_id}' is already stored"
            )
        return ExperienceStore(self.experiences + (experience,))

    def get(self, experience_id: str) -> Experience | None:
        for experience in self.experiences:
            if experience.experience_id == experience_id:
                return experience
        return None

    def list(self) -> tuple[Experience, ...]:
        return self.experiences
