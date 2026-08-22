from dataclasses import dataclass
import re

from src.database import get_connection


@dataclass
class MemoryResult:
    """
    A structured representation of a JARVIS memory.
    """

    memory_id: int
    memory_key: str
    content: str
    category: str
    confidence: float
    importance: float
    status: str
    relevance_score: float = 0.0
    evidence: list = None

    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []


def _build_memory_result(row, relevance_score=0.0, evidence=None):
    """
    Convert a database row into a MemoryResult.
    """

    return MemoryResult(
        memory_id=row[0],
        memory_key=row[1],
        content=row[2],
        category=row[3],
        confidence=row[4],
        importance=row[5],
        status=row[6],
        relevance_score=relevance_score,
        evidence=evidence or []
    )


def get_memory(memory_key):
    """
    Retrieve one ACTIVE memory using its exact memory key.

    Returns:
        MemoryResult | None
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory_key,
            content,
            category,
            confidence,
            importance,
            status
        FROM memories
        WHERE memory_key = ?
          AND status = 'ACTIVE'
        LIMIT 1
    """, (memory_key,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return _build_memory_result(row)


def get_memories_by_category(category):
    """
    Retrieve all ACTIVE memories belonging to a category.

    Returns:
        list[MemoryResult]
    """

    category = category.strip().upper()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory_key,
            content,
            category,
            confidence,
            importance,
            status
        FROM memories
        WHERE category = ?
          AND status = 'ACTIVE'
        ORDER BY importance DESC, confidence DESC
    """, (category,))

    rows = cursor.fetchall()

    connection.close()

    return [
        _build_memory_result(row)
        for row in rows
    ]


def _calculate_relevance(query, memory):
    """
    Calculate deterministic text relevance.

    V1 does not use embeddings or AI.

    Returns:
        float between 0.0 and 1.0
    """

    query = query.strip().casefold()

    if not query:
        return 0.0

    searchable_text = " ".join([
        memory[1],
        memory[2],
        memory[3]
    ]).casefold()

    # Exact phrase match gets maximum relevance.
    if query in searchable_text:
        return 1.0

    query_tokens = set(
        re.findall(r"\b[\w-]+\b", query)
    )

    if not query_tokens:
        return 0.0

    matching_tokens = {
        token
        for token in query_tokens
        if token in searchable_text
    }

    return len(matching_tokens) / len(query_tokens)


def search_memories(query, limit=10):
    """
    Search ACTIVE memories using deterministic text relevance.

    Results are ranked by:
        1. Text relevance
        2. Importance
        3. Confidence

    Returns:
        list[MemoryResult]
    """

    query = query.strip()

    if not query:
        return []

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory_key,
            content,
            category,
            confidence,
            importance,
            status
        FROM memories
        WHERE status = 'ACTIVE'
    """)

    rows = cursor.fetchall()

    connection.close()

    results = []

    for row in rows:

        relevance = _calculate_relevance(
            query,
            row
        )

        if relevance <= 0:
            continue

        result = _build_memory_result(
            row,
            relevance_score=relevance
        )

        results.append(result)

    results.sort(
        key=lambda result: (
            result.relevance_score,
            result.importance,
            result.confidence
        ),
        reverse=True
    )

    return results[:limit]


def get_memory_with_evidence(memory_id):
    """
    Retrieve an ACTIVE memory together with all of its evidence.

    Returns:
        MemoryResult | None
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory_key,
            content,
            category,
            confidence,
            importance,
            status
        FROM memories
        WHERE id = ?
          AND status = 'ACTIVE'
        LIMIT 1
    """, (memory_id,))

    memory_row = cursor.fetchone()

    if memory_row is None:
        connection.close()
        return None

    cursor.execute("""
        SELECT
            id,
            memory_id,
            conversation_id,
            message_id,
            evidence_text,
            evidence_type,
            confidence,
            source_created_at,
            created_at
        FROM memory_evidence
        WHERE memory_id = ?
        ORDER BY created_at
    """, (memory_id,))

    evidence_rows = cursor.fetchall()

    connection.close()

    return _build_memory_result(
        memory_row,
        evidence=evidence_rows
    )