"""M16.6 controlled self-development rollback and recovery boundary.

RollbackRecovery records a bounded recovery plan and recovery outcome for a
controlled self-development change. Recovery can restore a known prior state;
it does not create authority, approve changes, or authorize new execution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.safe_modification import SafeModificationExecution


class RollbackRecoveryValidationError(ValueError):
    """Raised when a rollback/recovery record violates the M16.6 boundary."""


class RecoveryStatus(str, Enum):
    """Descriptive recovery lifecycle state; never an authority decision."""

    AVAILABLE = "available"
    NOT_REQUIRED = "not_required"
    REQUESTED = "requested"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


MAX_ID_LENGTH = 256
MAX_ITEM_LENGTH = 512
MAX_DESCRIPTION_LENGTH = 2048
MAX_LIST_ITEMS = 64
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RollbackRecoveryValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise RollbackRecoveryValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _text_tuple(values: tuple[str, ...], field_name: str, maximum: int = MAX_ITEM_LENGTH) -> None:
    if not isinstance(values, tuple):
        raise RollbackRecoveryValidationError(f"{field_name} must be a tuple")
    if len(values) > MAX_LIST_ITEMS:
        raise RollbackRecoveryValidationError(
            f"{field_name} exceeds maximum count of {MAX_LIST_ITEMS}"
        )
    if len(set(values)) != len(values):
        raise RollbackRecoveryValidationError(f"{field_name} must be unique")
    for index, value in enumerate(values):
        _text(value, f"{field_name}[{index}]", maximum)


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if value != value or abs(value) == float("inf"):
            raise RollbackRecoveryValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise RollbackRecoveryValidationError(
                    f"{path} keys must be non-empty strings"
                )
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise RollbackRecoveryValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class RollbackRecovery:
    """Immutable bounded recovery record for a safe self-development handoff."""

    recovery_id: str
    execution: SafeModificationExecution
    prior_state_reference: str
    rollback_strategy: str
    status: RecoveryStatus = RecoveryStatus.AVAILABLE
    recovery_steps: tuple[str, ...] = ()
    recovery_evidence: tuple[str, ...] = ()
    outcome_notes: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.recovery_id, "recovery_id", MAX_ID_LENGTH)
        if not isinstance(self.execution, SafeModificationExecution):
            raise RollbackRecoveryValidationError(
                "execution must be a SafeModificationExecution"
            )
        _text(self.prior_state_reference, "prior_state_reference", MAX_ITEM_LENGTH)
        _text(self.rollback_strategy, "rollback_strategy", MAX_DESCRIPTION_LENGTH)
        if not isinstance(self.status, RecoveryStatus):
            raise RollbackRecoveryValidationError("status must be a RecoveryStatus")
        _text_tuple(self.recovery_steps, "recovery_steps")
        _text_tuple(self.recovery_evidence, "recovery_evidence", MAX_DESCRIPTION_LENGTH)
        _text_tuple(self.outcome_notes, "outcome_notes", MAX_DESCRIPTION_LENGTH)
        if not isinstance(self.metadata, Mapping):
            raise RollbackRecoveryValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise RollbackRecoveryValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

        if self.status in {
            RecoveryStatus.REQUESTED,
            RecoveryStatus.IN_PROGRESS,
            RecoveryStatus.COMPLETED,
        } and not self.execution.verified:
            raise RollbackRecoveryValidationError(
                "active recovery states require verified execution lineage"
            )
        if self.status is RecoveryStatus.COMPLETED and not self.recovery_evidence:
            raise RollbackRecoveryValidationError(
                "completed recovery requires evidence"
            )
        if self.status is RecoveryStatus.FAILED and not self.outcome_notes:
            raise RollbackRecoveryValidationError(
                "failed recovery requires outcome notes"
            )

    @property
    def proposal_id(self) -> str:
        return self.execution.proposal_id

    @property
    def assessment_id(self) -> str:
        return self.execution.assessment_id

    @property
    def plan_id(self) -> str:
        return self.execution.plan_id

    @property
    def execution_id(self) -> str:
        return self.execution.execution_id

    @property
    def recovered(self) -> bool:
        return self.status is RecoveryStatus.COMPLETED

    @property
    def authorization_granted(self) -> bool:
        """Always false: recovery cannot grant authorization."""

        return False

    @property
    def execution_requested(self) -> bool:
        """Always false: recovery does not request new execution."""

        return False

    @property
    def authority_scope_change(self) -> bool:
        """Always false: recovery cannot expand authority."""

        return False

    def with_recovery_step(self, step: str) -> "RollbackRecovery":
        _text(step, "step", MAX_ITEM_LENGTH)
        if step in self.recovery_steps:
            raise RollbackRecoveryValidationError("recovery step already exists")
        return RollbackRecovery(
            recovery_id=self.recovery_id,
            execution=self.execution,
            prior_state_reference=self.prior_state_reference,
            rollback_strategy=self.rollback_strategy,
            status=self.status,
            recovery_steps=self.recovery_steps + (step,),
            recovery_evidence=self.recovery_evidence,
            outcome_notes=self.outcome_notes,
            metadata=self.metadata,
        )

    def with_evidence(self, evidence: str) -> "RollbackRecovery":
        _text(evidence, "evidence", MAX_DESCRIPTION_LENGTH)
        if evidence in self.recovery_evidence:
            raise RollbackRecoveryValidationError("recovery evidence already exists")
        return RollbackRecovery(
            recovery_id=self.recovery_id,
            execution=self.execution,
            prior_state_reference=self.prior_state_reference,
            rollback_strategy=self.rollback_strategy,
            status=self.status,
            recovery_steps=self.recovery_steps,
            recovery_evidence=self.recovery_evidence + (evidence,),
            outcome_notes=self.outcome_notes,
            metadata=self.metadata,
        )

    def with_outcome_note(self, note: str) -> "RollbackRecovery":
        _text(note, "note", MAX_DESCRIPTION_LENGTH)
        if note in self.outcome_notes:
            raise RollbackRecoveryValidationError("outcome note already exists")
        return RollbackRecovery(
            recovery_id=self.recovery_id,
            execution=self.execution,
            prior_state_reference=self.prior_state_reference,
            rollback_strategy=self.rollback_strategy,
            status=self.status,
            recovery_steps=self.recovery_steps,
            recovery_evidence=self.recovery_evidence,
            outcome_notes=self.outcome_notes + (note,),
            metadata=self.metadata,
        )

    def with_status(self, status: RecoveryStatus) -> "RollbackRecovery":
        if not isinstance(status, RecoveryStatus):
            raise RollbackRecoveryValidationError("status must be a RecoveryStatus")
        return RollbackRecovery(
            recovery_id=self.recovery_id,
            execution=self.execution,
            prior_state_reference=self.prior_state_reference,
            rollback_strategy=self.rollback_strategy,
            status=status,
            recovery_steps=self.recovery_steps,
            recovery_evidence=self.recovery_evidence,
            outcome_notes=self.outcome_notes,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "recovery_id": self.recovery_id,
            "proposal_id": self.proposal_id,
            "assessment_id": self.assessment_id,
            "plan_id": self.plan_id,
            "execution_id": self.execution_id,
            "prior_state_reference": self.prior_state_reference,
            "rollback_strategy": self.rollback_strategy,
            "status": self.status.value,
            "recovery_steps": list(self.recovery_steps),
            "recovery_evidence": list(self.recovery_evidence),
            "outcome_notes": list(self.outcome_notes),
            "metadata": _thaw(self.metadata),
            "rollback_recovery": True,
            "recovered": self.recovered,
            "authorization_granted": False,
            "execution_requested": False,
            "authority_scope_change": False,
            "policy_authority": False,
            "identity_change_authorized": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
