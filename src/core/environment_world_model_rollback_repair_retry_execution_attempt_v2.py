"""M23.53: explicit execution-attempt boundary for rollback-repair retry v2."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from src.core.environment_world_model_rollback_repair_retry_execution_preparation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2,
)


class EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Error(RuntimeError):
    """Raised when v2 retry execution-attempt evidence is structurally invalid."""


class EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


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


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result:
    """Immutable observation of one v2 retry execution attempt."""

    execution_id: str
    preparation_id: str
    environment_id: str
    authorization_decision_id: str
    authorization_integrity_id: str
    proposal_id: str
    assessment_id: str | None
    evaluation_id: str | None
    feedback_id: str | None
    outcome_id: str | None
    expected_model_id: str
    observed_model_id: str
    requested_action: str
    decision: str
    eligible: bool
    status: EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status
    observed_result: Any = None
    worker_id: str | None = None
    failure_reason: str | None = None
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "execution_id", "preparation_id", "environment_id",
            "authorization_decision_id", "authorization_integrity_id", "proposal_id",
            "expected_model_id", "observed_model_id", "requested_action", "decision",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "evaluation_id", "feedback_id", "outcome_id", "worker_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if self.requested_action != "RETRY_REPAIR":
            raise ValueError("requested_action must be RETRY_REPAIR")
        if self.decision != "ACCEPT":
            raise ValueError("decision must be ACCEPT")
        if self.eligible is not True:
            raise ValueError("eligible must be True")
        if not isinstance(self.status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status):
            raise TypeError("status must be an execution-attempt v2 status")
        if self.status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED:
            if self.failure_reason is not None:
                raise ValueError("completed attempt cannot contain failure_reason")
        else:
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("failed attempt requires failure_reason")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "observed_result", _freeze(self.observed_result))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def execution_attempted(self) -> bool:
        return True

    @property
    def completed(self) -> bool:
        return self.status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED

    @property
    def grants_execution_authority(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def schedules_retry(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryExecutorV2(Protocol):
    def execute(self, preparation: EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2) -> Any:
        """Execute the exact prepared retry and return observed provider result."""


class EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Service:
    """Execute one exact M23.52 preparation through a replaceable executor."""

    def __init__(self, executor: EnvironmentWorldModelRollbackRepairRetryExecutorV2) -> None:
        if not callable(getattr(executor, "execute", None)):
            raise TypeError("executor must provide an execute(preparation) method")
        self._executor = executor

    def attempt(
        self,
        preparation: EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2,
        *,
        worker_id: str | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result:
        if type(preparation) is not EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2:
            raise TypeError(
                "preparation must be EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2"
            )
        if worker_id is not None and (not isinstance(worker_id, str) or not worker_id.strip()):
            raise ValueError("worker_id must be a non-empty string or None")

        execution_id = self._execution_id(preparation)
        try:
            observed = self._executor.execute(preparation)
        except Exception as exc:  # noqa: BLE001 - executor failures become explicit observation evidence
            return self._failed(preparation, execution_id, str(exc) or exc.__class__.__name__, worker_id, lineage)

        return EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result(
            execution_id=execution_id,
            preparation_id=preparation.preparation_id,
            environment_id=preparation.environment_id,
            authorization_decision_id=preparation.decision_id,
            authorization_integrity_id=preparation.integrity_id,
            proposal_id=preparation.proposal_id,
            assessment_id=preparation.assessment_id,
            evaluation_id=preparation.evaluation_id,
            feedback_id=preparation.feedback_id,
            outcome_id=preparation.outcome_id,
            expected_model_id=preparation.expected_model_id,
            observed_model_id=preparation.observed_model_id,
            requested_action=preparation.requested_action,
            decision=preparation.decision,
            eligible=preparation.eligible,
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED,
            observed_result=observed,
            worker_id=worker_id,
            lineage=lineage or {
                "preparation_id": preparation.preparation_id,
                "authorization_decision_id": preparation.decision_id,
                "authorization_integrity_id": preparation.integrity_id,
                "proposal_id": preparation.proposal_id,
                "assessment_id": preparation.assessment_id,
                "evaluation_id": preparation.evaluation_id,
                "feedback_id": preparation.feedback_id,
                "outcome_id": preparation.outcome_id,
            },
        )

    @staticmethod
    def _failed(preparation, execution_id, reason, worker_id, lineage):
        return EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result(
            execution_id=execution_id,
            preparation_id=preparation.preparation_id,
            environment_id=preparation.environment_id,
            authorization_decision_id=preparation.decision_id,
            authorization_integrity_id=preparation.integrity_id,
            proposal_id=preparation.proposal_id,
            assessment_id=preparation.assessment_id,
            evaluation_id=preparation.evaluation_id,
            feedback_id=preparation.feedback_id,
            outcome_id=preparation.outcome_id,
            expected_model_id=preparation.expected_model_id,
            observed_model_id=preparation.observed_model_id,
            requested_action=preparation.requested_action,
            decision=preparation.decision,
            eligible=preparation.eligible,
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.FAILED,
            worker_id=worker_id,
            failure_reason=reason,
            lineage=lineage or {"preparation_id": preparation.preparation_id},
        )

    @staticmethod
    def _execution_id(preparation) -> str:
        payload = json.dumps(
            {
                "preparation_id": preparation.preparation_id,
                "environment_id": preparation.environment_id,
                "decision_id": preparation.decision_id,
                "integrity_id": preparation.integrity_id,
                "proposal_id": preparation.proposal_id,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"retry-exec-v2-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Error",
    "EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status",
    "EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result",
    "EnvironmentWorldModelRollbackRepairRetryExecutorV2",
    "EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Service",
]
