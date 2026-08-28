"""Explicit data models for the tool layer.

These models are pure data. None of them contain executable tool
behavior -- that lives behind the ``ToolHandler`` contract in
``protocol.py``. JARVIS core, the registry, and the service all speak
to each other exclusively through these types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
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


@dataclass(frozen=True)
class ToolDefinition:
    """Static description of a tool's capability surface.

    Attributes:
        name: Stable, unique tool identifier (e.g. ``"read_file"``).
            Comparisons/lookups elsewhere are done on the *normalized*
            form of this name (see ``registry.normalize_name``); the
            definition itself stores the name as provided.
        description: Human-readable summary of what the tool does.
        version: Free-form version string for the tool implementation
            (e.g. ``"1.0.0"``).
        input_schema: JSON-schema-like mapping describing accepted
            arguments.
        output_schema: JSON-schema-like mapping describing the shape
            of successful result content.
        risk_level: Declared ``RiskLevel`` for this tool.
        requires_confirmation: Whether JARVIS must obtain user
            confirmation before invoking this tool. This is a
            declaration only; enforcement is out of scope here.
        metadata: Optional free-form metadata (author, tags, docs
            link, etc.). Must not contain executable behavior.
    """

    name: str
    description: str
    version: str
    input_schema: Mapping[str, Any]
    output_schema: Mapping[str, Any]
    risk_level: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False
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
        if not _is_mapping(self.metadata):
            raise InvalidToolDefinitionError("ToolDefinition.metadata must be a mapping")


@dataclass(frozen=True)
class ToolRequest:
    """A single request to invoke one tool.

    Attributes:
        tool_name: Name of the tool to invoke, as it will be looked up
            in the ``ToolRegistry`` (normalization happens there).
        arguments: Arguments for the invocation.
        metadata: Optional request-scoped metadata (e.g. tracing info,
            originating conversation id). Never used for control flow
            by the service itself.
        invocation_id: Optional caller-supplied identifier for
            correlating this request with its result.
    """

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


@dataclass(frozen=True)
class ToolResult:
    """Outcome of a single tool invocation.

    Attributes:
        success: Whether the invocation succeeded.
        tool_name: Name of the tool that produced this result. Used by
            ``ToolService`` to validate handlers didn't return a
            result for the wrong tool.
        content: Result payload on success. Should conform to the
            tool's declared ``output_schema``; this milestone does not
            enforce schema validation, only structural shape.
        metadata: Optional result-scoped metadata.
        error: Structured error information. Must be set when
            ``success`` is False, and must be None when ``success`` is
            True.
        invocation_id: Echoes the originating request's invocation id,
            when one was provided.
    """

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
