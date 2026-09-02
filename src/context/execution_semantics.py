"""Deterministic execution-boundary semantics.

M7.10 defines the final provider-neutral handoff into execution. An execution
request may only be prepared from an authorized decision whose authorization
integrity is valid. This module never selects tools, invokes providers,
executes side effects, consumes credentials, or mutates system state.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.authorization_integrity_semantics import (
    AuthorizationIntegrity,
    AuthorizationIntegrityStatus,
)
from src.context.authorization_semantics import AuthorizationDecision, AuthorizationStatus


class ExecutionPreparationStatus(str, Enum):
    READY = "ready"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ExecutionPreparationViolation:
    """A deterministic reason an execution handoff cannot be prepared."""

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
class ExecutionRequest:
    """Provider-neutral handoff describing what an executor may receive."""

    execution_id: str
    request: str
    proposal_id: str
    validation_id: str
    policy_decision_id: str
    confirmation_id: str | None
    authorization_id: str
    operation: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for field_name in (
            "execution_id",
            "request",
            "proposal_id",
            "validation_id",
            "policy_decision_id",
            "authorization_id",
            "operation",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        if self.confirmation_id is not None and (
            not isinstance(self.confirmation_id, str) or not self.confirmation_id.strip()
        ):
            raise ValueError("confirmation_id must be a non-empty string when provided.")
        if not isinstance(self.arguments, Mapping):
            raise TypeError("arguments must be a mapping.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        forbidden = {
            "authorize",
            "authorization",
            "authorized",
            "confirm",
            "confirmation",
            "confirmed",
            "execute",
            "execution",
            "tool_handle",
            "invoke",
            "provider",
            "credential",
            "credentials",
        }
        if any(key in forbidden for key in self.arguments):
            raise ValueError("execution arguments cannot contain authority, execution, provider, or credential controls.")
        if any(key in forbidden for key in self.metadata):
            raise ValueError("execution metadata cannot contain authority, execution, provider, or credential controls.")

    def to_context(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "request": self.request,
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
            "policy_decision_id": self.policy_decision_id,
            "confirmation_id": self.confirmation_id,
            "authorization_id": self.authorization_id,
            "operation": self.operation,
            "arguments": dict(self.arguments),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ExecutionPreparation:
    """Final semantic gate into execution; READY is not actual execution."""

    request: str
    execution_id: str
    status: ExecutionPreparationStatus
    execution_request: ExecutionRequest | None = None
    violations: tuple[ExecutionPreparationViolation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string.")
        if not isinstance(self.status, ExecutionPreparationStatus):
            raise TypeError("status must be an ExecutionPreparationStatus value.")
        if self.execution_request is not None and not isinstance(self.execution_request, ExecutionRequest):
            raise TypeError("execution_request must be an ExecutionRequest or None.")
        if not isinstance(self.violations, tuple):
            raise TypeError("violations must be a tuple.")
        if any(not isinstance(item, ExecutionPreparationViolation) for item in self.violations):
            raise TypeError("violations must contain ExecutionPreparationViolation values.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        if self.status is ExecutionPreparationStatus.READY:
            if self.execution_request is None:
                raise ValueError("READY preparation must contain an execution request.")
            if self.violations:
                raise ValueError("READY preparation cannot contain violations.")
        if self.status is ExecutionPreparationStatus.BLOCKED:
            if self.execution_request is not None:
                raise ValueError("BLOCKED preparation cannot contain an execution request.")
            if not self.violations:
                raise ValueError("BLOCKED preparation must contain a violation.")

    @property
    def ready(self) -> bool:
        return self.status is ExecutionPreparationStatus.READY

    def to_context(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "ready": self.ready,
            "execution_request": None if self.execution_request is None else self.execution_request.to_context(),
            "violations": tuple(item.to_context() for item in self.violations),
            "metadata": dict(self.metadata),
        }


class ExecutionGate:
    """Prepare execution only from an authorized and integrity-valid decision."""

    _FORBIDDEN_KEYS = {
        "authorize",
        "authorization",
        "authorized",
        "confirm",
        "confirmation",
        "confirmed",
        "execute",
        "execution",
        "tool_handle",
        "invoke",
        "provider",
        "credential",
        "credentials",
    }

    def prepare(
        self,
        authorization_decision: AuthorizationDecision,
        authorization_integrity: AuthorizationIntegrity,
        execution_id: str,
        operation: str,
        arguments: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ExecutionPreparation:
        if not isinstance(authorization_decision, AuthorizationDecision):
            raise TypeError("authorization_decision must be an AuthorizationDecision.")
        if not isinstance(authorization_integrity, AuthorizationIntegrity):
            raise TypeError("authorization_integrity must be an AuthorizationIntegrity.")
        if not isinstance(execution_id, str) or not execution_id.strip():
            raise ValueError("execution_id must be a non-empty string.")
        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("operation must be a non-empty string.")
        if arguments is not None and not isinstance(arguments, Mapping):
            raise TypeError("arguments must be a mapping or None.")
        if metadata is not None and not isinstance(metadata, Mapping):
            raise TypeError("metadata must be a mapping or None.")

        violations: list[ExecutionPreparationViolation] = []
        expected = {
            "request": authorization_decision.request,
            "authorization_id": authorization_decision.authorization_id,
            "proposal_id": authorization_decision.proposal_id,
            "validation_id": authorization_decision.validation_id,
            "policy_decision_id": authorization_decision.policy_decision_id,
            "confirmation_id": authorization_decision.confirmation_id,
        }
        actual = {
            "request": authorization_integrity.request,
            "authorization_id": authorization_integrity.authorization_id,
            "proposal_id": authorization_integrity.proposal_id,
            "validation_id": authorization_integrity.validation_id,
            "policy_decision_id": authorization_integrity.policy_decision_id,
            "confirmation_id": authorization_integrity.confirmation_id,
        }

        if authorization_decision.status is not AuthorizationStatus.AUTHORIZED:
            violations.append(
                ExecutionPreparationViolation(
                    "authorization_required",
                    "execution requires an AUTHORIZED authorization decision.",
                )
            )
        if authorization_integrity.status is not AuthorizationIntegrityStatus.VALID:
            violations.append(
                ExecutionPreparationViolation(
                    "authorization_integrity_required",
                    "execution requires VALID authorization integrity.",
                )
            )
        for field_name, expected_value in expected.items():
            if actual[field_name] != expected_value:
                violations.append(
                    ExecutionPreparationViolation(
                        f"integrity_{field_name}_mismatch",
                        f"authorization integrity {field_name} must match the authorization decision.",
                    )
                )
        if execution_id in {
            authorization_decision.authorization_id,
            authorization_decision.policy_decision_id,
            authorization_decision.proposal_id,
            authorization_decision.validation_id,
        } or execution_id == authorization_decision.confirmation_id:
            violations.append(
                ExecutionPreparationViolation(
                    "execution_identity_collision",
                    "execution_id must remain distinct from upstream semantic identities.",
                )
            )
        supplied_arguments = {} if arguments is None else dict(arguments)
        supplied_metadata = {} if metadata is None else dict(metadata)
        if any(key in self._FORBIDDEN_KEYS for key in supplied_arguments):
            violations.append(
                ExecutionPreparationViolation(
                    "forbidden_execution_control",
                    "execution arguments contain authority, execution, provider, or credential controls.",
                )
            )
        if any(key in self._FORBIDDEN_KEYS for key in supplied_metadata):
            violations.append(
                ExecutionPreparationViolation(
                    "forbidden_execution_metadata",
                    "execution metadata contains authority, execution, provider, or credential controls.",
                )
            )

        if violations:
            return ExecutionPreparation(
                request=authorization_decision.request,
                execution_id=execution_id,
                status=ExecutionPreparationStatus.BLOCKED,
                violations=tuple(violations),
                metadata={"execution_semantics": "m7.10"},
            )

        execution_request = ExecutionRequest(
            execution_id=execution_id,
            request=authorization_decision.request,
            proposal_id=authorization_decision.proposal_id,
            validation_id=authorization_decision.validation_id,
            policy_decision_id=authorization_decision.policy_decision_id,
            confirmation_id=authorization_decision.confirmation_id,
            authorization_id=authorization_decision.authorization_id,
            operation=operation,
            arguments=supplied_arguments,
            metadata=supplied_metadata,
        )
        return ExecutionPreparation(
            request=authorization_decision.request,
            execution_id=execution_id,
            status=ExecutionPreparationStatus.READY,
            execution_request=execution_request,
            metadata={"execution_semantics": "m7.10"},
        )
