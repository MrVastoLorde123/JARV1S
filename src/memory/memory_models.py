from dataclasses import dataclass


DEFAULT_CONFIDENCE = 0.85
DEFAULT_IMPORTANCE = 0.50

DIRECT_EVIDENCE_TYPE = "DIRECT"


@dataclass(frozen=True)
class CandidateMemory:
    """
    A potential memory extracted from a conversation.

    CandidateMemory is intentionally a data model.

    It does not:
        - access the database
        - make decisions
        - execute mutations
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