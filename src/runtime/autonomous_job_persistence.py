"""M56 provider-neutral persistence boundary for autonomous jobs."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Protocol

from src.runtime.autonomous_job import AutonomousJob


class AutonomousJobPersistenceValidationError(ValueError):
    """Raised when autonomous-job persistence violates its contract."""


class AutonomousJobStore(Protocol):
    """Explicit persistence authority for autonomous job snapshots."""

    def save(self, job: AutonomousJob) -> str:
        """Persist one immutable job snapshot and return a revision identifier."""
        ...

    def load(self, job_id: str) -> AutonomousJob | None:
        """Load the exact job identity or return None when it is absent."""
        ...


@dataclass(frozen=True)
class AutonomousJobPersistenceReceipt:
    """Immutable receipt proving that an injected store accepted a snapshot."""

    receipt_id: str
    job_id: str
    revision: str
    persisted: bool

    def __post_init__(self) -> None:
        for field_name, value in (
            ("receipt_id", self.receipt_id),
            ("job_id", self.job_id),
            ("revision", self.revision),
        ):
            if not isinstance(value, str) or not value.strip():
                raise AutonomousJobPersistenceValidationError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.persisted, bool):
            raise AutonomousJobPersistenceValidationError("persisted must be a bool")
        if not self.persisted:
            raise AutonomousJobPersistenceValidationError(
                "a persistence receipt must represent a persisted job"
            )

    def to_context(self) -> dict[str, object]:
        return {
            "autonomous_job_id": self.job_id,
            "autonomous_job_persistence_receipt_id": self.receipt_id,
            "autonomous_job_persistence_revision": self.revision,
            "autonomous_job_persisted": self.persisted,
            "memory_mutated": True,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "truth_guaranteed": False,
        }


class AutonomousJobPersistenceService:
    """Persist and restore autonomous jobs through an explicitly injected store."""

    def __init__(self, store: AutonomousJobStore | None = None) -> None:
        self._store = store

    def bind(self, store: AutonomousJobStore) -> None:
        if not hasattr(store, "save") or not callable(store.save):
            raise TypeError("store must provide a callable save method")
        if not hasattr(store, "load") or not callable(store.load):
            raise TypeError("store must provide a callable load method")
        self._store = store

    def persist(self, job: AutonomousJob) -> AutonomousJobPersistenceReceipt:
        if not isinstance(job, AutonomousJob):
            raise TypeError("job must be an AutonomousJob")
        if self._store is None:
            raise RuntimeError("autonomous job store is not bound")

        revision = self._store.save(job)
        if not isinstance(revision, str) or not revision.strip():
            raise AutonomousJobPersistenceValidationError(
                "autonomous job store must return a non-empty revision identifier"
            )
        return AutonomousJobPersistenceReceipt(
            receipt_id=self._receipt_id(job.job_id, revision),
            job_id=job.job_id,
            revision=revision,
            persisted=True,
        )

    def restore(self, job_id: str) -> AutonomousJob | None:
        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError("job_id must be a non-empty string")
        if self._store is None:
            raise RuntimeError("autonomous job store is not bound")

        job = self._store.load(job_id)
        if job is None:
            return None
        if not isinstance(job, AutonomousJob):
            raise AutonomousJobPersistenceValidationError(
                "autonomous job store returned an invalid job snapshot"
            )
        if job.job_id != job_id:
            raise AutonomousJobPersistenceValidationError(
                "autonomous job store returned a different job identity"
            )
        return job

    @staticmethod
    def _receipt_id(job_id: str, revision: str) -> str:
        payload = json.dumps(
            {"job_id": job_id, "revision": revision},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"autonomous-job-persistence-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "AutonomousJobPersistenceReceipt",
    "AutonomousJobPersistenceService",
    "AutonomousJobPersistenceValidationError",
    "AutonomousJobStore",
]
