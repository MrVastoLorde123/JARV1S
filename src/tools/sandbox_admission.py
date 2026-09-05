"""Sandbox admission integration between authorization integrity and execution.

This module consumes an already-authorized, integrity-verified ToolRequest and
checks that it is bound to a declared sandbox profile whose admission contract
is satisfied. It never grants authorization, activates containment, launches a
worker, or executes a plugin.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.plugins.sandbox import (
    SandboxAdmissionEvaluator,
    SandboxAdmissionStatus,
    SandboxProfile,
    SandboxProfileRegistry,
)

from .authorization import AuthorizationDecision
from .authorization_integrity import AuthorizationIntegrityResult
from .errors import InvalidRequestError
from .models import ToolRequest


class SandboxAdmissionIntegrationError(ValueError):
    """Raised when the sandbox admission integration contract is invalid."""


@dataclass(frozen=True)
class SandboxAdmissionDecision:
    """Immutable sandbox admission outcome for one authorized request."""

    authorization_id: str
    tool_name: str
    invocation_id: Optional[str]
    profile_id: str
    status: SandboxAdmissionStatus
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.authorization_id, str) or not self.authorization_id.strip():
            raise SandboxAdmissionIntegrationError(
                "authorization_id must be a non-empty string"
            )
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise SandboxAdmissionIntegrationError("tool_name must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise SandboxAdmissionIntegrationError(
                "invocation_id must be a string or None"
            )
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise SandboxAdmissionIntegrationError("profile_id must be a non-empty string")
        if not isinstance(self.status, SandboxAdmissionStatus):
            raise SandboxAdmissionIntegrationError(
                "status must be a SandboxAdmissionStatus member"
            )
        if self.reason is not None and not isinstance(self.reason, str):
            raise SandboxAdmissionIntegrationError("reason must be a string or None")
        if (
            self.status is SandboxAdmissionStatus.ADMISSIBLE
            and self.reason is not None
        ):
            raise SandboxAdmissionIntegrationError(
                "an admissible decision cannot contain a rejection reason"
            )
        if (
            self.status is SandboxAdmissionStatus.REJECTED
            and (self.reason is None or not self.reason.strip())
        ):
            raise SandboxAdmissionIntegrationError(
                "a rejected decision requires a reason"
            )

    @property
    def admissible(self) -> bool:
        return self.status is SandboxAdmissionStatus.ADMISSIBLE

    def to_context(self) -> dict[str, object]:
        return {
            "authorization_id": self.authorization_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "sandbox_profile_id": self.profile_id,
            "sandbox_admission_status": self.status.value,
            "sandbox_admitted": self.admissible,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_started": False,
            "containment_active": False,
        }


class SandboxAdmissionService:
    """Resolve and evaluate sandbox admission without execution authority."""

    DEFAULT_PROFILE_ID = "default"

    def __init__(
        self,
        profile_registry: SandboxProfileRegistry,
        evaluator: Optional[SandboxAdmissionEvaluator] = None,
        *,
        default_profile_id: str = DEFAULT_PROFILE_ID,
    ) -> None:
        if not isinstance(profile_registry, SandboxProfileRegistry):
            raise TypeError("profile_registry must be a SandboxProfileRegistry")
        if evaluator is not None and not isinstance(evaluator, SandboxAdmissionEvaluator):
            raise TypeError("evaluator must be a SandboxAdmissionEvaluator")
        if not isinstance(default_profile_id, str) or not default_profile_id.strip():
            raise SandboxAdmissionIntegrationError(
                "default_profile_id must be a non-empty string"
            )
        self._profiles = profile_registry
        self._evaluator = evaluator or SandboxAdmissionEvaluator()
        self._default_profile_id = default_profile_id.strip()

    def admit(
        self,
        decision: AuthorizationDecision,
        integrity: AuthorizationIntegrityResult,
        request: ToolRequest,
        *,
        profile_id: Optional[str] = None,
    ) -> SandboxAdmissionDecision:
        """Resolve a declared profile and evaluate admission for the exact request."""
        if not isinstance(decision, AuthorizationDecision):
            raise TypeError("decision must be an AuthorizationDecision")
        if not isinstance(integrity, AuthorizationIntegrityResult):
            raise TypeError("integrity must be an AuthorizationIntegrityResult")
        if not isinstance(request, ToolRequest):
            raise InvalidRequestError("request must be a ToolRequest")

        if not decision.authorized:
            return self._rejected(
                decision,
                request,
                profile_id or self._default_profile_id,
                "authorization is not granted",
            )
        if not integrity.valid:
            return self._rejected(
                decision,
                request,
                profile_id or self._default_profile_id,
                "authorization integrity is invalid",
            )
        if decision.tool_name.strip().lower() != request.tool_name.strip().lower():
            return self._rejected(
                decision,
                request,
                profile_id or self._default_profile_id,
                "authorization tool identity does not match request",
            )
        if decision.invocation_id != request.invocation_id:
            return self._rejected(
                decision,
                request,
                profile_id or self._default_profile_id,
                "authorization invocation identity does not match request",
            )
        if integrity.authorization_id != decision.authorization_id:
            return self._rejected(
                decision,
                request,
                profile_id or self._default_profile_id,
                "integrity authorization identity does not match decision",
            )

        resolved_profile_id = profile_id or self._default_profile_id
        if not isinstance(resolved_profile_id, str) or not resolved_profile_id.strip():
            raise SandboxAdmissionIntegrationError(
                "profile_id must be a non-empty string when provided"
            )
        resolved_profile_id = resolved_profile_id.strip()
        profile = self._profiles.get(resolved_profile_id)
        if profile is None:
            return self._rejected(
                decision,
                request,
                resolved_profile_id,
                f"sandbox profile '{resolved_profile_id}' is not registered",
            )

        evaluated = self._evaluator.evaluate(request.tool_name, profile)
        if not evaluated.admissible:
            return self._rejected(
                decision,
                request,
                resolved_profile_id,
                "; ".join(evaluated.reasons),
            )

        return SandboxAdmissionDecision(
            authorization_id=decision.authorization_id,
            tool_name=request.tool_name,
            invocation_id=request.invocation_id,
            profile_id=resolved_profile_id,
            status=SandboxAdmissionStatus.ADMISSIBLE,
        )

    @staticmethod
    def _rejected(
        decision: AuthorizationDecision,
        request: ToolRequest,
        profile_id: str,
        reason: str,
    ) -> SandboxAdmissionDecision:
        return SandboxAdmissionDecision(
            authorization_id=decision.authorization_id,
            tool_name=request.tool_name,
            invocation_id=request.invocation_id,
            profile_id=profile_id.strip() if isinstance(profile_id, str) else str(profile_id),
            status=SandboxAdmissionStatus.REJECTED,
            reason=reason,
        )


def build_default_sandbox_profiles() -> SandboxProfileRegistry:
    """Build the deterministic default profile registry used by the gate."""
    registry = SandboxProfileRegistry()
    registry.register(SandboxProfile(profile_id=SandboxAdmissionService.DEFAULT_PROFILE_ID))
    return registry
