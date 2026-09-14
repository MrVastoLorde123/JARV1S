from __future__ import annotations

import unittest

from src.agents.repository_context import RepositoryContextComposer
from src.tools.models import ToolResult


class FakeInvoker:
    def __init__(self) -> None:
        self.requests = []

    def invoke(self, request):
        self.requests.append(request)
        path = request.arguments.get("path")
        if request.tool_name != "list_directory":
            raise AssertionError("repository context must remain read-only")

        if path == ".":
            return ToolResult(
                success=True,
                tool_name="list_directory",
                content={
                    "path": ".",
                    "entries": [
                        {"name": "ui", "path": "ui", "type": "directory"},
                        {"name": "src", "path": "src", "type": "directory"},
                        {"name": "README.md", "path": "README.md", "type": "file"},
                    ],
                },
            )

        if path == "ui":
            return ToolResult(
                success=True,
                tool_name="list_directory",
                content={
                    "path": "ui",
                    "entries": [
                        {"name": "index.html", "path": "ui/index.html", "type": "file"},
                        {"name": "package.json", "path": "ui/package.json", "type": "file"},
                        {"name": "src", "path": "ui/src", "type": "directory"},
                    ],
                },
            )

        return ToolResult(
            success=True,
            tool_name="list_directory",
            content={"path": path, "entries": []},
        )


class M28RepositoryContextTests(unittest.TestCase):
    def test_context_uses_read_only_inventory_and_observes_ui_entrypoint(self) -> None:
        invoker = FakeInvoker()

        context = RepositoryContextComposer(invoker).compose()

        self.assertIn("ui/index.html", context.observed_paths)
        self.assertIn("ui/package.json", context.observed_paths)
        self.assertIn("ui/ exists as a repository directory", context.facts)
        self.assertIn("ui/index.html exists", context.facts)
        self.assertIn("WORKSPACE: .", context.render())
        self.assertTrue(invoker.requests)
        self.assertTrue(all(request.tool_name == "list_directory" for request in invoker.requests))
        self.assertTrue(all(request.metadata["actor"] == "jarvis_context_composer" for request in invoker.requests))

    def test_context_does_not_fabricate_missing_directory(self) -> None:
        invoker = FakeInvoker()
        context = RepositoryContextComposer(invoker).compose()

        self.assertNotIn("public", context.observed_paths)
        self.assertNotIn("public/index.html", context.observed_paths)

    def test_render_is_bounded_even_when_observation_is_large(self) -> None:
        invoker = FakeInvoker()
        context = RepositoryContextComposer(invoker).compose()
        context = type(context)(
            workspace=context.workspace,
            top_level_entries=context.top_level_entries,
            observed_paths=tuple(
                ["README.md", "ui/index.html", "ui/package.json"]
                + [f"src/generated/path_{index}.py" for index in range(1000)]
            ),
            facts=context.facts,
        )

        rendered = context.render()
        observed_section = rendered.split("OBSERVED REPOSITORY PATHS (bounded projection):", 1)[1]
        observed_path_lines = [line for line in observed_section.splitlines() if line.startswith("- ")]

        self.assertLessEqual(len(observed_path_lines), 61)
        self.assertIn("ui/index.html", rendered)
        self.assertIn("ui/package.json", rendered)
        self.assertIn("additional repository paths observed internally but omitted", rendered)


if __name__ == "__main__":
    unittest.main()
