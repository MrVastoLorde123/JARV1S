"""M23.43: explicit execution-attempt boundary for rollback-repair retry."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from src.core.environment_world_model_rollback_repair_retry_execution_preparation import (
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparation,
)


class EnvironmentWorldModelRollbackRepairRetryExecutionAttemptError(RuntimeError):
    """Raised when retry execution-attempt evidence is structurally invalid."""


class EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


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
class EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult:
    """Immutable observation of one retry execution attempt."""

    execution_id: str
    preparation_id: str
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    status: EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus
    observed_result: Any = None
    worker_id: str | None = None
    reason: str | None = None
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "execution_id",
            "preparation_id",
            "environment_id",
            "expected_model_id",
            "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus):
            raise TypeError("status must be an execution-attempt status")
        if self.worker_id is not None and (not isinstance(self.worker_id, str) or not self.worker_id.strip()):
            raise ValueError("worker_id must be a non-empty string or None")
        if self.status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED:
            if self.reason is not None:
                raise ValueError("completed attempt cannot contain a failure reason")
        else:
            if self.reason is None or not self.reason.strip():
                raise ValueError("failed attempt requires a reason")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "observed_result", _freeze(self.observed_result))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def completed(self) -> bool:
        return self.status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED

    @property
    def execution_attempted(self) -> bool:
        return True

    @property
    def grants_execution_authority(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryExecutor(Protocol):
    def execute(self, preparation: EnvironmentWorldModelRollbackRepairRetryExecutionPreparation) -> Any:
        """Execute the exact prepared retry and return its observed result."""


class EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService:
    """Execute one prepared retry through a replaceable executor and record the attempt."""

    def __init__(self, executor: EnvironmentWorldModelRollbackRepairRetryExecutor) -> None:
        if not callable(getattr(executor, "execute", None)):
            raise TypeError("executor must provide an execute(preparation) method")
        self._executor = executor

    def attempt(
        self,
        preparation: EnvironmentWorldModelRollbackRepairRetryExecutionPreparation,
        *,
        worker_id: str | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult:
        if type(preparation) is not EnvironmentWorldModelRollbackRepairRetryExecutionPreparation:
            raise TypeError(
                "preparation must be EnvironmentWorldModelRollbackRepairRetryExecutionPreparation"
            )
        if worker_id is not None and (not isinstance(worker_id, str) or not worker_id.strip()):
            raise ValueError("worker_id must be a non-empty string or None")

        execution_id = self._execution_id(preparation)
        try:
            observed = self._executor.execute(preparation)
        except Exception as exc:  # noqa: BLE001 - execution failures become explicit observation data
            return self._failed(preparation, execution_id, str(exc) or exc.__class__.__name__, worker_id, lineage)

        return EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id=execution_id,
            preparation_id=preparation.preparation_id,
            environment_id=preparation.environment_id,
            expected_model_id=preparation.expected_model_id,
            observed_model_id=preparation.observed_model_id,
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
            observed_result=observed,
            worker_id=worker_id,
            lineage=lineage or {
                "preparation_id": preparation.preparation_id,
                "authorization_decision_id": preparation.authorization_decision_id,
                "authorization_integrity_id": preparation.authorization_integrity_id,
            },
        )

    @staticmethod
    def _failed(preparation, execution_id, reason, worker_id, lineage):
        return EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id=execution_id,
            preparation_id=preparation.preparation_id,
            environment_id=preparation.environment_id,
            expected_model_id=preparation.expected_model_id,
            observed_model_id=preparation.observed_model_id,
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED,
            worker_id=worker_id,
            reason=reason,
            lineage=lineage or {"preparation_id": preparation.preparation_id},
        )

    @staticmethod
    def _execution_id(preparation) -> str:
        payload = json.dumps(
            {
                "preparation_id": preparation.preparation_id,
                "environment_id": preparation.environment_id,
                "expected_model_id": preparation.expected_model_id,
                "observed_model_id": preparation.observed_model_id,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"retry-exec-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryExecutionAttemptError",
    "EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus",
    "EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult",
    "EnvironmentWorldModelRollbackRepairRetryExecutor",
    "EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService",
]
