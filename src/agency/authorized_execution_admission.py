"""M54: bounded admission from M52/M53 authority into existing execution handoff.

This module proves continuity between a granted M52 authorization, its M53
binding to READY M7.10 preparation, and the existing M35 ExecutionHandoff.
It does not create authorization, prepare execution, select providers/tools,
request execution, or perform execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .authorization_execution_bridge import AuthorizationExecutionBridge
from .execution_handoff import ExecutionHandoff


@dataclass(frozen=True)
class AuthorizedExecutionAdmission:
    """Immutable continuity record for an already-authorized execution path."""

    authorization_execution_bridge: AuthorizationExecutionBridge
    execution_handoff: ExecutionHandoff
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.authorization_execution_bridge, AuthorizationExecutionBridge):
            raise TypeError("authorization_execution_bridge must be an AuthorizationExecutionBridge")
        if not isinstance(self.execution_handoff, ExecutionHandoff):
            raise TypeError("execution_handoff must be an ExecutionHandoff")

        bridge_preparation = self.authorization_execution_bridge.preparation
        handoff_preparation = self.execution_handoff.preparation
        if handoff_preparation != bridge_preparation:
            raise ValueError("execution handoff preparation must exactly match the M53 authorization bridge preparation")
        if self.execution_handoff.execution_id != self.authorization_execution_bridge.execution_id:
            raise ValueError("execution handoff execution identity must match the M53 authorization bridge")
        if self.execution_handoff.execution_id != handoff_preparation.execution_id:
            raise ValueError("execution handoff execution identity must match its preparation")

        authorization = self.authorization_execution_bridge.authorization
        execution_request = handoff_preparation.execution_request
        if execution_request is None:
            raise ValueError("admitted execution handoff must contain a READY execution request")
        if execution_request.authorization_id != authorization.authorization_id:
            raise ValueError("execution request authorization identity must match granted authorization")
        if execution_request.confirmation_id != authorization.confirmation_id:
            raise ValueError("execution request confirmation identity must match authorization confirmation")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.authorization_execution_bridge.execution_id

    @property
    def authorization_id(self) -> str:
        return self.authorization_execution_bridge.authorization_id

    def to_context(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "confirmation_id": self.authorization_execution_bridge.authorization.confirmation_id,
            "execution_id": self.execution_id,
            "authorization_execution_bridge": self.authorization_execution_bridge.to_context(),
            "execution_handoff": self.execution_handoff.to_context(),
            "metadata": dict(self.metadata),
            "authorization_created": False,
            "execution_prepared": False,
            "execution_requested": False,
            "execution_performed": False,
        }


def create_authorized_execution_admission(
    authorization_execution_bridge: AuthorizationExecutionBridge,
    execution_handoff: ExecutionHandoff,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> AuthorizedExecutionAdmission:
    """Admit only an exact M53 bridge plus exact existing M35 execution handoff."""
    return AuthorizedExecutionAdmission(
        authorization_execution_bridge=authorization_execution_bridge,
        execution_handoff=execution_handoff,
        metadata=metadata or {},
    )


__all__ = ["AuthorizedExecutionAdmission", "create_authorized_execution_admission"]
