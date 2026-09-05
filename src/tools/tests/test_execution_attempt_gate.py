from __future__ import annotations

import unittest

from src.tools.execution_attempt import ExecutionAttemptService
from src.tools.execution_preparation import ExecutionPreparationError, ExecutionPreparationService
from src.tools.gate import PolicyGate
from src.tools.models import RiskLevel, ToolRequest, ToolResult
from src.tools.policy import DefaultPolicy
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.tests.support import EchoHandler


class CountingExecutor:
    def __init__(self, result: ToolResult | None = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls = 0
        self.handoff = None

    def execute(self, handoff):
        self.calls += 1
        self.handoff = handoff
        if self.error is not None:
            raise self.error
        return self.result or ToolResult(
            success=True,
            tool_name=handoff.tool_name,
            content=dict(handoff.arguments),
            invocation_id=handoff.invocation_id,
        )


class ExecutionAttemptGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.registry.register(EchoHandler(name="echo", risk_level=RiskLevel.LOW))
        self.service = ToolService(self.registry)

    def make_gate(self, executor) -> PolicyGate:
        return PolicyGate(
            self.registry,
            self.service,
            DefaultPolicy(),
            AutoApproveConfirmationProvider(),
            executor=executor,
        )

    def test_authorized_prepared_request_crosses_attempt_boundary(self) -> None:
        executor = CountingExecutor()
        gate = self.make_gate(executor)

        result = gate.invoke(ToolRequest(tool_name="echo", arguments={"x": 1}, invocation_id="inv-1"))

        self.assertTrue(result.success)
        self.assertEqual(executor.calls, 1)
        self.assertIsNotNone(executor.handoff)
        self.assertEqual(executor.handoff.handoff_id.startswith("handoff-"), True)

    def test_executor_failure_does_not_look_like_success(self) -> None:
        executor = CountingExecutor(error=RuntimeError("worker failed"))
        gate = self.make_gate(executor)

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.code, "execution_attempt_failed")
        self.assertIn("worker failed", result.error.message)

    def test_failed_preparation_blocks_attempt(self) -> None:
        executor = CountingExecutor()
        gate = self.make_gate(executor)
        gate._execution_preparation.prepare = lambda *args: (_ for _ in ()).throw(  # type: ignore[method-assign]
            ExecutionPreparationError("forced preparation failure")
        )

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "execution_preparation_failed")
        self.assertEqual(executor.calls, 0)

    def test_attempt_service_is_replaceable(self) -> None:
        executor = CountingExecutor(result=ToolResult(success=True, tool_name="echo", content={"ok": True}))
        gate = self.make_gate(executor)

        self.assertIsInstance(gate._execution_attempt, ExecutionAttemptService)


if __name__ == "__main__":
    unittest.main()
