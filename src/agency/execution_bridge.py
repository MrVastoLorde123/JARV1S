"""M36: bounded bridge from verified execution handoff into M8.5 agency.

This bridge consumes an M35 ExecutionHandoff and delegates the exact
M7.10 READY preparation to the existing ControlledAgency runtime. It does not
create authorization, prepare execution, select providers, or execute directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.agency.controlled_agency import ControlledAgency, ControlledAgencyResult
from src.context.working_context import WorkingContext

from .execution_handoff import ExecutionHandoff


@dataclass(frozen=True)
class AgencyExecutionBridgeResult:
    """Immutable record tying an M35 handoff to the existing M8.5 result."""

    handoff: ExecutionHandoff
    agency_result: ControlledAgencyResult
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.handoff, ExecutionHandoff):
            raise TypeError("handoff must be an ExecutionHandoff")
        if not isinstance(self.agency_result, ControlledAgencyResult):
            raise TypeError("agency_result must be a ControlledAgencyResult")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.handoff.execution_id

    @property
    def steps_executed(self) -> int:
        return self.agency_result.steps_executed

    @property
    def succeeded(self) -> bool:
        return self.agency_result.succeeded

    def to_context(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "assignment_id": self.handoff.assignment_id,
            "worker_id": self.handoff.dispatch.worker_id,
            "steps_executed": self.steps_executed,
            "succeeded": self.succeeded,
            "agency_result": self.agency_result.to_context(),
            "metadata": dict(self.metadata),
            "authorization_created": False,
        }


def run_execution_handoff(
    agency: ControlledAgency,
    handoff: ExecutionHandoff,
    working_context: WorkingContext,
) -> AgencyExecutionBridgeResult:
    """Send an existing authorized preparation through M8.5 controlled agency."""
    if not isinstance(agency, ControlledAgency):
        raise TypeError("agency must be a ControlledAgency")
    if not isinstance(handoff, ExecutionHandoff):
        raise TypeError("handoff must be an ExecutionHandoff")
    if not isinstance(working_context, WorkingContext):
        raise TypeError("working_context must be a WorkingContext")

    result = agency.run(working_context, handoff.preparation)
    return AgencyExecutionBridgeResult(
        handoff=handoff,
        agency_result=result,
        metadata={"source": "M36", "execution_id": handoff.execution_id},
    )


__all__ = ["AgencyExecutionBridgeResult", "run_execution_handoff"]
