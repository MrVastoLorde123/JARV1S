"""Translate a completed coding-agent result into M29 claim/evidence records.

This adapter is deliberately observational. It does not invoke tools,
authorize actions, mutate policy, or decide what work should execute.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.tools.models import ToolResult

from .claim_evidence import (
    Claim,
    ClaimEvidenceEvaluator,
    ClaimEvaluation,
    Evidence,
    EvidenceType,
)
from .coding_worker import CodingAgentPlan, CodingAgentResult, CodingAgentTask


@dataclass(frozen=True)
class CodingClaimEvidenceResult:
    """Structured M29 outcome for one coding task execution."""

    claim: Claim
    evidence: tuple[Evidence, ...]
    evaluation: ClaimEvaluation

    @property
    def state(self):
        """Return the deterministic claim state derived from the evidence."""
        return self.evaluation.state


class CodingClaimEvidenceAdapter:
    """Construct and evaluate M29 records from one bounded coding result."""

    def __init__(self, evaluator: ClaimEvidenceEvaluator | None = None) -> None:
        self._evaluator = evaluator or ClaimEvidenceEvaluator()

    def evaluate(
        self,
        task: CodingAgentTask,
        plan: CodingAgentPlan,
        result: CodingAgentResult,
    ) -> CodingClaimEvidenceResult:
        """Build deterministic records without performing any side effects."""
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if not isinstance(plan, CodingAgentPlan):
            raise TypeError("plan must be a CodingAgentPlan")
        if not isinstance(result, CodingAgentResult):
            raise TypeError("result must be a CodingAgentResult")
        if result.task_id != task.task_id:
            raise ValueError("coding result task_id must match task task_id")

        operation_id = task.metadata.get("coding_operation_id")
        if operation_id is not None and not isinstance(operation_id, str):
            raise TypeError("coding_operation_id must be a string when provided")

        claim = Claim(
            task_id=task.task_id,
            actor="coding_agent",
            payload={
                "objective": task.objective,
                "status": result.status,
                "edits_attempted": result.edits_attempted,
                "edits_applied": result.edits_applied,
                "message": result.message,
            },
            provenance={
                "source": "coding_agent_worker",
                "operation_id": operation_id,
                "plan_rationale": plan.rationale,
                "verification_runner": plan.verification.runner,
                "verification_arguments": plan.verification.arguments,
            },
        )

        evidence: list[Evidence] = []
        for index, (edit, tool_result) in enumerate(zip(plan.edits, result.edit_results)):
            evidence.append(
                self._edit_evidence(
                    task,
                    operation_id,
                    index,
                    edit.path,
                    tool_result,
                )
            )

        if result.verification is not None:
            evidence.append(
                self._verification_evidence(
                    task,
                    operation_id,
                    plan,
                    result.verification,
                )
            )

        evaluation = self._evaluator.evaluate(claim, evidence)
        return CodingClaimEvidenceResult(
            claim=claim,
            evidence=tuple(evidence),
            evaluation=evaluation,
        )

    @staticmethod
    def _edit_evidence(
        task: CodingAgentTask,
        operation_id: str | None,
        edit_index: int,
        path: str,
        result: ToolResult,
    ) -> Evidence:
        """Represent one write-file observation with task/operation provenance."""
        payload: dict[str, Any] = {
            "tool_name": result.tool_name,
            "success": result.success,
            "path": path,
            "result_content": result.content,
        }
        if result.error is not None:
            payload["error"] = {
                "code": result.error.code,
                "message": result.error.message,
                "details": dict(result.error.details),
            }

        return Evidence(
            task_id=task.task_id,
            source_type=EvidenceType.FILESYSTEM_OBSERVATION,
            payload=payload,
            provenance={
                "source": "write_file",
                "invocation_id": result.invocation_id,
                "operation_id": operation_id,
                "edit_index": edit_index,
            },
        )

    @staticmethod
    def _verification_evidence(
        task: CodingAgentTask,
        operation_id: str | None,
        plan: CodingAgentPlan,
        result: ToolResult,
    ) -> Evidence:
        """Represent the bounded verification result as M29 verification evidence."""
        payload: dict[str, Any] = {
            "tool_name": result.tool_name,
            "passed": result.success,
            "content": result.content,
            "runner": plan.verification.runner,
            "arguments": plan.verification.arguments,
        }
        if result.error is not None:
            payload["error"] = {
                "code": result.error.code,
                "message": result.error.message,
                "details": dict(result.error.details),
            }

        source_type = (
            EvidenceType.BUILD_RESULT
            if plan.verification.runner == "npm_build"
            else EvidenceType.TEST_RESULT
        )
        return Evidence(
            task_id=task.task_id,
            source_type=source_type,
            payload=payload,
            provenance={
                "source": "run_test",
                "invocation_id": result.invocation_id,
                "operation_id": operation_id,
                "phase": "verification",
            },
        )


__all__ = ["CodingClaimEvidenceAdapter", "CodingClaimEvidenceResult"]
