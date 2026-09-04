"""M16.7 controlled self-development integration boundary.

SelfDevelopmentIntegration composes the M16 proposal, impact, planning,
verification, execution-handoff, and rollback records into one descriptive
lifecycle view. It does not introduce a new authority path or execute changes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.change_impact import ChangeImpactAssessment
from src.modification_planning import ControlledModificationPlan
from src.rollback_recovery import RollbackRecovery
from src.safe_modification import SafeModificationExecution
from src.self_development import SelfDevelopmentProposal
from src.test_verification import TestVerificationGate


class SelfDevelopmentIntegrationValidationError(ValueError):
    """Raised when the M16 integration boundary is violated."""


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if value != value or abs(value) == float("inf"):
            raise SelfDevelopmentIntegrationValidationError(
                f"{path} contains a non-finite number"
            )
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise SelfDevelopmentIntegrationValidationError(
                    f"{path} keys must be non-empty strings"
                )
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise SelfDevelopmentIntegrationValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class SelfDevelopmentIntegration:
    """Immutable lifecycle composition for controlled self-development."""

    proposal: SelfDevelopmentProposal
    assessment: ChangeImpactAssessment
    plan: ControlledModificationPlan
    verification: TestVerificationGate
    execution: SafeModificationExecution
    recovery: RollbackRecovery
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        chain = (
            ("proposal", self.proposal, SelfDevelopmentProposal),
            ("assessment", self.assessment, ChangeImpactAssessment),
            ("plan", self.plan, ControlledModificationPlan),
            ("verification", self.verification, TestVerificationGate),
            ("execution", self.execution, SafeModificationExecution),
            ("recovery", self.recovery, RollbackRecovery),
        )
        for name, value, expected in chain:
            if not isinstance(value, expected):
                raise SelfDevelopmentIntegrationValidationError(
                    f"{name} must be a {expected.__name__}"
                )

        if self.assessment.proposal is not self.proposal:
            raise SelfDevelopmentIntegrationValidationError(
                "assessment must reference the same proposal"
            )
        if self.plan.assessment is not self.assessment:
            raise SelfDevelopmentIntegrationValidationError(
                "plan must reference the same assessment"
            )
        if self.verification.plan is not self.plan:
            raise SelfDevelopmentIntegrationValidationError(
                "verification must reference the same plan"
            )
        if self.execution.verification is not self.verification:
            raise SelfDevelopmentIntegrationValidationError(
                "execution must reference the same verification"
            )
        if self.recovery.execution is not self.execution:
            raise SelfDevelopmentIntegrationValidationError(
                "recovery must reference the same execution"
            )

        if not isinstance(self.metadata, Mapping):
            raise SelfDevelopmentIntegrationValidationError("metadata must be a mapping")
        if len(self.metadata) > 32:
            raise SelfDevelopmentIntegrationValidationError(
                "metadata exceeds maximum item count of 32"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def proposal_id(self) -> str:
        return self.proposal.proposal_id

    @property
    def assessment_id(self) -> str:
        return self.assessment.assessment_id

    @property
    def plan_id(self) -> str:
        return self.plan.plan_id

    @property
    def gate_id(self) -> str:
        return self.verification.gate_id

    @property
    def execution_id(self) -> str:
        return self.execution.execution_id

    @property
    def recovery_id(self) -> str:
        return self.recovery.recovery_id

    @property
    def verified(self) -> bool:
        return self.verification.verified

    @property
    def executed(self) -> bool:
        """Always false: composition never performs the underlying change."""

        return False

    @property
    def recovered(self) -> bool:
        return self.recovery.recovered

    @property
    def authorization_granted(self) -> bool:
        """Always false: integration cannot grant authority."""

        return False

    @property
    def policy_authority(self) -> bool:
        return False

    @property
    def authority_scope_change(self) -> bool:
        return False

    @property
    def identity_change_authorized(self) -> bool:
        return False

    @property
    def execution_requested(self) -> bool:
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "assessment_id": self.assessment_id,
            "plan_id": self.plan_id,
            "gate_id": self.gate_id,
            "execution_id": self.execution_id,
            "recovery_id": self.recovery_id,
            "verified": self.verified,
            "executed": self.executed,
            "recovered": self.recovered,
            "metadata": _thaw(self.metadata),
            "self_development_integration": True,
            "authorization_granted": False,
            "policy_authority": False,
            "authority_scope_change": False,
            "identity_change_authorized": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
