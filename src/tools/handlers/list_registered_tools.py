"""``list_registered_tools``: the third real tool, and a deliberately
different shape than the first two.

``read_file`` and ``list_directory`` are both "read something scoped
to a base_dir" -- same failure modes, same safety pattern. This tool
has no filesystem access at all. Its only dependency is the
``ToolRegistry`` itself: it exists to let a caller (eventually JARVIS
core) discover what capabilities are currently available before
deciding what to do with them.

This is genuinely self-referential: once registered, this handler
appears in its own output. That's intentional, not a bug -- a
registry-introspection tool that couldn't see itself would be a
strange kind of blind spot. See the "chicken and egg" note on
``__init__`` for how construction order is handled.
"""

from __future__ import annotations

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..registry import ToolRegistry


class ListRegisteredToolsHandler:
    """Lists every tool currently registered in a ``ToolRegistry``."""

    TOOL_NAME = "list_registered_tools"

    def __init__(self, registry: ToolRegistry) -> None:
        """Bind to a registry.

        Note the construction order this implies: unlike
        ``ReadFileHandler``/``ListDirectoryHandler``, which are fully
        self-contained and only need a ``base_dir``, this handler
        needs a live reference to the very registry it will (usually)
        end up registered into. The caller must therefore:

            1. create the ``ToolRegistry``
            2. register any other handlers into it
            3. construct ``ListRegisteredToolsHandler(registry)``
            4. register *that* handler into the same registry

        ``bootstrap.build_tool_stack`` supports this via its optional
        ``registry=`` parameter, so an existing registry can be reused
        instead of a fresh one being created internally.
        """
        if not isinstance(registry, ToolRegistry):
            raise TypeError(
                f"registry must be a ToolRegistry, got {type(registry).__name__}"
            )
        self._registry = registry
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Lists every tool currently registered, with its description, "
                "version, risk level, and whether it requires confirmation. Has "
                "no filesystem or network access -- purely introspects the tool "
                "registry."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "include_metadata": {
                        "type": "boolean",
                        "description": (
                            "Include each tool's free-form metadata field in the "
                            "output. Off by default, since metadata is meant for "
                            "tooling/debugging, not necessarily for routine "
                            "listing."
                        ),
                        "default": False,
                    },
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "count": {"type": "integer"},
                    "tools": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "version": {"type": "string"},
                                "risk_level": {"type": "string"},
                                "requires_confirmation": {"type": "boolean"},
                                "metadata": {"type": "object"},
                            },
                        },
                    },
                },
            },
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            metadata={"category": "introspection", "read_only": True},
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        include_metadata = request.arguments.get("include_metadata", False)
        if not isinstance(include_metadata, bool):
            return self._failure(
                request, "invalid_argument", "argument 'include_metadata' must be a boolean"
            )

        tools = []
        for definition in self._registry.list_definitions():
            entry = {
                "name": definition.name,
                "description": definition.description,
                "version": definition.version,
                "risk_level": definition.risk_level.value,
                "requires_confirmation": definition.requires_confirmation,
            }
            if include_metadata:
                entry["metadata"] = dict(definition.metadata)
            tools.append(entry)

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={"count": len(tools), "tools": tools},
            invocation_id=request.invocation_id,
        )

    def _failure(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.TOOL_NAME,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
