from __future__ import annotations

import unittest

from src.agents.ai_coding_planner import AICodingAgentPlanner
from src.agents.coding_worker import CodingAgentTask
from src.ai.models import AICapabilities, AIResponse


class FakeAIService:
    def __init__(self, content) -> None:
        self.content = content
        self.calls = []

    def generate(self, request, provider_name=None, required_capabilities=None):
        self.calls.append((request, provider_name, required_capabilities))
        return AIResponse(
            content=self.content,
            provider=provider_name or "fake",
            model=request.model or "fake-model",
        )


class M28AICodingAgentPlannerTests(unittest.TestCase):
    def test_planner_converts_structured_response_into_bounded_plan(self) -> None:
        service = FakeAIService(
            {
                "rationale": "Update the interface and verify the build.",
                "edits": [
                    {
                        "path": "ui/src/App.tsx",
                        "content": "export default function App() { return <main />; }",
                        "overwrite": True,
                        "create_parents": False,
                    }
                ],
                "verification": {
                    "runner": "npm_build",
                    "arguments": [],
                    "timeout_seconds": 120,
                },
            }
        )
        task = CodingAgentTask(objective="Improve the interface")

        plan = AICodingAgentPlanner(service, provider_name="local").plan(task)

        self.assertEqual(plan.rationale, "Update the interface and verify the build.")
        self.assertEqual(len(plan.edits), 1)
        self.assertEqual(plan.edits[0].path, "ui/src/App.tsx")
        self.assertTrue(plan.edits[0].overwrite)
        self.assertEqual(plan.verification.runner, "npm_build")
        self.assertEqual(plan.verification.timeout_seconds, 120)

        request, provider_name, required_capabilities = service.calls[0]
        self.assertEqual(provider_name, "local")
        self.assertEqual(required_capabilities, ("structured_output",))
        self.assertEqual(request.generation_options["temperature"], 0)
        self.assertEqual(
            request.generation_options["response_format"],
            {"type": "json_object"},
        )
        self.assertIn("Improve the interface", request.task)

    def test_planner_defaults_python_unittest_to_canonical_prefix(self) -> None:
        service = FakeAIService(
            {
                "edits": [],
                "verification": {
                    "runner": "python_unittest",
                    "arguments": [],
                },
            }
        )
        task = CodingAgentTask(objective="Run repository tests")

        plan = AICodingAgentPlanner(service).plan(task)

        self.assertEqual(plan.verification.arguments, ("-m", "unittest"))

    def test_planner_rejects_invalid_python_unittest_prefix(self) -> None:
        service = FakeAIService(
            {
                "edits": [],
                "verification": {
                    "runner": "python_unittest",
                    "arguments": ["python", "tests"],
                },
            }
        )
        task = CodingAgentTask(objective="Run repository tests safely")

        with self.assertRaises(ValueError):
            AICodingAgentPlanner(service).plan(task)

    def test_planner_includes_jarvis_observed_repository_context(self) -> None:
        service = FakeAIService(
            {
                "rationale": "Use the observed frontend entrypoint.",
                "edits": [],
                "verification": {"runner": "npm_build", "arguments": []},
            }
        )
        task = CodingAgentTask(
            objective="Add a visible status indicator",
            metadata={
                "repository_context": (
                    "WORKSPACE: .\n"
                    "OBSERVED REPOSITORY PATHS:\n"
                    "- ui/index.html\n"
                    "- ui/package.json\n"
                    "JARVIS OBSERVED FACTS:\n"
                    "- ui/index.html exists"
                )
            },
        )

        AICodingAgentPlanner(service).plan(task)

        request, _, _ = service.calls[0]
        self.assertIn("JARVIS OBSERVED REPOSITORY CONTEXT:", request.task)
        self.assertIn("ui/index.html", request.task)
        self.assertIn("Do not invent directories or filenames", request.task)

    def test_planner_rejects_invalid_json_text(self) -> None:
        service = FakeAIService("not-json")
        task = CodingAgentTask(objective="Do something")

        with self.assertRaises(ValueError):
            AICodingAgentPlanner(service).plan(task)

    def test_planner_rejects_unsupported_runner(self) -> None:
        service = FakeAIService(
            {
                "edits": [],
                "verification": {
                    "runner": "shell",
                    "arguments": ["python", "app.py"],
                },
            }
        )
        task = CodingAgentTask(objective="Use only safe verification")

        with self.assertRaises(ValueError):
            AICodingAgentPlanner(service).plan(task)

    def test_planner_cannot_be_substituted_with_provider_without_structured_output(self) -> None:
        class NoStructuredProvider:
            def capabilities(self):
                return AICapabilities(text_generation=True, structured_output=False)

        self.assertFalse(NoStructuredProvider().capabilities().structured_output)


if __name__ == "__main__":
    unittest.main()
