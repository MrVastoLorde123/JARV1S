"""M57: bind an authorized execution outcome to an external verification result.

M56 produces bounded verifier input from the exact M55 runtime admission. M57
accepts the resulting independent verification decision and binds it back to
the same execution outcome. It does not perform verification, recovery,
authorization, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .authorized_execution_outcome import AuthorizedExecutionOutcome
from .execution_outcome import VerificationDecision, VerificationDisposition


@dataclass(frozen=True)
class AuthorizedExecutionVerification:
    """Immutable verification result bound to one exact authorized outcome."""

    authorized_outcome: AuthorizedExecutionOutcome
    verification: VerificationDecision
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.authorized_outcome, AuthorizedExecutionOutcome):
            raise TypeError("authorized_outcome must be an AuthorizedExecutionOutcome")
        if not isinstance(self.verification, VerificationDecision):
            raise TypeError("verification must be a VerificationDecision")
        if self.verification.execution_id != self.authorized_outcome.execution_id:
            raise ValueError("verification execution identity must match the authorized outcome")
        if self.verification.execution_id != self.authorized_outcome.outcome.execution_id:
            raise ValueError("verification must reference the exact M37 outcome execution")
        if self.verification.disposition is VerificationDisposition.VERIFIED and self.verification.evidence_id is None:
            raise ValueError("VERIFIED verification requires evidence_id")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.authorized_outcome.execution_id

    @property
    def authorization_id(self) -> str:
        return self.authorized_outcome.authorization_id

    @property
    def disposition(self) -> VerificationDisposition:
        return self.verification.disposition

    @property
    def evidence_id(self) -> str | None:
        return self.verification.evidence_id

    def to_context(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "execution_id": self.execution_id,
            "verification": {
                "execution_id": self.verification.execution_id,
                "disposition": self.verification.disposition.value,
                "reason": self.verification.reason,
                "evidence_id": self.verification.evidence_id,
                "metadata": dict(self.verification.metadata),
            },
            "authorized_outcome": self.authorized_outcome.to_context(),
            "metadata": dict(self.metadata),
            "verification_performed": True,
            "recovery_derived": False,
            "authorization_created": False,
            "execution_requested": False,
            "execution_performed": False,
        }


def bind_authorized_execution_verification(
    authorized_outcome: AuthorizedExecutionOutcome,
    verification: VerificationDecision,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> AuthorizedExecutionVerification:
    """Bind one externally produced verification decision to the exact outcome."""
    return AuthorizedExecutionVerification(
        authorized_outcome=authorized_outcome,
        verification=verification,
        metadata=metadata or {},
    )


__all__ = ["AuthorizedExecutionVerification", "bind_authorized_execution_verification"]
