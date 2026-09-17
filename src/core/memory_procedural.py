"""M87: procedural knowledge without execution authority."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.persistent_memory import (
    MemoryLifecycle,
    PersistentMemoryKind,
    PersistentMemoryRecord,
)


@dataclass(frozen=True)
class ProcedureStep:
    step_id: str
    description: str
    prerequisites: tuple[str, ...] = ()
    capability_id: str | None = None
    verification: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not self.step_id.strip():
            raise ValueError("step_id must be a non-empty string")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string")
        if not isinstance(self.prerequisites, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.prerequisites
        ):
            raise TypeError("prerequisites must be a tuple of non-empty strings")
        if self.capability_id is not None and (
            not isinstance(self.capability_id, str) or not self.capability_id.strip()
        ):
            raise ValueError("capability_id must be non-empty when provided")
        if self.verification is not None and (
            not isinstance(self.verification, str) or not self.verification.strip()
        ):
            raise ValueError("verification must be non-empty when provided")


@dataclass(frozen=True)
class ProceduralMemory:
    memory_id: str
    subject_id: str
    name: str
    purpose: str
    steps: tuple[ProcedureStep, ...]
    provenance_ids: tuple[str, ...] = ()
    confidence: float = 0.5
    importance: float = 0.5
    status: MemoryLifecycle = MemoryLifecycle.ACTIVE

    def __post_init__(self) -> None:
        for name in ("memory_id", "subject_id", "name", "purpose"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.steps, tuple) or not self.steps:
            raise ValueError("steps must be a non-empty tuple")
        if any(not isinstance(item, ProcedureStep) for item in self.steps):
            raise TypeError("steps must contain ProcedureStep values")
        step_ids = [step.step_id for step in self.steps]
        if len(set(step_ids)) != len(step_ids):
            raise ValueError("procedure step ids must be unique")
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise TypeError("provenance_ids must be a tuple of non-empty strings")
        for name, value in (("confidence", self.confidence), ("importance", self.importance)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if not isinstance(self.status, MemoryLifecycle):
            raise TypeError("status must be a MemoryLifecycle")

    def to_record(self, *, observed_at: str = "") -> PersistentMemoryRecord:
        return PersistentMemoryRecord(
            memory_id=self.memory_id,
            subject_id=self.subject_id,
            kind=PersistentMemoryKind.PROCEDURAL,
            content=self.purpose,
            confidence=self.confidence,
            importance=self.importance,
            status=self.status,
            created_at=observed_at,
            updated_at=observed_at,
            provenance_ids=self.provenance_ids,
            tags=(self.name,),
            metadata={
                "name": self.name,
                "purpose": self.purpose,
                "steps": tuple(
                    {
                        "step_id": step.step_id,
                        "description": step.description,
                        "prerequisites": step.prerequisites,
                        "capability_id": step.capability_id,
                        "verification": step.verification,
                    }
                    for step in self.steps
                ),
                "execution_authorized": False,
            },
        )


__all__ = ["ProcedureStep", "ProceduralMemory"]
