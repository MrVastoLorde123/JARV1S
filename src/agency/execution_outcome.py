"""M37: bounded execution outcome and verification boundary.

M36 records what controlled agency observed after consuming an authorized
execution preparation. M37 separates that observation from the independent
question of whether the intended work is actually verified complete.

This module does not authorize, execute, or manufacture verification evidence.
It provides immutable outcome classification and a narrow verification input
contract for an existing verifier.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .execution_bridge import AgencyExecutionBridgeResult


class AgencyOutcomeStatus(str, Enum):
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class VerificationDisposition(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class AgencyExecutionOutcome:
    """Immutable classification of one bounded agency result."""

    execution_id: str
    request: str
    status: AgencyOutcomeStatus
    observation_count: int
    succeeded: bool
    error: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("execution_id", "request"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, AgencyOutcomeStatus):
            raise TypeError("status must be an AgencyOutcomeStatus")
        if not isinstance(self.observation_count, int) or isinstance(self.observation_count, bool) or self.observation_count < 0:
            raise ValueError("observation_count must be a non-negative integer")
        if not isinstance(self.succeeded, bool):
            raise TypeError("succeeded must be a bool")
        if self.status is AgencyOutcomeStatus.SUCCEEDED and not self.succeeded:
            raise ValueError("SUCCEEDED outcome must set succeeded=True")
        if self.status is not AgencyOutcomeStatus.SUCCEEDED and self.succeeded:
            raise ValueError("only SUCCEEDED outcome may set succeeded=True")
        if self.error is not None and not isinstance(self.error, Mapping):
            raise TypeError("error must be a mapping or None")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "error", None if self.error is None else MappingProxyType(dict(self.error)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "request": self.request,
            "status": self.status.value,
            "observation_count": self.observation_count,
            "succeeded": self.succeeded,
            "error": None if self.error is None else dict(self.error),
            "metadata": dict(self.metadata),
            "verification_guaranteed": False,
        }


@dataclass(frozen=True)
class VerificationInput:
    """Bounded facts supplied to an existing verifier; not verification itself."""

    outcome: AgencyExecutionOutcome
    expected_request: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, AgencyExecutionOutcome):
            raise TypeError("outcome must be an AgencyExecutionOutcome")
        if not isinstance(self.expected_request, str) or not self.expected_request.strip():
            raise ValueError("expected_request must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class VerificationDecision:
    """Immutable result returned by an external verifier."""

    execution_id: str
    disposition: VerificationDisposition
    reason: str
    evidence_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")
        if not isinstance(self.disposition, VerificationDisposition):
            raise TypeError("disposition must be a VerificationDisposition")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if self.evidence_id is not None and (not isinstance(self.evidence_id, str) or not self.evidence_id.strip()):
            raise ValueError("evidence_id must be a non-empty string or None")
        if self.disposition is VerificationDisposition.VERIFIED and self.evidence_id is None:
            raise ValueError("VERIFIED requires evidence_id")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class AgencyVerifier(Protocol):
    """Existing verifier boundary consuming bounded verification input."""

    def verify(self, input: VerificationInput) -> VerificationDecision:
        ...


def classify_agency_outcome(result: AgencyExecutionBridgeResult) -> AgencyExecutionOutcome:
    """Classify observed agency execution without asserting independent verification."""
    if not isinstance(result, AgencyExecutionBridgeResult):
        raise TypeError("result must be an AgencyExecutionBridgeResult")
    stop_reason = result.agency_result.stop_reason.value
    if result.agency_result.steps_executed == 0:
        status = AgencyOutcomeStatus.BLOCKED if stop_reason != "completed" else AgencyOutcomeStatus.NOT_ATTEMPTED
        succeeded = False
    elif result.succeeded:
        status = AgencyOutcomeStatus.SUCCEEDED
        succeeded = True
    else:
        status = AgencyOutcomeStatus.FAILED
        succeeded = False
    error = None if result.succeeded else {"stop_reason": stop_reason}
    return AgencyExecutionOutcome(
        execution_id=result.execution_id,
        request=result.handoff.preparation.request,
        status=status,
        observation_count=result.steps_executed,
        succeeded=succeeded,
        error=error,
        metadata={"source": "M37", "stop_reason": stop_reason},
    )


def build_verification_input(
    outcome: AgencyExecutionOutcome,
    *,
    expected_request: str,
    metadata: Mapping[str, Any] | None = None,
) -> VerificationInput:
    """Build verifier input without performing verification."""
    return VerificationInput(
        outcome=outcome,
        expected_request=expected_request,
        metadata=metadata or {},
    )


__all__ = [
    "AgencyExecutionOutcome",
    "AgencyOutcomeStatus",
    "AgencyVerifier",
    "VerificationDecision",
    "VerificationDisposition",
    "VerificationInput",
    "build_verification_input",
    "classify_agency_outcome",
]
