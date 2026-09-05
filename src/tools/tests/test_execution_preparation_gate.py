from __future__ import annotations

import unittest

from src.tools.authorization_integrity import AuthorizationIntegrityService
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.execution_preparation import ExecutionPreparationError, ExecutionPreparationService
from src.tools.gate import PolicyGate
from src.tools.models import RiskLevel, ToolRequest
from src.tools.policy import DefaultPolicy
from src.tools.registry import ToolRegistry
from src.tools.sandbox_admission import SandboxAdmissionService, build_default_sandbox_profiles
from src.tools.service import ToolService
from src.tools.tests.support import EchoHandler


class CountingToolService(ToolService):
    def __init__(self, registry: ToolRegistry) -> None:
        super().__init__(registry)
        self.calls = 0

    def invoke(self, request: ToolRequest):
        self.calls += 1
        return super().invoke(request)


class RejectingPreparationService(ExecutionPreparationService):
    def prepare(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise ExecutionPreparationError("preparation deliberately blocked")


class ExecutionPreparationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.registry.register(EchoHandler(name="echo", risk_level=RiskLevel.LOW))
        self.service = CountingToolService(self.registry)
        self.gate = PolicyGate(
            self.registry,
            self.service,
            DefaultPolicy(),
            AutoApproveConfirmationProvider(),
        )

    def test_admitted_request_produces_preparation_before_service(self) -> None:
        request = ToolRequest(tool_name="echo", arguments={"x": 1}, invocation_id="inv-1")

        result = self.gate.invoke(request)

        self.assertTrue(result.success)
        self.assertEqual(self.service.calls, 1)

    def test_preparation_failure_blocks_before_service(self) -> None:
        self.gate._execution_preparation = RejectingPreparationService()
        request = ToolRequest(tool_name="echo", arguments={"x": 1}, invocation_id="inv-1")

        result = self.gate.invoke(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "execution_preparation_failed")
        self.assertIn("preparation deliberately blocked", result.error.message)
        self.assertEqual(self.service.calls, 0)

    def test_preparation_service_rejects_missing_upstream_evidence(self) -> None:
        request = ToolRequest(tool_name="echo")
        authorization = self.gate.authorize(request)
        integrity_service = AuthorizationIntegrityService()
        integrity = integrity_service.attest(authorization, request)
        admission = SandboxAdmissionService(build_default_sandbox_profiles()).admit(
            authorization,
            integrity,
            request,
        )
        preparation = ExecutionPreparationService()

        handoff = preparation.prepare(authorization, integrity, admission, request)

        self.assertTrue(handoff.handoff_id.startswith("handoff-"))
        self.assertEqual(self.service.calls, 0)

    def test_preparation_context_does_not_start_execution(self) -> None:
        request = ToolRequest(tool_name="echo")
        authorization = self.gate.authorize(request)
        integrity = AuthorizationIntegrityService().attest(authorization, request)
        admission = SandboxAdmissionService(build_default_sandbox_profiles()).admit(
            authorization,
            integrity,
            request,
        )
        handoff = ExecutionPreparationService().prepare(
            authorization,
            integrity,
            admission,
            request,
        )

        context = handoff.to_context()
        self.assertTrue(context["execution_prepared"])
        self.assertFalse(context["execution_started"])
        self.assertFalse(context["worker_assigned"])
        self.assertFalse(context["containment_active"])


if __name__ == "__main__":
    unittest.main()
