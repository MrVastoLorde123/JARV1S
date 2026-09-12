"""M32 bridge from an authority handoff to the existing tool authorization boundary.

M32 does not create a second policy system. It validates an M31 handoff,
binds that handoff to one exact ToolRequest, and delegates policy +
confirmation evaluation to the existing ExplicitAuthorizationService.
Authorization is still distinct from execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from src.agents.authority_handoff import AuthorityHandoffRequest, AuthorityHandoffStatus
from src.tools.authorization import AuthorizationDecision, ExplicitAuthorizationService
from src.tools.models import ToolDefinition, ToolRequest


class ConsequenceAuthorizationStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"


@dataclass(frozen=True)
class ConsequenceAuthorizationDecision:
    """Immutable consequence-level authorization result with M31 provenance."""

    authorization_id: str
    handoff_id: str
    claim_id: str
    task_id: str
    consequence_id: str
    tool_name: str
    invocation_id: str | None
    status: ConsequenceAuthorizationStatus
    underlying_decision: AuthorizationDecision
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]
    reason: str | None = None

    @property
    def authorized(self) -> bool:
        return self.status is ConsequenceAuthorizationStatus.AUTHORIZED

    @property
    def execution_allowed(self) -> bool:
        """M32 never authorizes execution as a separate authority concept."""
        return self.authorized

    def to_context(self) -> dict[str, object]:
        return {
            "authority_handoff_id": self.handoff_id,
            "authorization_id": self.authorization_id,
            "claim_id": self.claim_id,
            "task_id": self.task_id,
            "consequence_id": self.consequence_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "authorization_granted": self.authorized,
            "execution_requested": False,
        }


class ConsequenceAuthorizationService:
    """Bridge M31 authority handoffs into the existing M22.8 authorizer."""

    def __init__(
        self,
        authorization_service: ExplicitAuthorizationService,
        *,
        authority_target: str = "coding_confirmation",
    ) -> None:
        if not isinstance(authorization_service, ExplicitAuthorizationService):
            raise TypeError("authorization_service must be an ExplicitAuthorizationService")
        if not isinstance(authority_target, str) or not authority_target.strip():
            raise ValueError("authority_target must be a non-empty string")
        self._authorization_service = authorization_service
        self._authority_target = authority_target

    def authorize(
        self,
        handoff: AuthorityHandoffRequest,
        definition: ToolDefinition,
        request: ToolRequest,
        *,
        authorization_id: str,
    ) -> ConsequenceAuthorizationDecision:
        if not isinstance(handoff, AuthorityHandoffRequest):
            raise TypeError("handoff must be an AuthorityHandoffRequest")
        if handoff.status is not AuthorityHandoffStatus.READY_FOR_AUTHORITY:
            return self._denied(
                handoff,
                request,
                authorization_id,
                reason=f"authority handoff status {handoff.status.value} cannot enter authorization",
            )
        if handoff.authority_target != self._authority_target:
            return self._denied(
                handoff,
                request,
                authorization_id,
                reason="authority handoff target does not match this authorization boundary",
            )
        if not isinstance(definition, ToolDefinition):
            raise TypeError("definition must be a ToolDefinition")
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")
        if not isinstance(authorization_id, str) or not authorization_id.strip():
            raise ValueError("authorization_id must be a non-empty string")

        if request.metadata.get("authority_handoff_id") != handoff.handoff_id:
            return self._denied(
                handoff,
                request,
                authorization_id,
                reason="tool request is not bound to the supplied authority handoff",
            )
        if request.metadata.get("task_id") != handoff.task_id:
            return self._denied(
                handoff,
                request,
                authorization_id,
                reason="tool request task_id does not match the authority handoff",
            )

        underlying = self._authorization_service.authorize(
            definition,
            request,
            authorization_id=authorization_id,
        )
        status = (
            ConsequenceAuthorizationStatus.AUTHORIZED
            if underlying.authorized
            else ConsequenceAuthorizationStatus.DENIED
        )
        return ConsequenceAuthorizationDecision(
            authorization_id=underlying.authorization_id,
            handoff_id=handoff.handoff_id,
            claim_id=handoff.claim_id,
            task_id=handoff.task_id,
            consequence_id=handoff.consequence_id,
            tool_name=request.tool_name,
            invocation_id=request.invocation_id,
            status=status,
            underlying_decision=underlying,
            evidence_refs=handoff.evidence_refs,
            verification_refs=handoff.verification_refs,
            reason=underlying.reason,
        )

    @staticmethod
    def _denied(
        handoff: AuthorityHandoffRequest,
        request: ToolRequest,
        authorization_id: str,
        *,
        reason: str,
    ) -> ConsequenceAuthorizationDecision:
        return ConsequenceAuthorizationDecision(
            authorization_id=authorization_id,
            handoff_id=handoff.handoff_id,
            claim_id=handoff.claim_id,
            task_id=handoff.task_id,
            consequence_id=handoff.consequence_id,
            tool_name=request.tool_name if isinstance(request, ToolRequest) else "",
            invocation_id=request.invocation_id if isinstance(request, ToolRequest) else None,
            status=ConsequenceAuthorizationStatus.DENIED,
            underlying_decision=None,  # type: ignore[arg-type]
            evidence_refs=handoff.evidence_refs,
            verification_refs=handoff.verification_refs,
            reason=reason,
        )


__all__ = [
    "ConsequenceAuthorizationDecision",
    "ConsequenceAuthorizationService",
    "ConsequenceAuthorizationStatus",
]
