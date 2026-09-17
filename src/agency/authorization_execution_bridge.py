"""M53: bounded bridge from agency authorization to an existing execution preparation.

This module proves that a granted M52 authorization is bound to an already-READY
M7.10 execution preparation. It does not create authorization, prepare execution,
select providers/tools, invoke anything, or perform side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.context.execution_semantics import ExecutionPreparation, ExecutionPreparationStatus

from .authorization_decision import AuthorizationDecision, AuthorizationDisposition


@dataclass(frozen=True)
class AuthorizationExecutionBridge:
    """Immutable identity bridge between M52 authorization and M7.10 preparation."""

    authorization: AuthorizationDecision
    preparation: ExecutionPreparation
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.authorization, AuthorizationDecision):
            raise TypeError("authorization must be an AuthorizationDecision")
        if not isinstance(self.preparation, ExecutionPreparation):
            raise TypeError("preparation must be an ExecutionPreparation")
        if self.authorization.disposition is not AuthorizationDisposition.GRANTED:
            raise ValueError("authorization-execution bridge requires GRANTED authorization")
        if self.preparation.status is not ExecutionPreparationStatus.READY:
            raise ValueError("authorization-execution bridge requires READY execution preparation")
        request = self.preparation.execution_request
        if request is None:
            raise ValueError("READY execution preparation must contain an execution request")
        if request.authorization_id != self.authorization.authorization_id:
            raise ValueError("execution preparation authorization identity must match the granted authorization")
        if request.confirmation_id != self.authorization.confirmation_id:
            raise ValueError("execution preparation confirmation identity must match the authorization")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.preparation.execution_id

    @property
    def authorization_id(self) -> str:
        return self.authorization.authorization_id

    def to_context(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "confirmation_id": self.authorization.confirmation_id,
            "execution_id": self.execution_id,
            "authorization": self.authorization.to_context(),
            "preparation": self.preparation.to_context(),
            "metadata": dict(self.metadata),
            "authorization_created": False,
            "execution_prepared": False,
            "execution_requested": False,
            "execution_performed": False,
        }


def create_authorization_execution_bridge(
    authorization: AuthorizationDecision,
    preparation: ExecutionPreparation,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> AuthorizationExecutionBridge:
    """Bind a granted M52 authorization to an existing READY M7.10 preparation."""
    return AuthorizationExecutionBridge(
        authorization=authorization,
        preparation=preparation,
        metadata=metadata or {},
    )


__all__ = ["AuthorizationExecutionBridge", "create_authorization_execution_bridge"]
