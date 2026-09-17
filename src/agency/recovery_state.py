"""M39: reconcile bounded recovery outcomes into operational WorkState.

This module applies an already-derived M38 recovery decision to the M31 work
state substrate. It records the operational consequence of recovery without
creating authority, authorization, execution, verification, or persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any

from .verification_recovery import RecoveryDecision, RecoveryDisposition
from .work_state import WorkBlocker, WorkStage, WorkState, WorkStatus


class RecoveryStateDisposition(str, Enum):
    CONTINUING = "CONTINUING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    UNCERTAIN = "UNCERTAIN"
    FAILED = "FAILED"


@dataclass(frozen=True)
class RecoveryReconciliation:
    """Immutable lineage record for applying recovery to WorkState."""

    work_id: str
    execution_id: str
    decision: RecoveryDecision
    before: WorkState
    after: WorkState
    disposition: RecoveryStateDisposition
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.work_id, str) or not self.work_id.strip():
            raise ValueError("work_id must be a non-empty string")
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")
        if not isinstance(self.decision, RecoveryDecision):
            raise TypeError("decision must be a RecoveryDecision")
        if not isinstance(self.before, WorkState) or not isinstance(self.after, WorkState):
            raise TypeError("before and after must be WorkState values")
        if self.before.work_id != self.work_id or self.after.work_id != self.work_id:
            raise ValueError("reconciliation work identity must match both states")
        if self.decision.execution_id != self.execution_id:
            raise ValueError("reconciliation execution identity must match decision")
        if not isinstance(self.disposition, RecoveryStateDisposition):
            raise TypeError("disposition must be a RecoveryStateDisposition")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dict")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "work_id": self.work_id,
            "execution_id": self.execution_id,
            "recovery_disposition": self.decision.disposition.value,
            "state_disposition": self.disposition.value,
            "before_stage": self.before.stage.value,
            "after_stage": self.after.stage.value,
            "before_status": self.before.status.value,
            "after_status": self.after.status.value,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
        }


def _metadata(work_state: WorkState, decision: RecoveryDecision) -> dict[str, Any]:
    return {
        **dict(work_state.metadata),
        "recovery_execution_id": decision.execution_id,
        "recovery_disposition": decision.disposition.value,
        "recovery_objective_id": decision.continuation.objective.objective_id,
        "recovery_cycle_id": decision.continuation.cycle.cycle_id,
    }


def reconcile_recovery(
    work_state: WorkState,
    decision: RecoveryDecision,
) -> RecoveryReconciliation:
    """Project a bounded recovery decision into the operational work lifecycle."""
    if not isinstance(work_state, WorkState):
        raise TypeError("work_state must be a WorkState")
    if not isinstance(decision, RecoveryDecision):
        raise TypeError("decision must be a RecoveryDecision")

    common = {"metadata": _metadata(work_state, decision), "current_step": work_state.current_step}

    if decision.disposition is RecoveryDisposition.COMPLETE:
        after = WorkState(
            work_id=work_state.work_id,
            objective=work_state.objective,
            stage=WorkStage.COMPLETE,
            status=WorkStatus.COMPLETE,
            role=work_state.role,
            progress=1.0,
            current_step=None,
            blockers=(),
            required_capabilities=work_state.required_capabilities,
            assigned_agent_ids=work_state.assigned_agent_ids,
            evidence_cursor=work_state.evidence_cursor,
            source=work_state.source,
            metadata=common["metadata"],
        )
        disposition = RecoveryStateDisposition.COMPLETED
    elif decision.disposition is RecoveryDisposition.CONTINUE:
        proposal = decision.continuation.proposal
        if proposal is None:
            raise ValueError("CONTINUE recovery requires a continuation proposal")
        after = WorkState(
            work_id=work_state.work_id,
            objective=work_state.objective,
            stage=WorkStage.PLANNING,
            status=WorkStatus.ACTIVE,
            role=work_state.role,
            progress=work_state.progress,
            current_step=proposal.description,
            blockers=work_state.blockers,
            required_capabilities=work_state.required_capabilities,
            assigned_agent_ids=work_state.assigned_agent_ids,
            evidence_cursor=work_state.evidence_cursor,
            source=work_state.source,
            metadata={**common["metadata"], "recovery_proposal_id": proposal.proposal_id},
        )
        disposition = RecoveryStateDisposition.CONTINUING
    elif decision.disposition is RecoveryDisposition.STOP_BLOCKED:
        blocker = WorkBlocker(
            blocker_id=f"recovery:{decision.execution_id}",
            message=decision.reason,
            severity="BLOCKING",
            stage=WorkStage.BLOCKED,
            metadata={"source": "M39", "execution_id": decision.execution_id},
        )
        after = WorkState(
            work_id=work_state.work_id,
            objective=work_state.objective,
            stage=WorkStage.BLOCKED,
            status=WorkStatus.BLOCKED,
            role=work_state.role,
            progress=work_state.progress,
            current_step=None,
            blockers=work_state.blockers + (blocker,),
            required_capabilities=work_state.required_capabilities,
            assigned_agent_ids=work_state.assigned_agent_ids,
            evidence_cursor=work_state.evidence_cursor,
            source=work_state.source,
            metadata=common["metadata"],
        )
        disposition = RecoveryStateDisposition.BLOCKED
    elif decision.disposition is RecoveryDisposition.STOP_UNCERTAIN:
        blocker = WorkBlocker(
            blocker_id=f"recovery:{decision.execution_id}",
            message=decision.reason,
            severity="UNCERTAIN",
            stage=WorkStage.VERIFYING,
            metadata={"source": "M39", "execution_id": decision.execution_id},
        )
        after = WorkState(
            work_id=work_state.work_id,
            objective=work_state.objective,
            stage=WorkStage.VERIFYING,
            status=WorkStatus.BLOCKED,
            role=work_state.role,
            progress=work_state.progress,
            current_step=None,
            blockers=work_state.blockers + (blocker,),
            required_capabilities=work_state.required_capabilities,
            assigned_agent_ids=work_state.assigned_agent_ids,
            evidence_cursor=work_state.evidence_cursor,
            source=work_state.source,
            metadata=common["metadata"],
        )
        disposition = RecoveryStateDisposition.UNCERTAIN
    else:
        after = WorkState(
            work_id=work_state.work_id,
            objective=work_state.objective,
            stage=WorkStage.FAILED,
            status=WorkStatus.FAILED,
            role=work_state.role,
            progress=work_state.progress,
            current_step=None,
            blockers=work_state.blockers,
            required_capabilities=work_state.required_capabilities,
            assigned_agent_ids=work_state.assigned_agent_ids,
            evidence_cursor=work_state.evidence_cursor,
            source=work_state.source,
            metadata=common["metadata"],
        )
        disposition = RecoveryStateDisposition.FAILED

    return RecoveryReconciliation(
        work_id=work_state.work_id,
        execution_id=decision.execution_id,
        decision=decision,
        before=work_state,
        after=after,
        disposition=disposition,
        metadata={"source": "M39", "objective_id": decision.continuation.objective.objective_id},
    )


__all__ = ["RecoveryReconciliation", "RecoveryStateDisposition", "reconcile_recovery"]
