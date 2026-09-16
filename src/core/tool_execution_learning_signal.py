"""Convert execution-chain evidence into inert learning signals.

A learning signal is a bounded observation for downstream learning/adaptation
systems. It never authorizes, retries, executes, mutates policy, or claims that
the observed result is truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from src.core.tool_execution_chain import ToolExecutionChainTrace
from src.core.tool_execution_verification import ToolVerificationStatus


@dataclass(frozen=True)
class ToolExecutionLearningSignal:
    """Immutable, provider-neutral learning evidence for one execution chain."""

    signal_id: str
    invocation_id: str | None
    tool_name: str
    authorized: bool
    execution_succeeded: bool
    verification_status: ToolVerificationStatus
    verified: bool
    observation: Any
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in ("signal_id", "tool_name"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        for name in ("authorized", "execution_succeeded", "verified"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool")
        if not isinstance(self.verification_status, ToolVerificationStatus):
            raise TypeError("verification_status must be a ToolVerificationStatus")
        if self.verified != (
            self.verification_status is ToolVerificationStatus.VERIFIED
        ):
            raise ValueError("verified must match verification_status")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", MappingProxyType(dict(self.reasons)))
        object.__setattr__(self, "lineage", MappingProxyType(dict(self.lineage)))

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False


class ToolExecutionLearningSignalService:
    """Derive inert learning evidence from one completed execution trace."""

    def create(
        self,
        trace: ToolExecutionChainTrace,
        *,
        signal_id: str,
        observation: Any = None,
        reasons: Mapping[str, Any] | None = None,
    ) -> ToolExecutionLearningSignal:
        if not isinstance(trace, ToolExecutionChainTrace):
            raise TypeError("trace must be a ToolExecutionChainTrace")
        if not isinstance(signal_id, str) or not signal_id.strip():
            raise ValueError("signal_id must be a non-empty string")

        verification_status = trace.verification.status
        verified = verification_status is ToolVerificationStatus.VERIFIED
        return ToolExecutionLearningSignal(
            signal_id=signal_id,
            invocation_id=trace.request.invocation_id,
            tool_name=trace.request.tool_name,
            authorized=trace.authorization.authorized,
            execution_succeeded=trace.result.success,
            verification_status=verification_status,
            verified=verified,
            observation=(
                trace.result.content if observation is None else observation
            ),
            reasons=(
                reasons
                if reasons is not None
                else {
                    "authorization": trace.authorization.reason,
                    "verification": trace.verification.reason,
                }
            ),
            lineage={
                "signal_id": signal_id,
                "step_id": trace.step.step_id,
                "authorization_evidence_id": trace.authorization_evidence.evidence_id,
                "verification_evidence_id": trace.verification_evidence.evidence_id,
            },
        )


__all__ = [
    "ToolExecutionLearningSignal",
    "ToolExecutionLearningSignalService",
]
