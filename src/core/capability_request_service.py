"""Bind selected capability proposals to validated tool requests.

This module is the bridge between M22.6 capability selection and the existing
structural invocation boundary. It accepts only a discovery/selection
snapshot, asks the replaceable argument planner for inert argument data, and
materializes a validated ``ToolRequest``. It never authorizes or executes a
capability.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.core.capability_argument_planner import (
    CapabilityArgumentPlanner,
    CapabilityInvocationService,
)
from src.core.capability_selection import CapabilityCandidate
from src.core.capability_selection_service import CapabilityDiscoverySelection
from src.tools.models import ToolRequest


@dataclass(frozen=True)
class CapabilityRequestProposal:
    """Immutable selected-capability proposal carrying a validated request."""

    snapshot: CapabilityDiscoverySelection
    candidate: CapabilityCandidate
    arguments: Mapping[str, Any]
    request: ToolRequest

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot, CapabilityDiscoverySelection):
            raise TypeError("snapshot must be a CapabilityDiscoverySelection")
        if not isinstance(self.candidate, CapabilityCandidate):
            raise TypeError("candidate must be a CapabilityCandidate")
        if not isinstance(self.arguments, Mapping):
            raise TypeError("arguments must be a mapping")
        if not isinstance(self.request, ToolRequest):
            raise TypeError("request must be a ToolRequest")

        if not any(
            selected is self.candidate for selected in self.snapshot.selection.candidates
        ):
            raise ValueError("candidate must originate from the discovery selection snapshot")
        if self.request.tool_name.strip().lower() != self.candidate.capability.name.strip().lower():
            raise ValueError("request tool_name must match candidate capability")
        if dict(self.request.arguments) != dict(self.arguments):
            raise ValueError("request arguments must match proposed arguments")

    def to_context(self) -> dict[str, object]:
        return {
            "query": self.snapshot.query,
            "capability": self.candidate.capability.name,
            "validated_request": True,
            "authority_granted": False,
            "permission_granted": False,
            "authorization_granted": False,
            "confirmation_interpreted": False,
            "execution_requested": False,
        }


class CapabilityRequestProposalService:
    """Materialize one selected capability into an inert validated request."""

    def __init__(
        self,
        argument_planner: CapabilityArgumentPlanner,
    ) -> None:
        if not isinstance(argument_planner, CapabilityArgumentPlanner):
            raise TypeError("argument_planner must implement CapabilityArgumentPlanner")
        self._invocation = CapabilityInvocationService(argument_planner)

    def propose(
        self,
        snapshot: CapabilityDiscoverySelection,
        *,
        candidate: CapabilityCandidate | None = None,
        invocation_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> CapabilityRequestProposal:
        if not isinstance(snapshot, CapabilityDiscoverySelection):
            raise TypeError("snapshot must be a CapabilityDiscoverySelection")

        selected = candidate if candidate is not None else snapshot.best
        if selected is None:
            raise ValueError("snapshot contains no selected capability")
        if not any(
            candidate_item is selected for candidate_item in snapshot.selection.candidates
        ):
            raise ValueError("candidate must originate from the discovery selection snapshot")

        arguments = self._invocation._argument_planner.propose(snapshot.query, selected)
        request = self._invocation._builder.build(
            selected.capability,
            arguments,
            invocation_id=invocation_id,
            metadata=metadata,
        )
        return CapabilityRequestProposal(
            snapshot=snapshot,
            candidate=selected,
            arguments=dict(arguments),
            request=request,
        )
