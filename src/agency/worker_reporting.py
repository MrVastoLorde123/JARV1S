"""M9.4 worker reporting and result integration.

Worker reports are immutable evidence about delegated work. Integration into
JARVIS context preserves worker/assignment identity and never creates
authorization, permission, provider handles, or truth guarantees.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from src.agency.workforce import WorkerAssignment, WorkerReport, WorkerReportStatus
from src.context.models import ContextItem, OBSERVATION, PRIVATE
from src.context.working_context import WorkingContext


class WorkerReportConflictError(ValueError):
    """Raised when a worker report identity conflicts with stored state."""


@dataclass(frozen=True)
class WorkerReportStore:
    """Immutable deterministic store of worker reports keyed by report identity."""

    reports: tuple[WorkerReport, ...] = ()

    @staticmethod
    def _identity(report: WorkerReport) -> tuple[str, str]:
        return report.worker_id, report.assignment_id

    def __post_init__(self) -> None:
        if not isinstance(self.reports, tuple):
            raise TypeError("reports must be a tuple")
        seen: set[tuple[str, str]] = set()
        for report in self.reports:
            if not isinstance(report, WorkerReport):
                raise TypeError("reports must contain WorkerReport values")
            identity = self._identity(report)
            if identity in seen:
                raise WorkerReportConflictError(
                    f"worker report for worker '{identity[0]}' and assignment '{identity[1]}' is already stored"
                )
            seen.add(identity)

    def append(self, report: WorkerReport) -> "WorkerReportStore":
        if not isinstance(report, WorkerReport):
            raise TypeError("report must be a WorkerReport")
        if any(self._identity(item) == self._identity(report) for item in self.reports):
            raise WorkerReportConflictError(
                f"worker report for worker '{report.worker_id}' and assignment '{report.assignment_id}' is already stored"
            )
        return WorkerReportStore(self.reports + (report,))

    def get(self, worker_id: str, assignment_id: str) -> WorkerReport | None:
        for report in self.reports:
            if report.worker_id == worker_id and report.assignment_id == assignment_id:
                return report
        return None

    def list(self) -> tuple[WorkerReport, ...]:
        return self.reports


@dataclass(frozen=True)
class WorkerReportIntegrator:
    """Project worker reports into WorkingContext as non-authoritative observations."""

    store: WorkerReportStore = WorkerReportStore()

    def _validate_report(self, assignment: WorkerAssignment, report: WorkerReport) -> None:
        if not isinstance(assignment, WorkerAssignment):
            raise TypeError("assignment must be a WorkerAssignment")
        if not isinstance(report, WorkerReport):
            raise TypeError("report must be a WorkerReport")
        if report.worker_id != assignment.worker_id:
            raise ValueError("report worker identity must match assignment worker identity")
        unknown_outputs = set(report.outputs) - set(assignment.output_scope)
        if unknown_outputs:
            raise ValueError(
                f"worker report outputs exceed assignment scope: {sorted(unknown_outputs)}"
            )

    def record(self, assignment: WorkerAssignment, report: WorkerReport) -> ContextItem:
        self._validate_report(assignment, report)
        new_store = self.store.append(report)
        object.__setattr__(self, "store", new_store)
        return self.to_context_item(assignment, report)

    @staticmethod
    def to_context_item(assignment: WorkerAssignment, report: WorkerReport) -> ContextItem:
        if not isinstance(assignment, WorkerAssignment):
            raise TypeError("assignment must be a WorkerAssignment")
        if not isinstance(report, WorkerReport):
            raise TypeError("report must be a WorkerReport")
        if report.worker_id != assignment.worker_id:
            raise ValueError("report worker identity must match assignment worker identity")

        payload = {
            "assignment_id": report.assignment_id,
            "worker_id": report.worker_id,
            "status": report.status.value,
            "outputs": dict(report.outputs),
            "summary": report.summary,
            "metadata": dict(report.metadata),
            "authority_granted": False,
            "truth_guaranteed": False,
        }
        return ContextItem(
            source_type=OBSERVATION,
            content=json.dumps(payload, sort_keys=True, default=str),
            relevance_score=1.0,
            confidence=1.0,
            importance=1.0,
            privacy_level=PRIVATE,
            provenance={
                "source_id": f"worker:{report.worker_id}:assignment:{report.assignment_id}",
                "worker_id": report.worker_id,
                "assignment_id": report.assignment_id,
                "worker_report_status": report.status.value,
                "observation_type": "worker_report",
            },
        )

    def integrate(
        self,
        working_context: WorkingContext,
        assignment: WorkerAssignment,
        report: WorkerReport,
    ) -> WorkingContext:
        if not isinstance(working_context, WorkingContext):
            raise TypeError("working_context must be a WorkingContext")
        projected = self.record(assignment, report)
        return WorkingContext(
            request=working_context.request,
            context_package=working_context.context_package,
            conversation_state=working_context.conversation_state,
            task=working_context.task,
            execution_state=working_context.execution_state,
            execution_progress=working_context.execution_progress,
            observations=working_context.observations + (projected,),
            source_selection=working_context.source_selection,
            metadata={
                **dict(working_context.metadata),
                "worker_report_integration": "m9.4",
            },
        )
