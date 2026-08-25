"""
JARVIS Memory Formation Engine.

Memory Formation converts explicit user statements from a conversation
into structured, validated, deduplicated memories.

V1 is deliberately conservative.

The AI response is NOT treated as direct evidence for a memory.

Pipeline:

    User Statement
        |
    Candidate Extraction
        |
    Validation
        |
    Deduplication
        |
    Memory Store
        |
    Evidence Store

The user statement itself becomes DIRECT evidence.

Future versions may support AI-assisted candidate extraction, but any
AI-derived candidate must remain distinguishable from direct user evidence.
"""

from dataclasses import dataclass
import re

from src.memory.evidence_store import add_evidence
from src.memory.memory_retrieval import search_memories
from src.memory.memory_store import (
    add_memory,
    find_active_memory,
)
from src.memory.memory_validator import validate_memory


# ---------------------------------------------------------------------
# Formation Defaults
# ---------------------------------------------------------------------

DEFAULT_CONFIDENCE = 0.85
DEFAULT_IMPORTANCE = 0.50

DIRECT_EVIDENCE_TYPE = "DIRECT"
REPEATED_EVIDENCE_TYPE = "REPEATED"


# ---------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CandidateMemory:
    """
    A potential memory extracted from an explicit user statement.
    """

    content: str
    category: str
    memory_key: str

    subject: str

    confidence: float = DEFAULT_CONFIDENCE
    importance: float = DEFAULT_IMPORTANCE

    evidence_text: str = ""
    evidence_type: str = DIRECT_EVIDENCE_TYPE

    source_role: str = "user"


@dataclass(frozen=True)
class FormationDetail:
    """
    Describes one candidate's outcome.
    """

    action: str
    memory_key: str
    memory_id: int | None = None
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class FormationResult:
    """
    Result of processing one conversation turn.
    """

    candidates_extracted: int = 0
    memories_created: int = 0
    memories_deduplicated: int = 0
    evidence_added: int = 0

    details: tuple[FormationDetail, ...] = ()

    errors: tuple[str, ...] = ()


# ---------------------------------------------------------------------
# Text Helpers
# ---------------------------------------------------------------------


def _normalize_key(text: str) -> str:
    """
    Convert text into a stable identifier.

    Example:

        "PCVUE v17" -> "pcvue_v17"
    """

    key = text.strip().casefold()

    key = re.sub(
        r"[^a-z0-9]+",
        "_",
        key,
    )

    key = key.strip("_")

    return key


def _normalize_subject(text: str) -> str:
    """
    Normalize a candidate subject for storage and deduplication.
    """

    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    text = text.rstrip(
        ".,!?;:"
    )

    return text.strip()


def _meaningful_tokens(text: str) -> set[str]:
    """
    Return useful alphanumeric tokens from a subject.

    Very common conversational words are ignored.
    """

    stop_words = {
        "a",
        "an",
        "and",
        "for",
        "in",
        "is",
        "it",
        "my",
        "of",
        "on",
        "the",
        "to",
        "with",
    }

    tokens = re.findall(
        r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
        text.casefold(),
    )

    return {
        token
        for token in tokens
        if token not in stop_words
    }


def _split_sentences(text: str) -> list[str]:
    """
    Split a user message into individual statements.

    V1 deliberately uses simple deterministic splitting.
    """

    if not text or not text.strip():
        return []

    parts = re.split(
        r"(?:\r?\n+)|(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


# ---------------------------------------------------------------------
# Candidate Rule Definitions
# ---------------------------------------------------------------------


_SKILL_RULES = (
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:currently\s+)?learning\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is learning {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:currently\s+)?studying\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is studying {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:currently\s+)?using\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User uses {subject}.",
    ),
    (
        re.compile(
            r"^i\s+work\s+with\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User works with {subject}.",
    ),
)


_PROJECT_RULES = (
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:currently\s+)?building\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is building {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:currently\s+)?developing\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is developing {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:currently\s+)?working\s+on\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is working on {subject}.",
    ),
)


