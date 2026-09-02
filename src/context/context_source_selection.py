"""Deterministic policy for selecting persistent context sources.

This module intentionally does not retrieve, refresh, validate, authorize, or
execute anything. It decides which already-available persistent sources are
eligible for working context and whether each selected source requires an
explicit refresh before reuse.
"""

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Any


@dataclass(frozen=True)
class ContextSource:
    """A persistent context source available to the selector."""

    source_id: str
    source_type: str
    relevance_score: float = 0.0
    priority: int = 0
    enabled: bool = True
    persistent: bool = True
    last_refreshed_at: float | None = None
    refresh_interval_seconds: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.source_id, str) or not self.source_id.strip():
            raise ValueError("source_id must be a non-empty string.")
        if not isinstance(self.source_type, str) or not self.source_type.strip():
            raise ValueError("source_type must be a non-empty string.")
        if self.relevance_score < 0.0 or self.relevance_score > 1.0:
            raise ValueError("relevance_score must be between 0.0 and 1.0.")
        if self.refresh_interval_seconds is not None and self.refresh_interval_seconds < 0:
            raise ValueError("refresh_interval_seconds cannot be negative.")
        if self.last_refreshed_at is not None and self.last_refreshed_at < 0:
            raise ValueError("last_refreshed_at cannot be negative.")


@dataclass(frozen=True)
class ContextSourceDecision:
    """Deterministic selection decision for one persistent source."""

    source_id: str
    source_type: str
    selected: bool
    refresh_required: bool
    authority_allowed: bool
    reason: str


@dataclass(frozen=True)
class ContextSourceSelection:
    """Complete source-selection result for one working-context request."""

    request: str
    selected: tuple[ContextSourceDecision, ...]
    excluded: tuple[ContextSourceDecision, ...]
    refresh_required: tuple[str, ...]

    @property
    def selected_source_ids(self) -> tuple[str, ...]:
        return tuple(decision.source_id for decision in self.selected)

    @property
    def excluded_source_ids(self) -> tuple[str, ...]:
        return tuple(decision.source_id for decision in self.excluded)


class ContextSourceSelector:
    """Select eligible persistent sources without performing retrieval or refresh."""

    def __init__(
        self,
        *,
        minimum_relevance: float = 0.01,
        max_sources: int | None = None,
    ):
        if minimum_relevance < 0.0 or minimum_relevance > 1.0:
            raise ValueError("minimum_relevance must be between 0.0 and 1.0.")
        if max_sources is not None and max_sources <= 0:
            raise ValueError("max_sources must be positive when provided.")

        self.minimum_relevance = minimum_relevance
        self.max_sources = max_sources

    def select(
        self,
        request: str,
        sources: Iterable[ContextSource],
        *,
        now: float | None = None,
    ) -> ContextSourceSelection:
        """Select persistent sources deterministically.

        ``now`` is supplied by the caller so freshness is explicit and
        reproducible in tests. The selector never obtains current time itself.
        """

        if not isinstance(request, str):
            raise TypeError("request must be a string.")
        request = request.strip()
        if not request:
            raise ValueError("request cannot be empty.")

        source_list = tuple(sources)
        if any(not isinstance(source, ContextSource) for source in source_list):
            raise TypeError("sources must contain ContextSource values.")

        ordered = sorted(
            source_list,
            key=lambda source: (
                -source.relevance_score,
                -source.priority,
                source.source_id,
            ),
        )

        selected = []
        excluded = []
        refresh_required = []

        for source in ordered:
            decision = self._decide(source, now=now)
            if decision.selected:
                if self.max_sources is not None and len(selected) >= self.max_sources:
                    decision = ContextSourceDecision(
                        source_id=source.source_id,
                        source_type=source.source_type,
                        selected=False,
                        refresh_required=False,
                        authority_allowed=False,
                        reason="source_limit_reached",
                    )
                else:
                    selected.append(decision)
                    if decision.refresh_required:
                        refresh_required.append(source.source_id)

            if not decision.selected:
                excluded.append(decision)

        return ContextSourceSelection(
            request=request,
            selected=tuple(selected),
            excluded=tuple(excluded),
            refresh_required=tuple(refresh_required),
        )

    def _decide(
        self,
        source: ContextSource,
        *,
        now: float | None,
    ) -> ContextSourceDecision:
        if not source.enabled:
            return ContextSourceDecision(
                source.source_id,
                source.source_type,
                False,
                False,
                False,
                "source_disabled",
            )

        if not source.persistent:
            return ContextSourceDecision(
                source.source_id,
                source.source_type,
                False,
                False,
                False,
                "source_not_persistent",
            )

        if source.relevance_score < self.minimum_relevance:
            return ContextSourceDecision(
                source.source_id,
                source.source_type,
                False,
                False,
                False,
                "below_relevance_threshold",
            )

        stale = self._is_stale(source, now=now)
        if stale:
            return ContextSourceDecision(
                source.source_id,
                source.source_type,
                True,
                True,
                False,
                "refresh_required_before_authoritative_reuse",
            )

        return ContextSourceDecision(
            source.source_id,
            source.source_type,
            True,
            False,
            True,
            "selected",
        )

    @staticmethod
    def _is_stale(source: ContextSource, *, now: float | None) -> bool:
        if source.refresh_interval_seconds is None:
            return False
        if source.last_refreshed_at is None:
            return True
        if now is None:
            raise ValueError(
                "now is required when a source has a refresh interval."
            )
        return (now - source.last_refreshed_at) >= source.refresh_interval_seconds
