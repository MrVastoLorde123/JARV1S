"""Deterministic confirmation semantics for policy decisions.

M7.8 introduces an explicit human confirmation boundary. Confirmation is a
separate semantic artifact: policy may require it, but only confirmation
resolution can mark an action as confirmed. Confirmation never executes,
selects tools, invokes providers, or mutates state.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.policy_evaluation_semantics import PolicyDecision, PolicyOutcome


class ConfirmationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DENIED = "denied"


@dataclass(frozen=True)
class ConfirmationRequest:
    """A request for explicit user confirmation of one policy decision."""

    confirmation_id: str
    request: str
    proposal_id: str
    validation_id: str
    policy_decision_id: str
    policy_outcome: PolicyOutcome
    prompt: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for field_name in (
            "confirmation_id",
            "request",
            "proposal_id",
            "validation_id",
            "policy_decision_id",
            "prompt",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        if not isinstance(self.policy_outcome, PolicyOutcome):
            raise TypeError("policy_outcome must be a PolicyOutcome value.")
        if self.policy_outcome is not PolicyOutcome.REQUIRE_CONFIRMATION:
            raise ValueError("confirmation requests require REQUIRE_CONFIRMATION policy outcome.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        forbidden = {
            "execute",
            "execution",
            "tool_handle",
            "authorized",
            "authorization",
        }
        if any(key in forbidden for key in self.metadata):
            raise ValueError("confirmation request metadata cannot contain execution or authority controls.")

    def to_context(self) -> dict[str, Any]:
        return {
            "confirmation_id": self.confirmation_id,
            "request": self.request,
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
            "policy_decision_id": self.policy_decision_id,
            "policy_outcome": self.policy_outcome.value,
            "prompt": self.prompt,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ConfirmationResult:
    """Resolution of a confirmation request; never an execution command."""

    confirmation_id: str
    request: str
    proposal_id: str
    validation_id: str
    policy_decision_id: str
    status: ConfirmationStatus
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for field_name in (
            "confirmation_id",
            "request",
            "proposal_id",
            "validation_id",
            "policy_decision_id",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        if not isinstance(self.status, ConfirmationStatus):
            raise TypeError("status must be a ConfirmationStatus value.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        forbidden = {
            "execute",
            "execution",
            "tool_handle",
            "authorized",
            "authorization",
        }
        if any(key in forbidden for key in self.metadata):
            raise ValueError("confirmation result metadata cannot contain execution or authority controls.")

    @property
    def confirmed(self) -> bool:
        return self.status is ConfirmationStatus.CONFIRMED

    def to_context(self) -> dict[str, Any]:
        return {
            "confirmation_id": self.confirmation_id,
            "request": self.request,
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
            "policy_decision_id": self.policy_decision_id,
            "status": self.status.value,
            "confirmed": self.confirmed,
            "metadata": dict(self.metadata),
        }


class ConfirmationManager:
    """Create and resolve explicit confirmation artifacts."""

    def request(
        self,
        policy_decision: PolicyDecision,
        confirmation_id: str,
        prompt: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> ConfirmationRequest:
        if not isinstance(policy_decision, PolicyDecision):
            raise TypeError("policy_decision must be a PolicyDecision.")
        if policy_decision.outcome is not PolicyOutcome.REQUIRE_CONFIRMATION:
            raise ValueError("only REQUIRE_CONFIRMATION policy decisions may create confirmation requests.")
        if not isinstance(confirmation_id, str) or not confirmation_id.strip():
            raise ValueError("confirmation_id must be a non-empty string.")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string.")
        return ConfirmationRequest(
            confirmation_id=confirmation_id,
            request=policy_decision.request,
            proposal_id=policy_decision.proposal_id,
            validation_id=policy_decision.validation_id,
            policy_decision_id=f"policy:{policy_decision.proposal_id}:{policy_decision.validation_id}:{policy_decision.rule_id}",
            policy_outcome=policy_decision.outcome,
            prompt=prompt,
            metadata={} if metadata is None else dict(metadata),
        )

    def resolve(
        self,
        confirmation_request: ConfirmationRequest,
        status: ConfirmationStatus,
    ) -> ConfirmationResult:
        if not isinstance(confirmation_request, ConfirmationRequest):
            raise TypeError("confirmation_request must be a ConfirmationRequest.")
        if not isinstance(status, ConfirmationStatus):
            raise TypeError("status must be a ConfirmationStatus value.")
        if status is ConfirmationStatus.PENDING:
            raise ValueError("resolution must be CONFIRMED or DENIED.")
        return ConfirmationResult(
            confirmation_id=confirmation_request.confirmation_id,
            request=confirmation_request.request,
            proposal_id=confirmation_request.proposal_id,
            validation_id=confirmation_request.validation_id,
            policy_decision_id=confirmation_request.policy_decision_id,
            status=status,
            metadata={"confirmation_semantics": "m7.8"},
        )
