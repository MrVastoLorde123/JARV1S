"""M9.7 bounded objective continuation and driveability."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


class ObjectiveState(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"
    EXHAUSTED = "EXHAUSTED"


class ContinuationStopReason(str, Enum):
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"
    UNCERTAIN = "UNCERTAIN"
    BOUND_EXHAUSTED = "BOUND_EXHAUSTED"


@dataclass(frozen=True)
class Objective:
    """Immutable user-established objective state."""

    objective_id: str
    statement: str
    state: ObjectiveState = ObjectiveState.ACTIVE
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.objective_id, str) or not self.objective_id.strip():
            raise ValueError("objective_id must be a non-empty string")
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError("statement must be a non-empty string")
        if not isinstance(self.state, ObjectiveState):
            try:
                object.__setattr__(self, "state", ObjectiveState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be an ObjectiveState") from exc
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "objective_id": self.objective_id,
            "statement": self.statement,
            "state": self.state.value,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
        }


@dataclass(frozen=True)
class ContinuationCycle:
    """Immutable lineage record for one bounded continuation cycle."""

    cycle_id: str
    objective_id: str
    cycle_number: int
    parent_cycle_id: Optional[str] = None
    observation_ids: tuple[str, ...] = ()
    max_cycles: int = 1

    def __post_init__(self) -> None:
        for name in ("cycle_id", "objective_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.cycle_number, int) or isinstance(self.cycle_number, bool) or self.cycle_number < 0:
            raise ValueError("cycle_number must be a non-negative integer")
        if self.parent_cycle_id is not None and (
            not isinstance(self.parent_cycle_id, str) or not self.parent_cycle_id.strip()
        ):
            raise ValueError("parent_cycle_id must be None or a non-empty string")
        if self.parent_cycle_id == self.cycle_id:
            raise ValueError("cycle cannot be its own parent")
        if not isinstance(self.observation_ids, tuple):
            raise TypeError("observation_ids must be a tuple")
        if len(set(self.observation_ids)) != len(self.observation_ids):
            raise ValueError("observation_ids must be unique")
        for observation_id in self.observation_ids:
            if not isinstance(observation_id, str) or not observation_id.strip():
                raise ValueError("observation ids must be non-empty strings")
        if not isinstance(self.max_cycles, int) or isinstance(self.max_cycles, bool) or self.max_cycles <= 0:
            raise ValueError("max_cycles must be a positive integer")
        if self.cycle_number >= self.max_cycles:
            raise ValueError("cycle_number must be less than max_cycles")
        if self.cycle_number == 0 and self.parent_cycle_id is not None:
            raise ValueError("initial cycle cannot have a parent cycle")
        if self.cycle_number > 0 and self.parent_cycle_id is None:
            raise ValueError("non-initial cycle must preserve parent cycle identity")

    def to_context(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "objective_id": self.objective_id,
            "cycle_number": self.cycle_number,
            "parent_cycle_id": self.parent_cycle_id,
            "observation_ids": self.observation_ids,
            "max_cycles": self.max_cycles,
            "authorization_granted": False,
        }


@dataclass(frozen=True)
class NextStepProposal:
    """Bounded proposal only; never an execution or authorization request."""

    proposal_id: str
    objective_id: str
    cycle_id: str
    description: str
    evidence_ids: tuple[str, ...] = ()
    bounded: bool = True
    execution_requested: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        for name in ("proposal_id", "objective_id", "cycle_id", "description"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.evidence_ids, tuple):
            raise TypeError("evidence_ids must be a tuple")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids must be unique")
        for evidence_id in self.evidence_ids:
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                raise ValueError("evidence ids must be non-empty strings")
        if not isinstance(self.bounded, bool):
            raise TypeError("bounded must be a bool")
        if not isinstance(self.execution_requested, bool):
            raise TypeError("execution_requested must be a bool")
        if not isinstance(self.authorization_granted, bool):
            raise TypeError("authorization_granted must be a bool")
        if not self.bounded:
            raise ValueError("next-step proposals must remain bounded")
        if self.execution_requested:
            raise ValueError("next-step proposals cannot request execution")
        if self.authorization_granted:
            raise ValueError("next-step proposals cannot grant authorization")

    def to_context(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "objective_id": self.objective_id,
            "cycle_id": self.cycle_id,
            "description": self.description,
            "evidence_ids": self.evidence_ids,
            "bounded": self.bounded,
            "execution_requested": False,
            "authorization_granted": False,
        }


@dataclass(frozen=True)
class ContinuationDecision:
    """One bounded continuation outcome: either a proposal or a stop."""

    objective: Objective
    cycle: ContinuationCycle
    proposal: Optional[NextStepProposal] = None
    stop_reason: Optional[ContinuationStopReason] = None

    def __post_init__(self) -> None:
        if not isinstance(self.objective, Objective):
            raise TypeError("objective must be an Objective")
        if not isinstance(self.cycle, ContinuationCycle):
            raise TypeError("cycle must be a ContinuationCycle")
        if self.cycle.objective_id != self.objective.objective_id:
            raise ValueError("cycle/objective identity mismatch")
        if self.proposal is not None:
            if not isinstance(self.proposal, NextStepProposal):
                raise TypeError("proposal must be a NextStepProposal")
            if self.proposal.objective_id != self.objective.objective_id:
                raise ValueError("proposal/objective identity mismatch")
            if self.proposal.cycle_id != self.cycle.cycle_id:
                raise ValueError("proposal/cycle identity mismatch")
        if self.stop_reason is not None and not isinstance(self.stop_reason, ContinuationStopReason):
            try:
                object.__setattr__(self, "stop_reason", ContinuationStopReason(self.stop_reason))
            except (TypeError, ValueError) as exc:
                raise TypeError("stop_reason must be a ContinuationStopReason") from exc
        if self.proposal is None and self.stop_reason is None:
            raise ValueError("decision must contain a proposal or stop reason")
        if self.proposal is not None and self.stop_reason is not None:
            raise ValueError("decision cannot contain both a proposal and stop reason")

    def to_context(self) -> dict[str, Any]:
        return {
            "objective_id": self.objective.objective_id,
            "cycle_id": self.cycle.cycle_id,
            "proposal": None if self.proposal is None else self.proposal.to_context(),
            "stop_reason": None if self.stop_reason is None else self.stop_reason.value,
            "authorization_granted": False,
            "execution_performed": False,
        }


class DriveabilityController:
    """Select bounded continuation decisions without execution or authorization."""

    def decide(
        self,
        objective: Objective,
        cycle: ContinuationCycle,
        *,
        observation_ids: tuple[str, ...] = (),
        next_step: str | None = None,
        blocked: bool = False,
        uncertain: bool = False,
    ) -> ContinuationDecision:
        if not isinstance(objective, Objective):
            raise TypeError("objective must be an Objective")
        if not isinstance(cycle, ContinuationCycle):
            raise TypeError("cycle must be a ContinuationCycle")
        if cycle.objective_id != objective.objective_id:
            raise ValueError("cycle/objective identity mismatch")
        normalized_observations = tuple(observation_ids)
        if normalized_observations != cycle.observation_ids:
            raise ValueError("decision observation provenance must match cycle observations")
        if objective.state == ObjectiveState.COMPLETED:
            return ContinuationDecision(objective, cycle, stop_reason=ContinuationStopReason.COMPLETED)
        if objective.state == ObjectiveState.CANCELLED:
            return ContinuationDecision(objective, cycle, stop_reason=ContinuationStopReason.CANCELLED)
        if objective.state in (ObjectiveState.BLOCKED, ObjectiveState.EXHAUSTED) or blocked:
            return ContinuationDecision(objective, cycle, stop_reason=ContinuationStopReason.BLOCKED)
        if uncertain:
            return ContinuationDecision(objective, cycle, stop_reason=ContinuationStopReason.UNCERTAIN)
        if cycle.cycle_number + 1 >= cycle.max_cycles:
            return ContinuationDecision(objective, cycle, stop_reason=ContinuationStopReason.BOUND_EXHAUSTED)
        if next_step is None or not next_step.strip():
            return ContinuationDecision(objective, cycle, stop_reason=ContinuationStopReason.UNCERTAIN)
        proposal = NextStepProposal(
            proposal_id=f"{cycle.cycle_id}:proposal",
            objective_id=objective.objective_id,
            cycle_id=cycle.cycle_id,
            description=next_step.strip(),
            evidence_ids=normalized_observations,
        )
        return ContinuationDecision(objective, cycle, proposal=proposal)
