"""Orchestrate independent verification of a concrete tool outcome."""

from __future__ import annotations

from src.core.tool_execution_verification import (
    ToolExecutionVerification,
    ToolExecutionVerifier,
)
from src.tools.models import ToolRequest, ToolResult


class ToolExecutionVerificationService:
    """Delegate post-execution verification without executing or authorizing."""

    def __init__(self, verifier: ToolExecutionVerifier) -> None:
        if not isinstance(verifier, ToolExecutionVerifier):
            raise TypeError("verifier must implement ToolExecutionVerifier")
        self._verifier = verifier

    def verify(
        self,
        request: ToolRequest,
        result: ToolResult,
    ) -> ToolExecutionVerification:
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")
        if not isinstance(result, ToolResult):
            raise TypeError("result must be a ToolResult")
        if result.tool_name.strip().lower() != request.tool_name.strip().lower():
            raise ValueError("result tool_name does not match request")
        if result.invocation_id != request.invocation_id:
            raise ValueError("result invocation_id does not match request")

        verification = self._verifier.verify(request, result)
        if not isinstance(verification, ToolExecutionVerification):
            raise TypeError(
                "verifier returned an invalid ToolExecutionVerification"
            )
        return verification
