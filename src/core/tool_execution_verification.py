"""Verify tool execution outcomes without conflating execution with truth.

A tool result is an observation from the execution boundary. It is not proof
that the intended effect actually occurred. Verification is therefore an
independent, injected boundary that evaluates a concrete request/result pair.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from src.tools.models import ToolRequest, ToolResult


class ToolVerificationStatus(str, Enum):
    """Explicit post-execution verification state."""

    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class ToolExecutionVerification:
    """Immutable verification decision bound to one exact request/result."""

    request: ToolRequest
    result: ToolResult
    status: ToolVerificationStatus
    evidence: str
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.request, ToolRequest):
            raise TypeError("request must be a ToolRequest")
        if not isinstance(self.result, ToolResult):
            raise TypeError("result must be a ToolResult")
        if not isinstance(self.status, ToolVerificationStatus):
            raise TypeError("status must be a ToolVerificationStatus")
        if not isinstance(self.evidence, str) or not self.evidence.strip():
            raise ValueError("evidence must be a non-empty string")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if self.result.tool_name.strip().lower() != self.request.tool_name.strip().lower():
            raise ValueError("verification result tool_name does not match request")
        if self.result.invocation_id != self.request.invocation_id:
            raise ValueError("verification result invocation_id does not match request")


@runtime_checkable
class ToolExecutionVerifier(Protocol):
    """Independent authority for determining whether an effect was verified."""

    def verify(
        self,
        request: ToolRequest,
        result: ToolResult,
    ) -> ToolExecutionVerification:
        ...


def require_verified(verification: ToolExecutionVerification) -> None:
    """Require an explicit VERIFIED decision before treating an effect as verified."""
    if not isinstance(verification, ToolExecutionVerification):
        raise TypeError("verification must be a ToolExecutionVerification")
    if verification.status is not ToolVerificationStatus.VERIFIED:
        raise RuntimeError(
            f"tool execution is not verified: {verification.reason}"
        )
