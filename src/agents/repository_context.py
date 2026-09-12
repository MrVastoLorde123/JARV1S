"""JARVIS-owned, read-only repository context composition for agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from uuid import uuid4

from src.tools.models import ToolRequest, ToolResult


_MAX_RENDERED_PATHS = 60


@dataclass(frozen=True)
class RepositoryContext:
    """Observed environment facts safe to provide to an agent planner."""

    workspace: str
    top_level_entries: tuple[Mapping[str, object], ...]
    observed_paths: tuple[str, ...]
    facts: tuple[str, ...]

    def render(self) -> str:
        lines = [f"WORKSPACE: {self.workspace}"]
        if self.facts:
            lines.append("JARVIS OBSERVED FACTS:")
            lines.extend(f"- {fact}" for fact in self.facts)

        prioritized_paths = self._prioritized_paths()
        if prioritized_paths:
            lines.append("OBSERVED REPOSITORY PATHS (bounded projection):")
            lines.extend(f"- {path}" for path in prioritized_paths)

        if len(self.observed_paths) > len(prioritized_paths):
            lines.append(
                f"- additional repository paths observed internally but omitted from planner context: "
                f"{len(self.observed_paths) - len(prioritized_paths)}"
            )

        return "\n".join(lines)

    def _prioritized_paths(self) -> tuple[str, ...]:
        """Project broad observations into a small planner-safe context.

        JARVIS may observe more than the LLM needs. The planner receives only
        a bounded projection so small local models are not overwhelmed by raw
        repository inventory. The projection prioritizes top-level paths and
        common application surfaces such as the UI.
        """
        paths = tuple(sorted(self.observed_paths))
        top_level = [path for path in paths if "/" not in path and "\\" not in path]
        ui_paths = [path for path in paths if path == "ui" or path.startswith("ui/")]
        src_paths = [path for path in paths if path == "src" or path.startswith("src/")]

        selected: list[str] = []
        for group in (top_level, ui_paths, src_paths, list(paths)):
            for path in group:
                if path not in selected:
                    selected.append(path)
                if len(selected) >= _MAX_RENDERED_PATHS:
                    return tuple(selected)
        return tuple(selected)


class RepositoryContextComposer:
    """Build bounded environment context through existing read-only tools."""

    _INSPECTABLE_DIRECTORIES = ("ui", "src", "tests", "test", "frontend", "backend")
    _MAX_PATHS = 600
    _MAX_INSPECTED_DIRECTORIES = 3

    def __init__(self, tool_invoker) -> None:
        self._tool_invoker = tool_invoker

    def compose(self, *, workspace: str = ".") -> RepositoryContext:
        root = self._invoke(
            "list_directory",
            {"path": ".", "recursive": False, "include_hidden": False},
            "root",
        )
        if not root.success:
            message = root.error.message if root.error else "repository inspection failed"
            return RepositoryContext(workspace, (), (), (f"repository inspection unavailable: {message}",))

        content = root.content if isinstance(root.content, Mapping) else {}
        entries = content.get("entries", ())
        if not isinstance(entries, (list, tuple)):
            entries = ()

        normalized_entries = tuple(
            entry for entry in entries
            if isinstance(entry, Mapping) and isinstance(entry.get("path"), str)
        )
        observed_paths = {str(entry["path"]) for entry in normalized_entries}
        directory_names = {
            str(entry.get("name")): str(entry.get("path"))
            for entry in normalized_entries
            if entry.get("type") == "directory"
        }

        inspected = 0
        for name in self._INSPECTABLE_DIRECTORIES:
            path = directory_names.get(name)
            if path is None or inspected >= self._MAX_INSPECTED_DIRECTORIES:
                continue
            result = self._invoke(
                "list_directory",
                {"path": path, "recursive": True, "include_hidden": False},
                f"directory:{path}",
            )
            inspected += 1
            if not result.success:
                continue
            directory_content = result.content if isinstance(result.content, Mapping) else {}
            directory_entries = directory_content.get("entries", ())
            if not isinstance(directory_entries, (list, tuple)):
                continue
            for entry in directory_entries:
                if isinstance(entry, Mapping) and isinstance(entry.get("path"), str):
                    observed_paths.add(str(entry["path"]))
                    if len(observed_paths) >= self._MAX_PATHS:
                        break
            if len(observed_paths) >= self._MAX_PATHS:
                break

        facts = []
        if "ui" in directory_names:
            facts.append("ui/ exists as a repository directory")
        if "ui/index.html" in observed_paths:
            facts.append("ui/index.html exists")
        if "ui/package.json" in observed_paths:
            facts.append("ui/package.json exists; the frontend has a package manifest under ui/")
        if "package.json" in observed_paths:
            facts.append("package.json exists at the workspace root")
        if "pyproject.toml" in observed_paths:
            facts.append("pyproject.toml exists at the workspace root")
        if "requirements.txt" in observed_paths:
            facts.append("requirements.txt exists at the workspace root")

        return RepositoryContext(
            workspace=workspace,
            top_level_entries=normalized_entries,
            observed_paths=tuple(sorted(observed_paths))[: self._MAX_PATHS],
            facts=tuple(facts),
        )

    def _invoke(self, tool_name: str, arguments: Mapping[str, object], phase: str) -> ToolResult:
        return self._tool_invoker.invoke(
            ToolRequest(
                tool_name=tool_name,
                arguments=dict(arguments),
                metadata={"actor": "jarvis_context_composer", "phase": phase},
                invocation_id=f"context-{uuid4().hex}",
            )
        )


__all__ = ["RepositoryContext", "RepositoryContextComposer"]
