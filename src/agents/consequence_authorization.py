"""M32 bridge from an authority handoff to the existing tool authorization boundary.

M32 does not create a second policy system. It validates an M31 handoff,
binds that handoff to one exact ToolRequest, and delegates policy +
confirmation evaluation to the existing ExplicitAuthorizationService.
Authorization is still distinct from execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

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
    underlying_decision: AuthorizationDecision | None
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]
    verification_freshness: str = "UNASSESSED"
    verification_valid_until: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.authorization_id, str) or not self.authorization_id.strip():
            raise ValueError("authorization_id must be a non-empty string")
        if not isinstance(self.handoff_id, str) or not self.handoff_id.strip():
            raise ValueError("handoff_id must be a non-empty string")
        if not isinstance(self.claim_id, str) or not self.claim_id.strip():
            raise ValueError("claim_id must be a non-empty string")
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(self.consequence_id, str) or not self.consequence_id.strip():
            raise ValueError("consequence_id must be a non-empty string")
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise ValueError("tool_name must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        if not isinstance(self.status, ConsequenceAuthorizationStatus):
            raise TypeError("status must be a ConsequenceAuthorizationStatus")
        if self.underlying_decision is not None and not isinstance(
            self.underlying_decision, AuthorizationDecision
        ):
            raise TypeError("underlying_decision must be an AuthorizationDecision or None")
        if any(not isinstance(ref, str) or not ref for ref in self.evidence_refs):
            raise TypeError("evidence_refs must contain non-empty strings")
        if any(not isinstance(ref, str) or not ref for ref in self.verification_refs):
            raise TypeError("verification_refs must contain non-empty strings")
        if not isinstance(self.verification_freshness, str) or not self.verification_freshness.strip():
            raise TypeError("verification_freshness must be a non-empty string")
        if self.verification_valid_until is not None and (
            not isinstance(self.verification_valid_until, str)
            or not self.verification_valid_until.strip()
        ):
            raise TypeError("verification_valid_until must be a non-empty string or None")
        if self.reason is not None and not isinstance(self.reason, str):
            raise TypeError("reason must be a string or None")

        if self.status is ConsequenceAuthorizationStatus.AUTHORIZED:
            if self.underlying_decision is None or not self.underlying_decision.authorized:
                raise ValueError("AUTHORIZED requires an authorized underlying decision")
        elif self.underlying_decision is not None and self.underlying_decision.authorized:
            raise ValueError("DENIED cannot wrap an authorized underlying decision")

    @property
    def authorized(self) -> bool:
        return self.status is ConsequenceAuthorizationStatus.AUTHORIZED

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
            "verification_freshness": self.verification_freshness,
            "verification_valid_until": self.verification_valid_until,
            "execution_requested": False,
        }


class ConsequenceAuthorizationService:
    """Bridge M31 authority handoffs into the existing M22.8 authorizer."""

    def __init__(
        self,
        authorization_service: ExplicitAuthorizationService,
        *,
        authority_target: str = "coding_confirmation",
        clock=None,
    ) -> None:
        if not isinstance(authorization_service, ExplicitAuthorizationService):
            raise TypeError("authorization_service must be an ExplicitAuthorizationService")
        if not isinstance(authority_target, str) or not authority_target.strip():
            raise ValueError("authority_target must be a non-empty string")
        self._authorization_service = authorization_service
        self._authority_target = authority_target
        self._clock = clock or (lambda: datetime.now(timezone.utc))

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
        if not isinstance(definition, ToolDefinition):
            raise TypeError("definition must be a ToolDefinition")
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")
        if not isinstance(authorization_id, str) or not authorization_id.strip():
            raise ValueError("authorization_id must be a non-empty string")

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

        requires_current = bool(
            (handoff.consequence_metadata or {}).get("requires_current_verification", False)
        )
        if requires_current:
            valid_until = handoff.verification_valid_until
            if not isinstance(valid_until, str) or not valid_until.strip():
                return self._denied(
                    handoff,
                    request,
                    authorization_id,
                    reason="current verification handoff has no validity deadline",
                )
            try:
                expiry = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
            except ValueError:
                return self._denied(
                    handoff,
                    request,
                    authorization_id,
                    reason="current verification validity deadline is invalid",
                )
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            now = self._clock()
            if not isinstance(now, datetime):
                raise TypeError("clock must return a datetime")
            if now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)
            if now >= expiry:
                return self._denied(
                    handoff,
                    request,
                    authorization_id,
                    reason="current verification evidence expired before authorization",
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
            verification_freshness=handoff.verification_freshness,
            verification_valid_until=handoff.verification_valid_until,
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
            tool_name=request.tool_name,
            invocation_id=request.invocation_id,
            status=ConsequenceAuthorizationStatus.DENIED,
            underlying_decision=None,
            evidence_refs=handoff.evidence_refs,
            verification_refs=handoff.verification_refs,
            verification_freshness=handoff.verification_freshness,
            verification_valid_until=handoff.verification_valid_until,
            reason=reason,
        )


__all__ = [
    "ConsequenceAuthorizationDecision",
    "ConsequenceAuthorizationService",
    "ConsequenceAuthorizationStatus",
]
