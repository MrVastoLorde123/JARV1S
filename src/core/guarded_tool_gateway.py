"""M26.5: require a policy-guarded tool gateway at the runtime boundary.

The existing PolicyGate already performs policy, confirmation, authorization,
integrity, sandbox admission, preparation, and execution-attempt sequencing.
This adapter makes that guarded path an explicit core-facing gateway so a
runtime composition cannot accidentally wire ToolService directly into the
capability layer.
"""
from __future__ import annotations

from collections.abc import Sequence

from src.tools.gate import PolicyGate
from src.tools.models import ToolDefinition, ToolRequest, ToolResult


class GuardedToolCapabilityGateway:
    """Expose only the existing PolicyGate as a tool-capability gateway."""

    def __init__(self, gate: PolicyGate) -> None:
        if type(gate) is not PolicyGate:
            raise TypeError("gate must be a PolicyGate")
        self._gate = gate

    def list_definitions(self) -> Sequence[ToolDefinition]:
        """Return definitions visible through the guarded gate."""
        definitions = tuple(self._gate.list_definitions())
        if not all(type(item) is ToolDefinition for item in definitions):
            raise TypeError("PolicyGate returned a non-ToolDefinition capability")
        return definitions

    def invoke(self, request: ToolRequest) -> ToolResult:
        """Delegate one exact request to PolicyGate; never bypass the gate."""
        if type(request) is not ToolRequest:
            raise TypeError("request must be a ToolRequest")
        result = self._gate.invoke(request)
        if type(result) is not ToolResult:
            raise TypeError("PolicyGate must return a ToolResult")
        return result

    @property
    def bypasses_authorization(self) -> bool:
        return False

    @property
    def bypasses_confirmation(self) -> bool:
        return False

    @property
    def executes_directly(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False


__all__ = ["GuardedToolCapabilityGateway"]
