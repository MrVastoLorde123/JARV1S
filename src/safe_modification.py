"""M16.5 controlled self-development execution boundary.

SafeModificationExecution is the narrow handoff object between a verified
self-development plan and an execution mechanism. It records an explicit,
verified execution handoff without granting authority, changing policy, or
implicitly executing code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.test_verification import TestVerificationGate


class SafeModificationValidationError(ValueError):
    """Raised when a safe modification execution request violates M16.5."""


class ExecutionHandoffStatus(str, Enum):
    """Lifecycle state of an explicit execution handoff."""

    READY = "ready"
    BLOCKED = "blocked"
    HANDED_OFF = "handed_off"
    NOT_EXECUTED = "not_executed"


MAX_ID_LENGTH = 256
MAX_DESCRIPTION_LENGTH = 2048
MAX_ITEM_LENGTH = 512
MAX_LIST_ITEMS = 64
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SafeModificationValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise SafeModificationValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _text_tuple(values: tuple[str, ...], field_name: str) -> None:
    if not isinstance(values, tuple):
        raise SafeModificationValidationError(f"{field_name} must be a tuple")
    if len(values) > MAX_LIST_ITEMS:
        raise SafeModificationValidationError(
            f"{field_name} exceeds maximum count of {MAX_LIST_ITEMS}"
        )
    if len(set(values)) != len(values):
        raise SafeModificationValidationError(f"{field_name} must be unique")
    for index, value in enumerate(values):
        _text(value, f"{field_name}[{index}]", MAX_ITEM_LENGTH)


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if value != value or abs(value) == float("inf"):
            raise SafeModificationValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise SafeModificationValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise SafeModificationValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class SafeModificationExecution:
    """Immutable, bounded, explicit handoff for a verified self-change."""

    execution_id: str
    verification: TestVerificationGate
    status: ExecutionHandoffStatus = ExecutionHandoffStatus.NOT_EXECUTED
    execution_scope: tuple[str, ...] = ()
    preconditions: tuple[str, ...] = ()
    handoff_notes: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.execution_id, "execution_id", MAX_ID_LENGTH)
        if not isinstance(self.verification, TestVerificationGate):
            raise SafeModificationValidationError(
                "verification must be a TestVerificationGate"
            )
        if not isinstance(self.status, ExecutionHandoffStatus):
            raise SafeModificationValidationError("status must be an ExecutionHandoffStatus")
        _text_tuple(self.execution_scope, "execution_scope")
        _text_tuple(self.preconditions, "preconditions")
        _text_tuple(self.handoff_notes, "handoff_notes")
        if not isinstance(self.metadata, Mapping):
            raise SafeModificationValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise SafeModificationValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

        if self.status in {
            ExecutionHandoffStatus.READY,
            ExecutionHandoffStatus.HANDED_OFF,
        } and not self.verification.verified:
            raise SafeModificationValidationError(
                "ready or handed-off execution requires passed verification"
            )

    @property
    def plan_id(self) -> str:
        return self.verification.plan_id

    @property
    def assessment_id(self) -> str:
        return self.verification.assessment_id

    @property
    def proposal_id(self) -> str:
        return self.verification.proposal_id

    @property
    def verified(self) -> bool:
        return self.verification.verified

    @property
    def authorization_granted(self) -> bool:
        """Always false: execution handoff cannot grant authorization."""

        return False

    @property
    def policy_authority(self) -> bool:
        """Always false: execution cannot alter policy authority."""

        return False

    @property
    def authority_scope_change(self) -> bool:
        """Always false: execution cannot expand JARVIS authority."""

        return False

    @property
    def identity_change_authorized(self) -> bool:
        """Always false: execution cannot authorize an identity change."""

        return False

    @property
    def executed(self) -> bool:
        """Execution has not occurred merely because a handoff exists."""

        return False

    def with_scope(self, scope: str) -> "SafeModificationExecution":
        _text(scope, "scope", MAX_ITEM_LENGTH)
        if scope in self.execution_scope:
            raise SafeModificationValidationError("execution scope already exists")
        return SafeModificationExecution(
            execution_id=self.execution_id,
            verification=self.verification,
            status=self.status,
            execution_scope=self.execution_scope + (scope,),
            preconditions=self.preconditions,
            handoff_notes=self.handoff_notes,
            metadata=self.metadata,
        )

    def with_precondition(self, precondition: str) -> "SafeModificationExecution":
        _text(precondition, "precondition", MAX_ITEM_LENGTH)
        if precondition in self.preconditions:
            raise SafeModificationValidationError("precondition already exists")
        return SafeModificationExecution(
            execution_id=self.execution_id,
            verification=self.verification,
            status=self.status,
            execution_scope=self.execution_scope,
            preconditions=self.preconditions + (precondition,),
            handoff_notes=self.handoff_notes,
            metadata=self.metadata,
        )

    def with_handoff_note(self, note: str) -> "SafeModificationExecution":
        _text(note, "note", MAX_ITEM_LENGTH)
        if note in self.handoff_notes:
            raise SafeModificationValidationError("handoff note already exists")
        return SafeModificationExecution(
            execution_id=self.execution_id,
            verification=self.verification,
            status=self.status,
            execution_scope=self.execution_scope,
            preconditions=self.preconditions,
            handoff_notes=self.handoff_notes + (note,),
            metadata=self.metadata,
        )

    def with_status(self, status: ExecutionHandoffStatus) -> "SafeModificationExecution":
        if not isinstance(status, ExecutionHandoffStatus):
            raise SafeModificationValidationError("status must be an ExecutionHandoffStatus")
        return SafeModificationExecution(
            execution_id=self.execution_id,
            verification=self.verification,
            status=status,
            execution_scope=self.execution_scope,
            preconditions=self.preconditions,
            handoff_notes=self.handoff_notes,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "proposal_id": self.proposal_id,
            "assessment_id": self.assessment_id,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "execution_scope": list(self.execution_scope),
            "preconditions": list(self.preconditions),
            "handoff_notes": list(self.handoff_notes),
            "metadata": _thaw(self.metadata),
            "safe_modification_execution": True,
            "verified": self.verified,
            "authorization_granted": False,
            "policy_authority": False,
            "authority_scope_change": False,
            "identity_change_authorized": False,
            "executed": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
