"""Convenience wiring for assembling the tool-layer stack.

This module is intentionally separate from JARVIS core and is not
imported by it. It exists so that a caller (JARVIS core, a script, a
test) can get a fully-wired, safe-by-default stack for a given set of
handlers in one call, instead of hand-assembling
``ToolRegistry`` / ``ToolService`` / ``Policy`` / ``PolicyGate`` every
time. Wiring this into ``src/core/jarvis.py`` is a deliberate future
step, not done here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Union

from .confirmation import ConfirmationProvider
from .gate import PolicyGate
from .handlers.list_directory import ListDirectoryHandler
from .handlers.read_file import ReadFileHandler
from .handlers.search_files import SearchFilesHandler
from .handlers.write_file import WriteFileHandler
from .policy import DefaultPolicy, Policy
from .protocol import ToolHandler
from .registry import ToolRegistry
from .service import ToolService


@dataclass(frozen=True)
class ToolStack:
    """The assembled pieces of one wired tool-layer stack.

    ``gate`` is what JARVIS core should call (``gate.invoke(request)``)
    -- it's the only member that enforces policy and confirmation.
    ``registry`` and ``service`` are exposed too, since callers with a
    legitimate reason to bypass the confirmation boundary (e.g. tests)
    may want them directly, per the existing service-isolation design.
    """

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
    """Register ``handlers`` and wire a ``ToolStack`` around them.

    Args:
        handlers: Handlers to register, in the order given.
        registry: Use an existing ``ToolRegistry`` instead of creating
            a new one. Needed for handlers that introspect the
            registry itself (e.g. ``ListRegisteredToolsHandler``),
            which must be constructed *with* a registry reference
            before they can be registered into it -- the caller
            creates the registry, builds that handler against it, then
            passes both here. Defaults to a fresh ``ToolRegistry()``.
        policy: Defaults to ``DefaultPolicy()`` (LOW/MEDIUM risk
            allowed, HIGH/CRITICAL or ``requires_confirmation=True``
            gated on confirmation).
        confirmation_provider: Defaults to ``None``, which makes
            ``PolicyGate`` fall back to its own safe default
            (deny-by-default) -- see ``gate.py``.
    """
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
    read_file: Optional[ReadFileHandler] = None,
    list_directory: Optional[ListDirectoryHandler] = None,
    search_files: Optional[SearchFilesHandler] = None,
    write_file: Optional[WriteFileHandler] = None,
) -> ToolStack:
    """Build the standard workspace capability set in one call.

    The resulting stack contains the four filesystem capabilities that
    currently define the workspace subsystem: read, list, search, and
    write.  Callers do not need to know handler construction or
    registration details; policy and confirmation still belong to the
    shared ``PolicyGate`` created by ``build_tool_stack``.

    Optional handler overrides exist for advanced callers that need
    custom tool configuration while retaining the same composition
    boundary.
    """
    handlers: list[ToolHandler] = [
        read_file if read_file is not None else ReadFileHandler(base_dir),
        list_directory if list_directory is not None else ListDirectoryHandler(base_dir),
        search_files if search_files is not None else SearchFilesHandler(base_dir),
        write_file if write_file is not None else WriteFileHandler(base_dir),
    ]
    return build_tool_stack(
        handlers,
        registry=registry,
        policy=policy,
        confirmation_provider=confirmation_provider,
    )
