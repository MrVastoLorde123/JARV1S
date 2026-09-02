"""Deterministic integrity validation for confirmation artifacts.

M7.8.1 verifies that a confirmation result remains bound to the exact
confirmation request and upstream policy decision that produced it. Integrity
validation never grants authorization, selects tools, executes actions,
invokes providers, or mutates state.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.confirmation_semantics import (
    ConfirmationRequest,
    ConfirmationResult,
    ConfirmationStatus,
)
from src.context.policy_evaluation_semantics import PolicyDecision, PolicyOutcome


class ConfirmationIntegrityStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"


@dataclass(frozen=True)
class ConfirmationIntegrityViolation:
    """A deterministic confirmation provenance mismatch."""

    code: str
    message: str

    def __post_init__(self):
        if not isinstance(self.code, str) or not self.code.strip():
            raise ValueError("code must be a non-empty string.")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string.")

    def to_context(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class ConfirmationIntegrity:
    """Integrity result; validity never implies authorization or execution."""

    request: str
    confirmation_id: str
    proposal_id: str
    validation_id: str
    policy_decision_id: str
    status: ConfirmationIntegrityStatus
    violations: tuple[ConfirmationIntegrityViolation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for field_name in (
            "request",
            "confirmation_id",
            "proposal_id",
            "validation_id",
            "policy_decision_id",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        if not isinstance(self.status, ConfirmationIntegrityStatus):
            raise TypeError("status must be a ConfirmationIntegrityStatus value.")
        if not isinstance(self.violations, tuple):
            raise TypeError("violations must be a tuple.")
        if any(not isinstance(item, ConfirmationIntegrityViolation) for item in self.violations):
            raise TypeError("violations must contain ConfirmationIntegrityViolation values.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        has_violations = bool(self.violations)
        if self.status is ConfirmationIntegrityStatus.VALID and has_violations:
            raise ValueError("valid integrity cannot contain violations.")
        if self.status is ConfirmationIntegrityStatus.INVALID and not has_violations:
            raise ValueError("invalid integrity must contain a violation.")

    @property
    def intact(self) -> bool:
        return self.status is ConfirmationIntegrityStatus.VALID

    def to_context(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "confirmation_id": self.confirmation_id,
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
            "policy_decision_id": self.policy_decision_id,
            "status": self.status.value,
            "intact": self.intact,
            "violations": tuple(item.to_context() for item in self.violations),
            "metadata": dict(self.metadata),
        }


class ConfirmationIntegrityValidator:
    """Verify exact continuity from policy decision through confirmation result."""

    def validate(
        self,
        policy_decision: PolicyDecision,
        confirmation_request: ConfirmationRequest,
        confirmation_result: ConfirmationResult,
    ) -> ConfirmationIntegrity:
        if not isinstance(policy_decision, PolicyDecision):
            raise TypeError("policy_decision must be a PolicyDecision.")
        if not isinstance(confirmation_request, ConfirmationRequest):
            raise TypeError("confirmation_request must be a ConfirmationRequest.")
        if not isinstance(confirmation_result, ConfirmationResult):
            raise TypeError("confirmation_result must be a ConfirmationResult.")

        violations: list[ConfirmationIntegrityViolation] = []

        if policy_decision.outcome is not PolicyOutcome.REQUIRE_CONFIRMATION:
            violations.append(
                ConfirmationIntegrityViolation(
                    "policy_confirmation_not_required",
                    "upstream policy decision does not require confirmation.",
                )
            )

        expected_chain = {
            "request": policy_decision.request,
            "proposal_id": policy_decision.proposal_id,
            "validation_id": policy_decision.validation_id,
            "policy_decision_id": policy_decision.policy_decision_id,
        }
        request_chain = {
            "request": confirmation_request.request,
            "proposal_id": confirmation_request.proposal_id,
            "validation_id": confirmation_request.validation_id,
            "policy_decision_id": confirmation_request.policy_decision_id,
        }
        result_chain = {
            "request": confirmation_result.request,
            "proposal_id": confirmation_result.proposal_id,
            "validation_id": confirmation_result.validation_id,
            "policy_decision_id": confirmation_result.policy_decision_id,
        }

        for field_name, expected in expected_chain.items():
            if request_chain[field_name] != expected:
                violations.append(
                    ConfirmationIntegrityViolation(
                        f"request_{field_name}_mismatch",
                        f"confirmation request {field_name} does not match the policy decision.",
                    )
                )
            if result_chain[field_name] != expected:
                violations.append(
                    ConfirmationIntegrityViolation(
                        f"result_{field_name}_mismatch",
                        f"confirmation result {field_name} does not match the policy decision.",
                    )
                )

        if confirmation_result.confirmation_id != confirmation_request.confirmation_id:
            violations.append(
                ConfirmationIntegrityViolation(
                    "confirmation_id_mismatch",
                    "confirmation result must resolve the exact confirmation request.",
                )
            )

        if confirmation_result.status is ConfirmationStatus.PENDING:
            violations.append(
                ConfirmationIntegrityViolation(
                    "pending_resolution",
                    "confirmation integrity requires a terminal confirmation resolution.",
                )
            )

        status = (
            ConfirmationIntegrityStatus.INVALID
            if violations
            else ConfirmationIntegrityStatus.VALID
        )
        return ConfirmationIntegrity(
            request=policy_decision.request,
            confirmation_id=confirmation_request.confirmation_id,
            proposal_id=policy_decision.proposal_id,
            validation_id=policy_decision.validation_id,
            policy_decision_id=policy_decision.policy_decision_id,
            status=status,
            violations=tuple(violations),
            metadata={"confirmation_integrity_semantics": "m7.8.1"},
        )