_PREFERENCE_RULES = (
    (
        re.compile(
            r"^i\s+prefer\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User prefers {subject}.",
    ),
    (
        re.compile(
            r"^i\s+like\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User likes {subject}.",
    ),
    (
        re.compile(
            r"^my\s+preference\s+is\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User's preference is {subject}.",
    ),
)


_GOAL_RULES = (
    (
        re.compile(
            r"^i\s+want\s+to\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User wants to {subject}.",
    ),
    (
        re.compile(
            r"^i\s+plan\s+to\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User plans to {subject}.",
    ),
    (
        re.compile(
            r"^i\s+intend\s+to\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User intends to {subject}.",
    ),
    (
        re.compile(
            r"^my\s+goal\s+is\s+to\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User's goal is to {subject}.",
    ),
)


_PERSONAL_RULES = (
    (
        re.compile(
            r"^my\s+name\s+is\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User's name is {subject}.",
    ),
    (
        re.compile(
            r"^i\s+live\s+in\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User lives in {subject}.",
    ),
    (
        re.compile(
            r"^i\s+work\s+at\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User works at {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+from\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is from {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(\d{1,3})\s+years?\s+old$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is {subject} years old.",
    ),
)


_WORKFLOW_RULES = (
    (
        re.compile(
            r"^i\s+usually\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User usually {subject}.",
    ),
    (
        re.compile(
            r"^i\s+typically\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User typically {subject}.",
    ),
    (
        re.compile(
            r"^i\s+always\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User always {subject}.",
    ),
)


RULE_GROUPS = (
    (
        "SKILL",
        "_skill",
        _SKILL_RULES,
    ),
    (
        "PROJECT",
        "_project",
        _PROJECT_RULES,
    ),
    (
        "PREFERENCE",
        "_preference",
        _PREFERENCE_RULES,
    ),
    (
        "GOAL",
        "_goal",
        _GOAL_RULES,
    ),
    (
        "PERSONAL",
        "_personal",
        _PERSONAL_RULES,
    ),
    (
        "WORKFLOW",
        "_workflow",
        _WORKFLOW_RULES,
    ),
)


# ---------------------------------------------------------------------
# Candidate Extraction
# ---------------------------------------------------------------------


def _build_memory_key(
    category: str,
    subject: str,
    suffix: str,
) -> str:
    """
    Build a deterministic candidate memory key.
    """

    normalized_subject = _normalize_key(
        subject
    )

    if not normalized_subject:
        return ""

    return (
        f"{normalized_subject}"
        f"{suffix}"
    )


def _build_candidate(
    category: str,
    suffix: str,
    subject: str,
    content: str,
    evidence_text: str,
) -> CandidateMemory | None:
    """
    Construct a candidate after basic normalization.
    """

    subject = _normalize_subject(
        subject
    )

    content = _normalize_subject(
        content
    )

    if not subject:
        return None

    if len(subject) < 2:
        return None

    memory_key = _build_memory_key(
        category,
        subject,
        suffix,
    )

    if not memory_key:
        return None

    return CandidateMemory(
        content=content,
        category=category,
        memory_key=memory_key,
        subject=subject,
        confidence=DEFAULT_CONFIDENCE,
        importance=DEFAULT_IMPORTANCE,
        evidence_text=(
            evidence_text.strip()
        ),
        evidence_type=DIRECT_EVIDENCE_TYPE,
        source_role="user",
    )


def _extract_candidate_from_sentence(
    sentence: str,
) -> CandidateMemory | None:
    """
    Attempt to extract one memory candidate from one
    explicit user statement.

    Only the first matching rule is used.
    """

    sentence = sentence.strip()

    if not sentence:
        return None

    for (
        category,
        suffix,
        rules,
    ) in RULE_GROUPS:

        for pattern, builder in rules:

            match = pattern.match(
                sentence
            )

            if match is None:
                continue

            subject = (
                match.group(1).strip()
            )

            content = builder(
                subject
            )

            return _build_candidate(
                category=category,
                suffix=suffix,
                subject=subject,
                content=content,
                evidence_text=sentence,
            )

    return None


def extract_candidates(
    user_query: str,
    assistant_response: str | None = None,
) -> list[CandidateMemory]:
    """
    Extract conservative memory candidates from the USER message.

    The assistant response is intentionally not used as direct
    evidence.

    It remains an argument because memory formation happens after
    a completed conversation turn and future versions may use the
    assistant response for separate reasoning.

    Returns:
        list[CandidateMemory]
    """

    if not isinstance(
        user_query,
        str,
    ):
        return []

    sentences = _split_sentences(
        user_query
    )

    candidates = []

    seen_keys = set()

    for sentence in sentences:

        candidate = (
            _extract_candidate_from_sentence(
                sentence
            )
        )

        if candidate is None:
            continue

        if candidate.memory_key in seen_keys:
            continue

        seen_keys.add(
            candidate.memory_key
        )

        candidates.append(
            candidate
        )

    return candidates


# ---------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------


def _find_existing_memory(
    candidate: CandidateMemory,
):
    """
    Find an existing active memory.

    Strategy:

    1. Exact memory-key match.
    2. Deterministic subject search within the same category.

    This allows a manually created memory such as:

        pcvue_skill

    to match a later automatically generated candidate whose
    generated key may be:

        pcvue_v17_skill
    """

    exact = find_active_memory(
        candidate.memory_key
    )

    if exact is not None:
        return exact

    subject_tokens = (
        _meaningful_tokens(
            candidate.subject
        )
    )

    if not subject_tokens:
        return None

    search_results = search_memories(
        candidate.subject,
        limit=10,
    )

    for result in search_results:

        if result.category != candidate.category:
            continue

        memory_tokens = (
            _meaningful_tokens(
                result.content
            )
        )

        if not memory_tokens:
            continue

        matching_tokens = (
            subject_tokens
            & memory_tokens
        )

        coverage = (
            len(matching_tokens)
            / len(subject_tokens)
        )

        if (
            coverage >= 0.8
            or subject_tokens.issubset(
                memory_tokens
            )
        ):
            return (
                result.memory_id,
                result.memory_key,
                result.content,
                result.category,
                result.confidence,
                result.importance,
                result.status,
            )

    return None


# ---------------------------------------------------------------------
# Formation
# ---------------------------------------------------------------------


def _validate_candidate(
    candidate: CandidateMemory,
):
    """
    Validate a candidate using the existing memory validator.
    """

    return validate_memory({
        "content": candidate.content,
        "category": candidate.category,
        "confidence": candidate.confidence,
        "importance": candidate.importance,
        "status": "CANDIDATE",
    })


def process_turn(
    user_query: str,
    assistant_response: str | None,
    conversation_id: str | None = None,
    message_id: str | None = None,
    source_created_at: str | None = None,
) -> FormationResult:
    """
    Process one completed conversation turn.

    Memory formation is based on explicit USER statements.

    Parameters:

        user_query:
            The user's message.

        assistant_response:
            The generated assistant response.

            This is not used as direct memory evidence.

        conversation_id:
            Optional persistent conversation ID.

            Only pass this when the conversation exists in the
            persistent conversations table.

        message_id:
            Optional persistent source message ID.

        source_created_at:
            Timestamp of the user's source message.
    """

    candidates = extract_candidates(
        user_query=user_query,
        assistant_response=assistant_response,
    )

    if not candidates:
        return FormationResult()

    memories_created = 0
    memories_deduplicated = 0
    evidence_added = 0

    details = []
    errors = []

    for candidate in candidates:

        validation = _validate_candidate(
            candidate
        )

        if not validation["valid"]:

            details.append(
                FormationDetail(
                    action="rejected",
                    memory_key=(
                        candidate.memory_key
                    ),
                    errors=tuple(
                        validation["errors"]
                    ),
                )
            )

            continue

        existing = _find_existing_memory(
            candidate
        )

        if existing is not None:

            existing_id = existing[0]

            evidence_id = add_evidence(
                memory_id=existing_id,
                evidence_text=(
                    candidate.evidence_text
                ),
                evidence_type=(
                    REPEATED_EVIDENCE_TYPE
                ),
                confidence=(
                    candidate.confidence
                ),
                conversation_id=(
                    conversation_id
                ),
                message_id=(
                    message_id
                ),
                source_created_at=(
                    source_created_at
                ),
            )

            if evidence_id is None:

                errors.append(
                    "Failed to add repeated "
                    f"evidence for "
                    f"{candidate.memory_key}."
                )

            else:

                evidence_added += 1

            memories_deduplicated += 1

            details.append(
                FormationDetail(
                    action="deduplicated",
                    memory_key=(
                        candidate.memory_key
                    ),
                    memory_id=existing_id,
                )
            )

            continue

        memory_id = add_memory(
            content=candidate.content,
            category=candidate.category,
            memory_key=candidate.memory_key,
            source_conversation_id=(
                conversation_id
            ),
            confidence=candidate.confidence,
            importance=candidate.importance,
            status="ACTIVE",
        )

        if memory_id is None:

            error_message = (
                "Failed to create memory "
                f"{candidate.memory_key}."
            )

            errors.append(
                error_message
            )

            details.append(
                FormationDetail(
                    action="failed",
                    memory_key=(
                        candidate.memory_key
                    ),
                    errors=(
                        error_message,
                    ),
                )
            )

            continue

        memories_created += 1

        evidence_id = add_evidence(
            memory_id=memory_id,
            evidence_text=(
                candidate.evidence_text
            ),
            evidence_type=(
                candidate.evidence_type
            ),
            confidence=(
                candidate.confidence
            ),
            conversation_id=(
                conversation_id
            ),
            message_id=(
                message_id
            ),
            source_created_at=(
                source_created_at
            ),
        )

        if evidence_id is None:

            errors.append(
                "Memory created but evidence "
                f"could not be stored for "
                f"{candidate.memory_key}."
            )

        else:

            evidence_added += 1

        details.append(
            FormationDetail(
                action="created",
                memory_key=(
                    candidate.memory_key
                ),
                memory_id=memory_id,
            )
        )

    return FormationResult(
        candidates_extracted=len(
            candidates
        ),
        memories_created=memories_created,
        memories_deduplicated=(
            memories_deduplicated
        ),
        evidence_added=evidence_added,
        details=tuple(details),
        errors=tuple(errors),
    )