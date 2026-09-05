"""Integrity verification for explicit authorization decisions.

M22.9 binds an ``AuthorizationDecision`` to the exact ``ToolRequest`` it
was produced for. Integrity verification is distinct from policy,
confirmation, authorization, and execution: it detects substitution or
mutation of the authorized request before execution is allowed to proceed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from .authorization import AuthorizationDecision
from .models import ToolRequest


@dataclass(frozen=True)
class AuthorizationIntegrityResult:
    """Immutable integrity result for one authorization/request pair."""

    authorization_id: str
    request_fingerprint: str
    decision_fingerprint: str
    valid: bool
    reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.authorization_id, str) or not self.authorization_id.strip():
            raise ValueError("authorization_id must be a non-empty string")
        if not isinstance(self.request_fingerprint, str) or not self.request_fingerprint:
            raise ValueError("request_fingerprint must be a non-empty string")
        if not isinstance(self.decision_fingerprint, str) or not self.decision_fingerprint:
            raise ValueError("decision_fingerprint must be a non-empty string")
        if not isinstance(self.valid, bool):
            raise TypeError("valid must be a bool")
        if self.reason is not None and not isinstance(self.reason, str):
            raise TypeError("reason must be a string or None")
        if self.valid and self.reason is not None:
            raise ValueError("valid integrity result cannot carry a failure reason")
        if not self.valid and not self.reason:
            raise ValueError("invalid integrity result requires a reason")

    def to_context(self) -> dict[str, object]:
        return {
            "authorization_id": self.authorization_id,
            "request_fingerprint": self.request_fingerprint,
            "decision_fingerprint": self.decision_fingerprint,
            "authorization_integrity_valid": self.valid,
            "authority_granted": False,
            "execution_requested": False,
        }


class AuthorizationIntegrityService:
    """Create and verify deterministic request/authorization integrity."""

    @staticmethod
    def _request_fingerprint(request: ToolRequest) -> str:
        payload = {
            "tool_name": request.tool_name.strip().lower(),
            "arguments": request.arguments,
            "metadata": request.metadata,
            "invocation_id": request.invocation_id,
        }
        encoded = json.dumps(
            payload,
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def _decision_fingerprint(cls, decision: AuthorizationDecision) -> str:
        payload = {
            "authorization_id": decision.authorization_id,
            "tool_name": decision.tool_name.strip().lower(),
            "invocation_id": decision.invocation_id,
            "policy_decision": decision.policy_decision.value,
            "confirmation_approved": decision.confirmation_approved,
            "status": decision.status.value,
            "reason": decision.reason,
        }
        encoded = json.dumps(
            payload,
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def attest(
        self,
        decision: AuthorizationDecision,
        request: ToolRequest,
    ) -> AuthorizationIntegrityResult:
        if not isinstance(decision, AuthorizationDecision):
            raise TypeError("decision must be an AuthorizationDecision")
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")

        request_fp = self._request_fingerprint(request)
        decision_fp = self._decision_fingerprint(decision)
        valid = (
            decision.authorized
            and decision.tool_name.strip().lower() == request.tool_name.strip().lower()
            and decision.invocation_id == request.invocation_id
        )
        reason = None if valid else "authorization decision is not bound to the request"
        return AuthorizationIntegrityResult(
            authorization_id=decision.authorization_id,
            request_fingerprint=request_fp,
            decision_fingerprint=decision_fp,
            valid=valid,
            reason=reason,
        )

    def verify(
        self,
        result: AuthorizationIntegrityResult,
        decision: AuthorizationDecision,
        request: ToolRequest,
    ) -> bool:
        if not isinstance(result, AuthorizationIntegrityResult):
            raise TypeError("result must be an AuthorizationIntegrityResult")
        if not isinstance(decision, AuthorizationDecision):
            raise TypeError("decision must be an AuthorizationDecision")
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")

        return (
            result.valid
            and result.authorization_id == decision.authorization_id
            and result.request_fingerprint == self._request_fingerprint(request)
            and result.decision_fingerprint == self._decision_fingerprint(decision)
        )
