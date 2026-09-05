"""Typed composition for existing JARVIS boundary services.

M23.1 does not introduce a new authority layer. It provides a small,
provider-neutral mechanism for composing already-defined boundary services
without silently changing their contracts. Composition validates exact type
continuity, preserves deterministic stage order, and fails closed on invalid
inputs or stage outputs.

The composer never retries, skips, authorizes, executes, revokes, mutates
memory, or infers permission. Those responsibilities remain with the
individual boundaries that are composed.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any


class BoundaryCompositionError(RuntimeError):
    """Raised when a boundary pipeline cannot be composed or completed."""


@dataclass(frozen=True)
class BoundaryStageSpec:
    """One explicitly typed boundary stage."""

    name: str
    input_type: type[Any]
    output_type: type[Any]
    handler: Callable[[Any], Any]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise BoundaryCompositionError("stage name must be a non-empty string")
        if not isinstance(self.input_type, type):
            raise BoundaryCompositionError("stage input_type must be a type")
        if not isinstance(self.output_type, type):
            raise BoundaryCompositionError("stage output_type must be a type")
        if not callable(self.handler):
            raise BoundaryCompositionError("stage handler must be callable")


@dataclass(frozen=True)
class BoundaryStageObservation:
    """Immutable evidence that one stage completed."""

    index: int
    name: str
    input_type: str
    output_type: str


@dataclass(frozen=True)
class BoundaryCompositionResult:
    """Immutable record of a successful composition run."""

    initial_type: str
    final_value: Any
    stages: tuple[BoundaryStageObservation, ...]

    @property
    def stage_count(self) -> int:
        return len(self.stages)

    @property
    def completed(self) -> bool:
        return bool(self.stages)


@dataclass(frozen=True)
class BoundaryPipeline:
    """Deterministic typed composition of existing boundary stages."""

    stages: tuple[BoundaryStageSpec, ...]

    def __post_init__(self) -> None:
        if not self.stages:
            raise BoundaryCompositionError("pipeline must contain at least one stage")
        for index, stage in enumerate(self.stages):
            if not isinstance(stage, BoundaryStageSpec):
                raise BoundaryCompositionError("pipeline stages must be BoundaryStageSpec instances")
            if index == 0:
                continue
            previous = self.stages[index - 1]
            if previous.output_type is not stage.input_type:
                raise BoundaryCompositionError(
                    f"stage {stage.name!r} input type {stage.input_type.__name__} does not match "
                    f"previous stage {previous.name!r} output type {previous.output_type.__name__}"
                )

    @classmethod
    def from_stages(cls, stages: Sequence[BoundaryStageSpec]) -> "BoundaryPipeline":
        """Build a pipeline from an ordered sequence of explicit stages."""
        return cls(tuple(stages))

    def run(self, value: Any) -> BoundaryCompositionResult:
        """Run every stage exactly once in declaration order; fail closed on mismatch."""
        current = value
        observations: list[BoundaryStageObservation] = []

        for index, stage in enumerate(self.stages):
            if type(current) is not stage.input_type:
                raise BoundaryCompositionError(
                    f"stage {stage.name!r} expected {stage.input_type.__name__}, "
                    f"received {type(current).__name__}"
                )

            try:
                output = stage.handler(current)
            except Exception as exc:
                raise BoundaryCompositionError(
                    f"stage {stage.name!r} failed: {exc}"
                ) from exc

            if type(output) is not stage.output_type:
                raise BoundaryCompositionError(
                    f"stage {stage.name!r} returned {type(output).__name__}, "
                    f"expected {stage.output_type.__name__}"
                )

            observations.append(
                BoundaryStageObservation(
                    index=index,
                    name=stage.name,
                    input_type=stage.input_type.__name__,
                    output_type=stage.output_type.__name__,
                )
            )
            current = output

        return BoundaryCompositionResult(
            initial_type=type(value).__name__,
            final_value=current,
            stages=tuple(observations),
        )
