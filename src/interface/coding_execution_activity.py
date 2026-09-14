"""Runtime activity bridge for bounded coding tool execution."""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Mapping

from src.core.interface_backend import InterfaceOperation, InterfaceResponseStatus
from src.core.runtime_activity_stream import RuntimeActivityEvent, RuntimeActivityKind, RuntimeActivityStream
from src.tools.models import ToolError, ToolRequest, ToolResult


@dataclass
class CodingExecutionActivityRecorder:
    """Publish sanitized coding execution lifecycle observations."""

    stream: RuntimeActivityStream
    durable_store: object | None = None

    def __post_init__(self) -> None:
        if type(self.stream) is not RuntimeActivityStream:
            raise TypeError("stream must be a RuntimeActivityStream")
        if self.durable_store is not None and not callable(getattr(self.durable_store, "append", None)):
            raise TypeError("durable_store must provide append(event)")
        self._lock = RLock()
        self._counter = self.stream.size

    def publish_started(self, request: ToolRequest) -> RuntimeActivityEvent:
        verification = request.tool_name.strip().lower() == "run_test"
        kind = RuntimeActivityKind.VERIFICATION_STARTED if verification else RuntimeActivityKind.TOOL_EXECUTION_STARTED
        operation = InterfaceOperation.VERIFY if verification else InterfaceOperation.APPLY
        return self._publish(
            request=request,
            operation=operation,
            kind=kind,
            status=None,
            stage="VERIFICATION" if verification else "TOOL_EXECUTION",
            summary="coding verification started" if verification else "coding tool execution started",
            metadata=self._safe_metadata(request),
        )

    def publish_completed(self, request: ToolRequest, result: ToolResult) -> RuntimeActivityEvent:
        verification = request.tool_name.strip().lower() == "run_test"
        kind = RuntimeActivityKind.VERIFICATION_COMPLETED if verification else RuntimeActivityKind.TOOL_EXECUTION_COMPLETED
        operation = InterfaceOperation.VERIFY if verification else InterfaceOperation.APPLY
        metadata = self._safe_metadata(request)
        metadata["success"] = result.success
        if result.error is not None:
            metadata["error_code"] = result.error.code
            metadata["error"] = result.error.message
        return self._publish(
            request=request,
            operation=operation,
            kind=kind,
            status=InterfaceResponseStatus.ACCEPTED if result.success else InterfaceResponseStatus.FAILED,
            stage="VERIFICATION" if verification else "TOOL_EXECUTION",
            summary="coding verification completed" if verification else "coding tool execution completed",
            metadata=metadata,
        )

    @staticmethod
    def _safe_metadata(request: ToolRequest) -> dict[str, object]:
        metadata = request.metadata
        safe: dict[str, object] = {
            "event_source": "coding_worker",
            "tool_name": request.tool_name,
            "invocation_id": request.invocation_id,
        }
        for key in ("task_id", "coding_operation_id", "edit_index", "phase"):
            if key in metadata and isinstance(metadata[key], (str, int, bool)):
                safe[key] = metadata[key]
        return safe

    def _publish(
        self,
        *,
        request: ToolRequest,
        operation: InterfaceOperation,
        kind: RuntimeActivityKind,
        status: InterfaceResponseStatus | None,
        stage: str,
        summary: str,
        metadata: Mapping[str, object],
    ) -> RuntimeActivityEvent:
        with self._lock:
            self._counter += 1
            event = RuntimeActivityEvent(
                event_id=f"coding-activity-{self._counter}",
                sequence=self.stream.size + 1,
                session_id="runtime",
                actor_id="coding_agent",
                request_id=request.invocation_id or request.tool_name,
                operation=operation,
                kind=kind,
                status=status,
                stage=stage,
                summary=summary,
                metadata=dict(metadata),
            )
            if self.durable_store is not None:
                self.durable_store.append(event)
            self.stream.publish(event)
            return event


class ObservingToolInvoker:
    """Wrap an existing tool invoker without changing its authority semantics."""

    def __init__(self, delegate, recorder: CodingExecutionActivityRecorder) -> None:
        if not callable(getattr(delegate, "invoke", None)):
            raise TypeError("delegate must provide invoke(request)")
        if not isinstance(recorder, CodingExecutionActivityRecorder):
            raise TypeError("recorder must be CodingExecutionActivityRecorder")
        self._delegate = delegate
        self._recorder = recorder

    def __eq__(self, other: object) -> bool:
        """Preserve identity semantics for legacy dependency-injection contracts."""
        if isinstance(other, ObservingToolInvoker):
            return self._delegate == other._delegate and self._recorder == other._recorder
        return self._delegate == other

    def invoke(self, request: ToolRequest) -> ToolResult:
        self._recorder.publish_started(request)
        try:
            result = self._delegate.invoke(request)
        except Exception as exc:
            result = ToolResult(
                tool_name=request.tool_name,
                invocation_id=request.invocation_id,
                success=False,
                error=ToolError(code="executor_exception", message=str(exc) or exc.__class__.__name__),
            )
            self._recorder.publish_completed(request, result)
            raise
        self._recorder.publish_completed(request, result)
        return result


__all__ = ["CodingExecutionActivityRecorder", "ObservingToolInvoker"]
