"""M10.3 bounded preference and behavior adaptation boundary.

Adaptation is a proposal/state mechanism. It may change how JARVIS behaves,
but it never changes authority, policy, permission, capability, objective,
or execution semantics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.learning.evaluation import Evaluation


class AdaptationKind(str, Enum):
    PREFERENCE = "PREFERENCE"
    BEHAVIOR = "BEHAVIOR"


class AdaptationState(str, Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVERSED = "REVERSED"


class AdaptationConflictError(ValueError):
    """Raised when adaptation identity conflicts with stored state."""


@dataclass(frozen=True)
class AdaptationProposal:
    """Immutable candidate for a bounded non-authoritative adaptation."""

    proposal_id: str
    kind: AdaptationKind
    target: str
    current_value: Any
    proposed_value: Any
    supporting_evaluation_ids: tuple[str, ...]
    rationale: str
    confidence: float | None = None
    reversible: bool = True
    explicit_user_preference: bool = False

    def __post_init__(self) -> None:
        for name in ("proposal_id", "target", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.kind, AdaptationKind):
            try:
                object.__setattr__(self, "kind", AdaptationKind(self.kind))
            except (TypeError, ValueError) as exc:
                raise TypeError("kind must be an AdaptationKind") from exc
        if not isinstance(self.supporting_evaluation_ids, tuple):
            raise TypeError("supporting_evaluation_ids must be a tuple")
        if len(set(self.supporting_evaluation_ids)) != len(self.supporting_evaluation_ids):
            raise ValueError("supporting evaluation identities must be unique")
        if not all(isinstance(item, str) and item.strip() for item in self.supporting_evaluation_ids):
            raise ValueError("supporting evaluation ids must contain non-empty strings")
        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
                raise TypeError("confidence must be a number or None")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.reversible, bool):
            raise TypeError("reversible must be a bool")
        if not self.reversible:
            raise ValueError("adaptation proposals must remain reversible")
        if not isinstance(self.explicit_user_preference, bool):
            raise TypeError("explicit_user_preference must be a bool")

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "kind": self.kind.value,
            "target": self.target,
            "current_value": self.current_value,
            "proposed_value": self.proposed_value,
            "supporting_evaluation_ids": self.supporting_evaluation_ids,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "reversible": True,
            "explicit_user_preference": self.explicit_user_preference,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }


@dataclass(frozen=True)
class AdaptationRecord:
    """Immutable accepted/rejected/reversed adaptation state."""

    record_id: str
    proposal: AdaptationProposal
    state: AdaptationState
    acceptance_reference: str | None = None
    reversal_reference: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.record_id, str) or not self.record_id.strip():
            raise ValueError("record_id must be a non-empty string")
        if not isinstance(self.proposal, AdaptationProposal):
            raise TypeError("proposal must be an AdaptationProposal")
        if not isinstance(self.state, AdaptationState):
            try:
                object.__setattr__(self, "state", AdaptationState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be an AdaptationState") from exc
        if self.state == AdaptationState.ACCEPTED:
            if not isinstance(self.acceptance_reference, str) or not self.acceptance_reference.strip():
                raise ValueError("accepted adaptations require an acceptance reference")
        if self.state == AdaptationState.REVERSED:
            if not isinstance(self.reversal_reference, str) or not self.reversal_reference.strip():
                raise ValueError("reversed adaptations require a reversal reference")

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "proposal": self.proposal.to_dict(),
            "state": self.state.value,
            "acceptance_reference": self.acceptance_reference,
            "reversal_reference": self.reversal_reference,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }


class AdaptationController:
    """Create and explicitly accept/reverse bounded adaptations."""

    def propose(
        self,
        *,
        proposal_id: str,
        kind: AdaptationKind,
        target: str,
        current_value: Any,
        proposed_value: Any,
        evaluations: tuple[Evaluation, ...],
        rationale: str,
        confidence: float | None = None,
        explicit_user_preference: bool = False,
    ) -> AdaptationProposal:
        if not isinstance(evaluations, tuple):
            raise TypeError("evaluations must be a tuple")
        if not all(isinstance(item, Evaluation) for item in evaluations):
            raise TypeError("evaluations must contain Evaluation values")
        if not evaluations:
            raise ValueError("adaptation proposals require supporting evaluations")
        return AdaptationProposal(
            proposal_id=proposal_id,
            kind=kind,
            target=target,
            current_value=current_value,
            proposed_value=proposed_value,
            supporting_evaluation_ids=tuple(item.evaluation_id for item in evaluations),
            rationale=rationale,
            confidence=confidence,
            explicit_user_preference=explicit_user_preference,
        )

    def accept(self, proposal: AdaptationProposal, acceptance_reference: str) -> AdaptationRecord:
        if not isinstance(proposal, AdaptationProposal):
            raise TypeError("proposal must be an AdaptationProposal")
        if not isinstance(acceptance_reference, str) or not acceptance_reference.strip():
            raise ValueError("acceptance_reference must be a non-empty string")
        return AdaptationRecord(
            record_id=f"{proposal.proposal_id}:record",
            proposal=proposal,
            state=AdaptationState.ACCEPTED,
            acceptance_reference=acceptance_reference.strip(),
        )

    def reject(self, proposal: AdaptationProposal, rejection_reference: str) -> AdaptationRecord:
        if not isinstance(proposal, AdaptationProposal):
            raise TypeError("proposal must be an AdaptationProposal")
        if not isinstance(rejection_reference, str) or not rejection_reference.strip():
            raise ValueError("rejection_reference must be a non-empty string")
        return AdaptationRecord(
            record_id=f"{proposal.proposal_id}:record",
            proposal=proposal,
            state=AdaptationState.REJECTED,
            acceptance_reference=rejection_reference.strip(),
        )

    def reverse(self, record: AdaptationRecord, reversal_reference: str) -> AdaptationRecord:
        if not isinstance(record, AdaptationRecord):
            raise TypeError("record must be an AdaptationRecord")
        if record.state != AdaptationState.ACCEPTED:
            raise ValueError("only accepted adaptations can be reversed")
        if not isinstance(reversal_reference, str) or not reversal_reference.strip():
            raise ValueError("reversal_reference must be a non-empty string")
        return AdaptationRecord(
            record_id=f"{record.record_id}:reversed",
            proposal=record.proposal,
            state=AdaptationState.REVERSED,
            acceptance_reference=record.acceptance_reference,
            reversal_reference=reversal_reference.strip(),
        )


@dataclass(frozen=True)
class AdaptationStore:
    records: tuple[AdaptationRecord, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple")
        seen: set[str] = set()
        for record in self.records:
            if not isinstance(record, AdaptationRecord):
                raise TypeError("records must contain AdaptationRecord values")
            if record.record_id in seen:
                raise AdaptationConflictError(f"adaptation record '{record.record_id}' is already stored")
            seen.add(record.record_id)

    def append(self, record: AdaptationRecord) -> "AdaptationStore":
        if not isinstance(record, AdaptationRecord):
            raise TypeError("record must be an AdaptationRecord")
        if any(item.record_id == record.record_id for item in self.records):
            raise AdaptationConflictError(f"adaptation record '{record.record_id}' is already stored")
        return AdaptationStore(self.records + (record,))

    def get(self, record_id: str) -> AdaptationRecord | None:
        return next((item for item in self.records if item.record_id == record_id), None)

    def list(self) -> tuple[AdaptationRecord, ...]:
        return self.records

    def to_json(self) -> str:
        return json.dumps(
            {"records": [record.to_dict() for record in self.records]},
            sort_keys=True,
            default=str,
        )
