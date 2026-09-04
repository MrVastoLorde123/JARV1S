"""M16.4 controlled self-development test and verification boundary.

A TestVerificationGate records whether the checks defined for a controlled
modification plan have been evaluated. Verification is evidence about a
proposed change; it does not authorize, approve, execute, or request execution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.modification_planning import ControlledModificationPlan


class TestVerificationValidationError(ValueError):
    """Raised when a test/verification gate violates the M16.4 boundary."""


class VerificationStatus(str, Enum):
    """Descriptive verification state; never an authority decision."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


MAX_ID_LENGTH = 256
MAX_ITEM_LENGTH = 512
MAX_EVIDENCE_LENGTH = 2048
MAX_LIST_ITEMS = 64
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TestVerificationValidationError(
            f"{field_name} must be a non-empty string"
        )
    if len(value) > maximum:
        raise TestVerificationValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _text_tuple(values: tuple[str, ...], field_name: str, maximum: int = MAX_ITEM_LENGTH) -> None:
    if not isinstance(values, tuple):
        raise TestVerificationValidationError(f"{field_name} must be a tuple")
    if len(values) > MAX_LIST_ITEMS:
        raise TestVerificationValidationError(
            f"{field_name} exceeds maximum count of {MAX_LIST_ITEMS}"
        )
    if len(set(values)) != len(values):
        raise TestVerificationValidationError(f"{field_name} must be unique")
    for index, value in enumerate(values):
        _text(value, f"{field_name}[{index}]", maximum)


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if value != value or abs(value) == float("inf"):
            raise TestVerificationValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise TestVerificationValidationError(
                    f"{path} keys must be non-empty strings"
                )
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise TestVerificationValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class TestVerificationGate:
    """Immutable bounded evidence record for a controlled modification plan."""

    gate_id: str
    plan: ControlledModificationPlan
    status: VerificationStatus = VerificationStatus.PENDING
    required_checks: tuple[str, ...] = ()
    completed_checks: tuple[str, ...] = ()
    failed_checks: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    verifier_notes: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.gate_id, "gate_id", MAX_ID_LENGTH)
        if not isinstance(self.plan, ControlledModificationPlan):
            raise TestVerificationValidationError(
                "plan must be a ControlledModificationPlan"
            )
        if not isinstance(self.status, VerificationStatus):
            raise TestVerificationValidationError(
                "status must be a VerificationStatus"
            )
        _text_tuple(self.required_checks, "required_checks")
        _text_tuple(self.completed_checks, "completed_checks")
        _text_tuple(self.failed_checks, "failed_checks")
        _text_tuple(self.evidence, "evidence", MAX_EVIDENCE_LENGTH)
        _text_tuple(self.verifier_notes, "verifier_notes", MAX_EVIDENCE_LENGTH)

        required = set(self.required_checks)
        completed = set(self.completed_checks)
        failed = set(self.failed_checks)
        if not completed.issubset(required):
            raise TestVerificationValidationError(
                "completed_checks must be a subset of required_checks"
            )
        if not failed.issubset(completed):
            raise TestVerificationValidationError(
                "failed_checks must be a subset of completed_checks"
            )
        if self.status is VerificationStatus.PASSED:
            if not required:
                raise TestVerificationValidationError(
                    "passed verification requires at least one required check"
                )
            if completed != required:
                raise TestVerificationValidationError(
                    "passed verification requires every required check to be completed"
                )
            if failed:
                raise TestVerificationValidationError(
                    "passed verification cannot contain failed checks"
                )
            if not self.evidence:
                raise TestVerificationValidationError(
                    "passed verification requires evidence"
                )
        if self.status is VerificationStatus.FAILED and not failed:
            raise TestVerificationValidationError(
                "failed verification requires at least one failed check"
            )
        if not isinstance(self.metadata, Mapping):
            raise TestVerificationValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise TestVerificationValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def plan_id(self) -> str:
        """Stable lineage back to the M16.3 modification plan."""

        return self.plan.plan_id

    @property
    def assessment_id(self) -> str:
        """Stable lineage back to the M16.2 impact assessment."""

        return self.plan.assessment_id

    @property
    def proposal_id(self) -> str:
        """Stable lineage back to the M16.1 self-development proposal."""

        return self.plan.proposal_id

    @property
    def verified(self) -> bool:
        """True only when the declared checks have passed with evidence."""

        return self.status is VerificationStatus.PASSED

    @property
    def authorization_granted(self) -> bool:
        """Always false: verification evidence never grants authorization."""

        return False

    @property
    def execution_requested(self) -> bool:
        """Always false: verification never requests execution."""

        return False

    def with_required_check(self, check: str) -> "TestVerificationGate":
        _text(check, "check", MAX_ITEM_LENGTH)
        if check in self.required_checks:
            raise TestVerificationValidationError("required check already exists")
        return TestVerificationGate(
            gate_id=self.gate_id,
            plan=self.plan,
            status=self.status,
            required_checks=self.required_checks + (check,),
            completed_checks=self.completed_checks,
            failed_checks=self.failed_checks,
            evidence=self.evidence,
            verifier_notes=self.verifier_notes,
            metadata=self.metadata,
        )

    def with_completed_check(self, check: str) -> "TestVerificationGate":
        _text(check, "check", MAX_ITEM_LENGTH)
        if check not in self.required_checks:
            raise TestVerificationValidationError(
                "completed check must already be required"
            )
        if check in self.completed_checks:
            raise TestVerificationValidationError("completed check already exists")
        return TestVerificationGate(
            gate_id=self.gate_id,
            plan=self.plan,
            status=self.status,
            required_checks=self.required_checks,
            completed_checks=self.completed_checks + (check,),
            failed_checks=self.failed_checks,
            evidence=self.evidence,
            verifier_notes=self.verifier_notes,
            metadata=self.metadata,
        )

    def with_failed_check(self, check: str) -> "TestVerificationGate":
        _text(check, "check", MAX_ITEM_LENGTH)
        if check not in self.completed_checks:
            raise TestVerificationValidationError(
                "failed check must already be completed"
            )
        if check in self.failed_checks:
            raise TestVerificationValidationError("failed check already exists")
        return TestVerificationGate(
            gate_id=self.gate_id,
            plan=self.plan,
            status=self.status,
            required_checks=self.required_checks,
            completed_checks=self.completed_checks,
            failed_checks=self.failed_checks + (check,),
            evidence=self.evidence,
            verifier_notes=self.verifier_notes,
            metadata=self.metadata,
        )

    def with_evidence(self, evidence: str) -> "TestVerificationGate":
        _text(evidence, "evidence", MAX_EVIDENCE_LENGTH)
        if evidence in self.evidence:
            raise TestVerificationValidationError("evidence already exists")
        return TestVerificationGate(
            gate_id=self.gate_id,
            plan=self.plan,
            status=self.status,
            required_checks=self.required_checks,
            completed_checks=self.completed_checks,
            failed_checks=self.failed_checks,
            evidence=self.evidence + (evidence,),
            verifier_notes=self.verifier_notes,
            metadata=self.metadata,
        )

    def with_status(self, status: VerificationStatus) -> "TestVerificationGate":
        if not isinstance(status, VerificationStatus):
            raise TestVerificationValidationError("status must be a VerificationStatus")
        return TestVerificationGate(
            gate_id=self.gate_id,
            plan=self.plan,
            status=status,
            required_checks=self.required_checks,
            completed_checks=self.completed_checks,
            failed_checks=self.failed_checks,
            evidence=self.evidence,
            verifier_notes=self.verifier_notes,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "plan_id": self.plan_id,
            "assessment_id": self.assessment_id,
            "proposal_id": self.proposal_id,
            "status": self.status.value,
            "required_checks": list(self.required_checks),
            "completed_checks": list(self.completed_checks),
            "failed_checks": list(self.failed_checks),
            "evidence": list(self.evidence),
            "verifier_notes": list(self.verifier_notes),
            "metadata": _thaw(self.metadata),
            "verification_gate": True,
            "verified": self.verified,
            "authorization_granted": False,
            "instruction_granted": False,
            "execution_requested": False,
            "policy_authority": False,
            "authority_scope_change_authorized": False,
            "identity_change_authorized": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
