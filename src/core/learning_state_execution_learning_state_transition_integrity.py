"""M23.166: validate learning-state transition integrity without mutating or applying it."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.learning_state_execution_learning_state_transition import LearningStateExecutionLearningStateTransition


class LearningStateExecutionLearningStateTransitionIntegrityError(RuntimeError):
    """Raised when learning-state transition integrity evidence cannot be formed safely."""


class LearningStateExecutionLearningStateTransitionIntegrityStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical(item) for item in value), key=lambda item: repr(item))
    if isinstance(value, Enum):
        return value.value
    return value


def _transition_integrity_fingerprint(transition: "LearningStateExecutionLearningStateTransition") -> str:
    payload = {
        "transition_id": transition.transition_id,
        "evidence_id": transition.evidence_id,
        "integrity_id": transition.integrity_id,
        "application_id": transition.application_id,
        "decision_id": transition.decision_id,
        "proposal_id": transition.proposal_id,
        "eligibility_id": transition.eligibility_id,
        "source_integrity_id": transition.source_integrity_id,
        "state_key": transition.state_key,
        "state_before": _canonical(transition.state_before),
        "state_after": _canonical(transition.state_after),
        "proposed_change": _canonical(transition.proposed_change),
        "transition_fingerprint": transition.transition_fingerprint,
        "status": _canonical(transition.status),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningStateTransitionIntegrity:
    """Immutable evidence that one learning-state transition artifact is structurally intact."""

    integrity_id: str
    transition_id: str
    evidence_id: str
    source_integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    eligibility_id: str
    transition_fingerprint: str
    computed_transition_fingerprint: str
    transition_status: Any
    state_key: str
    state_before: Any
    state_after: Any
    proposed_change: Any
    transition_actor_id: str
    transition_purpose: str
    transition_rationale: Any
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]
    status: LearningStateExecutionLearningStateTransitionIntegrityStatus

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "transition_id", "evidence_id", "source_integrity_id", "application_id", "decision_id",
            "proposal_id", "eligibility_id", "transition_fingerprint", "computed_transition_fingerprint", "state_key",
            "transition_actor_id", "transition_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if len(self.transition_fingerprint) != 64 or len(self.computed_transition_fingerprint) != 64:
            raise ValueError("learning-state transition integrity requires SHA-256 fingerprints")
        if not isinstance(self.status, LearningStateExecutionLearningStateTransitionIntegrityStatus):
            raise TypeError("status must be a learning-state transition integrity status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "state_before", _freeze(self.state_before))
        object.__setattr__(self, "state_after", _freeze(self.state_after))
        object.__setattr__(self, "proposed_change", _freeze(self.proposed_change))
        object.__setattr__(self, "transition_rationale", _freeze(self.transition_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_valid(self) -> bool:
        return self.status is LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID

    @property
    def validates_transition(self) -> bool:
        return self.is_valid

    @property
    def is_learning(self) -> bool:
        return False

    @property
    def authorizes_learning(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def invokes_learner(self) -> bool:
        return False

    @property
    def invokes_executor(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def plans_work(self) -> bool:
        return False

    @property
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def applies_learning(self) -> bool:
        return False

    @property
    def transitions_state(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def repairs_transition(self) -> bool:
        return False


class LearningStateExecutionLearningStateTransitionIntegrityService:
    """Verify one learning-state transition artifact without repairing or applying it."""

    def verify(
        self,
        transition: "LearningStateExecutionLearningStateTransition",
        *,
        integrity_id: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateTransitionIntegrity:
        from src.core.learning_state_execution_learning_state_transition import LearningStateExecutionLearningStateTransition

        if type(transition) is not LearningStateExecutionLearningStateTransition:
            raise TypeError("transition must be a learning-state transition artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        if integrity_id in (transition.integrity_id, transition.transition_id):
            raise ValueError("transition-integrity identity must be distinct")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        anchored_transition_id = transition.lineage.get("transition_id", transition.transition_id)
        anchored_evidence_id = transition.lineage.get("evidence_id", transition.evidence_id)
        anchored_integrity_id = transition.lineage.get("integrity_id", transition.integrity_id)
        anchored_application_id = transition.lineage.get("application_id", transition.application_id)
        anchored_source_integrity_id = transition.lineage.get("source_integrity_id", transition.source_integrity_id)
        lineage_consistent = (
            anchored_transition_id == transition.transition_id
            and anchored_evidence_id == transition.evidence_id
            and anchored_integrity_id == transition.integrity_id
            and anchored_application_id == transition.application_id
            and anchored_source_integrity_id == transition.source_integrity_id
        )
        computed = _transition_integrity_fingerprint(transition)
        fingerprint_valid = computed == transition.lineage.get("transition_integrity_fingerprint", computed)
        transition_fingerprint_valid = transition.transition_fingerprint == _recompute_transition_fingerprint(transition)
        valid = transition.status.value == "FORMULATED" and transition.represents_transition and lineage_consistent and fingerprint_valid and transition_fingerprint_valid
        if reasons is not None:
            final_reasons = reasons
        elif not lineage_consistent:
            final_reasons = ("learning-state transition lineage is not valid",)
        elif not transition_fingerprint_valid:
            final_reasons = ("learning-state transition fingerprint mismatch",)
        elif not fingerprint_valid:
            final_reasons = ("learning-state transition integrity fingerprint mismatch",)
        elif not (transition.status.value == "FORMULATED" and transition.represents_transition):
            final_reasons = ("learning-state transition is not formulated",)
        else:
            final_reasons = ("learning-state transition integrity is valid",)
        return LearningStateExecutionLearningStateTransitionIntegrity(
            integrity_id=integrity_id,
            transition_id=transition.transition_id,
            evidence_id=transition.evidence_id,
            source_integrity_id=transition.source_integrity_id,
            application_id=transition.application_id,
            decision_id=transition.decision_id,
            proposal_id=transition.proposal_id,
            eligibility_id=transition.eligibility_id,
            transition_fingerprint=transition.transition_fingerprint,
            computed_transition_fingerprint=_recompute_transition_fingerprint(transition),
            transition_status=transition.status,
            state_key=transition.state_key,
            state_before=transition.state_before,
            state_after=transition.state_after,
            proposed_change=transition.proposed_change,
            transition_actor_id=transition.transition_actor_id,
            transition_purpose=transition.transition_purpose,
            transition_rationale=transition.transition_rationale,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "integrity_id": integrity_id,
                "transition_id": transition.transition_id,
                "evidence_id": transition.evidence_id,
                "source_integrity_id": transition.source_integrity_id,
                "application_id": transition.application_id,
                "transition_integrity_fingerprint": computed,
            },
            status=LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID if valid else LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID,
        )


def _recompute_transition_fingerprint(transition: "LearningStateExecutionLearningStateTransition") -> str:
    from src.core.learning_state_execution_learning_state_transition import _transition_fingerprint
    return _transition_fingerprint(
        transition_id=transition.transition_id,
        state_key=transition.state_key,
        state_before=transition.state_before,
        state_after=transition.state_after,
        evidence_id=transition.evidence_id,
        integrity_id=transition.integrity_id,
        proposed_change=transition.proposed_change,
    )


__all__ = [
    "LearningStateExecutionLearningStateTransitionIntegrityError",
    "LearningStateExecutionLearningStateTransitionIntegrityStatus",
    "LearningStateExecutionLearningStateTransitionIntegrity",
    "LearningStateExecutionLearningStateTransitionIntegrityService",
    "_transition_integrity_fingerprint",
]
