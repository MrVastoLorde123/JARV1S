"""M90: deterministic memory lifecycle and proposal-only consolidation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.core.memory_episodic import EpisodicMemory
from src.core.persistent_memory import MemoryLifecycle, PersistentMemoryRecord


_ALLOWED_TRANSITIONS: dict[MemoryLifecycle, frozenset[MemoryLifecycle]] = {
    MemoryLifecycle.CANDIDATE: frozenset({MemoryLifecycle.ACTIVE, MemoryLifecycle.ARCHIVED}),
    MemoryLifecycle.ACTIVE: frozenset({MemoryLifecycle.SUPERSEDED, MemoryLifecycle.ARCHIVED}),
    MemoryLifecycle.SUPERSEDED: frozenset({MemoryLifecycle.ARCHIVED}),
    MemoryLifecycle.ARCHIVED: frozenset(),
}


@dataclass(frozen=True)
class MemoryTransition:
    memory_id: str
    from_status: MemoryLifecycle
    to_status: MemoryLifecycle
    reason: str
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.memory_id, str) or not self.memory_id.strip():
            raise ValueError("memory_id must be a non-empty string")
        if not isinstance(self.from_status, MemoryLifecycle) or not isinstance(self.to_status, MemoryLifecycle):
            raise TypeError("statuses must be MemoryLifecycle values")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.evidence_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.evidence_ids
        ):
            raise TypeError("evidence_ids must be a tuple of non-empty strings")


def validate_transition(
    record: PersistentMemoryRecord,
    transition: MemoryTransition,
) -> tuple[str, ...]:
    if not isinstance(record, PersistentMemoryRecord):
        raise TypeError("record must be a PersistentMemoryRecord")
    if not isinstance(transition, MemoryTransition):
        raise TypeError("transition must be a MemoryTransition")
    errors: list[str] = []
    if record.memory_id != transition.memory_id:
        errors.append("transition memory id does not match record")
    if record.status is not transition.from_status:
        errors.append("transition source status does not match record")
    if transition.to_status not in _ALLOWED_TRANSITIONS[transition.from_status]:
        errors.append(
            f"invalid memory lifecycle transition: "
            f"{transition.from_status.value} -> {transition.to_status.value}"
        )
    if transition.from_status is transition.to_status:
        errors.append("memory lifecycle transition must change status")
    return tuple(errors)


@dataclass(frozen=True)
class ConsolidationProposal:
    proposal_id: str
    subject_id: str
    source_memory_ids: tuple[str, ...]
    proposed_kind: str
    proposed_content: str
    rationale: str
    confidence: float

    def __post_init__(self) -> None:
        for name in ("proposal_id", "subject_id", "proposed_kind", "proposed_content", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_memory_ids, tuple) or not self.source_memory_ids:
            raise ValueError("source_memory_ids must be a non-empty tuple")
        if any(not isinstance(item, str) or not item.strip() for item in self.source_memory_ids):
            raise TypeError("source_memory_ids must contain non-empty strings")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")



def propose_semantic_consolidation(
    episodes: Iterable[EpisodicMemory],
) -> tuple[ConsolidationProposal, ...]:
    """Derive semantic candidates from repeated episode summaries.

    The function is deterministic and proposal-only. It never mutates memory
    and never authorizes or executes any action.
    """

    grouped: dict[tuple[str, str, str], list[EpisodicMemory]] = {}
    for episode in episodes:
        if not isinstance(episode, EpisodicMemory):
            raise TypeError("episodes must contain EpisodicMemory values")
        key = (episode.subject_id, episode.event_type, episode.summary.strip().casefold())
        grouped.setdefault(key, []).append(episode)

    proposals: list[ConsolidationProposal] = []
    for index, ((subject_id, event_type, summary_key), items) in enumerate(sorted(grouped.items()), start=1):
        if len(items) < 2:
            continue
        memory_ids = tuple(item.memory_id for item in items)
        average_confidence = sum(float(item.confidence) for item in items) / len(items)
        proposals.append(
            ConsolidationProposal(
                proposal_id=f"consolidation-{index}",
                subject_id=subject_id,
                source_memory_ids=memory_ids,
                proposed_kind="SEMANTIC",
                proposed_content=items[0].summary,
                rationale=(
                    f"Repeated episodic evidence for event type '{event_type}' "
                    f"occurred {len(items)} times."
                ),
                confidence=min(1.0, average_confidence),
            )
        )

    return tuple(proposals)


__all__ = [
    "ConsolidationProposal",
    "MemoryTransition",
    "propose_semantic_consolidation",
    "validate_transition",
]
