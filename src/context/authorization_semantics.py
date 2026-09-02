"""Deterministic authorization semantics after policy and confirmation integrity.

M7.9 produces an explicit authorization artifact when the current policy state
permits the consequence. Confirmation is evidence of an explicit user decision;
authorization is a separate deterministic system decision. Authorization never
selects tools, executes actions, invokes providers, or mutates state.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.confirmation_integrity_semantics import ConfirmationIntegrity, ConfirmationIntegrityStatus
from src.context.confirmation_semantics import ConfirmationResult, ConfirmationStatus
from src.context.policy_evaluation_semantics import PolicyDecision, PolicyOutcome


class AuthorizationStatus(str, Enum):
    AUTHORIZED = "authorized"
    DENIED = "denied"


@dataclass(frozen=True)
class AuthorizationDecision:
    """Deterministic authorization result; never an execution command."""

    authorization_id: str
    request: str
    proposal_id: str
    validation_id: str
    policy_decision_id: str
    confirmation_id: str | None
    status: AuthorizationStatus
    rationale: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for field_name in (
            "authorization_id",
            "request",
            "proposal_id",
            "validation_id",
            "policy_decision_id",
            "rationale",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        if self.confirmation_id is not None and (
            not isinstance(self.confirmation_id, str) or not self.confirmation_id.strip()
        ):
            raise ValueError("confirmation_id must be a non-empty string when provided.")
        if not isinstance(self.status, AuthorizationStatus):
            raise TypeError("status must be an AuthorizationStatus value.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        forbidden = {
            "execute",
            "execution",
            "tool_handle",
            "invoke",
            "provider",
            "confirmed",
        }
        if any(key in forbidden for key in self.metadata):
            raise ValueError("authorization metadata cannot contain execution, provider, or confirmation controls.")

    @property
    def authorized(self) -> bool:
        return self.status is AuthorizationStatus.AUTHORIZED

    def to_context(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "request": self.request,
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
            "policy_decision_id": self.policy_decision_id,
            "confirmation_id": self.confirmation_id,
            "status": self.status.value,
            "authorized": self.authorized,
            "rationale": self.rationale,
            "metadata": dict(self.metadata),
        }


class AuthorizationEvaluator:
    """Authorize only from the supplied policy state and, when required, intact confirmation."""

    def evaluate(
        self,
        policy_decision: PolicyDecision,
        confirmation_result: ConfirmationResult | None = None,
        confirmation_integrity: ConfirmationIntegrity | None = None,
        authorization_id: str = "",
    ) -> AuthorizationDecision:
        if not isinstance(policy_decision, PolicyDecision):
            raise TypeError("policy_decision must be a PolicyDecision.")
        if confirmation_result is not None and not isinstance(confirmation_result, ConfirmationResult):
            raise TypeError("confirmation_result must be a ConfirmationResult or None.")
        if confirmation_integrity is not None and not isinstance(confirmation_integrity, ConfirmationIntegrity):
            raise TypeError("confirmation_integrity must be a ConfirmationIntegrity or None.")
        if not isinstance(authorization_id, str) or not authorization_id.strip():
            raise ValueError("authorization_id must be a non-empty string.")

        confirmation_id = confirmation_result.confirmation_id if confirmation_result is not None else None

        if policy_decision.outcome is PolicyOutcome.DENY:
            return self._decision(
                policy_decision,
                authorization_id,
                AuthorizationStatus.DENIED,
                confirmation_id,
                "policy decision denies authorization.",
            )

        if policy_decision.outcome is PolicyOutcome.ALLOW:
            if confirmation_result is not None or confirmation_integrity is not None:
                return self._decision(
                    policy_decision,
                    authorization_id,
                    AuthorizationStatus.DENIED,
                    confirmation_id,
                    "ALLOW policy does not require a confirmation artifact.",
                )
            return self._decision(
                policy_decision,
                authorization_id,
                AuthorizationStatus.AUTHORIZED,
                None,
                "policy allows the consequence without a confirmation requirement.",
            )

        if policy_decision.outcome is PolicyOutcome.REQUIRE_CONFIRMATION:
            if confirmation_result is None or confirmation_integrity is None:
                return self._decision(
                    policy_decision,
                    authorization_id,
                    AuthorizationStatus.DENIED,
                    confirmation_id,
                    "confirmation and integrity are required before authorization.",
                )
            if confirmation_integrity.status is not ConfirmationIntegrityStatus.VALID:
                return self._decision(
                    policy_decision,
                    authorization_id,
                    AuthorizationStatus.DENIED,
                    confirmation_result.confirmation_id,
                    "confirmation integrity is invalid.",
                )
            if confirmation_result.status is not ConfirmationStatus.CONFIRMED:
                return self._decision(
                    policy_decision,
                    authorization_id,
                    AuthorizationStatus.DENIED,
                    confirmation_result.confirmation_id,
                    "confirmation is not explicitly confirmed.",
                )
            return self._decision(
                policy_decision,
                authorization_id,
                AuthorizationStatus.AUTHORIZED,
                confirmation_result.confirmation_id,
                "policy requires confirmation and the exact confirmation chain is intact and confirmed.",
            )

        raise ValueError("unsupported policy outcome.")

    @staticmethod
    def _decision(
        policy_decision: PolicyDecision,
        authorization_id: str,
        status: AuthorizationStatus,
        confirmation_id: str | None,
        rationale: str,
    ) -> AuthorizationDecision:
        return AuthorizationDecision(
            authorization_id=authorization_id,
            request=policy_decision.request,
            proposal_id=policy_decision.proposal_id,
            validation_id=policy_decision.validation_id,
            policy_decision_id=policy_decision.policy_decision_id,
            confirmation_id=confirmation_id,
            status=status,
            rationale=rationale,
            metadata={"authorization_semantics": "m7.9"},
        )
