"""Validate and materialize selected capabilities into tool requests."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.tools.models import ToolDefinition, ToolRequest


class CapabilityInvocationError(ValueError):
    """Raised when a capability selection cannot become a valid request."""


class CapabilityInvocationBuilder:
    """Build validated ``ToolRequest`` values from tool definitions.

    This layer performs only structural validation implied by the declared
    input schema. It never invokes a capability and never decides policy or
    confirmation.
    """

    def build(
        self,
        capability: ToolDefinition,
        arguments: Mapping[str, Any],
        *,
        invocation_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ToolRequest:
        if not isinstance(capability, ToolDefinition):
            raise TypeError("capability must be a ToolDefinition")
        if not isinstance(arguments, Mapping):
            raise CapabilityInvocationError("arguments must be a mapping")
        if invocation_id is not None and not isinstance(invocation_id, str):
            raise CapabilityInvocationError("invocation_id must be a string or None")
        if metadata is not None and not isinstance(metadata, Mapping):
            raise CapabilityInvocationError("metadata must be a mapping or None")

        schema = capability.input_schema
        if schema.get("type") not in (None, "object"):
            raise CapabilityInvocationError(
                f"unsupported input schema type for '{capability.name}'"
            )

        required = schema.get("required", ())
        if not isinstance(required, (list, tuple)):
            raise CapabilityInvocationError(
                f"invalid required declaration for '{capability.name}'"
            )

        missing = [
            name
            for name in required
            if isinstance(name, str) and name not in arguments
        ]
        if missing:
            raise CapabilityInvocationError(
                f"missing required argument(s): {', '.join(missing)}"
            )

        properties = schema.get("properties", {})
        if not isinstance(properties, Mapping):
            raise CapabilityInvocationError(
                f"invalid properties declaration for '{capability.name}'"
            )

        for name, value in arguments.items():
            if name not in properties:
                continue
            expected = properties[name].get("type") if isinstance(properties[name], Mapping) else None
            if expected is not None and not self._matches_type(value, expected):
                raise CapabilityInvocationError(
                    f"argument '{name}' must be of type {expected}"
                )

        return ToolRequest(
            tool_name=capability.name,
            arguments=dict(arguments),
            metadata=dict(metadata or {}),
            invocation_id=invocation_id,
        )

    @staticmethod
    def _matches_type(value: Any, expected: str) -> bool:
        if expected == "string":
            return isinstance(value, str)
        if expected == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected == "boolean":
            return isinstance(value, bool)
        if expected == "object":
            return isinstance(value, Mapping)
        if expected == "array":
            return isinstance(value, (list, tuple))
        if expected == "null":
            return value is None
        return True
