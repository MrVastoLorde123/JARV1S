"""M28 local bootstrap for the runtime-owned world boundary.

The local launcher is not allowed to invent worker execution just to make the
browser world look populated. This bootstrap creates the real M28 composition
with an empty worker registry and an explicit unavailable M8 adapter. No agent
can be instantiated until the application supplies a real M9 worker definition
and a real authorized M7/M8 execution path.
"""

from __future__ import annotations

from typing import Any

from src.agency.execution_runtime import ExecutionOutcome, ExecutionRuntime
from src.agency.observation_integration import ExecutionObservationContextIntegrator
from src.agency.worker_runtime import BoundedWorkerRuntime
from src.agency.workforce import WorkerRegistry
from src.agency.world_runtime import AgentWorldRuntime


class UnavailableExecutionAdapter:
    """Explicitly unavailable local execution surface; never pretends to execute."""

    def execute(self, request: Any) -> ExecutionOutcome:
        return ExecutionOutcome(
            success=False,
            error={
                "code": "execution_adapter_not_configured",
                "message": "No local M8 execution adapter is configured for world workers.",
                "operation": getattr(request, "operation", None),
            },
            metadata={"bootstrap": "m28-local-world"},
        )


def create_local_world_runtime() -> AgentWorldRuntime:
    """Build the real world runtime without manufacturing executable workers."""
    registry = WorkerRegistry()
    worker_runtime = BoundedWorkerRuntime(
        registry,
        ExecutionRuntime(UnavailableExecutionAdapter()),
        ExecutionObservationContextIntegrator(),
    )
    return AgentWorldRuntime(registry, worker_runtime)


__all__ = ["UnavailableExecutionAdapter", "create_local_world_runtime"]
