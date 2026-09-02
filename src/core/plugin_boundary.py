"""Provider-neutral capability to plugin execution boundary for M8.2.

This module resolves an authorized M8 ``ExecutionRequest`` to a concrete
capability supplied by a plugin. Plugins provide execution behavior; they do
not own policy, confirmation, authorization, or continuation decisions.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from src.context.execution_semantics import ExecutionRequest
from src.tools.models import ToolDefinition, ToolRequest, ToolResult


def _normalize(value: str) -> str:
    return value.strip().lower()


@dataclass(frozen=True)
class PluginDefinition:
    """Static identity and metadata for one capability plugin."""

    plugin_id: str
    version: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.plugin_id, str) or not self.plugin_id.strip():
            raise ValueError("plugin_id must be a non-empty string")
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("version must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")


@runtime_checkable
class CapabilityPlugin(Protocol):
    """Contract for a plugin that supplies one or more capabilities."""

    def definition(self) -> PluginDefinition:
        """Return stable plugin identity and metadata."""
        ...

    def capabilities(self) -> Sequence[ToolDefinition]:
        """Return the capability definitions exposed by this plugin."""
        ...

    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute one already-authorized capability request."""
        ...


@dataclass(frozen=True)
class CapabilityBinding:
    """Resolved mapping from a provider-neutral operation to a plugin capability."""

    operation: str
    plugin_id: str
    capability: ToolDefinition
    plugin: CapabilityPlugin


class CapabilityPluginRegistry:
    """Deterministic registry mapping operations to plugin capabilities."""

    def __init__(self) -> None:
        self._plugins: dict[str, CapabilityPlugin] = {}
        self._capabilities: dict[str, tuple[str, ToolDefinition]] = {}
        self._operations: dict[str, str] = {}

    def register(self, plugin: CapabilityPlugin) -> PluginDefinition:
        if not isinstance(plugin, CapabilityPlugin):
            raise TypeError("plugin must satisfy the CapabilityPlugin contract")
        definition = plugin.definition()
        if not isinstance(definition, PluginDefinition):
            raise TypeError("plugin.definition() must return PluginDefinition")

        plugin_key = _normalize(definition.plugin_id)
        if plugin_key in self._plugins:
            raise ValueError(f"plugin '{definition.plugin_id}' is already registered")

        capabilities = tuple(plugin.capabilities())
        if not all(isinstance(item, ToolDefinition) for item in capabilities):
            raise TypeError("plugin.capabilities() must return ToolDefinition values")
        seen: set[str] = set()
        for capability in capabilities:
            key = _normalize(capability.name)
            if key in seen:
                raise ValueError(
                    f"plugin '{definition.plugin_id}' declares duplicate capability '{capability.name}'"
                )
            if key in self._capabilities:
                owner = self._capabilities[key][0]
                raise ValueError(
                    f"capability '{capability.name}' is already owned by plugin '{owner}'"
                )
            seen.add(key)

        self._plugins[plugin_key] = plugin
        for capability in capabilities:
            self._capabilities[_normalize(capability.name)] = (definition.plugin_id, capability)
        return definition

    def bind(self, operation: str, capability_name: str) -> None:
        """Bind one provider-neutral operation to a registered capability."""
        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("operation must be a non-empty string")
        if not isinstance(capability_name, str) or not capability_name.strip():
            raise ValueError("capability_name must be a non-empty string")
        capability_key = _normalize(capability_name)
        if capability_key not in self._capabilities:
            raise KeyError(f"unknown capability '{capability_name}'")
        operation_key = _normalize(operation)
        if operation_key in self._operations:
            raise ValueError(f"operation '{operation}' is already bound")
        self._operations[operation_key] = capability_key

    def resolve(self, operation: str) -> CapabilityBinding:
        """Resolve an operation without executing anything."""
        if not isinstance(operation, str) or not operation.strip():
            raise KeyError("operation must be a non-empty string")
        operation_key = _normalize(operation)
        capability_key = self._operations.get(operation_key)
        if capability_key is None:
            raise KeyError(f"no capability binding exists for operation '{operation}'")
        plugin_id, capability = self._capabilities[capability_key]
        plugin = self._plugins[_normalize(plugin_id)]
        return CapabilityBinding(
            operation=operation,
            plugin_id=plugin_id,
            capability=capability,
            plugin=plugin,
        )

    def execute(self, request: ExecutionRequest) -> ToolResult:
        """Resolve and execute an already-authorized provider-neutral request."""
        if not isinstance(request, ExecutionRequest):
            raise TypeError("request must be an ExecutionRequest")
        binding = self.resolve(request.operation)
        tool_request = ToolRequest(
            tool_name=binding.capability.name,
            arguments=dict(request.arguments),
            metadata={
                **dict(request.metadata),
                "execution_id": request.execution_id,
                "plugin_id": binding.plugin_id,
                "operation": request.operation,
            },
            invocation_id=request.execution_id,
        )
        result = binding.plugin.execute(tool_request)
        if not isinstance(result, ToolResult):
            raise TypeError("plugin.execute() must return ToolResult")
        if _normalize(result.tool_name) != _normalize(binding.capability.name):
            raise ValueError(
                f"plugin '{binding.plugin_id}' returned a result for '{result.tool_name}' "
                f"instead of '{binding.capability.name}'"
            )
        return result

    def list_plugins(self) -> tuple[PluginDefinition, ...]:
        """Return registered plugin definitions deterministically."""
        return tuple(
            self._plugins[key].definition()
            for key in sorted(self._plugins)
        )

    def list_capabilities(self) -> tuple[ToolDefinition, ...]:
        """Return registered capabilities deterministically."""
        return tuple(
            self._capabilities[key][1]
            for key in sorted(self._capabilities)
        )
