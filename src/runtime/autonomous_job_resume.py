from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceReceipt, AutonomousJobPersistenceService
from src.runtime.autonomous_tool_authorization import build_tool_resume_authorization


class AutonomousJobResumeKind(str, Enum):
    AUTHORIZATION = "AUTHORIZATION"
    INPUT = "INPUT"
    TOOL = "TOOL"
    PAUSE = "PAUSE"


_RUNTIME_RESUME_AUTHORIZATION_KEY = "_runtime_resume_authorization"


@dataclass(frozen=True)
class AutonomousJobResumeRequest:
    job_id: str
    kind: AutonomousJobResumeKind
    confirmed: bool = False
    input_context: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class AutonomousJobResumeResult:
    job: AutonomousJob
    persistence_receipt: AutonomousJobPersistenceReceipt


class AutonomousJobResumeBoundary:
    """Explicit state transition for resuming persisted autonomous work."""

    def __init__(self, persistence: AutonomousJobPersistenceService) -> None:
        if not isinstance(persistence, AutonomousJobPersistenceService):
            raise TypeError("persistence must be an AutonomousJobPersistenceService")
        self._persistence = persistence

    def resume(self, request: AutonomousJobResumeRequest) -> AutonomousJobResumeResult:
        if not isinstance(request, AutonomousJobResumeRequest):
            raise TypeError("request must be an AutonomousJobResumeRequest")
        if not isinstance(request.job_id, str) or not request.job_id.strip():
            raise ValueError("job_id must be a non-empty string")
        if not isinstance(request.kind, AutonomousJobResumeKind):
            raise TypeError("kind must be an AutonomousJobResumeKind")
        if not isinstance(request.confirmed, bool):
            raise TypeError("confirmed must be a bool")

        job = self._persistence.restore(request.job_id)
        if job is None:
            raise LookupError(f"autonomous job not found: {request.job_id}")
        expected = {
            AutonomousJobResumeKind.AUTHORIZATION: AutonomousJobStatus.WAITING_AUTHORIZATION,
            AutonomousJobResumeKind.INPUT: AutonomousJobStatus.WAITING_INPUT,
            AutonomousJobResumeKind.TOOL: AutonomousJobStatus.WAITING_TOOL,
            AutonomousJobResumeKind.PAUSE: AutonomousJobStatus.PAUSED,
        }[request.kind]
        if job.status is not expected:
            raise ValueError(f"resume kind {request.kind.value} does not match persisted status {job.status.value}")
        if request.kind in {AutonomousJobResumeKind.AUTHORIZATION, AutonomousJobResumeKind.TOOL} and not request.confirmed:
            raise PermissionError(f"explicit confirmation is required to resume {request.kind.value.lower()} wait")
        if request.kind is not AutonomousJobResumeKind.INPUT and request.input_context is not None:
            raise ValueError("input_context is only valid when resuming input wait")
        if request.kind is AutonomousJobResumeKind.INPUT and (
            not isinstance(request.input_context, Mapping) or not request.input_context
        ):
            raise ValueError("input_context must be a non-empty mapping when resuming input wait")

        next_job = job.resume()
        if request.kind is AutonomousJobResumeKind.TOOL:
            pending = job.working_context.get("pending_tool_request")
            if not isinstance(pending, Mapping):
                raise ValueError("waiting tool task must retain its pending tool request before confirmation")
            tool_name = pending.get("tool_name")
            arguments = pending.get("arguments", {})
            if not isinstance(tool_name, str) or not tool_name.strip():
                raise ValueError("pending tool request must contain a valid tool name")
            if not isinstance(arguments, Mapping):
                raise ValueError("pending tool request arguments must be a mapping")
            next_job = next_job.with_working_context(
                {_RUNTIME_RESUME_AUTHORIZATION_KEY: build_tool_resume_authorization(tool_name, arguments)}
            )
        if request.input_context is not None:
            next_job = next_job.with_working_context(request.input_context)

        return AutonomousJobResumeResult(next_job, self._persistence.persist(next_job))


__all__ = ["AutonomousJobResumeBoundary", "AutonomousJobResumeKind", "AutonomousJobResumeRequest", "AutonomousJobResumeResult"]
