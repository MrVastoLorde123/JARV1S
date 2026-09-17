"""M56: bind an authorized runtime result to the existing M37 outcome boundary.

M55 records continuity from authorization/admission into the exact M36
controlled execution result. M56 classifies that exact result using the
existing M37 outcome contract and prepares bounded verifier input. It does not
perform verification, recovery, authorization, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .authorized_execution_runtime_admission import AuthorizedExecutionRuntimeAdmission
from .execution_outcome import AgencyExecutionOutcome, VerificationInput, build_verification_input, classify_agency_outcome


@dataclass(frozen=True)
class AuthorizedExecutionOutcome:
    """Immutable outcome record bound to one exact authorized runtime admission."""

    runtime_admission: AuthorizedExecutionRuntimeAdmission
    outcome: AgencyExecutionOutcome
    verification_input: VerificationInput
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.runtime_admission, AuthorizedExecutionRuntimeAdmission):
            raise TypeError("runtime_admission must be an AuthorizedExecutionRuntimeAdmission")
        if not isinstance(self.outcome, AgencyExecutionOutcome):
            raise TypeError("outcome must be an AgencyExecutionOutcome")
        if not isinstance(self.verification_input, VerificationInput):
            raise TypeError("verification_input must be a VerificationInput")
        if self.outcome.execution_id != self.runtime_admission.execution_id:
            raise ValueError("outcome execution identity must match the runtime admission")
        expected_request = self.runtime_admission.execution_result.handoff.preparation.request
        if self.outcome.request != expected_request:
            raise ValueError("outcome request must match the admitted execution request")
        if self.outcome.observation_count != self.runtime_admission.steps_executed:
            raise ValueError("outcome observation count must match the runtime execution result")
        if self.outcome.succeeded != self.runtime_admission.succeeded:
            raise ValueError("outcome success state must match the runtime execution result")
        if self.verification_input.outcome != self.outcome:
            raise ValueError("verification input must reference the exact outcome")
        if self.verification_input.expected_request != expected_request:
            raise ValueError("verification input expected request must match the admitted execution request")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.runtime_admission.execution_id

    @property
    def authorization_id(self) -> str:
        return self.runtime_admission.authorization_id

    @property
    def status(self):
        return self.outcome.status

    def to_context(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "confirmation_id": self.runtime_admission.admission.authorization_execution_bridge.authorization.confirmation_id,
            "execution_id": self.execution_id,
            "outcome": self.outcome.to_context(),
            "verification_input": {
                "expected_request": self.verification_input.expected_request,
                "metadata": dict(self.verification_input.metadata),
            },
            "runtime_admission": self.runtime_admission.to_context(),
            "metadata": dict(self.metadata),
            "verification_performed": False,
            "recovery_derived": False,
            "authorization_created": False,
            "execution_requested": False,
        }


def build_authorized_execution_outcome(
    runtime_admission: AuthorizedExecutionRuntimeAdmission,
    *,
    expected_request: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AuthorizedExecutionOutcome:
    """Classify one exact M55 runtime result and build bounded verifier input."""
    if not isinstance(runtime_admission, AuthorizedExecutionRuntimeAdmission):
        raise TypeError("runtime_admission must be an AuthorizedExecutionRuntimeAdmission")
    outcome = classify_agency_outcome(runtime_admission.execution_result)
    request = outcome.request if expected_request is None else expected_request
    verification_input = build_verification_input(
        outcome,
        expected_request=request,
        metadata={"source": "M56", **(dict(metadata) if metadata is not None else {})},
    )
    return AuthorizedExecutionOutcome(
        runtime_admission=runtime_admission,
        outcome=outcome,
        verification_input=verification_input,
        metadata=metadata or {},
    )


__all__ = ["AuthorizedExecutionOutcome", "build_authorized_execution_outcome"]
