from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RequestType(str, Enum):
    """
    Top-level classification of an incoming JARVIS request.
    """

    CONVERSATION = "CONVERSATION"
    COMMAND = "COMMAND"
    TASK = "TASK"


class TaskType(str, Enum):
    """
    Broad task categories.

    V1 keeps this intentionally small.
    """

    INFORMATION = "INFORMATION"
    ACTION = "ACTION"
    TOOL = "TOOL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class TaskRequest:
    """
    Structured representation of a task-oriented request.
    """

    content: str

    task_type: TaskType = TaskType.UNKNOWN

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class RouteDecision:
    """
    Provider-neutral result of request routing.

    The router decides where the request should go.
    It does not execute the destination.
    """

    request_type: RequestType

    original_input: str

    command_name: str | None = None

    task: TaskRequest | None = None

    reason: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )