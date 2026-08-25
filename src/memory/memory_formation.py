"""
JARVIS Memory Formation Engine

This module is responsible for converting conversation turns
into structured memories.

Memory Formation is the point where JARVIS stops merely
retrieving knowledge and starts maintaining its own
structured knowledge base under explicit rules.

Pipeline:

    Conversation Turn
        |
    Candidate Extraction
        |
    Validation
        |
    Deduplication
        |
    Memory Store + Evidence Store
"""

from dataclasses import dataclass, field
from typing import Any

from src.memory.memory_validator import (
    validate_memory,
    VALID_CATEGORIES,
)

from src.memory.memory_retrieval import (
    get_memory,
)

from src.memory.memory_store import (
    add_memory,
    find_active_memory,
)

from src.memory.evidence_store import (
    add_evidence,
)


# -----------------------------------------------------------------
# Extraction Rules
# -----------------------------------------------------------------
#
# V1 uses deterministic keyword-based extraction.
#
# Each rule maps a trigger pattern to a memory category.
# The extraction engine scans the assistant response for
# these patterns and produces candidate memories.
#
# This approach is intentionally conservative.
# It is better to miss a memory than to create a false one.
# -----------------------------------------------------------------

EXTRACTION_RULES = (

    {
        "keywords": (
            "user is learning",
            "user is studying",
            "user is working on",
            "user is building",
            "user is developing",
            "user is using",
            "user is practicing",
        ),
        "category": "SKILL",
    },

    {
        "keywords": (
            "user's goal",
            "user wants to",
            "user intends to",
            "user plans to",
        ),
        "category": "GOAL",
    },

    {
        "keywords": (
            "user prefers",
            "user likes",
            "user wants",
            "user chose",
            "user's preference",
        ),
        "category": "PREFERENCE",
    },

    {
        "keywords": (
            "user's project",
            "user is building",
            "user is developing",
            "user is creating",
            "the project",
        ),
        "category": "PROJECT",
    },

    {
        "keywords": (
            "user works at",
            "user lives in",
            "user's name",
            "user is from",
            "user's age",
            "user was born",
        ),
        "category": "PERSONAL",
    },

    {
        "keywords": (
            "user's workflow",
            "user typically",
            "user usually",
            "user always",
        ),
        "category": "WORKFLOW",
    },

)


# -----------------------------------------------------------------
# Candidate Memory
# -----------------------------------------------------------------

@dataclass
class CandidateMemory:
    """
    A potential memory extracted from a conversation turn.

    Candidate memories are validated and deduplicated before
    being persisted.
    """

    content: str
    category: str
    memory_key: str

    confidence: float = 0.7
    importance: float = 0.5

    evidence_text: str = ""
    evidence_type: str = "DIRECT"

    source_turn: str = ""


# -----------------------------------------------------------------
# Formation Result
# -----------------------------------------------------------------

@dataclass(frozen=True)
class FormationResult:
    """
    The outcome of processing a conversation turn
    through the memory formation pipeline.
    """

    candidates_extracted: int = 0
    memories_created: int = 0
    memories_deduplicated: int = 0
    evidence_added: int = 0

    details: tuple = ()


# -----------------------------------------------------------------
# Extraction
# -----------------------------------------------------------------

def _normalize_key(text):
    """
    Create a memory key from a text fragment.

    Keys are lowercase, underscore-separated identifiers
    used for deduplication.
    """

    key = text.strip().casefold()

    key = (
        key.replace(" ", "_")
        .replace("-", "_")
        .replace(".", "")
        .replace(",", "")
        .replace("'", "")
        .replace("\"", "")
    )

    # Collapse multiple underscores.
    while "__" in key:
        key = key.replace("__", "_")

    # Remove leading/trailing underscores.
    key = key.strip("_")

    return key


def _extract_claim(line, keyword):
    """
    Extract the meaningful claim from a line
    that matched a keyword trigger.

    Returns the portion of the line starting
    from the keyword match.
    """

    lower = line.casefold()
    position = lower.find(keyword)

    if position < 0:
        return ""

    claim = line[position:].strip()

    # Remove trailing periods for cleaner storage.
    if claim.endswith("."):
        claim = claim[:-1].strip()

    return claim


