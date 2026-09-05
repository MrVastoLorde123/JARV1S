from __future__ import annotations

import unittest

from src.tools.authorization_integrity import AuthorizationIntegrityResult
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.gate import PolicyGate
from src.tools.models import RiskLevel, ToolRequest
from src.tools.policy import DefaultPolicy
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService
from src.tools.tests.support import EchoHandler


class TamperingIntegrityService:
    def attest(self, decision, request):
        return AuthorizationIntegrityResult(
            authorization_id=decision.authorization_id,
            request_fingerprint="tampered",
            decision_fingerprint="tampered",
            valid=True,
        )

    def verify(self, result, decision, request):
        return False


class AuthorizationIntegrityGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.registry.register(EchoHandler(name="echo", risk_level=RiskLevel.LOW))
        self.service = ToolService(self.registry)
        self.gate = PolicyGate(self.registry, self.service, DefaultPolicy())

    def test_normal_authorized_request_passes_integrity(self) -> None:
        result = self.gate.invoke(ToolRequest(tool_name="echo", arguments={"x": 1}))
        self.assertTrue(result.success)

    def test_integrity_failure_blocks_before_service(self) -> None:
        self.gate._authorization_integrity = TamperingIntegrityService()
        result = self.gate.invoke(ToolRequest(tool_name="echo", arguments={"x": 1}))
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "authorization_integrity_failed")

    def test_high_risk_confirmed_request_still_passes_integrity(self) -> None:
        self.registry = ToolRegistry()
        self.registry.register(EchoHandler(name="echo", risk_level=RiskLevel.HIGH))
        self.service = ToolService(self.registry)
        self.gate = PolicyGate(
            self.registry,
            self.service,
            DefaultPolicy(),
            AutoApproveConfirmationProvider(),
        )
        result = self.gate.invoke(ToolRequest(tool_name="echo"))
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
