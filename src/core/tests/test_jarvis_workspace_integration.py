import tempfile
import unittest

from src.ai.service import AIService
from src.core.jarvis import JARVIS
from src.core.task_models import TaskRequest, TaskType
from src.tools.bootstrap import build_workspace_tool_stack


class JARVISWorkspaceIntegrationTests(unittest.TestCase):
    def test_jarvis_reads_workspace_file_through_injected_capability_boundary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text("JARVIS workspace", encoding="utf-8")

            stack = build_workspace_tool_stack(root)
            jarvis = JARVIS(
                ai_service=AIService(),
                tool_invoker=stack.gate,
            )

            response = jarvis.ask_task(
                TaskRequest(
                    content="Read the README",
                    task_type=TaskType.TOOL,
                    metadata={
                        "tool_name": "read_file",
                        "arguments": {"path": "README.md"},
                    },
                )
            )

            self.assertEqual("TASK", response.metadata["route"])
            self.assertEqual("EXECUTION", response.metadata["stage"])
            self.assertEqual("COMPLETED", response.metadata["execution_status"])
            self.assertIn("JARVIS workspace", response.content)
            self.assertEqual(
                (
                    {
                        "path": "README.md",
                        "content": "JARVIS workspace",
                        "size_bytes": len("JARVIS workspace".encode("utf-8")),
                    },
                ),
                response.metadata["execution_outputs"],
            )

    def test_jarvis_respects_tool_confirmation_boundary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stack = build_workspace_tool_stack(root)
            jarvis = JARVIS(
                ai_service=AIService(),
                tool_invoker=stack.gate,
            )

            response = jarvis.ask_task(
                TaskRequest(
                    content="Write a file",
                    task_type=TaskType.TOOL,
                    metadata={
                        "tool_name": "write_file",
                        "arguments": {
                            "path": "notes.txt",
                            "content": "should not be written",
                        },
                    },
                )
            )

            self.assertEqual("TASK", response.metadata["route"])
            self.assertEqual("EXECUTION", response.metadata["stage"])
            self.assertEqual("FAILED", response.metadata["execution_status"])
            self.assertIn("confirmation_denied", response.content)
            self.assertFalse((root / "notes.txt").exists())


if __name__ == "__main__":
    unittest.main()