def extract_candidates(
    user_query,
    assistant_response,
):
    """
    Scan a conversation turn and extract candidate memories.

    V1 extraction is rule-based and conservative.
    Only explicit statements matching known patterns
    are extracted.

    Returns:
        list[CandidateMemory]
    """

    if not assistant_response or not assistant_response.strip():
        return []

    candidates = []

    lines = assistant_response.strip().splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        lower_line = line.casefold()

        for rule in EXTRACTION_RULES:

            for keyword in rule["keywords"]:

                if keyword not in lower_line:
                    continue

                claim = _extract_claim(
                    line,
                    keyword,
                )

                if len(claim) < 10:
                    continue

                memory_key = _normalize_key(claim)

                if not memory_key:
                    continue

                candidate = CandidateMemory(
                    content=claim,
                    category=rule["category"],
                    memory_key=memory_key,
                    confidence=0.7,
                    importance=0.5,
                    evidence_text=line,
                    evidence_type="DIRECT",
                    source_turn=user_query,
                )

                candidates.append(candidate)

                # One match per line is enough.
                break

            else:
                continue

            break

    return candidates


# -----------------------------------------------------------------
# Formation Engine
# -----------------------------------------------------------------

def process_turn(
    user_query,
    assistant_response,
    conversation_id=None,
    message_id=None,
):
    """
    Run the full memory formation pipeline on a single
    conversation turn.

    Steps:

        1. Extract candidates from the assistant response.
        2. Validate each candidate.
        3. Deduplicate against existing active memories.
        4. Persist new memories with evidence.

    Returns:
        FormationResult
    """

    candidates = extract_candidates(
        user_query,
        assistant_response,
    )

    if not candidates:
        return FormationResult()

    created = 0
    deduplicated = 0
    evidence_count = 0
    details = []

    for candidate in candidates:

        # ---------------------------------------------------------
        # Step 1 — Validate
        # ---------------------------------------------------------

        validation = validate_memory({
            "content": candidate.content,
            "category": candidate.category,
            "confidence": candidate.confidence,
            "importance": candidate.importance,
            "status": "CANDIDATE",
        })

        if not validation["valid"]:
            details.append({
                "action": "rejected",
                "memory_key": candidate.memory_key,
                "errors": validation["errors"],
            })
            continue

        # ---------------------------------------------------------
        # Step 2 — Deduplication
        # ---------------------------------------------------------

        existing = find_active_memory(
            candidate.memory_key,
        )

        if existing is not None:

            # Memory already exists.
            # Add corroborating evidence instead.

            existing_id = existing[0]

            if candidate.evidence_text:

                evidence_id = add_evidence(
                    memory_id=existing_id,
                    evidence_text=candidate.evidence_text,
                    evidence_type="CORROBORATING",
                    confidence=candidate.confidence,
                    conversation_id=conversation_id,
                    message_id=message_id,
                )

                if evidence_id is not None:
                    evidence_count += 1

            deduplicated += 1

            details.append({
                "action": "deduplicated",
                "memory_key": candidate.memory_key,
                "existing_memory_id": existing_id,
            })

            continue

        # ---------------------------------------------------------
        # Step 3 — Persist
        # ---------------------------------------------------------

        memory_id = add_memory(
            content=candidate.content,
            category=candidate.category,
            memory_key=candidate.memory_key,
            confidence=candidate.confidence,
            importance=candidate.importance,
            status="ACTIVE",
        )

        if memory_id is None:
            details.append({
                "action": "failed",
                "memory_key": candidate.memory_key,
            })
            continue

        created += 1

        # ---------------------------------------------------------
        # Step 4 — Evidence
        # ---------------------------------------------------------

        if candidate.evidence_text:

            evidence_id = add_evidence(
                memory_id=memory_id,
                evidence_text=candidate.evidence_text,
                evidence_type=candidate.evidence_type,
                confidence=candidate.confidence,
                conversation_id=conversation_id,
                message_id=message_id,
            )

            if evidence_id is not None:
                evidence_count += 1

        details.append({
            "action": "created",
            "memory_key": candidate.memory_key,
            "memory_id": memory_id,
        })

    return FormationResult(
        candidates_extracted=len(candidates),
        memories_created=created,
        memories_deduplicated=deduplicated,
        evidence_added=evidence_count,
        details=tuple(details),
    )
