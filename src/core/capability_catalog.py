"""Provider-neutral discovery of available JARVIS tool capabilities."""

from __future__ import annotations

from collections.abc import Sequence

from src.core.tool_execution import ToolCapabilityGateway
from src.tools.models import ToolDefinition


class CapabilityCatalog:
    """Read-only view of the capabilities exposed by a tool gateway."""

    def __init__(self, gateway: ToolCapabilityGateway) -> None:
        if not isinstance(gateway, ToolCapabilityGateway):
            raise TypeError("gateway must implement ToolCapabilityGateway")
        self._gateway = gateway

    def list(self) -> tuple[ToolDefinition, ...]:
        """Return a deterministic immutable snapshot of available tools."""
        definitions = tuple(self._gateway.list_definitions())
        if not all(isinstance(item, ToolDefinition) for item in definitions):
            raise TypeError("gateway returned a non-ToolDefinition capability")
        return definitions

    def find(self, name: str) -> ToolDefinition | None:
        """Find one capability by normalized tool name."""
        normalized = name.strip().lower() if isinstance(name, str) else ""
        for definition in self.list():
            if definition.name.strip().lower() == normalized:
                return definition
        return None
