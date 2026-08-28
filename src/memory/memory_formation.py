"""
JARVIS Memory Formation Engine.

Memory Formation converts explicit user statements from a conversation
into structured memory candidates, asks a MemoryDecisionService what
should happen to each candidate, and delegates the resulting mutation
to a MemoryDecisionExecutor.

Pipeline:

    User Statement
        |
    Candidate Extraction
        |
    Validation
        |
    Existing Memory Lookup
        |
    Memory Decision Service
        |
    Memory Decision
        |
    Memory Decision Executor
        |
    Memory / Evidence Store

Important boundaries:

    - Candidate extraction does not mutate the database.
    - Decision providers do not mutate the database.
    - The decision service does not mutate the database.
    - The executor is the mutation boundary.
    - Assistant responses are never treated as DIRECT evidence.
"""


from dataclasses import dataclass
import re

from src.memory.memory_decision import (
    MemoryDecisionService,
)

from src.memory.memory_decision_executor import (
    MemoryDecisionExecutor,
)

from src.memory.memory_decision_models import (
    CREATE,
    CONFIRM,
    UPDATE,
    CONTRADICT,
    IGNORE,
    MemoryDecisionContext,
)

from src.memory.providers.deterministic_memory_decision import (
    DeterministicMemoryDecisionProvider,
)

from src.memory.memory_models import (
    CandidateMemory,
)

from src.memory.memory_retrieval import (
    get_memory,
    search_memories,
)

from src.memory.memory_validator import (
    validate_memory,
)

DEFAULT_CONFIDENCE = 0.85
DEFAULT_IMPORTANCE = 0.50

DIRECT_EVIDENCE_TYPE = "DIRECT"

REPEATED_EVIDENCE_TYPE = "REPEATED"


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
    Describes one candidate's formation outcome.
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

    memories_updated: int = 0

    memories_contradicted: int = 0

    memories_ignored: int = 0

    evidence_added: int = 0

    details: tuple[FormationDetail, ...] = ()

    errors: tuple[str, ...] = ()


# ---------------------------------------------------------------------
# Normalization helpers
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

    return key.strip("_")


def _normalize_subject(text: str) -> str:
    """
    Normalize a candidate subject.
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


def _normalize_content(text: str) -> str:
    """
    Normalize memory content without destroying terminal punctuation.
    """

    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def _meaningful_tokens(
    text: str,
) -> set[str]:
    """
    Return useful alphanumeric tokens from text.
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
        "user",
        "still",
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


def _split_sentences(
    text: str,
) -> list[str]:
    """
    Split a user message into deterministic statement units.
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
# Extraction rules
# ---------------------------------------------------------------------


_SKILL_RULES = (
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:(?:currently|still)\s+)?"
            r"learning\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is learning {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:(?:currently|still)\s+)?"
            r"studying\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is studying {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:(?:currently|still)\s+)?"
            r"using\s+(.+)$",
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
            r"(?:(?:currently|still)\s+)?"
            r"building\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is building {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:(?:currently|still)\s+)?"
            r"developing\s+(.+)$",
            re.IGNORECASE,
        ),
        lambda subject:
            f"User is developing {subject}.",
    ),
    (
        re.compile(
            r"^(?:i\s+am|i'm)\s+"
            r"(?:(?:currently|still)\s+)?"
            r"working\s+on\s+(.+)$",
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
# Candidate construction
# ---------------------------------------------------------------------


def _build_memory_key(
    category: str,
    subject: str,
    suffix: str,
) -> str:
    """
    Build a deterministic candidate memory key.

    Category is intentionally not included in the current key because
    legacy memory keys and semantic matching already define identity.
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

    subject = _normalize_subject(
        subject
    )

    content = _normalize_content(
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
        evidence_text=evidence_text.strip(),
        evidence_type=DIRECT_EVIDENCE_TYPE,
        source_role="user",
    )


