from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CommandRequest:
    """
    Parsed representation of an explicit JARVIS command.

    Example:

        /DELETE pcvue_skill

    becomes:

        name="DELETE"
        arguments=("pcvue_skill",)
    """

    name: str

    arguments: tuple[str, ...] = ()

    raw_text: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class CommandResult:
    """
    Provider-neutral result returned by a command handler.
    """

    success: bool

    command: str

    message: str

    requires_confirmation: bool = False

    metadata: dict[str, Any] = field(
        default_factory=dict
    )