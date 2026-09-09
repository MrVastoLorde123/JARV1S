"""M26.4: explicit integration boundary for real tool capabilities."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from src.core.capability_registry import CapabilityDefinition, CapabilityRegistry
from src.core.tool_execution import ToolCapabilityGateway
from src.tools.models import ToolDefinition, ToolRequest, ToolResult


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _freeze_definition(definition: ToolDefinition) -> ToolDefinition:
    return ToolDefinition(
        name=definition.name,
        description=definition.description,
        version=definition.version,
        input_schema=_freeze(definition.input_schema),
        output_schema=_freeze(definition.output_schema),
        risk_level=definition.risk_level,
        requires_confirmation=definition.requires_confirmation,
        metadata=_freeze(definition.metadata),
    )


@dataclass(frozen=True)
class ToolCapabilitySnapshot:
    """Immutable observation of currently exposed tool capabilities."""

    definitions: tuple[ToolDefinition, ...]

    def __post_init__(self) -> None:
        if not all(type(item) is ToolDefinition for item in self.definitions):
            raise TypeError("definitions must contain only exact ToolDefinition values")


class ToolCapabilityIntegrationBoundary:
    """Bridge declared tool capabilities to JARVIS and explicit invocation."""

    def __init__(self, gateway: ToolCapabilityGateway, registry: CapabilityRegistry) -> None:
        if not isinstance(gateway, ToolCapabilityGateway):
            raise TypeError("gateway must implement ToolCapabilityGateway")
        if type(registry) is not CapabilityRegistry:
            raise TypeError("registry must be a capability registry")
        self._gateway = gateway
        self._registry = registry

    def snapshot(self) -> ToolCapabilitySnapshot:
        """Take a distinct immutable snapshot of gateway declarations."""
        definitions = tuple(self._gateway.list_definitions())
        if not all(type(item) is ToolDefinition for item in definitions):
            raise TypeError("gateway returned a non-ToolDefinition capability")
        return ToolCapabilitySnapshot(tuple(_freeze_definition(item) for item in definitions))

    def register_capabilities(self) -> tuple[CapabilityDefinition, ...]:
        """Register gateway declarations in the provider-neutral capability registry."""
        registered: list[CapabilityDefinition] = []
        for definition in self.snapshot().definitions:
            capability = CapabilityDefinition(
                capability_id=f"tool:{definition.name.strip().lower()}",
                name=definition.name,
                description=definition.description,
                category="tool",
                metadata=_freeze(
                    {
                        "tool_version": definition.version,
                        "input_schema": definition.input_schema,
                        "output_schema": definition.output_schema,
                        "risk_level": definition.risk_level.value,
                        "requires_confirmation": definition.requires_confirmation,
                        "tool_metadata": definition.metadata,
                    }
                ),
            )
            registered.append(self._registry.register(capability))
        return tuple(registered)

    def invoke(self, request: ToolRequest) -> ToolResult:
        """Explicitly delegate one exact request to the injected tool gateway."""
        if type(request) is not ToolRequest:
            raise TypeError("request must be a ToolRequest")
        result = self._gateway.invoke(request)
        if type(result) is not ToolResult:
            raise TypeError("gateway must return a ToolResult")
        return result

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def selects_tool(self) -> bool:
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


__all__ = ["ToolCapabilitySnapshot", "ToolCapabilityIntegrationBoundary"]
