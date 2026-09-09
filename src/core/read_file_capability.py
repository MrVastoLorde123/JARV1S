"""M26.6: wire the real read_file capability through the complete guarded path."""
from __future__ import annotations

from pathlib import Path

from src.core.capability_registry import CapabilityDefinition, CapabilityRegistry
from src.core.guarded_tool_gateway import GuardedToolCapabilityGateway
from src.core.tool_capability_integration import ToolCapabilityIntegrationBoundary
from src.tools.bootstrap import build_tool_stack
from src.tools.confirmation import ConfirmationProvider
from src.tools.handlers.read_file import ReadFileHandler
from src.tools.models import ToolRequest, ToolResult
from src.tools.policy import Policy


class RealReadFileCapability:
    """Concrete V1 composition of the existing read_file tool and JARVIS boundaries.

    This class does not implement filesystem semantics itself. The real
    ``ReadFileHandler`` remains the tool implementation; this composition
    ensures its declaration is registered as a JARVIS capability and its
    explicit ``ToolRequest`` crosses the guarded gateway before execution.
    """

    def __init__(
        self,
        base_dir: str | Path,
        *,
        policy: Policy | None = None,
        confirmation_provider: ConfirmationProvider | None = None,
    ) -> None:
        handler = ReadFileHandler(base_dir)
        stack = build_tool_stack(
            [handler],
            policy=policy,
            confirmation_provider=confirmation_provider,
        )
        gateway = GuardedToolCapabilityGateway(stack.gate)
        registry = CapabilityRegistry()
        integration = ToolCapabilityIntegrationBoundary(gateway, registry)
        registered = integration.register_capabilities()
        if len(registered) != 1:
            raise RuntimeError("read_file capability registration did not produce exactly one capability")

        self._integration = integration
        self._registry = registry
        self._capability = registered[0]

    @property
    def capability(self) -> CapabilityDefinition:
        """Return the immutable provider-neutral capability declaration."""
        return self._capability

    @property
    def capability_registry(self) -> CapabilityRegistry:
        return self._registry

    @property
    def tool_name(self) -> str:
        return self._capability.name

    def invoke(self, request: ToolRequest) -> ToolResult:
        """Invoke the real ``read_file`` tool through the guarded integration path."""
        return self._integration.invoke(request)

    def read(self, path: str, *, encoding: str = "utf-8", invocation_id: str | None = None) -> ToolResult:
        """Construct one explicit request and send it through the same guarded path."""
        request = ToolRequest(
            tool_name="read_file",
            arguments={"path": path, "encoding": encoding},
            invocation_id=invocation_id,
        )
        return self.invoke(request)

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def selects_capability(self) -> bool:
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


__all__ = ["RealReadFileCapability"]
