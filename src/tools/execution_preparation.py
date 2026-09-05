"""Final non-executing preparation boundary before tool execution.

This module binds one exact ToolRequest to its upstream authorization,
integrity, and sandbox-admission evidence. Preparation produces an immutable
handoff artifact but does not assign a worker, activate containment, launch a
process, or execute a plugin.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .authorization import AuthorizationDecision
from .authorization_integrity import AuthorizationIntegrityResult
from .models import ToolRequest
from .sandbox_admission import SandboxAdmissionDecision


class ExecutionPreparationError(ValueError):
    """Raised when execution preparation evidence is structurally invalid."""


@dataclass(frozen=True)
class ExecutionHandoff:
    """Immutable, inspectable handoff artifact immediately before execution."""

    handoff_id: str
    authorization_id: str
    request_fingerprint: str
    decision_fingerprint: str
    sandbox_profile_id: str
    tool_name: str
    invocation_id: Optional[str]
    arguments: Mapping[str, Any]

    def __post_init__(self) -> None:
        for field_name, value in (
            ("handoff_id", self.handoff_id),
            ("authorization_id", self.authorization_id),
            ("request_fingerprint", self.request_fingerprint),
            ("decision_fingerprint", self.decision_fingerprint),
            ("sandbox_profile_id", self.sandbox_profile_id),
            ("tool_name", self.tool_name),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ExecutionPreparationError(
                    f"{field_name} must be a non-empty string"
                )
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise ExecutionPreparationError("invocation_id must be a string or None")
        if not isinstance(self.arguments, Mapping):
            raise ExecutionPreparationError("arguments must be a mapping")

    def to_context(self) -> dict[str, object]:
        return {
            "handoff_id": self.handoff_id,
            "authorization_id": self.authorization_id,
            "request_fingerprint": self.request_fingerprint,
            "decision_fingerprint": self.decision_fingerprint,
            "sandbox_profile_id": self.sandbox_profile_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "arguments": dict(self.arguments),
            "execution_prepared": True,
            "authority_granted": False,
            "permission_granted": False,
            "execution_started": False,
            "worker_assigned": False,
            "containment_active": False,
        }


class ExecutionPreparationService:
    """Validate upstream evidence and produce an inert execution handoff."""

    def prepare(
        self,
        decision: AuthorizationDecision,
        integrity: AuthorizationIntegrityResult,
        admission: SandboxAdmissionDecision,
        request: ToolRequest,
    ) -> ExecutionHandoff:
        if not isinstance(decision, AuthorizationDecision):
            raise TypeError("decision must be an AuthorizationDecision")
        if not isinstance(integrity, AuthorizationIntegrityResult):
            raise TypeError("integrity must be an AuthorizationIntegrityResult")
        if not isinstance(admission, SandboxAdmissionDecision):
            raise TypeError("admission must be a SandboxAdmissionDecision")
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")

        if not decision.authorized:
            raise ExecutionPreparationError("authorization is not granted")
        if not integrity.valid:
            raise ExecutionPreparationError("authorization integrity is invalid")
        if not admission.admissible:
            raise ExecutionPreparationError("sandbox admission is not admissible")

        tool_name = request.tool_name.strip().lower()
        if decision.tool_name.strip().lower() != tool_name:
            raise ExecutionPreparationError(
                "authorization tool identity does not match request"
            )
        if admission.tool_name.strip().lower() != tool_name:
            raise ExecutionPreparationError(
                "sandbox admission tool identity does not match request"
            )
        if decision.invocation_id != request.invocation_id:
            raise ExecutionPreparationError(
                "authorization invocation identity does not match request"
            )
        if admission.invocation_id != request.invocation_id:
            raise ExecutionPreparationError(
                "sandbox admission invocation identity does not match request"
            )
        if integrity.authorization_id != decision.authorization_id:
            raise ExecutionPreparationError(
                "integrity authorization identity does not match decision"
            )
        if admission.authorization_id != decision.authorization_id:
            raise ExecutionPreparationError(
                "sandbox admission authorization identity does not match decision"
            )

        payload = json.dumps(
            {
                "authorization_id": decision.authorization_id,
                "request_fingerprint": integrity.request_fingerprint,
                "decision_fingerprint": integrity.decision_fingerprint,
                "sandbox_profile_id": admission.profile_id.strip(),
                "tool_name": tool_name,
                "invocation_id": request.invocation_id,
                "arguments": request.arguments,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        handoff_id = f"handoff-{hashlib.sha256(payload).hexdigest()[:24]}"

        return ExecutionHandoff(
            handoff_id=handoff_id,
            authorization_id=decision.authorization_id,
            request_fingerprint=integrity.request_fingerprint,
            decision_fingerprint=integrity.decision_fingerprint,
            sandbox_profile_id=admission.profile_id.strip(),
            tool_name=request.tool_name,
            invocation_id=request.invocation_id,
            arguments=MappingProxyType(dict(request.arguments)),
        )
