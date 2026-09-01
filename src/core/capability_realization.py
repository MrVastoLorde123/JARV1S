"""Turn natural-language tool intent into an existing safe execution request."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.capability_argument_planner import CapabilityInvocationService
from src.core.capability_selection import CapabilityCandidate, CapabilitySelection
from src.core.capability_selection_service import CapabilitySelectionService
from src.tools.models import ToolRequest


@dataclass(frozen=True)
class CapabilityRealization:
    """The read-only result of realizing one natural-language capability intent."""

    intent: str
    selection: CapabilitySelection
    candidate: CapabilityCandidate
    request: ToolRequest


class CapabilityRealizationService:
    """Compose capability selection and invocation preparation.

    The service chooses a registered capability, asks the argument planner for
    structured arguments, and lets ``CapabilityInvocationService`` perform the
    deterministic request validation. It never invokes a tool and never makes
    policy or confirmation decisions.
    """

    def __init__(
        self,
        selection_service: CapabilitySelectionService,
        invocation_service: CapabilityInvocationService,
    ) -> None:
        if not isinstance(selection_service, CapabilitySelectionService):
            raise TypeError("selection_service must be a CapabilitySelectionService")
        if not isinstance(invocation_service, CapabilityInvocationService):
            raise TypeError("invocation_service must be a CapabilityInvocationService")
        self._selection_service = selection_service
        self._invocation_service = invocation_service

    def realize(self, intent: str) -> CapabilityRealization:
        """Select the best capability and materialize its validated request."""
        if not isinstance(intent, str) or not intent.strip():
            raise ValueError("intent must be a non-empty string")

        normalized_intent = intent.strip()
        selection = self._selection_service.select(normalized_intent)
        candidate = selection.best
        if candidate is None:
            raise LookupError("No capability matched the requested intent")

        request = self._invocation_service.build_request(
            normalized_intent,
            candidate,
        )

        return CapabilityRealization(
            intent=normalized_intent,
            selection=selection,
            candidate=candidate,
            request=request,
        )
