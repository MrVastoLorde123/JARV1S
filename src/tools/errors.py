"""Error hierarchy for the JARVIS tool layer.

All exceptions defined here are structural/programmer-facing errors:
malformed requests, unknown tools, invalid handlers, or handlers that
violate the ToolHandler contract. Runtime failures that occur *inside*
a tool's execution (e.g. "file not found") are represented as a failed
``ToolResult`` returned by ``ToolService.invoke``, not as exceptions.
This keeps the distinction clear:

    * Exceptions  -> something is wrong with the tool layer wiring.
    * ToolResult  -> something is wrong (or right) with the tool call.
"""

from __future__ import annotations


class ToolLayerError(Exception):
    """Base class for all tool-layer errors."""


class InvalidToolDefinitionError(ToolLayerError):
    """Raised when a ``ToolDefinition`` is constructed with bad data."""


class InvalidHandlerError(ToolLayerError):
    """Raised when an object does not satisfy the ``ToolHandler`` contract."""


class DuplicateToolError(ToolLayerError):
    """Raised when registering a tool name that is already registered."""


class UnknownToolError(ToolLayerError):
    """Raised when a request references a tool the registry does not know."""


class InvalidRequestError(ToolLayerError):
    """Raised when a ``ToolRequest`` is malformed."""


class InvalidResultError(ToolLayerError):
    """Raised when a handler returns something that is not a valid ``ToolResult``."""


class InvalidPolicyVerdictError(ToolLayerError):
    """Raised when a ``Policy`` returns something other than a ``PolicyVerdict``."""


class InvalidConfirmationResponseError(ToolLayerError):
    """Raised when a ``ConfirmationProvider`` returns something other than a
    ``ConfirmationResponse``."""


class InvalidAuthorizationDecisionError(ToolLayerError):
    """Raised when an ``AuthorizationDecision`` contains inconsistent data."""
