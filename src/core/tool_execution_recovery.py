"""Produce bounded recovery recommendations from execution verification evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.core.tool_execution_chain import ToolExecutionChainTrace
from src.core.tool_execution_verification import ToolVerificationStatus


class ToolExecutionRecoveryAction(str, Enum):
    COMPLETE = "COMPLETE"
    REVIEW = "REVIEW"
    CORRECT = "CORRECT"


@dataclass(frozen=True)
class ToolExecutionRecoveryRecommendation:
    """Non-authoritative recommendation for the next control stage."""

    action: ToolExecutionRecoveryAction
    reason: str
    verification_status: ToolVerificationStatus

    def __post_init__(self) -> None:
        if not isinstance(self.action, ToolExecutionRecoveryAction):
            raise TypeError("action must be a ToolExecutionRecoveryAction")
        if not isinstance(self.verification_status, ToolVerificationStatus):
            raise TypeError("verification_status must be a ToolVerificationStatus")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def executes(self) -> bool:
        return False


class ToolExecutionRecoveryService:
    """Derive only a bounded recovery recommendation from one chain trace."""

    def recommend(
        self,
        trace: ToolExecutionChainTrace,
    ) -> ToolExecutionRecoveryRecommendation:
        if not isinstance(trace, ToolExecutionChainTrace):
            raise TypeError("trace must be a ToolExecutionChainTrace")

        status = trace.verification.status
        if status is ToolVerificationStatus.VERIFIED:
            return ToolExecutionRecoveryRecommendation(
                action=ToolExecutionRecoveryAction.COMPLETE,
                reason="execution effect has explicit independent verification",
                verification_status=status,
            )
        if status is ToolVerificationStatus.FAILED:
            return ToolExecutionRecoveryRecommendation(
                action=ToolExecutionRecoveryAction.CORRECT,
                reason="verification evidence indicates the expected effect was not established",
                verification_status=status,
            )
        return ToolExecutionRecoveryRecommendation(
            action=ToolExecutionRecoveryAction.REVIEW,
            reason="execution completed without sufficient evidence to establish the expected effect",
            verification_status=status,
        )


__all__ = [
    "ToolExecutionRecoveryAction",
    "ToolExecutionRecoveryRecommendation",
    "ToolExecutionRecoveryService",
]
