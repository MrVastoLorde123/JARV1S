"""M15.4 initiative proposal boundary.

An InitiativeProposal turns an evaluated candidate into a structured proposal
for downstream validation. It preserves lineage and descriptive reasoning,
but does not create authority, confirmation, or permission to execute.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .evaluation import InitiativeEvaluation


class InitiativeProposalValidationError(ValueError):
    """Raised when an initiative proposal violates the M15.4 boundary."""


MAX_ID_LENGTH = 256
MAX_TITLE_LENGTH = 512
MAX_DESCRIPTION_LENGTH = 2048
MAX_ACTION_LENGTH = 2048
MAX_REASONS = 16
MAX_REASON_LENGTH = 512
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InitiativeProposalValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise InitiativeProposalValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise InitiativeProposalValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise InitiativeProposalValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise InitiativeProposalValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class InitiativeProposal:
    """Immutable proposal derived from one evaluated initiative."""

    proposal_id: str
    evaluation: InitiativeEvaluation
    title: str
    description: str
    proposed_action: str
    reasons: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.proposal_id, "proposal_id", MAX_ID_LENGTH)
        if not isinstance(self.evaluation, InitiativeEvaluation):
            raise InitiativeProposalValidationError(
                "evaluation must be an InitiativeEvaluation"
            )
        _text(self.title, "title", MAX_TITLE_LENGTH)
        _text(self.description, "description", MAX_DESCRIPTION_LENGTH)
        _text(self.proposed_action, "proposed_action", MAX_ACTION_LENGTH)
        if not isinstance(self.reasons, tuple):
            raise InitiativeProposalValidationError("reasons must be a tuple")
        if len(self.reasons) > MAX_REASONS:
            raise InitiativeProposalValidationError(
                f"reasons exceeds maximum count of {MAX_REASONS}"
            )
        if len(set(self.reasons)) != len(self.reasons):
            raise InitiativeProposalValidationError("reasons must be unique")
        for index, reason in enumerate(self.reasons):
            _text(reason, f"reasons[{index}]", MAX_REASON_LENGTH)
        if not isinstance(self.metadata, Mapping):
            raise InitiativeProposalValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise InitiativeProposalValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def candidate_id(self) -> str:
        return self.evaluation.candidate.initiative_id

    @property
    def evaluation_id(self) -> str:
        return self.evaluation.evaluation_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "candidate_id": self.candidate_id,
            "evaluation_id": self.evaluation_id,
            "title": self.title,
            "description": self.description,
            "proposed_action": self.proposed_action,
            "reasons": list(self.reasons),
            "metadata": _thaw(self.metadata),
            "proposal_is_instruction": False,
            "proposal_is_authorization": False,
            "confirmation_required": True,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
            "truth_guaranteed": False,
            "user_intent_guaranteed": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
