"""M9.2 bounded worker runtime.

Workers operate inside explicit M9.1 assignments, but they do not own
authority. Each executable action must already arrive as a READY M7
ExecutionPreparation and is consumed through the existing M8 ExecutionRuntime.
Capability names are resolved through an injected resolver so provider-neutral
operation names are never mistaken for capability names.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.agency.controlled_agency import AgencyStopReason, ControlledAgency
from src.agency.execution_lifecycle import ExecutionLifecycle
from src.agency.execution_runtime import ExecutionObservation, ExecutionRuntime
from src.agency.observation_integration import ExecutionObservationContextIntegrator
from src.agency.workforce import WorkerAssignment, WorkerDefinition, WorkerRegistry, WorkerReport, WorkerReportStatus
from src.context.execution_semantics import ExecutionPreparation, ExecutionPreparationStatus
from src.context.working_context import WorkingContext


class WorkerStepProvider(Protocol):
    """Provider of already-authorized M7 preparations for one worker assignment."""

    def next_preparation(
        self,
        worker_context: WorkingContext,
        previous_observation: ExecutionObservation | None,
    ) -> ExecutionPreparation | None:
        """Return the next already-authorized preparation or stop."""
        ...


class WorkerCapabilityResolver(Protocol):
    """Resolve a provider-neutral operation to its declared capability name."""

    def resolve_capability(self, operation: str) -> str:
        """Return capability identity without executing anything."""
        ...


class IdentityCapabilityResolver:
    """Resolver for systems where operation names equal capability names."""

    def resolve_capability(self, operation: str) -> str:
        if not isinstance(operation, str) or not operation.strip():
            raise KeyError("operation must be a non-empty string")
        return operation.strip()


@dataclass(frozen=True)
class WorkerRuntimeResult:
    """Immutable result of one bounded worker run."""

    worker: WorkerDefinition
    assignment: WorkerAssignment
    observations: tuple[ExecutionObservation, ...]
    lifecycles: tuple[ExecutionLifecycle, ...]
    working_context: WorkingContext
    report: WorkerReport
    stop_reason: AgencyStopReason

    @property
    def succeeded(self) -> bool:
        return self.report.status is WorkerReportStatus.COMPLETED


class BoundedWorkerRuntime:
    """Run a worker only within its registered bounds and M7/M8 execution path."""

    def __init__(
        self,
        registry: WorkerRegistry,
        execution_runtime: ExecutionRuntime,
        observation_integrator: ExecutionObservationContextIntegrator,
        capability_resolver: WorkerCapabilityResolver | None = None,
    ) -> None:
        if not isinstance(registry, WorkerRegistry):
            raise TypeError("registry must be a WorkerRegistry.")
        if not isinstance(execution_runtime, ExecutionRuntime):
            raise TypeError("execution_runtime must be an ExecutionRuntime.")
        if not isinstance(observation_integrator, ExecutionObservationContextIntegrator):
            raise TypeError("observation_integrator must be an ExecutionObservationContextIntegrator.")
        resolver = capability_resolver or IdentityCapabilityResolver()
        if not callable(getattr(resolver, "resolve_capability", None)):
            raise TypeError("capability_resolver must expose resolve_capability(operation).")
        self._registry = registry
        self._execution_runtime = execution_runtime
        self._observation_integrator = observation_integrator
        self._capability_resolver = resolver

    def _validate_preparation_capability(self, preparation: ExecutionPreparation, label: str, assignment: WorkerAssignment) -> None:
        if not isinstance(preparation, ExecutionPreparation):
            raise TypeError(f"{label} must be an ExecutionPreparation.")
        if preparation.status is not ExecutionPreparationStatus.READY:
            return
        request = preparation.execution_request
        if request is None:
            raise ValueError(f"READY {label} must contain an execution request.")
        capability = self._capability_resolver.resolve_capability(request.operation)
        if capability not in assignment.allowed_capabilities:
            raise ValueError(f"{label} operation exceeds worker assignment capability bounds.")

    def run(
        self,
        assignment: WorkerAssignment,
        working_context: WorkingContext,
        initial_preparation: ExecutionPreparation | None = None,
        next_step_provider: WorkerStepProvider | None = None,
    ) -> WorkerRuntimeResult:
        """Execute a bounded worker assignment through M8; authority stays upstream."""
        if not isinstance(assignment, WorkerAssignment):
            raise TypeError("assignment must be a WorkerAssignment.")
        if not isinstance(working_context, WorkingContext):
            raise TypeError("working_context must be a WorkingContext.")
        if next_step_provider is not None and not callable(getattr(next_step_provider, "next_preparation", None)):
            raise TypeError("next_step_provider must expose next_preparation(worker_context, previous_observation).")

        worker = self._registry.validate_assignment(assignment)
        if initial_preparation is None:
            report = WorkerReport(
                assignment_id=assignment.assignment_id,
                worker_id=assignment.worker_id,
                status=WorkerReportStatus.BLOCKED,
                summary="worker run requires an initial M7 execution preparation",
            )
            return WorkerRuntimeResult(worker, assignment, (), (), working_context, report, AgencyStopReason.INITIAL_PREPARATION_BLOCKED)

        if initial_preparation.status is not ExecutionPreparationStatus.READY:
            report = WorkerReport(
                assignment_id=assignment.assignment_id,
                worker_id=assignment.worker_id,
                status=WorkerReportStatus.BLOCKED,
                summary="initial worker execution preparation is not READY",
            )
            return WorkerRuntimeResult(worker, assignment, (), (), working_context, report, AgencyStopReason.INITIAL_PREPARATION_BLOCKED)

        self._validate_preparation_capability(initial_preparation, "initial preparation", assignment)

        provider = _BoundedWorkerStepProvider(next_step_provider, assignment, self._capability_resolver) if next_step_provider is not None else None
        agency = ControlledAgency(
            runtime=self._execution_runtime,
            observation_integrator=self._observation_integrator,
            max_steps=min(worker.max_steps, assignment.max_steps),
            next_step_provider=provider,
        )
        result = agency.run(working_context, initial_preparation)

        if result.stop_reason is AgencyStopReason.COMPLETED:
            report_status = WorkerReportStatus.COMPLETED
        elif result.observations:
            report_status = WorkerReportStatus.PARTIAL if result.observations[-1].succeeded else WorkerReportStatus.FAILED
        else:
            report_status = WorkerReportStatus.BLOCKED

        report = WorkerReport(
            assignment_id=assignment.assignment_id,
            worker_id=worker.worker_id,
            status=report_status,
            outputs={"steps_executed": result.steps_executed, "stop_reason": result.stop_reason.value},
            summary=f"worker run stopped: {result.stop_reason.value}",
            metadata={"worker_runtime": "m9.2"},
        )
        return WorkerRuntimeResult(worker, assignment, result.observations, result.lifecycles, result.working_context, report, result.stop_reason)


class _BoundedWorkerStepProvider:
    """Validate every subsequent preparation against the same assignment."""

    def __init__(self, provider: WorkerStepProvider, assignment: WorkerAssignment, capability_resolver: WorkerCapabilityResolver) -> None:
        self._provider = provider
        self._assignment = assignment
        self._capability_resolver = capability_resolver

    def next_preparation(self, working_context: WorkingContext, previous_observation: ExecutionObservation) -> ExecutionPreparation | None:
        preparation = self._provider.next_preparation(working_context, previous_observation)
        if preparation is None:
            return None
        if not isinstance(preparation, ExecutionPreparation):
            return preparation
        if preparation.status is ExecutionPreparationStatus.READY:
            self._validate(preparation)
        return preparation

    def _validate(self, preparation: ExecutionPreparation) -> None:
        request = preparation.execution_request
        if request is None:
            raise ValueError("READY next preparation must contain an execution request.")
        capability = self._capability_resolver.resolve_capability(request.operation)
        if capability not in self._assignment.allowed_capabilities:
            raise ValueError("next execution operation exceeds worker assignment capability bounds.")
