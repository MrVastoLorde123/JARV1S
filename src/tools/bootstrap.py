"""Convenience wiring for assembling the tool-layer stack."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Union

from .confirmation import ConfirmationProvider
from .gate import PolicyGate
from .handlers.list_directory import ListDirectoryHandler
from .handlers.read_file import ReadFileHandler
from .handlers.search_files import SearchFilesHandler
from .handlers.test_runner import TestRunnerHandler
from .handlers.write_file import WriteFileHandler
from .policy import DefaultPolicy, Policy
from .protocol import ToolHandler
from .registry import ToolRegistry
from .service import ToolService


@dataclass(frozen=True)
class ToolStack:
    """The assembled pieces of one wired tool-layer stack."""

    registry: ToolRegistry
    service: ToolService
    gate: PolicyGate


def build_tool_stack(
    handlers: Iterable[ToolHandler],
    *,
    registry: Optional[ToolRegistry] = None,
    policy: Optional[Policy] = None,
    confirmation_provider: Optional[ConfirmationProvider] = None,
) -> ToolStack:
    """Register handlers and wire registry, service, and policy gate."""
    registry = registry if registry is not None else ToolRegistry()
    for handler in handlers:
        registry.register(handler)

    service = ToolService(registry)
    gate = PolicyGate(
        registry,
        service,
        policy or DefaultPolicy(),
        confirmation_provider,
    )
    return ToolStack(registry=registry, service=service, gate=gate)


def build_workspace_tool_stack(
    base_dir: Union[str, Path],
    *,
    registry: Optional[ToolRegistry] = None,
    policy: Optional[Policy] = None,
    confirmation_provider: Optional[ConfirmationProvider] = None,
) -> ToolStack:
    """Build the standard workspace filesystem capability set."""
    handlers: list[ToolHandler] = [
        ReadFileHandler(base_dir),
        ListDirectoryHandler(base_dir),
        SearchFilesHandler(base_dir),
        WriteFileHandler(base_dir),
    ]
    return build_tool_stack(
        handlers,
        registry=registry,
        policy=policy,
        confirmation_provider=confirmation_provider,
    )


def build_local_development_tool_stack(
    base_dir: Union[str, Path],
    *,
    registry: Optional[ToolRegistry] = None,
    policy: Optional[Policy] = None,
    confirmation_provider: Optional[ConfirmationProvider] = None,
) -> ToolStack:
    """Build workspace tools plus the constrained repository test/build runner."""
    handlers: list[ToolHandler] = [
        ReadFileHandler(base_dir),
        ListDirectoryHandler(base_dir),
        SearchFilesHandler(base_dir),
        WriteFileHandler(base_dir),
        TestRunnerHandler(base_dir),
    ]
    return build_tool_stack(
        handlers,
        registry=registry,
        policy=policy,
        confirmation_provider=confirmation_provider,
    )
