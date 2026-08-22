from src.context.models import (
    ContextItem,
    ContextOptions,
    ContextPackage,
    MEMORY,
    EVIDENCE,
    HISTORY,
    PRIVATE,
)

from src.memory.memory_retrieval import (
    search_memories,
    get_memory_with_evidence,
)


DEFAULT_INSTRUCTIONS = (
    "Treat stored memories as claims rather than unquestionable truth.",
    "Use confidence and evidence when evaluating stored information.",
    "Do not invent information that is absent from the provided context.",
    "Distinguish source information from derived information.",
)


def _build_memory_item(memory):
    """
    Convert a MemoryResult into a ContextItem.
    """

    return ContextItem(
        source_type=MEMORY,
        content=memory.content,
        relevance_score=memory.relevance_score,
        confidence=memory.confidence,
        importance=memory.importance,
        privacy_level=PRIVATE,
        provenance={
            "memory_id": memory.memory_id,
            "memory_key": memory.memory_key,
            "category": memory.category,
            "status": memory.status,
        },
    )


def _build_evidence_item(evidence):
    """
    Convert a memory_evidence database row into a ContextItem.

    Evidence row layout:

    0 = id
    1 = memory_id
    2 = conversation_id
    3 = message_id
    4 = evidence_text
    5 = evidence_type
    6 = confidence
    7 = source_created_at
    8 = created_at
    """

    return ContextItem(
        source_type=EVIDENCE,
        content=evidence[4],
        confidence=evidence[6],
        privacy_level=PRIVATE,
        provenance={
            "evidence_id": evidence[0],
            "memory_id": evidence[1],
            "conversation_id": evidence[2],
            "message_id": evidence[3],
            "evidence_type": evidence[5],
            "source_created_at": evidence[7],
            "created_at": evidence[8],
        },
    )


def _normalize_history_item(item):
    """
    Convert externally supplied history into a ContextItem.

    History retrieval is intentionally not implemented here yet.
    Context Builder can accept history supplied by a future
    history-retrieval layer.
    """

    if isinstance(item, ContextItem):
        return item

    return ContextItem(
        source_type=HISTORY,
        content=str(item["content"]),
        relevance_score=float(
            item.get("relevance_score", 0.0)
        ),
        confidence=item.get("confidence"),
        importance=item.get("importance"),
        privacy_level=item.get(
            "privacy_level",
            PRIVATE
        ),
        provenance=item.get(
            "provenance",
            {}
        ),
    )


def build_context(
    query,
    options=None,
    history_items=None,
):
    """
    Build a provider-neutral ContextPackage.

    This function is READ-ONLY.

    It does not:
        - modify memories
        - modify evidence
        - call an AI
        - call an external provider
    """

    if options is None:
        options = ContextOptions()

    query = query.strip()

    items = []

    memories = []

    if options.include_memories and query:

        memories = search_memories(
            query,
            limit=options.max_memories
        )

        for memory in memories:

            items.append(
                _build_memory_item(memory)
            )

    evidence_count = 0

    if (
        options.include_evidence
        and memories
        and options.max_evidence > 0
    ):

        for memory in memories:

            remaining = (
                options.max_evidence
                - evidence_count
            )

            if remaining <= 0:
                break

            memory_with_evidence = (
                get_memory_with_evidence(
                    memory.memory_id
                )
            )

            if memory_with_evidence is None:
                continue

            for evidence in (
                memory_with_evidence.evidence
            ):

                if evidence_count >= options.max_evidence:
                    break

                items.append(
                    _build_evidence_item(evidence)
                )

                evidence_count += 1

    history_count = 0

    if options.include_history and history_items:

        for history_item in history_items:

            if history_count >= options.max_history:
                break

            item = _normalize_history_item(
                history_item
            )

            items.append(item)

            history_count += 1

    metadata = {
        "builder_version": "1.0",
        "memory_count": sum(
            1
            for item in items
            if item.source_type == MEMORY
        ),
        "evidence_count": sum(
            1
            for item in items
            if item.source_type == EVIDENCE
        ),
        "history_count": sum(
            1
            for item in items
            if item.source_type == HISTORY
        ),
        "source_types": sorted(
            {
                item.source_type
                for item in items
            }
        ),
    }

    return ContextPackage(
        request=query,
        items=tuple(items),
        instructions=DEFAULT_INSTRUCTIONS,
        metadata=metadata,
    )