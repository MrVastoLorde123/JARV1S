"""M15.7 integrated proactive initiative boundary.

InitiativeRuntime composes the M15 proactive stages into one immutable facade.
It does not create an authority path: detection, evaluation, proposal,
scheduling, and safety remain descriptive and downstream of the existing
validation/policy/confirmation/authorization chain.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .evaluation import InitiativeEvaluation
from .initiative import InitiativeCandidate
from .initiative_safety import InitiativeSafetyResult, check_initiative_safety
from .opportunities import OpportunityDetectionSet
from .proposals import InitiativeProposal
from .scheduling import ProactiveSchedule


class InitiativeRuntimeValidationError(ValueError):
    """Raised when the integrated initiative runtime is invalid."""


@dataclass(frozen=True)
class InitiativeRuntime:
    """Immutable composition of M15 proactive initiative artifacts."""

    detections: OpportunityDetectionSet | None = None
    candidate: InitiativeCandidate | None = None
    evaluation: InitiativeEvaluation | None = None
    proposal: InitiativeProposal | None = None
    schedule: ProactiveSchedule | None = None
    safety: InitiativeSafetyResult | None = None

    def __post_init__(self) -> None:
        values = (
            ("detections", self.detections, OpportunityDetectionSet),
            ("candidate", self.candidate, InitiativeCandidate),
            ("evaluation", self.evaluation, InitiativeEvaluation),
            ("proposal", self.proposal, InitiativeProposal),
            ("schedule", self.schedule, ProactiveSchedule),
            ("safety", self.safety, InitiativeSafetyResult),
        )
        for name, value, expected in values:
            if value is not None and not isinstance(value, expected):
                raise InitiativeRuntimeValidationError(
                    f"{name} must be {expected.__name__} or None"
                )

        if self.evaluation is not None and self.candidate is not None:
            if self.evaluation.candidate.initiative_id != self.candidate.initiative_id:
                raise InitiativeRuntimeValidationError("evaluation must reference candidate")
        if self.proposal is not None and self.evaluation is not None:
            if self.proposal.evaluation_id != self.evaluation.evaluation_id:
                raise InitiativeRuntimeValidationError("proposal must reference evaluation")
        if self.schedule is not None and self.proposal is not None:
            if self.schedule.proposal_id != self.proposal.proposal_id:
                raise InitiativeRuntimeValidationError("schedule must reference proposal")
        if self.safety is not None and self.proposal is not None:
            if self.safety.proposal_id != self.proposal.proposal_id:
                raise InitiativeRuntimeValidationError("safety must reference proposal")

    def with_detections(self, detections: OpportunityDetectionSet | None) -> "InitiativeRuntime":
        return InitiativeRuntime(detections, self.candidate, self.evaluation, self.proposal, self.schedule, self.safety)

    def with_candidate(self, candidate: InitiativeCandidate | None) -> "InitiativeRuntime":
        return InitiativeRuntime(self.detections, candidate, self.evaluation, self.proposal, self.schedule, self.safety)

    def with_evaluation(self, evaluation: InitiativeEvaluation | None) -> "InitiativeRuntime":
        return InitiativeRuntime(self.detections, self.candidate, evaluation, self.proposal, self.schedule, self.safety)

    def with_proposal(self, proposal: InitiativeProposal | None) -> "InitiativeRuntime":
        return InitiativeRuntime(self.detections, self.candidate, self.evaluation, proposal, self.schedule, self.safety)

    def with_schedule(self, schedule: ProactiveSchedule | None) -> "InitiativeRuntime":
        return InitiativeRuntime(self.detections, self.candidate, self.evaluation, self.proposal, schedule, self.safety)

    def with_safety(self, safety: InitiativeSafetyResult | None) -> "InitiativeRuntime":
        return InitiativeRuntime(self.detections, self.candidate, self.evaluation, self.proposal, self.schedule, safety)

    def safety_check(self) -> InitiativeSafetyResult:
        if self.proposal is None:
            raise InitiativeRuntimeValidationError("proposal is required for safety check")
        return check_initiative_safety(self.proposal)

    def to_dict(self) -> dict[str, Any]:
        return {
            "detections": None if self.detections is None else self.detections.to_dict(),
            "candidate": None if self.candidate is None else self.candidate.to_dict(),
            "evaluation": None if self.evaluation is None else self.evaluation.to_dict(),
            "proposal": None if self.proposal is None else self.proposal.to_dict(),
            "schedule": None if self.schedule is None else self.schedule.to_dict(),
            "safety": None if self.safety is None else self.safety.to_dict(),
            "initiative_is_instruction": False,
            "obligation_created": False,
            "confirmation_granted": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
