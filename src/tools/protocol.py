"""The stable contracts every tool implementation must satisfy.

The ToolHandler contract is intentionally minimal: a handler describes itself
(definition) and executes one request (execute). It never decides whether it
should run -- that decision belongs to JARVIS core, mediated by the future
policy/confirmation layer.

Optional outcome-evidence provider contracts are additive: capabilities may
expose typed external observation and verification evidence without making
evidence mandatory for ordinary tool execution.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import ToolDefinition, ToolRequest, ToolResult
from .outcome import ExternalObservation, ExternalVerification


@runtime_checkable
class ToolHandler(Protocol):
    """Structural contract for a tool implementation."""

    def definition(self) -> ToolDefinition:
        """Return this tool's static ToolDefinition."""
        ...

    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute one invocation and return its ToolResult."""
        ...


@runtime_checkable
class ToolObservationProvider(Protocol):
    """Optional typed external-observation evidence for one invocation."""

    def provide_external_observation(
        self,
        request: ToolRequest,
        result: ToolResult,
    ) -> ExternalObservation | None:
        """Return typed observation evidence or None when unavailable."""
        ...


@runtime_checkable
class ToolVerificationProvider(Protocol):
    """Optional typed verification evidence for one observed invocation."""

    def provide_external_verification(
        self,
        request: ToolRequest,
        result: ToolResult,
        observation: ExternalObservation,
    ) -> ExternalVerification | None:
        """Return typed verification evidence or None when unavailable."""
        ...


@runtime_checkable
class ToolVerificationBindingProvider(Protocol):
    """Registration-bound identity of the concrete verification provider."""

    def verification_source_id(self, request: ToolRequest) -> str | None:
        """Return the verifier identity bound by the capability registry."""
        ...


@runtime_checkable
class ToolVerificationAdmissibilityProvider(Protocol):
    """Optional deterministic trust anchor for verification source identities."""

    def admissible_verification_sources(
        self,
        request: ToolRequest,
    ) -> tuple[str, ...]:
        """Return source IDs configured as admissible for this capability."""
        ...
