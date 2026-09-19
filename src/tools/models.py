"""Explicit data models for the tool layer.

These models are pure data. None of them contain executable tool
behavior -- that lives behind the ``ToolHandler`` contract in
``protocol.py``. JARVIS core, the registry, and the service all speak
to each other exclusively through these types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .errors import InvalidToolDefinitionError, InvalidRequestError


class RiskLevel(str, Enum):
    """Declared risk classification for a tool.

    This milestone only *models* risk. No automatic permission bypass,
    escalation, or enforcement logic is implemented here -- that is
    the job of the (future) confirmation/policy layer sitting between
    JARVIS core and ``ToolService``.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


class _FrozenList(list[Any]):
    """List-shaped immutable snapshot preserving JSON-array semantics."""

    def _immutable(self, *_args: Any, **_kwargs: Any) -> None:
        raise TypeError("frozen tool contract data cannot be mutated")

    __setitem__ = _immutable
    __delitem__ = _immutable
    __iadd__ = _immutable
    __imul__ = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    pop = _immutable
    remove = _immutable
    reverse = _immutable
    sort = _immutable


def _freeze(value: Any) -> Any:
    """Recursively snapshot common mutable containers into immutable values."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return _FrozenList(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class ToolDefinition:
    """Static description of a tool's capability surface."""

    name: str
    description: str
    version: str
    input_schema: Mapping[str, Any]
    output_schema: Mapping[str, Any]
    risk_level: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False
    admissible_verification_sources: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise InvalidToolDefinitionError("ToolDefinition.name must be a non-empty string")
        if not isinstance(self.description, str) or not self.description.strip():
            raise InvalidToolDefinitionError(
                "ToolDefinition.description must be a non-empty string"
            )
        if not isinstance(self.version, str) or not self.version.strip():
            raise InvalidToolDefinitionError("ToolDefinition.version must be a non-empty string")
        if not _is_mapping(self.input_schema):
            raise InvalidToolDefinitionError("ToolDefinition.input_schema must be a mapping")
        if not _is_mapping(self.output_schema):
            raise InvalidToolDefinitionError("ToolDefinition.output_schema must be a mapping")
        if not isinstance(self.risk_level, RiskLevel):
            raise InvalidToolDefinitionError(
                "ToolDefinition.risk_level must be a RiskLevel member"
            )
        if not isinstance(self.requires_confirmation, bool):
            raise InvalidToolDefinitionError(
                "ToolDefinition.requires_confirmation must be a bool"
            )
        if not isinstance(self.admissible_verification_sources, tuple):
            raise InvalidToolDefinitionError(
                "ToolDefinition.admissible_verification_sources must be a tuple"
            )
        if any(
            not isinstance(source, str) or not source.strip()
            for source in self.admissible_verification_sources
        ):
            raise InvalidToolDefinitionError(
                "ToolDefinition.admissible_verification_sources must contain "
                "non-empty strings"
            )
        normalized_sources = tuple(
            dict.fromkeys(
                source.strip()
                for source in self.admissible_verification_sources
            )
        )
        if not _is_mapping(self.metadata):
            raise InvalidToolDefinitionError("ToolDefinition.metadata must be a mapping")
        object.__setattr__(self, "admissible_verification_sources", normalized_sources)
        object.__setattr__(self, "input_schema", _freeze(self.input_schema))
        object.__setattr__(self, "output_schema", _freeze(self.output_schema))
        object.__setattr__(self, "metadata", _freeze(self.metadata))


@dataclass(frozen=True)
class ToolRequest:
    """A single request to invoke one tool."""

    tool_name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    invocation_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise InvalidRequestError("ToolRequest.tool_name must be a non-empty string")
        if not _is_mapping(self.arguments):
            raise InvalidRequestError("ToolRequest.arguments must be a mapping")
        if not _is_mapping(self.metadata):
            raise InvalidRequestError("ToolRequest.metadata must be a mapping")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise InvalidRequestError("ToolRequest.invocation_id must be a string or None")
        object.__setattr__(self, "arguments", _freeze(self.arguments))
        object.__setattr__(self, "metadata", _freeze(self.metadata))


@dataclass(frozen=True)
class ToolError:
    """Structured error information carried by a failed ``ToolResult``."""

    code: str
    message: str
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not self.code.strip():
            raise InvalidRequestError("ToolError.code must be a non-empty string")
        if not isinstance(self.message, str) or not self.message.strip():
            raise InvalidRequestError("ToolError.message must be a non-empty string")
        if not _is_mapping(self.details):
            raise InvalidRequestError("ToolError.details must be a mapping")
        object.__setattr__(self, "details", _freeze(self.details))


@dataclass(frozen=True)
class ToolResult:
    """Outcome of a single tool invocation."""

    success: bool
    tool_name: str
    content: Any = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    error: Optional[ToolError] = None
    invocation_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise InvalidRequestError("ToolResult.success must be a bool")
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise InvalidRequestError("ToolResult.tool_name must be a non-empty string")
        if not _is_mapping(self.metadata):
            raise InvalidRequestError("ToolResult.metadata must be a mapping")
        if self.error is not None and not isinstance(self.error, ToolError):
            raise InvalidRequestError("ToolResult.error must be a ToolError or None")
        if not self.success and self.error is None:
            raise InvalidRequestError("ToolResult.error must be set when success is False")
        if self.success and self.error is not None:
            raise InvalidRequestError("ToolResult.error must be None when success is True")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise InvalidRequestError("ToolResult.invocation_id must be a string or None")
        object.__setattr__(self, "content", _freeze(self.content))
        object.__setattr__(self, "metadata", _freeze(self.metadata))
