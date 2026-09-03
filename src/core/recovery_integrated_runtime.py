"""M12.6 recovery-integrated system runtime.

This module composes the verified EventIntegratedRuntime with the existing
provider-neutral interface reliability runtime. Recovery state is transport
continuity metadata only; RETRY, RESUME, and REPLAY never become authorization,
execution permission, or semantic intent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from uuid import uuid4

from src.core.event_integrated_runtime import EventIntegratedResult, EventIntegratedRuntime
from src.interface.boundary import InterfaceChannel, InterfaceRequest, InterfaceResponse
from src.interface.reliability import (
    InterfaceRecoveryAction,
    InterfaceRecoveryState,
    InterfaceReliabilityRuntime,
)


@dataclass(frozen=True)
class RecoveryIntegratedResult:
    """Canonical event result paired with immutable recovery state."""

    result: EventIntegratedResult
    recovery: InterfaceRecoveryState

    def to_interface_response(self) -> InterfaceResponse:
        return self.result.to_interface_response()


class RecoveryIntegratedRuntime:
    """Add transport recovery observation around the existing event runtime."""

    def __init__(
        self,
        event_integrated_runtime: EventIntegratedRuntime,
        *,
        reliability_runtime: InterfaceReliabilityRuntime | None = None,
        recovery_id_factory: Callable[[], str] | None = None,
    ) -> None:
        if not isinstance(event_integrated_runtime, EventIntegratedRuntime):
            raise TypeError("event_integrated_runtime must be an EventIntegratedRuntime")
        if reliability_runtime is not None and not isinstance(
            reliability_runtime, InterfaceReliabilityRuntime
        ):
            raise TypeError("reliability_runtime must be an InterfaceReliabilityRuntime")
        if recovery_id_factory is not None and not callable(recovery_id_factory):
            raise TypeError("recovery_id_factory must be callable or None")

        self._event_integrated_runtime = event_integrated_runtime
        self._reliability_runtime = reliability_runtime or InterfaceReliabilityRuntime()
        self._recovery_id_factory = recovery_id_factory or (lambda: str(uuid4()))

    @property
    def event_integrated_runtime(self) -> EventIntegratedRuntime:
        return self._event_integrated_runtime

    @property
    def reliability_runtime(self) -> InterfaceReliabilityRuntime:
        return self._reliability_runtime

    def receive(
        self,
        *,
        request_id: str,
        channel: InterfaceChannel,
        content: str,
        session_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> RecoveryIntegratedResult:
        """Create an interface request and route it through event/recovery integration."""
        request = InterfaceRequest(
            request_id=request_id,
            channel=channel,
            content=content,
            session_id=session_id,
            metadata={} if metadata is None else metadata,
        )
        return self.process(request)

    def process(self, request: InterfaceRequest) -> RecoveryIntegratedResult:
        """Run one request and record only mechanical reliability state."""
        if not isinstance(request, InterfaceRequest):
            raise TypeError("request must be an InterfaceRequest")

        recovery = self._reliability_runtime.start(request.request_id)
        try:
            result = self._event_integrated_runtime.process(request)
            recovery = self._reliability_runtime.healthy(
                recovery,
                record_id=self._recovery_id_factory(),
                metadata={"integration": "M12.6"},
            )
            return RecoveryIntegratedResult(result=result, recovery=recovery)
        except Exception as exc:
            recovery = self._reliability_runtime.failed(
                recovery,
                record_id=self._recovery_id_factory(),
                reason=f"{type(exc).__name__}: {exc}",
                action=InterfaceRecoveryAction.ABANDON,
                metadata={"integration": "M12.6"},
            )
            # Recovery state is intentionally observable through a returned
            # result only on success. On failure the original exception remains
            # the semantic/control-flow signal and is never converted to retry
            # permission or authorization.
            raise

    def respond(self, result: RecoveryIntegratedResult) -> InterfaceResponse:
        """Project only the underlying canonical response."""
        if not isinstance(result, RecoveryIntegratedResult):
            raise TypeError("result must be a RecoveryIntegratedResult")
        return result.to_interface_response()


__all__ = ["RecoveryIntegratedResult", "RecoveryIntegratedRuntime"]
