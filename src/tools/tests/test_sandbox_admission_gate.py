from __future__ import annotations

import unittest

from src.plugins.sandbox import SandboxProfile, SandboxProfileRegistry
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.gate import PolicyGate
from src.tools.models import RiskLevel, ToolRequest
from src.tools.policy import DefaultPolicy
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService
from src.tools.tests.support import EchoHandler, allow_policy


class SandboxAdmissionGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.service = ToolService(self.registry)

    def test_integrity_verified_request_passes_sandbox_before_service(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        profiles = SandboxProfileRegistry()
        profiles.register(SandboxProfile(profile_id="default"))
        gate = PolicyGate(
            self.registry,
            self.service,
            allow_policy(),
            sandbox_profile_registry=profiles,
        )

        result = gate.invoke(ToolRequest(tool_name="echo", arguments={"x": 1}))

        self.assertTrue(result.success)
        self.assertEqual(result.content, {"x": 1})

    def test_missing_sandbox_profile_blocks_before_tool_service(self) -> None:
        self.registry.register(
            EchoHandler(name="echo", metadata={"sandbox_profile_id": "missing"})
        )
        gate = PolicyGate(self.registry, self.service, allow_policy())

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "sandbox_admission_failed")
        self.assertIn("not registered", result.error.message)

    def test_sandbox_admission_can_use_declared_profile(self) -> None:
        self.registry.register(
            EchoHandler(name="echo", metadata={"sandbox_profile_id": "restricted"})
        )
        profiles = SandboxProfileRegistry()
        profiles.register(SandboxProfile(profile_id="restricted"))
        gate = PolicyGate(
            self.registry,
            self.service,
            allow_policy(),
            sandbox_profile_registry=profiles,
        )

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertTrue(result.success)

    def test_high_risk_confirmed_request_passes_sandbox_and_executes(self) -> None:
        self.registry.register(
            EchoHandler(name="danger", risk_level=RiskLevel.HIGH)
        )
        profiles = SandboxProfileRegistry()
        profiles.register(SandboxProfile(profile_id="default"))
        gate = PolicyGate(
            self.registry,
            self.service,
            DefaultPolicy(),
            AutoApproveConfirmationProvider(),
            profiles,
        )

        result = gate.invoke(ToolRequest(tool_name="danger", arguments={"ok": True}))

        self.assertTrue(result.success)
        self.assertEqual(result.content, {"ok": True})

    def test_custom_profile_is_resolved_from_definition_metadata(self) -> None:
        self.registry.register(
            EchoHandler(name="echo", metadata={"sandbox_profile_id": "custom"})
        )
        profiles = SandboxProfileRegistry()
        profiles.register(SandboxProfile(profile_id="custom"))
        gate = PolicyGate(
            self.registry,
            self.service,
            allow_policy(),
            sandbox_profile_registry=profiles,
        )

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
