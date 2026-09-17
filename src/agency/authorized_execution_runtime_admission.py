"""M55: bind authorized admission to the existing M36 execution result.

This module records end-to-end continuity from M52 authorization through M53
identity bridging and M54 execution admission into the existing M36 controlled
execution result. It does not execute work, create authorization, or select
providers/tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .authorized_execution_admission import AuthorizedExecutionAdmission
from .execution_bridge import AgencyExecutionBridgeResult


@dataclass(frozen=True)
class AuthorizedExecutionRuntimeAdmission:
    """Immutable runtime result bound to one admitted authorized path."""

    admission: AuthorizedExecutionAdmission
    execution_result: AgencyExecutionBridgeResult
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.admission, AuthorizedExecutionAdmission):
            raise TypeError("admission must be an AuthorizedExecutionAdmission")
        if not isinstance(self.execution_result, AgencyExecutionBridgeResult):
            raise TypeError("execution_result must be an AgencyExecutionBridgeResult")
        if self.execution_result.handoff != self.admission.execution_handoff:
            raise ValueError("execution result handoff must exactly match the admitted execution handoff")
        if self.execution_result.execution_id != self.admission.execution_id:
            raise ValueError("execution result identity must match the admitted execution identity")
        if self.execution_result.handoff.preparation != self.admission.execution_handoff.preparation:
            raise ValueError("execution result preparation must match the admitted preparation")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.admission.execution_id

    @property
    def authorization_id(self) -> str:
        return self.admission.authorization_id

    @property
    def succeeded(self) -> bool:
        return self.execution_result.succeeded

    @property
    def steps_executed(self) -> int:
        return self.execution_result.steps_executed

    def to_context(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "confirmation_id": self.admission.authorization_execution_bridge.authorization.confirmation_id,
            "execution_id": self.execution_id,
            "succeeded": self.succeeded,
            "steps_executed": self.steps_executed,
            "admission": self.admission.to_context(),
            "execution_result": self.execution_result.to_context(),
            "metadata": dict(self.metadata),
            "authorization_created": False,
            "execution_requested": False,
            "execution_performed": True,
        }


def create_authorized_execution_runtime_admission(
    admission: AuthorizedExecutionAdmission,
    execution_result: AgencyExecutionBridgeResult,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> AuthorizedExecutionRuntimeAdmission:
    """Bind an existing M36 execution result to one exact M54 admission."""
    return AuthorizedExecutionRuntimeAdmission(
        admission=admission,
        execution_result=execution_result,
        metadata=metadata or {},
    )


__all__ = ["AuthorizedExecutionRuntimeAdmission", "create_authorized_execution_runtime_admission"]
