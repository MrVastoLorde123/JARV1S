"""M19.2 preference-context resolution.

This layer reads established memory records and converts relevant preference
memories into bounded personalization signals. It does not mutate memory,
change policy, grant authority, or authorize execution.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.memory.memory_retrieval import get_memory_with_evidence, search_memories

from .profile import PersonalizationProfile, PersonalizationSignal, build_profile


class PreferenceContextResolver:
    """Resolve relevant PREFERENCE memories into an immutable profile."""

    def __init__(
        self,
        *,
        searcher: Callable[..., list[Any]] = search_memories,
        loader: Callable[[int], Any] = get_memory_with_evidence,
    ) -> None:
        if not callable(searcher):
            raise TypeError("searcher must be callable")
        if not callable(loader):
            raise TypeError("loader must be callable")
        self._searcher = searcher
        self._loader = loader

    def resolve(
        self,
        query: str,
        *,
        profile_id: str = "personalization-profile",
        limit: int = 10,
    ) -> PersonalizationProfile:
        """Resolve preference memories relevant to one request."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an integer")
        if limit < 0:
            raise ValueError("limit cannot be negative")
        if limit == 0:
            return build_profile(profile_id, (), provenance={"query": query.strip()})

        memories = tuple(self._searcher(query.strip(), limit=limit))
        signals: list[PersonalizationSignal] = []

        for memory in memories:
            if str(getattr(memory, "category", "")).strip().upper() != "PREFERENCE":
                continue

            source_ids = [f"memory:{memory.memory_id}"]
            loaded = self._loader(memory.memory_id)
            evidence_count = 0
            if loaded is not None:
                for evidence in getattr(loaded, "evidence", ()):
                    evidence_id = evidence[0]
                    source_ids.append(f"evidence:{evidence_id}")
                    evidence_count += 1

            signals.append(
                PersonalizationSignal(
                    signal_id=f"preference:{memory.memory_id}",
                    category="PREFERENCE",
                    key=memory.memory_key,
                    value=memory.content,
                    confidence=memory.confidence,
                    importance=memory.importance,
                    source_ids=tuple(source_ids),
                    explicit_user_preference=True,
                    metadata={
                        "memory_id": memory.memory_id,
                        "memory_status": memory.status,
                        "relevance_score": memory.relevance_score,
                        "evidence_count": evidence_count,
                    },
                )
            )

        return build_profile(
            profile_id,
            tuple(signals),
            provenance={
                "query": query.strip(),
                "resolver": "m19.2",
                "candidate_count": len(memories),
                "preference_count": len(signals),
            },
        )


__all__ = ["PreferenceContextResolver"]
