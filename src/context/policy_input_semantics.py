"""Canonical policy input semantics after consequence validation.

M7.6 defines the narrow, provider-neutral input that a future policy
 evaluator may consume. Construction requires a valid consequence validation
 result and never grants authorization or requests confirmation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.consequence_validation_semantics import (
    ConsequenceValidation,
    ConsequenceValidationStatus,
)
from src.context.proposed_consequence_semantics import ConsequenceKind
from src.context.reasoning_semantics import ReasoningContext


class ActionEffect(str, Enum):
    NONE = "none"
    STATE_CHANGE = "state_change"
    EXTERNAL_COMMUNICATION = "external_communication"
    IRREVERSIBLE = "irreversible"


@dataclass(frozen=True)
class ActionCharacteristics:
    """Descriptive action facts supplied to policy; never authorization."""

    effect: ActionEffect = ActionEffect.NONE
    resource_scope: str = "none"
    sensitivity: float = 0.0
    reversibility: float = 1.0

    def __post_init__(self):
        if not isinstance(self.effect, ActionEffect):
            raise TypeError("effect must be an ActionEffect value.")
        if not isinstance(self.resource_scope, str) or not self.resource_scope.strip():
            raise ValueError("resource_scope must be a non-empty string.")
        if not 0.0 <= self.sensitivity <= 1.0:
            raise ValueError("sensitivity must be between 0.0 and 1.0.")
        if not 0.0 <= self.reversibility <= 1.0:
            raise ValueError("reversibility must be between 0.0 and 1.0.")

    def to_context(self) -> dict[str, Any]:
        return {
            "effect": self.effect.value,
            "resource_scope": self.resource_scope,
            "sensitivity": self.sensitivity,
            "reversibility": self.reversibility,
        }


@dataclass(frozen=True)
class PolicyInputProvenance:
    """Explicit provenance tying policy input to upstream semantic artifacts."""

    proposal_id: str
    validation_id: str

    def __post_init__(self):
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string.")
        if not isinstance(self.validation_id, str) or not self.validation_id.strip():
            raise ValueError("validation_id must be a non-empty string.")

    def to_context(self) -> dict[str, str]:
        return {
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
        }


@dataclass(frozen=True)
class PolicyInput:
    """Canonical authority-relevant facts presented to policy evaluation."""

    request: str
    proposal_id: str
    validation_id: str
    proposal_kind: ConsequenceKind
    validation_status: ConsequenceValidationStatus
    action: ActionCharacteristics
    provenance: PolicyInputProvenance
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string.")
        if not isinstance(self.validation_id, str) or not self.validation_id.strip():
            raise ValueError("validation_id must be a non-empty string.")
        if not isinstance(self.proposal_kind, ConsequenceKind):
            raise TypeError("proposal_kind must be a ConsequenceKind value.")
        if not isinstance(self.validation_status, ConsequenceValidationStatus):
            raise TypeError("validation_status must be a ConsequenceValidationStatus value.")
        if not isinstance(self.action, ActionCharacteristics):
            raise TypeError("action must be an ActionCharacteristics value.")
        if not isinstance(self.provenance, PolicyInputProvenance):
            raise TypeError("provenance must be a PolicyInputProvenance value.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        if self.validation_status is not ConsequenceValidationStatus.VALID:
            raise ValueError("policy input requires VALID consequence validation.")
        if self.provenance.proposal_id != self.proposal_id:
            raise ValueError("provenance proposal_id must match policy input proposal_id.")
        if self.provenance.validation_id != self.validation_id:
            raise ValueError("provenance validation_id must match policy input validation_id.")
        forbidden = {
            "authorize",
            "authorization",
            "authorized",
            "approve",
            "approval",
            "confirm",
            "confirmation",
            "execute",
            "execution",
            "tool_handle",
        }
        if any(key in forbidden for key in self.metadata):
            raise ValueError("policy input metadata cannot contain authority or execution controls.")

    @property
    def authorized(self) -> bool:
        """Policy input never grants authorization."""
        return False

    def to_context(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
            "proposal_kind": self.proposal_kind.value,
            "validation_status": self.validation_status.value,
            "action": self.action.to_context(),
            "provenance": self.provenance.to_context(),
            "metadata": dict(self.metadata),
            "authorized": False,
        }


class PolicyInputProjector:
    """Build policy input only from an already validated proposal."""

    def project(
        self,
        reasoning_context: ReasoningContext,
        validation: ConsequenceValidation,
        proposal_kind: ConsequenceKind,
        proposal_id: str,
        action: ActionCharacteristics | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> PolicyInput:
        if not isinstance(reasoning_context, ReasoningContext):
            raise TypeError("reasoning_context must be a ReasoningContext.")
        if not isinstance(validation, ConsequenceValidation):
            raise TypeError("validation must be a ConsequenceValidation.")
        if not isinstance(proposal_kind, ConsequenceKind):
            raise TypeError("proposal_kind must be a ConsequenceKind value.")
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string.")
        if validation.request != reasoning_context.request:
            raise ValueError("validation request must match reasoning context request.")
        if validation.proposal_id != proposal_id:
            raise ValueError("validation proposal_id must match proposal_id.")
        if validation.status is not ConsequenceValidationStatus.VALID:
            raise ValueError("only VALID consequence validations may become policy input.")
        if action is not None and not isinstance(action, ActionCharacteristics):
            raise TypeError("action must be an ActionCharacteristics value or None.")

        return PolicyInput(
            request=reasoning_context.request,
            proposal_id=proposal_id,
            validation_id=validation.validation_id,
            proposal_kind=proposal_kind,
            validation_status=validation.status,
            action=action or ActionCharacteristics(),
            provenance=PolicyInputProvenance(
                proposal_id=proposal_id,
                validation_id=validation.validation_id,
            ),
            metadata={} if metadata is None else dict(metadata),
        )
