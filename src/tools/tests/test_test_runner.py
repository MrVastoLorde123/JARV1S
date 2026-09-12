import tempfile
import unittest
from pathlib import Path

from src.tools.handlers.test_runner import TestRunnerHandler
from src.tools.models import ToolRequest


class M28_TestRunnerTests(unittest.TestCase):
    def test_python_unittest_executes_in_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "test_smoke.py").write_text(
                "import unittest\n\nclass Smoke(unittest.TestCase):\n    def test_ok(self):\n        self.assertEqual(2 + 2, 4)\n",
                encoding="utf-8",
            )

            result = TestRunnerHandler(root).execute(
                ToolRequest(
                    tool_name="run_test",
                    arguments={
                        "runner": "python_unittest",
                        "arguments": ["-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"],
                    },
                    invocation_id="runner-test",
                )
            )

            self.assertTrue(result.success)
            self.assertIsNone(result.error)
            self.assertEqual(result.content["exit_code"], 0)
            self.assertIn("OK", result.content["stderr"] + result.content["stdout"])

    def test_arbitrary_python_command_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = TestRunnerHandler(temp_dir).execute(
                ToolRequest(
                    tool_name="run_test",
                    arguments={
                        "runner": "python_unittest",
                        "arguments": ["-c", "print('not allowed')"],
                    },
                )
            )

            self.assertFalse(result.success)
            self.assertEqual(result.error.code, "invalid_arguments")

    def test_npm_build_requires_no_custom_arguments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = TestRunnerHandler(temp_dir)
            self.assertEqual(
                handler._build_command("npm_build", ()),  # noqa: SLF001
                [handler._build_command("npm_build", ())[0], "run", "build"],  # noqa: SLF001
            )
            self.assertIsInstance(
                handler._build_command("npm_build", ("run", "build")),  # noqa: SLF001
                str,
            )


if __name__ == "__main__":
    unittest.main()
