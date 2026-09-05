"""Explicit authorization boundary for tool requests.

Authorization is deliberately separate from policy, confirmation, and
execution. This module evaluates an existing policy verdict and, when
required, an existing confirmation response, then produces an immutable
authorization decision. It never invokes a handler or grants permission by
itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .confirmation import ConfirmationProvider, ConfirmationResponse
from .errors import (
    InvalidAuthorizationDecisionError,
    InvalidConfirmationResponseError,
    InvalidPolicyVerdictError,
)
from .models import ToolDefinition, ToolRequest
from .policy import Policy, PolicyDecision, PolicyVerdict


class AuthorizationStatus(str, Enum):
    """Whether a request crossed the explicit authorization boundary."""

    GRANTED = "granted"
    DENIED = "denied"


@dataclass(frozen=True)
class AuthorizationDecision:
    """Immutable, inspectable authorization outcome for one request."""

    authorization_id: str
    tool_name: str
    invocation_id: Optional[str]
    policy_decision: PolicyDecision
    confirmation_approved: Optional[bool]
    status: AuthorizationStatus
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.authorization_id, str) or not self.authorization_id.strip():
            raise InvalidAuthorizationDecisionError(
                "authorization_id must be a non-empty string"
            )
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise InvalidAuthorizationDecisionError(
                "tool_name must be a non-empty string"
            )
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise InvalidAuthorizationDecisionError(
                "invocation_id must be a string or None"
            )
        if not isinstance(self.policy_decision, PolicyDecision):
            raise InvalidAuthorizationDecisionError(
                "policy_decision must be a PolicyDecision member"
            )
        if self.confirmation_approved is not None and not isinstance(
            self.confirmation_approved, bool
        ):
            raise InvalidAuthorizationDecisionError(
                "confirmation_approved must be a bool or None"
            )
        if not isinstance(self.status, AuthorizationStatus):
            raise InvalidAuthorizationDecisionError(
                "status must be an AuthorizationStatus member"
            )
        if self.reason is not None and not isinstance(self.reason, str):
            raise InvalidAuthorizationDecisionError("reason must be a string or None")

        if self.status is AuthorizationStatus.GRANTED:
            if self.policy_decision is PolicyDecision.DENY:
                raise InvalidAuthorizationDecisionError(
                    "a policy-denied request cannot be authorized"
                )
            if (
                self.policy_decision is PolicyDecision.REQUIRE_CONFIRMATION
                and self.confirmation_approved is not True
            ):
                raise InvalidAuthorizationDecisionError(
                    "confirmation-required authorization must have approved confirmation"
                )

    @property
    def authorized(self) -> bool:
        return self.status is AuthorizationStatus.GRANTED

    def to_context(self) -> dict[str, object]:
        return {
            "authorization_id": self.authorization_id,
            "tool_name": self.tool_name,
            "policy_decision": self.policy_decision.value,
            "confirmation_approved": self.confirmation_approved,
            "authorization_granted": self.authorized,
            "authority_granted": self.authorized,
            "execution_requested": False,
        }


class ExplicitAuthorizationService:
    """Evaluate policy + confirmation into an explicit authorization result."""

    def __init__(
        self,
        policy: Policy,
        confirmation_provider: ConfirmationProvider,
    ) -> None:
        if not isinstance(policy, Policy):
            raise TypeError("policy must implement Policy")
        if not isinstance(confirmation_provider, ConfirmationProvider):
            raise TypeError(
                "confirmation_provider must implement ConfirmationProvider"
            )
        self._policy = policy
        self._confirmation_provider = confirmation_provider

    def authorize(
        self,
        definition: ToolDefinition,
        request: ToolRequest,
        *,
        authorization_id: str,
    ) -> AuthorizationDecision:
        if not isinstance(definition, ToolDefinition):
            raise TypeError("definition must be a ToolDefinition")
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")

        verdict = self._policy.evaluate(definition, request)
        if not isinstance(verdict, PolicyVerdict):
            raise InvalidPolicyVerdictError(
                f"Policy {self._policy!r} returned {type(verdict).__name__}, expected PolicyVerdict"
            )

        if verdict.decision is PolicyDecision.DENY:
            return AuthorizationDecision(
                authorization_id=authorization_id,
                tool_name=request.tool_name,
                invocation_id=request.invocation_id,
                policy_decision=verdict.decision,
                confirmation_approved=None,
                status=AuthorizationStatus.DENIED,
                reason=verdict.reason
                or f"Tool '{request.tool_name}' was denied by policy",
            )

        if verdict.decision is PolicyDecision.REQUIRE_CONFIRMATION:
            response = self._confirmation_provider.confirm(definition, request)
            if not isinstance(response, ConfirmationResponse):
                raise InvalidConfirmationResponseError(
                    f"Confirmation provider {self._confirmation_provider!r} returned "
                    f"{type(response).__name__}, expected ConfirmationResponse"
                )
            if not response.approved:
                return AuthorizationDecision(
                    authorization_id=authorization_id,
                    tool_name=request.tool_name,
                    invocation_id=request.invocation_id,
                    policy_decision=verdict.decision,
                    confirmation_approved=False,
                    status=AuthorizationStatus.DENIED,
                    reason=response.reason
                    or f"Confirmation was not granted for tool '{request.tool_name}'",
                )
            return AuthorizationDecision(
                authorization_id=authorization_id,
                tool_name=request.tool_name,
                invocation_id=request.invocation_id,
                policy_decision=verdict.decision,
                confirmation_approved=True,
                status=AuthorizationStatus.GRANTED,
                reason=response.reason,
            )

        return AuthorizationDecision(
            authorization_id=authorization_id,
            tool_name=request.tool_name,
            invocation_id=request.invocation_id,
            policy_decision=verdict.decision,
            confirmation_approved=None,
            status=AuthorizationStatus.GRANTED,
            reason=verdict.reason,
        )
