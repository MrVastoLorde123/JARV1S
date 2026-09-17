"""M61: structured experience records derived from bounded feedback."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .experience_feedback import ExperienceFeedback


@dataclass(frozen=True)
class ExperienceRecord:
    experience_id: str
    feedback: ExperienceFeedback
    situation: str
    action: str
    result: str
    evidence_ids: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    learning_candidate: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.feedback, ExperienceFeedback):
            raise TypeError("feedback must be an ExperienceFeedback")
        if self.experience_id != self.feedback.experience_id:
            raise ValueError("experience identity must match feedback")
        for name in ("situation", "action", "result"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.evidence_ids, tuple) or any(not isinstance(v, str) or not v.strip() for v in self.evidence_ids):
            raise TypeError("evidence_ids must be a tuple of non-empty strings")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids must be unique")
        if not isinstance(self.tags, tuple) or any(not isinstance(v, str) or not v.strip() for v in self.tags):
            raise TypeError("tags must be a tuple of non-empty strings")
        if len(set(self.tags)) != len(self.tags):
            raise ValueError("tags must be unique")
        if not isinstance(self.learning_candidate, bool):
            raise TypeError("learning_candidate must be a bool")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.feedback.execution_id

    @property
    def verification_evidence_id(self) -> str | None:
        return self.feedback.verification_evidence_id

    def to_context(self) -> dict[str, Any]:
        return {
            "experience_id": self.experience_id,
            "execution_id": self.execution_id,
            "situation": self.situation,
            "action": self.action,
            "result": self.result,
            "evidence_ids": self.evidence_ids,
            "tags": self.tags,
            "learning_candidate": self.learning_candidate,
            "feedback": self.feedback.to_context(),
            "metadata": dict(self.metadata),
            "authority_created": False,
            "execution_requested": False,
        }


def build_experience_record(
    feedback: ExperienceFeedback,
    *,
    situation: str,
    action: str,
    result: str,
    evidence_ids: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
    learning_candidate: bool = True,
    metadata: Mapping[str, Any] | None = None,
) -> ExperienceRecord:
    if not isinstance(feedback, ExperienceFeedback):
        raise TypeError("feedback must be an ExperienceFeedback")
    return ExperienceRecord(
        experience_id=feedback.experience_id,
        feedback=feedback,
        situation=situation,
        action=action,
        result=result,
        evidence_ids=evidence_ids,
        tags=tags,
        learning_candidate=learning_candidate,
        metadata=metadata or {},
    )


__all__ = ["ExperienceRecord", "build_experience_record"]
