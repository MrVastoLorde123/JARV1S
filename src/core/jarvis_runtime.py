"""M12.7 canonical JARVIS runtime facade.

The canonical runtime is the application-facing composition root for the
already-bounded M11/M12 transport path. It does not interpret intent, create
authority, authorize execution, mutate policy, or introduce a second semantic
path. It only composes existing runtime contracts.
"""

from __future__ import annotations

from typing import Callable

from src.core.conversation_store import ConversationStore
from src.core.event_integrated_runtime import EventIntegratedRuntime
from src.core.recovery_integrated_runtime import RecoveryIntegratedResult, RecoveryIntegratedRuntime
from src.core.system_runtime import SystemRuntime
from src.interface.boundary import InterfaceChannel, InterfaceRequest, InterfaceResponse
from src.interface.events import InterfaceEventRuntime
from src.interface.reliability import InterfaceReliabilityRuntime


class JARVISRuntime:
    """Canonical application-facing entrypoint for the integrated JARVIS runtime."""

    def __init__(self, recovery_runtime: RecoveryIntegratedRuntime) -> None:
        if not isinstance(recovery_runtime, RecoveryIntegratedRuntime):
            raise TypeError("recovery_runtime must be a RecoveryIntegratedRuntime")
        self._recovery_runtime = recovery_runtime

    @classmethod
    def from_processor(
        cls,
        processor,
        *,
        conversation_store: ConversationStore | None = None,
        durable_processor_factory=None,
        event_runtime: InterfaceEventRuntime | None = None,
        event_id_factory: Callable[[], str] | None = None,
        reliability_runtime: InterfaceReliabilityRuntime | None = None,
        recovery_id_factory: Callable[[], str] | None = None,
    ) -> "JARVISRuntime":
        """Build the canonical runtime around one existing JARVIS processor."""
        system_runtime = SystemRuntime(
            processor,
            conversation_store=conversation_store,
            durable_processor_factory=durable_processor_factory,
        )
        event_integrated_runtime = EventIntegratedRuntime(
            system_runtime,
            event_runtime=event_runtime,
            event_id_factory=event_id_factory,
        )
        recovery_integrated_runtime = RecoveryIntegratedRuntime(
            event_integrated_runtime,
            reliability_runtime=reliability_runtime,
            recovery_id_factory=recovery_id_factory,
        )
        return cls(recovery_integrated_runtime)

    @property
    def recovery_runtime(self) -> RecoveryIntegratedRuntime:
        return self._recovery_runtime

    @property
    def event_integrated_runtime(self) -> EventIntegratedRuntime:
        return self._recovery_runtime.event_integrated_runtime

    @property
    def system_runtime(self) -> SystemRuntime:
        return self.event_integrated_runtime.system_runtime

    def receive(
        self,
        *,
        request_id: str,
        channel: InterfaceChannel,
        content: str,
        session_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> RecoveryIntegratedResult:
        """Process interface traffic through the canonical integrated path."""
        return self._recovery_runtime.receive(
            request_id=request_id,
            channel=channel,
            content=content,
            session_id=session_id,
            metadata=metadata,
        )

    def process(self, request: InterfaceRequest) -> RecoveryIntegratedResult:
        """Process an existing interface request through the canonical path."""
        if not isinstance(request, InterfaceRequest):
            raise TypeError("request must be an InterfaceRequest")
        return self._recovery_runtime.process(request)

    def respond(self, result: RecoveryIntegratedResult) -> InterfaceResponse:
        """Project a canonical result back to the interface boundary."""
        if not isinstance(result, RecoveryIntegratedResult):
            raise TypeError("result must be a RecoveryIntegratedResult")
        return self._recovery_runtime.respond(result)


__all__ = ["JARVISRuntime"]
