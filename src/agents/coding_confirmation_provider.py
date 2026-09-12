"""Translate an approved coding operation into exact tool confirmations."""

from __future__ import annotations

from src.tools.confirmation import ConfirmationProvider, ConfirmationResponse
from src.tools.models import ToolDefinition, ToolRequest

from .coding_confirmation import CodingAgentConfirmationService


class CodingAgentConfirmationProvider(ConfirmationProvider):
    """Approve only tool requests that belong to an approved coding plan."""

    def __init__(self, confirmation_service: CodingAgentConfirmationService) -> None:
        if not isinstance(confirmation_service, CodingAgentConfirmationService):
            raise TypeError("confirmation_service must be a CodingAgentConfirmationService")
        self._confirmation_service = confirmation_service

    def confirm(
        self,
        definition: ToolDefinition,
        request: ToolRequest,
    ) -> ConfirmationResponse:
        operation_id = request.metadata.get("coding_operation_id")
        if not isinstance(operation_id, str) or not operation_id.strip():
            return ConfirmationResponse(
                approved=False,
                reason="coding tool confirmation requires a coding operation ID",
            )

        operation = self._confirmation_service.get(operation_id)
        if operation is None or not operation.is_confirmed:
            return ConfirmationResponse(
                approved=False,
                reason="coding operation is not confirmed",
            )

        if request.invocation_id is None:
            return ConfirmationResponse(
                approved=False,
                reason="coding tool confirmation requires an invocation ID",
            )

        if not self._confirmation_service.authorize_tool_request(
            operation_id,
            request,
        ):
            return ConfirmationResponse(
                approved=False,
                reason="tool request does not match the approved coding plan",
            )

        return ConfirmationResponse(
            approved=True,
            reason=f"approved by coding operation {operation_id}",
        )


__all__ = ["CodingAgentConfirmationProvider"]
