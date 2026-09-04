"""M15.6 initiative safety boundary.

The proactive layer may detect, evaluate, propose, and schedule initiatives.
This module makes the non-authoritative boundary explicit: an initiative
artifact cannot become an instruction, authorization, policy decision,
confirmation, or execution request merely because it is considered useful,
urgent, or scheduled.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .proposals import InitiativeProposal


class InitiativeSafetyValidationError(ValueError):
    """Raised when an initiative safety check is invalid."""


@dataclass(frozen=True)
class InitiativeSafetyResult:
    """Immutable result of checking an initiative proposal's authority boundary."""

    proposal_id: str
    safe_for_downstream_validation: bool
    blocked_authority_transitions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise InitiativeSafetyValidationError("proposal_id must be a non-empty string")
        if not isinstance(self.safe_for_downstream_validation, bool):
            raise InitiativeSafetyValidationError(
                "safe_for_downstream_validation must be a bool"
            )
        if not isinstance(self.blocked_authority_transitions, tuple):
            raise InitiativeSafetyValidationError(
                "blocked_authority_transitions must be a tuple"
            )
        if any(
            not isinstance(item, str) or not item.strip()
            for item in self.blocked_authority_transitions
        ):
            raise InitiativeSafetyValidationError(
                "blocked_authority_transitions must contain non-empty strings"
            )
        if len(set(self.blocked_authority_transitions)) != len(
            self.blocked_authority_transitions
        ):
            raise InitiativeSafetyValidationError(
                "blocked_authority_transitions must be unique"
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "safe_for_downstream_validation": self.safe_for_downstream_validation,
            "blocked_authority_transitions": list(self.blocked_authority_transitions),
            "initiative_is_instruction": False,
            "confirmation_granted": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


def check_initiative_safety(proposal: InitiativeProposal) -> InitiativeSafetyResult:
    """Verify that a proposal remains proposal-only before downstream authority steps."""
    if not isinstance(proposal, InitiativeProposal):
        raise TypeError("proposal must be an InitiativeProposal")

    return InitiativeSafetyResult(
        proposal_id=proposal.proposal_id,
        safe_for_downstream_validation=True,
        blocked_authority_transitions=(
            "proposal_to_instruction",
            "proposal_to_confirmation",
            "proposal_to_authorization",
            "proposal_to_policy",
            "proposal_to_execution",
        ),
    )
