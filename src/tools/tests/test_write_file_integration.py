from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.confirmation import AutoApproveConfirmationProvider, AutoDenyConfirmationProvider
from src.tools.gate import PolicyGate
from src.tools.models import ToolRequest
from src.tools.policy import DefaultPolicy
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService
from src.tools.handlers.write_file import WriteFileHandler


class WriteFileIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.registry = ToolRegistry()
        self.handler = WriteFileHandler(self.base_dir)
        self.registry.register(self.handler)
        self.service = ToolService(self.registry)
        self.policy = DefaultPolicy()

    def request(self, **arguments: object) -> ToolRequest:
        return ToolRequest(
            tool_name="write_file",
            arguments=arguments,
            invocation_id="write-integration-1",
        )

    def test_registered_write_tool_is_high_risk_and_confirmation_required(self) -> None:
        definition = self.registry.get("write_file").definition()
        self.assertEqual(definition.risk_level.value, "high")
        self.assertTrue(definition.requires_confirmation)
        self.assertFalse(definition.metadata["read_only"])

    def test_default_gate_denies_without_confirmation(self) -> None:
        gate = PolicyGate(
            self.registry,
            self.service,
            self.policy,
            AutoDenyConfirmationProvider(),
        )

        result = gate.invoke(self.request(path="notes.txt", content="blocked"))

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "confirmation_denied")
        self.assertFalse((self.base_dir / "notes.txt").exists())
        self.assertEqual(result.invocation_id, "write-integration-1")

    def test_approved_write_passes_through_gate(self) -> None:
        gate = PolicyGate(
            self.registry,
            self.service,
            self.policy,
            AutoApproveConfirmationProvider(),
        )

        result = gate.invoke(self.request(path="notes.txt", content="approved"))

        self.assertTrue(result.success)
        self.assertEqual(
            (self.base_dir / "notes.txt").read_text(encoding="utf-8"),
            "approved",
        )

    def test_gate_never_skips_confirmation_for_write_tool(self) -> None:
        provider = AutoDenyConfirmationProvider()
        gate = PolicyGate(self.registry, self.service, self.policy, provider)

        result = gate.invoke(self.request(path="notes.txt", content="blocked"))

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "confirmation_denied")
        self.assertFalse((self.base_dir / "notes.txt").exists())
