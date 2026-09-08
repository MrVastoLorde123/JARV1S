"""M23.137: perform a bounded durable-state read from an explicit consumption request."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_consumption_request import (
    LearningStateExecutionLearningStateConsumptionRequest,
    LearningStateExecutionLearningStateConsumptionRequestStatus,
)


class LearningStateExecutionLearningStateDurableReadConsumptionError(RuntimeError):
    """Raised when a durable-state read cannot be formed safely."""


class LearningStateExecutionLearningStateDurableReadConsumptionStatus(str, Enum):
    READ = "READ"
    REJECTED = "REJECTED"


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
        return sorted((_canonical(item) for item in value), key=repr)
    return value


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), default=repr).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningStateDurableReadConsumption:
    """Immutable evidence that a bounded durable-state payload was actually read."""

    read_id: str
    consumption_request_id: str
    validation_id: str
    integrity_id: str
    transition_id: str
    evidence_id: str
    source_validation_id: str
    state_key: str
    requested_scope: Any
    read_payload: Any
    read_fingerprint: str
    computed_read_fingerprint: str
    reader_id: str
    read_purpose: str
    request_rationale: Any
    confidence: float
    status: LearningStateExecutionLearningStateDurableReadConsumptionStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "read_id", "consumption_request_id", "validation_id", "integrity_id", "transition_id", "evidence_id",
            "state_key", "reader_id", "read_purpose", "read_fingerprint", "computed_read_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus):
            raise TypeError("status must be a durable-read consumption status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "requested_scope", _freeze(self.requested_scope))
        object.__setattr__(self, "read_payload", _freeze(self.read_payload))
        object.__setattr__(self, "request_rationale", _freeze(self.request_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_read(self) -> bool:
        return self.status is LearningStateExecutionLearningStateDurableReadConsumptionStatus.READ

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED

    @property
    def reads_state(self) -> bool:
        return self.is_read

    @property
    def consumes_state(self) -> bool:
        return self.is_read

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
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
    def interprets_state(self) -> bool:
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


class LearningStateExecutionLearningStateDurableReadConsumptionService:
    """Perform only the bounded read explicitly described by a REQUESTED consumption request."""

    def read(
        self,
        request: LearningStateExecutionLearningStateConsumptionRequest,
        durable_state: Mapping[str, Any],
        *,
        read_id: str,
        reader_id: str,
        read_purpose: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateDurableReadConsumption:
        if type(request) is not LearningStateExecutionLearningStateConsumptionRequest:
            raise TypeError("request must be a learning-state consumption request artifact")
        for name, value in (("read_id", read_id), ("reader_id", reader_id), ("read_purpose", read_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if request.request_purpose is None or request.request_rationale is None:
            raise ValueError("request metadata must be present")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(durable_state, Mapping):
            raise TypeError("durable_state must be a mapping")

        checks: list[str] = []
        if request.status is not LearningStateExecutionLearningStateConsumptionRequestStatus.REQUESTED:
            checks.append("consumption request is not REQUESTED")
        lineage_request_id = request.lineage.get("consumption_request_id", request.consumption_request_id)
        lineage_validation_id = request.lineage.get("validation_id", request.validation_id)
        if lineage_request_id != request.consumption_request_id:
            checks.append("consumption request lineage mismatch")
        if lineage_validation_id != request.validation_id:
            checks.append("validation lineage mismatch")
        if read_id == request.consumption_request_id:
            checks.append("read identity must be distinct from consumption request identity")
        if not isinstance(request.requested_scope, Mapping):
            checks.append("requested scope must be a mapping")
        else:
            scope_state_key = request.requested_scope.get("state_key", request.state_key)
            if scope_state_key != request.state_key:
                checks.append("requested scope state key mismatch")
            if "fields" in request.requested_scope:
                fields = request.requested_scope["fields"]
                if not isinstance(fields, (list, tuple)) or not fields or not all(isinstance(field, str) and field.strip() for field in fields):
                    checks.append("requested scope fields must be a non-empty sequence of names")
                elif len(set(fields)) != len(fields):
                    checks.append("requested scope fields must be distinct")

        payload: Any = None
        if not checks:
            state_key_present = request.state_key in durable_state
            if not state_key_present:
                checks.append("requested state key is absent from durable state")
            else:
                source = durable_state[request.state_key]
                if "fields" in request.requested_scope:
                    fields = request.requested_scope["fields"]
                    if not isinstance(source, Mapping):
                        checks.append("field-bounded read requires mapped state at requested state key")
                    else:
                        missing = [field for field in fields if field not in source]
                        if missing:
                            checks.append("requested scope field is absent from durable state")
                        else:
                            payload = {field: source[field] for field in fields}
                else:
                    payload = source

        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("bounded durable-state read completed",)
        else:
            final_reasons = tuple(checks)
        status = (
            LearningStateExecutionLearningStateDurableReadConsumptionStatus.READ
            if valid
            else LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED
        )
        computed = _fingerprint(payload) if valid else _fingerprint(None)
        return LearningStateExecutionLearningStateDurableReadConsumption(
            read_id=read_id,
            consumption_request_id=request.consumption_request_id,
            validation_id=request.validation_id,
            integrity_id=request.integrity_id,
            transition_id=request.transition_id,
            evidence_id=request.evidence_id,
            source_validation_id=request.source_validation_id,
            state_key=request.state_key,
            requested_scope=request.requested_scope,
            read_payload=payload,
            read_fingerprint=computed,
            computed_read_fingerprint=computed,
            reader_id=reader_id,
            read_purpose=read_purpose,
            request_rationale=request.request_rationale,
            confidence=request.confidence,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"read_id": read_id, "consumption_request_id": request.consumption_request_id, "validation_id": request.validation_id},
        )


__all__ = [
    "LearningStateExecutionLearningStateDurableReadConsumptionError",
    "LearningStateExecutionLearningStateDurableReadConsumptionStatus",
    "LearningStateExecutionLearningStateDurableReadConsumption",
    "LearningStateExecutionLearningStateDurableReadConsumptionService",
]
