from __future__ import annotations

import unittest

from src.agents.coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentTask,
    CodingAgentVerification,
    CodingAgentWorker,
)
from src.tools.models import ToolError, ToolRequest, ToolResult


class FixedPlanner:
    def __init__(self, plan: CodingAgentPlan) -> None:
        self.plan_value = plan
        self.seen_task: CodingAgentTask | None = None
        self.calls = 0

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        self.calls += 1
        self.seen_task = task
        return self.plan_value


class RecordingInvoker:
    def __init__(self, responses: list[ToolResult]) -> None:
        self.responses = list(responses)
        self.requests: list[ToolRequest] = []

    def __call__(self, request: ToolRequest) -> ToolResult:
        self.requests.append(request)
        return self.responses.pop(0)


def success(tool_name: str, invocation_id: str | None = None, content=None) -> ToolResult:
    return ToolResult(
        success=True,
        tool_name=tool_name,
        content=content,
        invocation_id=invocation_id,
    )


def failure(tool_name: str, code: str, message: str) -> ToolResult:
    return ToolResult(
        success=False,
        tool_name=tool_name,
        error=ToolError(code=code, message=message),
    )


class M28CodingAgentWorkerTests(unittest.TestCase):
    def test_worker_plans_without_invoking_tools(self) -> None:
        task = CodingAgentTask(objective="Propose an interface improvement")
        plan = CodingAgentPlan(
            edits=(CodingAgentEdit(path="ui/src/App.tsx", content="proposed"),),
            verification=CodingAgentVerification(runner="npm_build"),
        )
        planner = FixedPlanner(plan)
        invoker = RecordingInvoker([])
        worker = CodingAgentWorker(planner, invoker)

        result = worker.plan(task)

        self.assertIs(result, plan)
        self.assertEqual(planner.calls, 1)
        self.assertEqual(invoker.requests, [])
        self.assertIs(planner.seen_task, task)

    def test_worker_executes_exactly_the_supplied_plan(self) -> None:
        task = CodingAgentTask(objective="Execute approved change")
        approved_plan = CodingAgentPlan(
            edits=(
                CodingAgentEdit(
                    path="ui/src/App.tsx",
                    content="approved content",
                    overwrite=True,
                    create_parents=True,
                ),
                CodingAgentEdit(
                    path="ui/src/main.tsx",
                    content="second approved content",
                ),
            ),
            verification=CodingAgentVerification(
                runner="python_unittest",
                arguments=("-m", "unittest", "src.interface.tests.test_boundary"),
                timeout_seconds=120,
            ),
            rationale="Use the smallest approved change set.",
        )
        planner = FixedPlanner(approved_plan)
        invoker = RecordingInvoker([
            success("write_file"),
            success("write_file"),
            success("run_test", content={"exit_code": 0}),
        ])
        worker = CodingAgentWorker(planner, invoker)

        result = worker.execute(task, approved_plan)

        self.assertEqual(result.status, "verified")
        self.assertTrue(result.successful)
        self.assertEqual(planner.calls, 0)
        self.assertEqual(len(invoker.requests), 3)
        self.assertEqual(invoker.requests[0].arguments["path"], "ui/src/App.tsx")
        self.assertEqual(invoker.requests[0].arguments["content"], "approved content")
        self.assertTrue(invoker.requests[0].arguments["overwrite"])
        self.assertTrue(invoker.requests[0].arguments["create_parents"])
        self.assertEqual(invoker.requests[1].arguments["path"], "ui/src/main.tsx")
        self.assertEqual(invoker.requests[2].arguments["runner"], "python_unittest")
        self.assertEqual(
            invoker.requests[2].arguments["arguments"],
            ["-m", "unittest", "src.interface.tests.test_boundary"],
        )
        self.assertEqual(invoker.requests[2].arguments["timeout_seconds"], 120)

    def test_worker_run_keeps_plan_then_execute_convenience(self) -> None:
        task = CodingAgentTask(objective="Improve the interface")
        plan = CodingAgentPlan(
            edits=(
                CodingAgentEdit(
                    path="ui/src/App.tsx",
                    content="updated",
                    overwrite=True,
                ),
            ),
            verification=CodingAgentVerification(
                runner="npm_build",
            ),
        )
        planner = FixedPlanner(plan)
        invoker = RecordingInvoker([
            success("write_file"),
            success("run_test", content={"exit_code": 0}),
        ])

        result = CodingAgentWorker(planner, invoker).run(task)

        self.assertEqual(result.status, "verified")
        self.assertTrue(result.successful)
        self.assertEqual(result.edits_attempted, 1)
        self.assertEqual(result.edits_applied, 1)
        self.assertEqual(len(invoker.requests), 2)
        self.assertEqual(invoker.requests[0].tool_name, "write_file")
        self.assertEqual(invoker.requests[0].metadata["actor"], "coding_agent")
        self.assertEqual(invoker.requests[1].tool_name, "run_test")
        self.assertEqual(invoker.requests[1].arguments["runner"], "npm_build")
        self.assertEqual(planner.calls, 1)

    def test_worker_stops_when_edit_is_blocked(self) -> None:
        task = CodingAgentTask(objective="Change one file")
        plan = CodingAgentPlan(
            edits=(CodingAgentEdit(path="ui/src/App.tsx", content="blocked"),),
            verification=CodingAgentVerification(
                runner="python_unittest",
                arguments=("-m", "unittest", "src.interface.tests.test_http_command"),
            ),
        )
        invoker = RecordingInvoker([
            failure("write_file", "confirmation_denied", "confirmation required"),
        ])

        result = CodingAgentWorker(FixedPlanner(plan), invoker).execute(task, plan)

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.blocked_tool, "write_file")
        self.assertEqual(result.edits_attempted, 1)
        self.assertEqual(result.edits_applied, 0)
        self.assertIsNone(result.verification)
        self.assertEqual(len(invoker.requests), 1)

    def test_worker_returns_verification_failure_as_evidence(self) -> None:
        task = CodingAgentTask(objective="Make a failing change")
        plan = CodingAgentPlan(
            edits=(),
            verification=CodingAgentVerification(
                runner="python_unittest",
                arguments=("-m", "unittest", "src.interface.tests.test_http_command"),
            ),
        )
        verification_failure = failure(
            "run_test",
            "verification_failed",
            "verification command exited with code 1",
        )
        invoker = RecordingInvoker([verification_failure])

        result = CodingAgentWorker(FixedPlanner(plan), invoker).execute(task, plan)

        self.assertEqual(result.status, "verification_failed")
        self.assertFalse(result.successful)
        self.assertIs(result.verification, verification_failure)
        self.assertIn("exited with code 1", result.message)

    def test_worker_does_not_offer_an_arbitrary_command_surface(self) -> None:
        with self.assertRaises(ValueError):
            CodingAgentVerification(runner="shell")


if __name__ == "__main__":
    unittest.main()
