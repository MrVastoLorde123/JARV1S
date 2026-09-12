"""Bounded coding-agent worker orchestration for JARVIS.

The worker deliberately separates three concerns:

* a planning adapter proposes repository edits and verification;
* the existing tool gate performs every filesystem or verification action;
* the worker returns structured evidence about what happened.

This milestone does not assume that an AI provider has native tool calling.
A future model adapter can implement the planner contract without changing
this execution boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol
from uuid import uuid4

from src.tools.models import ToolRequest, ToolResult


MAX_EDITS = 32
MAX_PATH_LENGTH = 512


@dataclass(frozen=True)
class CodingAgentEdit:
    """One bounded text-file edit requested by a coding agent."""

    path: str
    content: str
    overwrite: bool = False
    create_parents: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.path, str) or not self.path.strip():
            raise ValueError("edit path must be a non-empty string")
        if len(self.path) > MAX_PATH_LENGTH:
            raise ValueError(f"edit path exceeds {MAX_PATH_LENGTH} characters")
        if not isinstance(self.content, str):
            raise TypeError("edit content must be a string")
        if not isinstance(self.overwrite, bool):
            raise TypeError("edit overwrite must be a bool")
        if not isinstance(self.create_parents, bool):
            raise TypeError("edit create_parents must be a bool")


@dataclass(frozen=True)
class CodingAgentVerification:
    """The constrained verification operation the worker must execute."""

    runner: str
    arguments: tuple[str, ...] = ()
    timeout_seconds: int | None = None

    def __post_init__(self) -> None:
        if self.runner not in {"python_unittest", "npm_build"}:
            raise ValueError("runner must be 'python_unittest' or 'npm_build'")
        if any(not isinstance(item, str) for item in self.arguments):
            raise TypeError("verification arguments must be strings")
        if self.timeout_seconds is not None:
            if not isinstance(self.timeout_seconds, int) or isinstance(self.timeout_seconds, bool):
                raise TypeError("timeout_seconds must be an integer or None")
            if self.timeout_seconds < 1:
                raise ValueError("timeout_seconds must be positive")


@dataclass(frozen=True)
class CodingAgentPlan:
    """A planner's complete bounded proposal for one coding task."""

    edits: tuple[CodingAgentEdit, ...]
    verification: CodingAgentVerification
    rationale: str = ""

    def __post_init__(self) -> None:
        if len(self.edits) > MAX_EDITS:
            raise ValueError(f"plan exceeds maximum of {MAX_EDITS} edits")
        if any(not isinstance(edit, CodingAgentEdit) for edit in self.edits):
            raise TypeError("edits must contain CodingAgentEdit values")
        if not isinstance(self.verification, CodingAgentVerification):
            raise TypeError("verification must be a CodingAgentVerification")
        if not isinstance(self.rationale, str):
            raise TypeError("rationale must be a string")


@dataclass(frozen=True)
class CodingAgentTask:
    """A JARVIS-assigned coding task."""

    objective: str
    task_id: str = field(default_factory=lambda: f"coding-{uuid4().hex[:16]}")
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be a non-empty string")
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")


@dataclass(frozen=True)
class CodingAgentResult:
    """Structured evidence returned by one worker attempt."""

    task_id: str
    status: str
    edits_attempted: int
    edits_applied: int
    verification: ToolResult | None
    blocked_tool: str | None = None
    message: str = ""

    @property
    def successful(self) -> bool:
        return self.status == "verified"


class CodingAgentPlanner(Protocol):
    """Planner contract implemented by a future model-backed coding agent."""

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        ...


class CodingAgentToolInvoker(Protocol):
    """Execution contract for the existing JARVIS tool gate."""

    def __call__(self, request: ToolRequest) -> ToolResult:
        ...


class CodingAgentWorker:
    """Plan and execute bounded coding work through existing tool authority."""

    def __init__(
        self,
        planner: CodingAgentPlanner,
        tool_invoker: CodingAgentToolInvoker,
    ) -> None:
        self._planner = planner
        self._tool_invoker = tool_invoker

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        """Generate a bounded proposal without invoking any repository tool."""
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")

        plan = self._planner.plan(task)
        if not isinstance(plan, CodingAgentPlan):
            raise TypeError("planner must return a CodingAgentPlan")
        return plan

    def execute(self, task: CodingAgentTask, plan: CodingAgentPlan) -> CodingAgentResult:
        """Execute exactly the supplied plan through the existing tool gate."""
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if not isinstance(plan, CodingAgentPlan):
            raise TypeError("plan must be a CodingAgentPlan")

        coding_operation_id = task.metadata.get("coding_operation_id")
        if coding_operation_id is not None and not isinstance(coding_operation_id, str):
            raise TypeError("coding_operation_id must be a string when provided")

        edits_applied = 0
        for index, edit in enumerate(plan.edits):
            request_metadata = {
                "actor": "coding_agent",
                "task_id": task.task_id,
                "edit_index": index,
            }
            if coding_operation_id is not None:
                request_metadata["coding_operation_id"] = coding_operation_id

            result = self._tool_invoker(
                ToolRequest(
                    tool_name="write_file",
                    arguments={
                        "path": edit.path,
                        "content": edit.content,
                        "overwrite": edit.overwrite,
                        "create_parents": edit.create_parents,
                    },
                    metadata=request_metadata,
                    invocation_id=f"{task.task_id}-edit-{index + 1}",
                )
            )
            if not result.success:
                blocked_codes = {
                    "policy_denied",
                    "confirmation_denied",
                    "authorization_integrity_failed",
                    "sandbox_admission_failed",
                }
                blocked = result.error is not None and result.error.code in blocked_codes
                return CodingAgentResult(
                    task_id=task.task_id,
                    status="blocked" if blocked else "edit_failed",
                    edits_attempted=index + 1,
                    edits_applied=edits_applied,
                    verification=None,
                    blocked_tool="write_file" if blocked else None,
                    message=result.error.message if result.error else "edit failed",
                )
            edits_applied += 1

        verification_arguments = list(plan.verification.arguments)
        verification_arguments_payload = {
            "runner": plan.verification.runner,
            "arguments": verification_arguments,
        }
        if plan.verification.timeout_seconds is not None:
            verification_arguments_payload["timeout_seconds"] = plan.verification.timeout_seconds

        verification_metadata = {
            "actor": "coding_agent",
            "task_id": task.task_id,
            "phase": "verification",
        }
        if coding_operation_id is not None:
            verification_metadata["coding_operation_id"] = coding_operation_id

        verification = self._tool_invoker(
            ToolRequest(
                tool_name="run_test",
                arguments=verification_arguments_payload,
                metadata=verification_metadata,
                invocation_id=f"{task.task_id}-verification",
            )
        )

        return CodingAgentResult(
            task_id=task.task_id,
            status="verified" if verification.success else "verification_failed",
            edits_attempted=len(plan.edits),
            edits_applied=edits_applied,
            verification=verification,
            message=(
                "verification passed"
                if verification.success
                else (verification.error.message if verification.error else "verification failed")
            ),
        )

    def run(self, task: CodingAgentTask) -> CodingAgentResult:
        """Plan and immediately execute; retained for convenience/internal use."""
        return self.execute(task, self.plan(task))


__all__ = [
    "CodingAgentEdit",
    "CodingAgentPlan",
    "CodingAgentPlanner",
    "CodingAgentResult",
    "CodingAgentTask",
    "CodingAgentToolInvoker",
    "CodingAgentVerification",
    "CodingAgentWorker",
]
