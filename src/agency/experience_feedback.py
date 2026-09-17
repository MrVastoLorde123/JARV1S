"""M60: bounded experience feedback from reconciled agency outcomes.

Feedback is an observational input to learning. It does not authorize, execute,
verify, persist, or mutate JARVIS state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .authorized_execution_reconciliation import AuthorizedExecutionReconciliation


@dataclass(frozen=True)
class ExperienceFeedback:
    experience_id: str
    reconciliation: AuthorizedExecutionReconciliation
    request: str
    before_status: str
    after_status: str
    verification_disposition: str
    recovery_disposition: str
    succeeded: bool
    value_delta: float | None = None
    notes: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.experience_id, str) or not self.experience_id.strip():
            raise ValueError("experience_id must be a non-empty string")
        if not isinstance(self.reconciliation, AuthorizedExecutionReconciliation):
            raise TypeError("reconciliation must be an AuthorizedExecutionReconciliation")
        for name in ("request", "before_status", "after_status", "verification_disposition", "recovery_disposition"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.succeeded, bool):
            raise TypeError("succeeded must be a bool")
        if self.value_delta is not None and not isinstance(self.value_delta, (int, float)):
            raise TypeError("value_delta must be numeric or None")
        if not isinstance(self.notes, str):
            raise TypeError("notes must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        if self.request != self.reconciliation.authorized_recovery.authorized_verification.authorized_outcome.outcome.request:
            raise ValueError("feedback request must match the reconciled outcome request")
        if self.before_status != self.reconciliation.reconciliation.before.status.value:
            raise ValueError("feedback before_status must match reconciliation")
        if self.after_status != self.reconciliation.reconciliation.after.status.value:
            raise ValueError("feedback after_status must match reconciliation")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.reconciliation.execution_id

    @property
    def authorization_id(self) -> str:
        return self.reconciliation.authorization_id

    @property
    def verification_evidence_id(self) -> str | None:
        return self.reconciliation.authorized_recovery.authorized_verification.evidence_id

    def to_context(self) -> dict[str, Any]:
        return {
            "experience_id": self.experience_id,
            "authorization_id": self.authorization_id,
            "execution_id": self.execution_id,
            "request": self.request,
            "before_status": self.before_status,
            "after_status": self.after_status,
            "verification_disposition": self.verification_disposition,
            "recovery_disposition": self.recovery_disposition,
            "succeeded": self.succeeded,
            "value_delta": self.value_delta,
            "notes": self.notes,
            "metadata": dict(self.metadata),
            "authority_created": False,
            "execution_requested": False,
        }


def build_experience_feedback(
    reconciliation: AuthorizedExecutionReconciliation,
    *,
    experience_id: str,
    value_delta: float | None = None,
    notes: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> ExperienceFeedback:
    if not isinstance(reconciliation, AuthorizedExecutionReconciliation):
        raise TypeError("reconciliation must be an AuthorizedExecutionReconciliation")
    verified = reconciliation.authorized_recovery.authorized_verification
    return ExperienceFeedback(
        experience_id=experience_id,
        reconciliation=reconciliation,
        request=verified.authorized_outcome.outcome.request,
        before_status=reconciliation.reconciliation.before.status.value,
        after_status=reconciliation.reconciliation.after.status.value,
        verification_disposition=verified.disposition.value,
        recovery_disposition=reconciliation.reconciliation.decision.disposition.value,
        succeeded=verified.authorized_outcome.outcome.succeeded,
        value_delta=value_delta,
        notes=notes,
        metadata=metadata or {},
    )


__all__ = ["ExperienceFeedback", "build_experience_feedback"]
