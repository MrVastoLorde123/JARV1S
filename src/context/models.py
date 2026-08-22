from dataclasses import dataclass, field
from typing import Any


MEMORY = "MEMORY"
EVIDENCE = "EVIDENCE"
HISTORY = "HISTORY"

PRIVATE = "PRIVATE"
INTERNAL = "INTERNAL"
PUBLIC = "PUBLIC"


@dataclass(frozen=True)
class ContextItem:
    """
    One piece of information placed into a ContextPackage.
    """

    source_type: str
    content: str

    relevance_score: float = 0.0
    confidence: float | None = None
    importance: float | None = None

    privacy_level: str = PRIVATE

    provenance: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class ContextOptions:
    """
    Controls what information Context Builder is allowed
    to include.
    """

    include_memories: bool = True
    include_evidence: bool = True
    include_history: bool = False

    max_memories: int = 10
    max_evidence: int = 20
    max_history: int = 30


@dataclass(frozen=True)
class ContextPackage:
    """
    Provider-neutral context prepared by JARVIS.
    """

    request: str
    items: tuple[ContextItem, ...]

    instructions: tuple[str, ...]

    metadata: dict[str, Any] = field(
        default_factory=dict
    )