"""M38: bounded recovery decisions from independent verification outcomes.

This module translates an existing verification decision into a bounded
continuation/stop decision. It never authorizes, executes, verifies the world,
or turns a recovery proposal into an execution request.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .driveability import ContinuationCycle, ContinuationDecision, DriveabilityController, Objective, ObjectiveState
from .execution_outcome import VerificationDecision, VerificationDisposition


class RecoveryDisposition(str, Enum):
    CONTINUE = "CONTINUE"
    COMPLETE = "COMPLETE"
    STOP_BLOCKED = "STOP_BLOCKED"
    STOP_UNCERTAIN = "STOP_UNCERTAIN"
    STOP_REJECTED = "STOP_REJECTED"


@dataclass(frozen=True)
class RecoveryDecision:
    """Immutable bounded recovery result derived from verification evidence."""

    execution_id: str
    disposition: RecoveryDisposition
    continuation: ContinuationDecision
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")
        if not isinstance(self.disposition, RecoveryDisposition):
            raise TypeError("disposition must be a RecoveryDisposition")
        if not isinstance(self.continuation, ContinuationDecision):
            raise TypeError("continuation must be a ContinuationDecision")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")

    @property
    def execution_requested(self) -> bool:
        return False

    @property
    def authorization_granted(self) -> bool:
        return False

    def to_context(self) -> dict[str, object]:
        return {
            "execution_id": self.execution_id,
            "disposition": self.disposition.value,
            "reason": self.reason,
            "continuation": self.continuation.to_context(),
            "execution_requested": False,
            "authorization_granted": False,
        }


def derive_recovery_decision(
    verification: VerificationDecision,
    objective: Objective,
    cycle: ContinuationCycle,
    *,
    observation_ids: tuple[str, ...] = (),
    next_step: str | None = None,
    controller: DriveabilityController | None = None,
) -> RecoveryDecision:
    """Translate an existing verification decision into a bounded recovery decision."""
    if not isinstance(verification, VerificationDecision):
        raise TypeError("verification must be a VerificationDecision")
    if not isinstance(objective, Objective):
        raise TypeError("objective must be an Objective")
    if not isinstance(cycle, ContinuationCycle):
        raise TypeError("cycle must be a ContinuationCycle")
    if cycle.objective_id != objective.objective_id:
        raise ValueError("cycle/objective identity mismatch")
    if not isinstance(observation_ids, tuple):
        raise TypeError("observation_ids must be a tuple")

    chooser = controller or DriveabilityController()

    if verification.disposition is VerificationDisposition.VERIFIED:
        completed_objective = Objective(
            objective_id=objective.objective_id,
            statement=objective.statement,
            state=ObjectiveState.COMPLETED,
            metadata=objective.metadata,
        )
        continuation = chooser.decide(completed_objective, cycle, observation_ids=observation_ids)
        return RecoveryDecision(
            execution_id=verification.execution_id,
            disposition=RecoveryDisposition.COMPLETE,
            continuation=continuation,
            reason="independent verification marked the execution verified",
        )

    if verification.disposition is VerificationDisposition.BLOCKED:
        continuation = chooser.decide(objective, cycle, observation_ids=observation_ids, blocked=True)
        return RecoveryDecision(
            execution_id=verification.execution_id,
            disposition=RecoveryDisposition.STOP_BLOCKED,
            continuation=continuation,
            reason=verification.reason,
        )

    if verification.disposition is VerificationDisposition.REJECTED:
        continuation = chooser.decide(objective, cycle, observation_ids=observation_ids, next_step=next_step)
        disposition = RecoveryDisposition.CONTINUE if continuation.proposal is not None else RecoveryDisposition.STOP_REJECTED
        return RecoveryDecision(
            execution_id=verification.execution_id,
            disposition=disposition,
            continuation=continuation,
            reason=verification.reason,
        )

    continuation = chooser.decide(objective, cycle, observation_ids=observation_ids, uncertain=True)
    return RecoveryDecision(
        execution_id=verification.execution_id,
        disposition=RecoveryDisposition.STOP_UNCERTAIN,
        continuation=continuation,
        reason=verification.reason,
    )


__all__ = ["RecoveryDecision", "RecoveryDisposition", "derive_recovery_decision"]
