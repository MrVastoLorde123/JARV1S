from typing import Iterable, Mapping

from src.context.context_source_provider import ContextSourceProvider
from src.context.context_source_selection import ContextSource
from src.context.models import ContextItem, EVIDENCE, MEMORY, PRIVATE
from src.memory.memory_retrieval import get_memory_with_evidence, search_memories


class MemoryContextSourceProvider(ContextSourceProvider):
    """Acquire deterministic memory-backed persistent context for the runtime."""

    def __init__(
        self,
        *,
        include_memories: bool = True,
        include_evidence: bool = True,
        max_memories: int = 10,
        max_evidence: int = 20,
    ):
        if max_memories < 0:
            raise ValueError("max_memories cannot be negative.")
        if max_evidence < 0:
            raise ValueError("max_evidence cannot be negative.")
        self.include_memories = include_memories
        self.include_evidence = include_evidence
        self.max_memories = max_memories
        self.max_evidence = max_evidence

    def get_sources(self, request: str) -> Iterable[ContextSource]:
        if not self.include_memories or self.max_memories == 0:
            return ()

        memories = search_memories(
            request,
            limit=self.max_memories,
        )

        return tuple(
            ContextSource(
                source_id=f"memory:{memory.memory_id}",
                source_type=MEMORY,
                relevance_score=memory.relevance_score,
                priority=int(round(memory.importance * 100)),
                persistent=True,
                metadata={
                    "memory_id": memory.memory_id,
                    "memory_key": memory.memory_key,
                    "category": memory.category,
                },
            )
            for memory in memories
        )

    def get_context_items(
        self,
        request: str,
        sources: Iterable[ContextSource],
    ) -> Mapping[str, ContextItem]:
        del request
        items: dict[str, ContextItem] = {}
        evidence_count = 0

        for source in sources:
            if source.source_type != MEMORY:
                continue

            memory_id = source.metadata.get("memory_id")
            if memory_id is None:
                continue

            memory = get_memory_with_evidence(int(memory_id))
            if memory is None:
                continue

            source_id = source.source_id
            items[source_id] = ContextItem(
                source_type=MEMORY,
                content=memory.content,
                relevance_score=source.relevance_score,
                confidence=memory.confidence,
                importance=memory.importance,
                privacy_level=PRIVATE,
                provenance={
                    "source_id": source_id,
                    "memory_id": memory.memory_id,
                    "memory_key": memory.memory_key,
                    "category": memory.category,
                    "status": memory.status,
                },
            )

            if not self.include_evidence or self.max_evidence == 0:
                continue

            for evidence in memory.evidence:
                if evidence_count >= self.max_evidence:
                    break
                evidence_item = ContextItem(
                    source_type=EVIDENCE,
                    content=evidence[4],
                    confidence=evidence[6],
                    privacy_level=PRIVATE,
                    provenance={
                        "source_id": source_id,
                        "evidence_id": evidence[0],
                        "memory_id": evidence[1],
                        "conversation_id": evidence[2],
                        "message_id": evidence[3],
                        "evidence_type": evidence[5],
                        "source_created_at": evidence[7],
                        "created_at": evidence[8],
                    },
                )
                evidence_key = f"{source_id}:evidence:{evidence[0]}"
                items[evidence_key] = evidence_item
                evidence_count += 1

        return items
