from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.read_file_capability import RealReadFileCapability
from src.tools.models import ToolRequest
from src.tools.policy import PolicyDecision, PolicyVerdict


class DenyAllPolicy:
    def evaluate(self, definition, request):
        return PolicyVerdict(PolicyDecision.DENY, reason="blocked for test")


class M26_6RealReadFileCapabilityTests(unittest.TestCase):
    def test_real_tool_is_registered_as_provider_neutral_capability(self):
        with tempfile.TemporaryDirectory() as directory:
            capability = RealReadFileCapability(directory)
            self.assertEqual(capability.tool_name, "read_file")
            self.assertEqual(len(capability.capability_registry), 1)
            registered = capability.capability_registry.find_by_name("READ_FILE")
            self.assertIs(registered, capability.capability)
            self.assertEqual(registered.capability_id, "tool:read_file")
            self.assertEqual(registered.metadata["tool_version"], "1.0.0")
            self.assertEqual(registered.metadata["risk_level"], "low")
            self.assertFalse(registered.metadata["requires_confirmation"])

    def test_real_read_file_crosses_full_guarded_path_and_returns_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "hello.txt"
            target.write_text("HELLO JARVIS", encoding="utf-8")
            capability = RealReadFileCapability(directory)

            result = capability.read("hello.txt", invocation_id="m26-6-inv-1")

            self.assertTrue(result.success)
            self.assertEqual(result.tool_name, "read_file")
            self.assertEqual(result.invocation_id, "m26-6-inv-1")
            self.assertEqual(result.content["path"], "hello.txt")
            self.assertEqual(result.content["content"], "HELLO JARVIS")
            self.assertEqual(result.content["size_bytes"], len("HELLO JARVIS"))

    def test_request_can_be_supplied_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "data.txt").write_text("data", encoding="utf-8")
            capability = RealReadFileCapability(directory)
            request = ToolRequest(
                tool_name="read_file",
                arguments={"path": "data.txt"},
                invocation_id="explicit-1",
            )
            result = capability.invoke(request)
            self.assertTrue(result.success)
            self.assertEqual(result.invocation_id, "explicit-1")
            self.assertEqual(result.content["content"], "data")

    def test_tool_failure_remains_a_result(self):
        with tempfile.TemporaryDirectory() as directory:
            capability = RealReadFileCapability(directory)
            result = capability.read("missing.txt", invocation_id="missing-1")
            self.assertFalse(result.success)
            self.assertEqual(result.error.code, "file_not_found")
            self.assertEqual(result.invocation_id, "missing-1")

    def test_workspace_escape_is_rejected_by_real_tool(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            outside_file = Path(outside) / "secret.txt"
            outside_file.write_text("SECRET", encoding="utf-8")
            relative_escape = str(outside_file)
            capability = RealReadFileCapability(directory)
            result = capability.read(relative_escape, invocation_id="escape-1")
            self.assertFalse(result.success)
            self.assertIn(result.error.code, {"path_escape", "absolute_path_not_allowed"})
            self.assertEqual(result.invocation_id, "escape-1")

    def test_policy_denial_prevents_real_handler_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "blocked.txt").write_text("BLOCKED", encoding="utf-8")
            capability = RealReadFileCapability(directory, policy=DenyAllPolicy())
            result = capability.read("blocked.txt", invocation_id="denied-1")
            self.assertFalse(result.success)
            self.assertEqual(result.error.code, "policy_denied")
            self.assertEqual(result.invocation_id, "denied-1")

    def test_only_explicit_invocation_executes_capability(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "explicit.txt").write_text("EXPLICIT", encoding="utf-8")
            capability = RealReadFileCapability(directory)
            self.assertTrue(hasattr(capability, "invoke"))
            result = capability.read("explicit.txt", invocation_id="explicit-2")
            self.assertTrue(result.success)
            self.assertEqual(result.content["content"], "EXPLICIT")

    def test_boundary_does_not_authorize_select_mutate_or_establish_truth(self):
        with tempfile.TemporaryDirectory() as directory:
            capability = RealReadFileCapability(directory)
            self.assertFalse(capability.authorizes_execution)
            self.assertFalse(capability.selects_capability)
            self.assertFalse(capability.mutates_state)
            self.assertFalse(capability.persists_state)
            self.assertFalse(capability.establishes_truth)
            self.assertFalse(capability.establishes_certainty)


if __name__ == "__main__":
    unittest.main()
