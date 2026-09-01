"""Provider-neutral capability selection.

Selection proposes a capability. It does not construct or execute a
ToolRequest and therefore cannot cross the execution safety boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

from src.tools.models import ToolDefinition


@dataclass(frozen=True)
class CapabilityCandidate:
    """One proposed capability with a deterministic relevance score."""

    capability: ToolDefinition
    score: float
    reason: str


@dataclass(frozen=True)
class CapabilitySelection:
    """Read-only selection result for a natural-language intent."""

    query: str
    candidates: tuple[CapabilityCandidate, ...]

    @property
    def best(self) -> CapabilityCandidate | None:
        return self.candidates[0] if self.candidates else None


@runtime_checkable
class CapabilitySelector(Protocol):
    """Contract for anything that ranks available capabilities."""

    def select(
        self,
        query: str,
        capabilities: Sequence[ToolDefinition],
    ) -> CapabilitySelection:
        """Return ranked capability candidates without executing anything."""
        ...


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in value.lower().replace("_", " ").split()
        if token
    }


class DeterministicCapabilitySelector:
    """Small dependency-free selector used as a safe V1 fallback.

    It ranks capabilities using token overlap across the capability name and
    description. It is intentionally simple and deterministic; a future model-
    backed selector can implement the same ``CapabilitySelector`` contract.
    """

    def select(
        self,
        query: str,
        capabilities: Sequence[ToolDefinition],
    ) -> CapabilitySelection:
        if not isinstance(query, str):
            raise TypeError("query must be a string")
        if not query.strip():
            raise ValueError("query cannot be empty")

        definitions = tuple(capabilities)
        if not all(isinstance(item, ToolDefinition) for item in definitions):
            raise TypeError("capabilities must contain only ToolDefinition values")

        query_tokens = _tokens(query)
        ranked: list[CapabilityCandidate] = []

        for definition in definitions:
            name_tokens = _tokens(definition.name)
            description_tokens = _tokens(definition.description)
            name_overlap = len(query_tokens & name_tokens)
            description_overlap = len(query_tokens & description_tokens)
            score = float((name_overlap * 2) + description_overlap)
            if score <= 0:
                continue

            reason = (
                f"Matched {name_overlap} name token(s) and "
                f"{description_overlap} description token(s)."
            )
            ranked.append(
                CapabilityCandidate(
                    capability=definition,
                    score=score,
                    reason=reason,
                )
            )

        ranked.sort(
            key=lambda candidate: (
                -candidate.score,
                candidate.capability.name.strip().lower(),
            )
        )

        return CapabilitySelection(
            query=query,
            candidates=tuple(ranked),
        )
