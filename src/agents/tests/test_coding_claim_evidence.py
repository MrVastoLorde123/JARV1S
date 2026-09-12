from __future__ import annotations

import unittest

from src.agents.claim_evidence import ClaimState, EvidenceType
from src.agents.coding_claim_evidence import CodingClaimEvidenceAdapter
from src.agents.coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentResult,
    CodingAgentTask,
    CodingAgentVerification,
)
from src.tools.models import ToolError, ToolResult


def success(tool_name: str, *, content=None, invocation_id=None) -> ToolResult:
    return ToolResult(
        success=True,
        tool_name=tool_name,
        content=content,
        invocation_id=invocation_id,
    )


def failure(tool_name: str, code: str, message: str, *, invocation_id=None) -> ToolResult:
    return ToolResult(
        success=False,
        tool_name=tool_name,
        error=ToolError(code=code, message=message),
        invocation_id=invocation_id,
    )


class M29CodingClaimEvidenceTests(unittest.TestCase):
    def make_task_and_plan(self):
        task = CodingAgentTask(
            objective="Add visible agent status",
            task_id="coding-m29-integration",
            metadata={"coding_operation_id": "operation-123"},
        )
        plan = CodingAgentPlan(
            edits=(
                CodingAgentEdit(
                    path="ui/index.html",
                    content="<div>Agent Online</div>",
                    overwrite=True,
                ),
            ),
            verification=CodingAgentVerification(runner="npm_build"),
            rationale="Make the smallest visible interface change.",
        )
        return task, plan

    def test_successful_coding_result_becomes_verified_claim(self):
        task, plan = self.make_task_and_plan()
        result = CodingAgentResult(
            task_id=task.task_id,
            status="verified",
            edits_attempted=1,
            edits_applied=1,
            edit_results=(
                success(
                    "write_file",
                    content={"path": "ui/index.html", "written": True},
                    invocation_id="edit-1",
                ),
            ),
            verification=success(
                "run_test",
                content={"exit_code": 0},
                invocation_id="verify-1",
            ),
            message="verification passed",
        )

        outcome = CodingClaimEvidenceAdapter().evaluate(task, plan, result)

        self.assertEqual(outcome.state, ClaimState.VERIFIED)
        self.assertEqual(outcome.claim.state, ClaimState.PROPOSED)
        self.assertEqual(len(outcome.evidence), 2)
        self.assertEqual(
            {item.source_type for item in outcome.evidence},
            {EvidenceType.FILESYSTEM_OBSERVATION, EvidenceType.BUILD_RESULT},
        )
        self.assertEqual(outcome.evaluation.verification_refs, (outcome.evidence[1].evidence_id,))
        self.assertEqual(outcome.evaluation.claim.claim_id, outcome.claim.claim_id)
        self.assertEqual(outcome.evaluation.claim.task_id, task.task_id)
        self.assertEqual(outcome.evidence[0].provenance["operation_id"], "operation-123")

    def test_failed_verification_contradicts_even_after_successful_edit(self):
        task, plan = self.make_task_and_plan()
        result = CodingAgentResult(
            task_id=task.task_id,
            status="verification_failed",
            edits_attempted=1,
            edits_applied=1,
            edit_results=(success("write_file", invocation_id="edit-1"),),
            verification=failure(
                "run_test",
                "verification_failed",
                "npm build failed",
                invocation_id="verify-1",
            ),
            message="npm build failed",
        )

        outcome = CodingClaimEvidenceAdapter().evaluate(task, plan, result)

        self.assertEqual(outcome.state, ClaimState.CONTRADICTED)
        self.assertEqual(outcome.evidence[-1].source_type, EvidenceType.BUILD_RESULT)
        self.assertFalse(outcome.evidence[-1].payload["passed"])

    def test_edit_failure_without_verification_cannot_be_verified(self):
        task, plan = self.make_task_and_plan()
        result = CodingAgentResult(
            task_id=task.task_id,
            status="edit_failed",
            edits_attempted=1,
            edits_applied=0,
            edit_results=(
                failure(
                    "write_file",
                    "write_failed",
                    "filesystem write failed",
                    invocation_id="edit-1",
                ),
            ),
            verification=None,
            message="filesystem write failed",
        )

        outcome = CodingClaimEvidenceAdapter().evaluate(task, plan, result)

        self.assertEqual(outcome.state, ClaimState.SUPPORTED)
        self.assertEqual(len(outcome.evaluation.verification_refs), 0)
        self.assertEqual(outcome.evidence[0].source_type, EvidenceType.FILESYSTEM_OBSERVATION)

    def test_result_task_lineage_is_required(self):
        task, plan = self.make_task_and_plan()
        result = CodingAgentResult(
            task_id="different-task",
            status="verified",
            edits_attempted=0,
            edits_applied=0,
            verification=None,
        )

        with self.assertRaises(ValueError):
            CodingClaimEvidenceAdapter().evaluate(task, plan, result)

    def test_adapter_is_observational_and_does_not_execute_tools(self):
        task, plan = self.make_task_and_plan()
        result = CodingAgentResult(
            task_id=task.task_id,
            status="verified",
            edits_attempted=0,
            edits_applied=0,
            verification=success("run_test", invocation_id="verify-1"),
        )

        outcome = CodingClaimEvidenceAdapter().evaluate(task, plan, result)

        self.assertEqual(outcome.claim.actor, "coding_agent")
        self.assertEqual(outcome.claim.state, ClaimState.PROPOSED)
        self.assertNotIn("authorize", outcome.claim.payload)
        self.assertEqual(len(outcome.evidence), 1)
        self.assertEqual(outcome.evidence[0].source_type, EvidenceType.BUILD_RESULT)


if __name__ == "__main__":
    unittest.main()
