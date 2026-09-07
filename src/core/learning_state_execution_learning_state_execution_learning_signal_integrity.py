"""M23.158: verify integrity of one recorded learning-signal artifact without granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignal,
    LearningStateExecutionLearningSignalKind,
    LearningStateExecutionLearningSignalStatus,
)


class LearningStateExecutionLearningSignalIntegrityError(RuntimeError):
    """Raised when bounded learning-signal integrity evidence cannot be formed safely."""


class LearningStateExecutionLearningSignalIntegrityStatus(str, Enum):
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
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    return value


def _signal_fingerprint(signal: LearningStateExecutionLearningSignal) -> str:
    payload = {
        key: _canonical(value)
        for key, value in signal.__dict__.items()
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningSignalIntegrity:
    """Immutable integrity evidence for one learning-signal artifact."""

    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    attempt_id: str
    admission_id: str
    eligibility_id: str
    handling_id: str
    consumption_id: str
    receipt_id: str
    handoff_id: str
    inherited_integrity_id: str
    validation_id: str
    semantic_use_id: str
    source_request_id: str
    source_request_lineage_id: str
    source_validation_id: str
    source_validation_lineage_id: str
    interpretation_id: str
    read_id: str
    consumption_request_id: str
    requester_id: str
    consumer_id: str
    handoff_target_id: str
    recipient_id: str
    handling_target_id: str
    execution_target_id: str
    signal_kind: LearningStateExecutionLearningSignalKind
    signal_purpose: str
    signal_context: Any
    signal_status: LearningStateExecutionLearningSignalStatus
    source_signal_fingerprint: str
    computed_signal_fingerprint: str
    status: LearningStateExecutionLearningSignalIntegrityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id",
            "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id", "inherited_integrity_id",
            "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id", "source_validation_id",
            "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id", "requester_id",
            "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id",
            "signal_purpose", "source_signal_fingerprint", "computed_signal_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if len(self.source_signal_fingerprint) != 64 or len(self.computed_signal_fingerprint) != 64:
            raise ValueError("learning-signal integrity requires SHA-256 fingerprints")
        if not isinstance(self.signal_kind, LearningStateExecutionLearningSignalKind):
            raise TypeError("signal_kind must be a learning-signal kind")
        if not isinstance(self.signal_status, LearningStateExecutionLearningSignalStatus):
            raise TypeError("signal_status must be a learning-signal status")
        if not isinstance(self.status, LearningStateExecutionLearningSignalIntegrityStatus):
            raise TypeError("status must be a learning-signal integrity status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "signal_context", _freeze(self.signal_context))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_valid(self) -> bool:
        return self.status is LearningStateExecutionLearningSignalIntegrityStatus.VALID

    @property
    def is_invalid(self) -> bool:
        return self.status is LearningStateExecutionLearningSignalIntegrityStatus.INVALID

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def reads_durable_state(self) -> bool:
        return False

    @property
    def rereads_durable_state(self) -> bool:
        return False

    @property
    def interprets_state(self) -> bool:
        return False

    @property
    def is_learning(self) -> bool:
        return False

    @property
    def applies_learning(self) -> bool:
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
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_correctness(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False

    @property
    def establishes_usefulness(self) -> bool:
        return False


class LearningStateExecutionLearningSignalIntegrityService:
    """Verify exactly one recorded learning-signal artifact and emit inert integrity evidence."""

    def verify(
        self,
        signal: LearningStateExecutionLearningSignal,
        *,
        integrity_id: str,
        signal_fingerprint: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningSignalIntegrity:
        if type(signal) is not LearningStateExecutionLearningSignal:
            raise TypeError("signal must be a learning-signal artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        if not isinstance(signal_fingerprint, str) or len(signal_fingerprint) != 64:
            raise ValueError("signal_fingerprint must be a SHA-256 fingerprint")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if signal.status is not LearningStateExecutionLearningSignalStatus.RECORDED:
            checks.append("learning signal status must be RECORDED")
        if integrity_id == signal.signal_id:
            checks.append("integrity identity must be distinct")

        anchored = (
            ("signal_id", signal.signal_id, "signal lineage mismatch"),
            ("evaluation_id", signal.evaluation_id, "evaluation lineage mismatch"),
            ("feedback_id", signal.feedback_id, "feedback lineage mismatch"),
            ("outcome_id", signal.outcome_id, "outcome lineage mismatch"),
            ("attempt_id", signal.attempt_id, "attempt lineage mismatch"),
            ("admission_id", signal.admission_id, "admission lineage mismatch"),
            ("eligibility_id", signal.eligibility_id, "eligibility lineage mismatch"),
            ("handling_id", signal.handling_id, "handling lineage mismatch"),
            ("consumption_id", signal.consumption_id, "consumption lineage mismatch"),
            ("receipt_id", signal.receipt_id, "receipt lineage mismatch"),
            ("handoff_id", signal.handoff_id, "handoff lineage mismatch"),
            ("integrity_id", signal.integrity_id, "inherited integrity lineage mismatch"),
            ("validation_id", signal.validation_id, "validation lineage mismatch"),
            ("semantic_use_id", signal.semantic_use_id, "semantic-use lineage mismatch"),
            ("request_id", signal.source_request_lineage_id, "source request lineage mismatch"),
            ("source_validation_id", signal.source_validation_lineage_id, "source validation lineage mismatch"),
            ("interpretation_id", signal.interpretation_id, "interpretation lineage mismatch"),
            ("source_request_provenance_id", signal.source_request_id, "source request provenance mismatch"),
            ("source_validation_provenance_id", signal.source_validation_id, "source validation provenance mismatch"),
            ("read_id", signal.read_id, "read lineage mismatch"),
            ("consumption_request_id", signal.consumption_request_id, "consumption request lineage mismatch"),
        )
        checks.extend(message for key, expected, message in anchored if signal.lineage.get(key, expected) != expected)

        computed = _signal_fingerprint(signal)
        if signal_fingerprint != computed:
            checks.append("learning signal fingerprint mismatch")

        valid = not checks
        status = LearningStateExecutionLearningSignalIntegrityStatus.VALID if valid else LearningStateExecutionLearningSignalIntegrityStatus.INVALID
        final_reasons = reasons if reasons is not None else (("learning signal integrity verified",) if valid else tuple(checks))
        return LearningStateExecutionLearningSignalIntegrity(
            integrity_id=integrity_id,
            signal_id=signal.signal_id,
            evaluation_id=signal.evaluation_id,
            feedback_id=signal.feedback_id,
            outcome_id=signal.outcome_id,
            attempt_id=signal.attempt_id,
            admission_id=signal.admission_id,
            eligibility_id=signal.eligibility_id,
            handling_id=signal.handling_id,
            consumption_id=signal.consumption_id,
            receipt_id=signal.receipt_id,
            handoff_id=signal.handoff_id,
            inherited_integrity_id=signal.integrity_id,
            validation_id=signal.validation_id,
            semantic_use_id=signal.semantic_use_id,
            source_request_id=signal.source_request_id,
            source_request_lineage_id=signal.source_request_lineage_id,
            source_validation_id=signal.source_validation_id,
            source_validation_lineage_id=signal.source_validation_lineage_id,
            interpretation_id=signal.interpretation_id,
            read_id=signal.read_id,
            consumption_request_id=signal.consumption_request_id,
            requester_id=signal.requester_id,
            consumer_id=signal.consumer_id,
            handoff_target_id=signal.handoff_target_id,
            recipient_id=signal.recipient_id,
            handling_target_id=signal.handling_target_id,
            execution_target_id=signal.execution_target_id,
            signal_kind=signal.signal_kind,
            signal_purpose=signal.signal_purpose,
            signal_context=signal.signal_context,
            signal_status=signal.status,
            source_signal_fingerprint=signal_fingerprint,
            computed_signal_fingerprint=computed,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "integrity_id": integrity_id,
                "signal_id": signal.signal_id,
                "evaluation_id": signal.evaluation_id,
                "feedback_id": signal.feedback_id,
                "outcome_id": signal.outcome_id,
                "attempt_id": signal.attempt_id,
                "admission_id": signal.admission_id,
                "eligibility_id": signal.eligibility_id,
                "handling_id": signal.handling_id,
                "consumption_id": signal.consumption_id,
                "receipt_id": signal.receipt_id,
                "handoff_id": signal.handoff_id,
                "integrity_source_id": signal.integrity_id,
                "validation_id": signal.validation_id,
                "semantic_use_id": signal.semantic_use_id,
                "request_id": signal.source_request_lineage_id,
                "source_validation_id": signal.source_validation_lineage_id,
                "interpretation_id": signal.interpretation_id,
                "source_request_provenance_id": signal.source_request_id,
                "source_validation_provenance_id": signal.source_validation_id,
                "read_id": signal.read_id,
                "consumption_request_id": signal.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningSignalIntegrityError",
    "LearningStateExecutionLearningSignalIntegrityStatus",
    "LearningStateExecutionLearningSignalIntegrity",
    "LearningStateExecutionLearningSignalIntegrityService",
    "_signal_fingerprint",
]
