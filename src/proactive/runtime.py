"""M21.6 bounded proactive runtime and feedback integration.

Composes the advisory proactive stages into one inspectable runtime result and
records outcome/feedback signals without granting authority or executing work.
The runtime is deliberately a composition boundary, not an autonomy boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .information_gain import InformationGainAssessment
from .initiative import InitiativeCandidate, InitiativeEvaluation
from .proposal import ProposalEvaluation
from .scheduling import SchedulingEvaluation, SchedulingStatus
from .value import ProposalValueAssessment


class RuntimeError(ValueError):
    """Raised when a proactive runtime contract is invalid."""


class RuntimeStatus(str, Enum):
    READY = "READY"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    INCOMPLETE = "INCOMPLETE"


class FeedbackOutcome(str, Enum):
    NOT_OBSERVED = "NOT_OBSERVED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    SUPERSEDED = "SUPERSEDED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ProactiveFeedback:
    """Immutable outcome signal for later learning."""

    proposal_id: str
    outcome: FeedbackOutcome
    observed: bool = True
    notes: str | None = None
    authority_granted: bool = False
    policy_changed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        if not isinstance(self.outcome, FeedbackOutcome):
            try:
                object.__setattr__(self, "outcome", FeedbackOutcome(self.outcome))
            except (TypeError, ValueError) as exc:
                raise TypeError("outcome must be a FeedbackOutcome") from exc
        if not isinstance(self.observed, bool):
            raise TypeError("observed must be a bool")
        if self.notes is not None and (not isinstance(self.notes, str) or not self.notes.strip()):
            raise ValueError("notes must be None or a non-empty string")
        if not isinstance(self.authority_granted, bool):
            raise TypeError("authority_granted must be a bool")
        if not isinstance(self.policy_changed, bool):
            raise TypeError("policy_changed must be a bool")
        if self.authority_granted:
            raise RuntimeError("feedback cannot grant authority")
        if self.policy_changed:
            raise RuntimeError("feedback cannot mutate policy")
        if self.outcome is FeedbackOutcome.NOT_OBSERVED and self.observed:
            raise ValueError("NOT_OBSERVED feedback cannot be marked observed")
        if self.outcome is not FeedbackOutcome.NOT_OBSERVED and not self.observed:
            raise ValueError("observed feedback requires an observed outcome")

    def to_context(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "outcome": self.outcome.value,
            "observed": self.observed,
            "notes": self.notes,
            "authority_granted": False,
            "policy_changed": False,
        }


@dataclass(frozen=True)
class ProactiveRuntimeResult:
    """Immutable composition result for one bounded proactive proposal."""

    proposal_id: str
    status: RuntimeStatus
    initiative: InitiativeEvaluation
    proposal: ProposalEvaluation
    value: ProposalValueAssessment
    information_gain: InformationGainAssessment
    scheduling: SchedulingEvaluation
    feedback: ProactiveFeedback

    def __post_init__(self) -> None:
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        for name, expected in (
            ("initiative", InitiativeEvaluation),
            ("proposal", ProposalEvaluation),
            ("value", ProposalValueAssessment),
            ("information_gain", InformationGainAssessment),
            ("scheduling", SchedulingEvaluation),
            ("feedback", ProactiveFeedback),
        ):
            if not isinstance(getattr(self, name), expected):
                raise TypeError(f"{name} has an invalid type")
        if not isinstance(self.status, RuntimeStatus):
            try:
                object.__setattr__(self, "status", RuntimeStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise TypeError("status must be a RuntimeStatus") from exc
        if self.proposal.proposal is not None and self.proposal.proposal.proposal_id != self.proposal_id:
            raise ValueError("proposal identity mismatch")
        if self.initiative.candidate_id != self.proposal.candidate_id:
            raise ValueError("initiative/proposal candidate identity mismatch")
        if self.initiative.trigger_id != self.proposal.trigger_id:
            raise ValueError("initiative/proposal trigger identity mismatch")
        for name, value in (
            ("value", self.value.proposal_id),
            ("information_gain", self.information_gain.proposal_id),
            ("scheduling", self.scheduling.proposal_id),
            ("feedback", self.feedback.proposal_id),
        ):
            if value != self.proposal_id:
                raise ValueError(f"{name}/proposal identity mismatch")

    def to_context(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "status": self.status.value,
            "initiative": self.initiative.to_context(),
            "proposal": self.proposal.to_context(),
            "value": self.value.to_context(),
            "information_gain": self.information_gain.to_context(),
            "scheduling": self.scheduling.to_context(),
            "feedback": self.feedback.to_context(),
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "executed": False,
        }


def compose_proactive_runtime(
    *,
    proposal_id: str,
    initiative: InitiativeCandidate,
    initiative_evaluation: InitiativeEvaluation,
    proposal_evaluation: ProposalEvaluation,
    value_assessment: ProposalValueAssessment,
    information_gain: InformationGainAssessment,
    scheduling: SchedulingEvaluation,
    feedback: ProactiveFeedback | None = None,
) -> ProactiveRuntimeResult:
    """Compose bounded proactive outputs without creating authority or execution."""
    if not isinstance(initiative, InitiativeCandidate):
        raise TypeError("initiative must be an InitiativeCandidate")
    if not isinstance(initiative_evaluation, InitiativeEvaluation):
        raise TypeError("initiative_evaluation must be an InitiativeEvaluation")
    if not isinstance(proposal_evaluation, ProposalEvaluation):
        raise TypeError("proposal_evaluation must be a ProposalEvaluation")
    if not isinstance(value_assessment, ProposalValueAssessment):
        raise TypeError("value_assessment must be a ProposalValueAssessment")
    if not isinstance(information_gain, InformationGainAssessment):
        raise TypeError("information_gain must be an InformationGainAssessment")
    if not isinstance(scheduling, SchedulingEvaluation):
        raise TypeError("scheduling must be a SchedulingEvaluation")
    if feedback is None:
        feedback = ProactiveFeedback(
            proposal_id=proposal_id,
            outcome=FeedbackOutcome.NOT_OBSERVED,
            observed=False,
        )
    if initiative_evaluation.candidate_id != initiative.candidate_id:
        raise ValueError("initiative evaluation candidate identity mismatch")
    if initiative_evaluation.trigger_id != initiative.trigger_id:
        raise ValueError("initiative evaluation trigger identity mismatch")
    if proposal_evaluation.candidate_id != initiative.candidate_id:
        raise ValueError("proposal candidate identity mismatch")
    if proposal_evaluation.trigger_id != initiative.trigger_id:
        raise ValueError("proposal trigger identity mismatch")
    if proposal_evaluation.proposal is not None and proposal_evaluation.proposal.proposal_id != proposal_id:
        raise ValueError("proposal evaluation identity mismatch")
    if value_assessment.proposal_id != proposal_id:
        raise ValueError("value assessment identity mismatch")
    if information_gain.proposal_id != proposal_id:
        raise ValueError("information-gain identity mismatch")
    if scheduling.proposal_id != proposal_id:
        raise ValueError("scheduling identity mismatch")
    if feedback.proposal_id != proposal_id:
        raise ValueError("feedback identity mismatch")
    if initiative_evaluation.disposition.value != "ELIGIBLE" or proposal_evaluation.proposal is None:
        status = RuntimeStatus.NEEDS_REVIEW
    elif scheduling.status is not SchedulingStatus.PROPOSED:
        status = RuntimeStatus.NEEDS_REVIEW
    else:
        status = RuntimeStatus.READY
    if value_assessment.authority_granted or value_assessment.authorization_granted or value_assessment.execution_requested:
        raise RuntimeError("value assessment contains forbidden authority or execution state")
    if information_gain.authority_granted or information_gain.authorization_granted or information_gain.execution_requested:
        raise RuntimeError("information-gain assessment contains forbidden authority or execution state")
    return ProactiveRuntimeResult(
        proposal_id=proposal_id,
        status=status,
        initiative=initiative_evaluation,
        proposal=proposal_evaluation,
        value=value_assessment,
        information_gain=information_gain,
        scheduling=scheduling,
        feedback=feedback,
    )


def rank_runtime_results(
    results: Mapping[str, ProactiveRuntimeResult],
) -> tuple[ProactiveRuntimeResult, ...]:
    """Order bounded runtime results deterministically by combined advisory score."""
    for proposal_id, result in results.items():
        if result.proposal_id != proposal_id:
            raise ValueError("mapping key must match runtime proposal_id")
    return tuple(
        sorted(
            results.values(),
            key=lambda item: (-(item.value.score + item.information_gain.score), item.proposal_id),
        )
    )