def _extract_candidate_from_sentence(
    sentence: str,
) -> CandidateMemory | None:

    sentence = sentence.strip()

    if not sentence:
        return None

    for (
        category,
        suffix,
        rules,
    ) in RULE_GROUPS:

        for (
            pattern,
            builder,
        ) in rules:

            match = pattern.match(
                sentence
            )

            if match is None:
                continue

            subject = _normalize_subject(
                match.group(1)
            )

            if not subject:
                return None

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

    assistant_response is accepted for API compatibility and future
    analysis, but is intentionally ignored for direct evidence.
    """

    if not isinstance(
        user_query,
        str,
    ):
        return []

    candidates = []

    seen_keys = set()

    for sentence in _split_sentences(
        user_query
    ):

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
# Existing-memory lookup
# ---------------------------------------------------------------------


def _find_existing_memory(
    candidate: CandidateMemory,
):
    """
    Find an existing ACTIVE memory.

    Always returns:

        MemoryResult | None

    Exact memory-key matches are preferred.

    Semantic matching compares the full candidate claim against
    existing memory content so that a more-specific candidate can
    still identify the older, less-specific memory.
    """

    # ---------------------------------------------------------
    # 1. Exact memory-key lookup
    # ---------------------------------------------------------

    exact = get_memory(
        candidate.memory_key
    )

    if exact is not None:
        return exact

    # ---------------------------------------------------------
    # 2. Semantic search
    # ---------------------------------------------------------

    candidate_tokens = _meaningful_tokens(
        candidate.content
    )

    if not candidate_tokens:
        return None

    search_results = search_memories(
        candidate.content,
        limit=10,
    )

    best_match = None
    best_score = 0.0

    for result in search_results:

        if result.category != candidate.category:
            continue

        existing_tokens = _meaningful_tokens(
            result.content
        )

        if not existing_tokens:
            continue

        shared_tokens = (
            candidate_tokens
            & existing_tokens
        )

        if not shared_tokens:
            continue

        candidate_coverage = (
            len(shared_tokens)
            / len(candidate_tokens)
        )

        existing_coverage = (
            len(shared_tokens)
            / len(existing_tokens)
        )

        # -----------------------------------------------------
        # Strong match in either direction:
        #
        # 1. Candidate is mostly represented by existing
        # 2. Existing is fully represented by candidate
        #
        # The second case is critical for UPDATE.
        # -----------------------------------------------------

        if (
            candidate_coverage >= 0.80
            or existing_coverage >= 0.80
        ):

            score = max(
                candidate_coverage,
                existing_coverage,
            )

            if score > best_score:

                best_score = score
                best_match = result

    return best_match

def _formation_action_name(
    decision_action: str,
) -> str:
    """
    Translate canonical MemoryDecision actions into the
    historical FormationDetail action vocabulary.
    """

    return {
        CREATE: "created",
        CONFIRM: "deduplicated",
        UPDATE: "updated",
        CONTRADICT: "contradicted",
        IGNORE: "ignored",
    }.get(
        decision_action,
        "failed",
    )


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------


def _validate_candidate(
    candidate: CandidateMemory,
):
    """
    Validate a candidate before asking the decision layer
    what should happen to it.
    """

    return validate_memory({
        "content": candidate.content,
        "category": candidate.category,
        "confidence": candidate.confidence,
        "importance": candidate.importance,
        "status": "CANDIDATE",
    })


# ---------------------------------------------------------------------
# Default decision stack
# ---------------------------------------------------------------------


def _build_default_decision_service():
    """
    Construct the default deterministic decision stack.

    This is kept in a helper so callers can inject a different
    provider later without changing Memory Formation.
    """

    service = MemoryDecisionService(
        default_provider="deterministic"
    )

    service.register_provider(
        DeterministicMemoryDecisionProvider()
    )

    return service


# ---------------------------------------------------------------------
# Formation pipeline
# ---------------------------------------------------------------------


def process_turn(
    user_query: str,
    assistant_response: str | None,
    conversation_id: str | None = None,
    message_id: str | None = None,
    source_created_at: str | None = None,
    decision_service: MemoryDecisionService | None = None,
    executor: MemoryDecisionExecutor | None = None,
    decision_provider: str | None = None,
) -> FormationResult:
    """
    Process one completed conversation turn.

    The architecture is:

        extraction
            ->
        validation
            ->
        existing-memory lookup
            ->
        decision service
            ->
        decision
            ->
        executor

    The assistant response is never treated as DIRECT evidence.
    """

    candidates = extract_candidates(
        user_query=user_query,
        assistant_response=assistant_response,
    )

    if not candidates:
        return FormationResult()

    if decision_service is None:
        decision_service = (
            _build_default_decision_service()
        )

    if executor is None:
        executor = MemoryDecisionExecutor()

    memories_created = 0

    memories_deduplicated = 0

    memories_updated = 0

    memories_contradicted = 0

    memories_ignored = 0

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

        decision_context = (
            MemoryDecisionContext(
                candidate=candidate,
                existing_memory=existing,
            )
        )

        try:

            decision = (
                decision_service.decide(
                    decision_context,
                    provider_name=(
                        decision_provider
                    ),
                )
            )

        except Exception as exc:

            error_message = (
                "Memory decision failed for "
                f"{candidate.memory_key}: "
                f"{exc}"
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

        try:

            execution = executor.execute(
                decision=decision,
                conversation_id=(
                    conversation_id
                ),
                message_id=message_id,
                source_created_at=(
                    source_created_at
                ),
            )

        except Exception as exc:

            error_message = (
                "Memory execution failed for "
                f"{candidate.memory_key}: "
                f"{exc}"
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
                    memory_id=(
                        decision.memory_id
                    ),
                    errors=(
                        error_message,
                    ),
                )
            )

            continue

        action = decision.action

        if action == CREATE:

            if execution.status == "SUCCESS":

                memories_created += 1

            else:

                errors.append(
                    execution.reason
                )

        elif action == CONFIRM:

            if execution.status == "SUCCESS":

                memories_deduplicated += 1

            else:

                errors.append(
                    execution.reason
                )

        elif action == UPDATE:

            if execution.status == "SUCCESS":

                memories_updated += 1

            else:

                errors.append(
                    execution.reason
                )

        elif action == CONTRADICT:

            if execution.status == "SUCCESS":

                memories_contradicted += 1

            else:

                errors.append(
                    execution.reason
                )

        elif action == IGNORE:

            memories_ignored += 1

        if execution.evidence_id is not None:

            evidence_added += 1

        detail_errors = ()

        if execution.status == "FAILED":

            detail_errors = (
                execution.reason,
            )

        details.append(
            FormationDetail(
                action=_formation_action_name(
                    decision.action
                ),
                memory_key=candidate.memory_key,
                memory_id=(
                        execution.memory_id
                        or decision.memory_id
                ),
                errors=detail_errors,
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
        memories_updated=(
            memories_updated
        ),
        memories_contradicted=(
            memories_contradicted
        ),
        memories_ignored=(
            memories_ignored
        ),
        evidence_added=evidence_added,
        details=tuple(details),
        errors=tuple(errors),
    )