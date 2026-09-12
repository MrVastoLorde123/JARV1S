"""Deterministic claim/evidence boundary for JARVIS.

This module records agent claims separately from independently produced evidence.
It is intentionally inert: it cannot execute tools, authorize actions, mutate
memory, or grant authority. A claim may be evaluated only from supplied evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping, Sequence
from types import MappingProxyType


class ClaimState(str, Enum):
    """Deterministic state of a claim after evidence evaluation."""

    PROPOSED = "PROPOSED"
    SUPPORTED = "SUPPORTED"
    VERIFIED = "VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"
    REJECTED = "REJECTED"


class EvidenceType(str, Enum):
    """Source class for independently inspectable evidence."""

    TOOL_OBSERVATION = "TOOL_OBSERVATION"
    FILESYSTEM_OBSERVATION = "FILESYSTEM_OBSERVATION"
    TEST_RESULT = "TEST_RESULT"
    BUILD_RESULT = "BUILD_RESULT"
    POLICY_DECISION = "POLICY_DECISION"
    PEER_REVIEW = "PEER_REVIEW"
    CONTRADICTION = "CONTRADICTION"


def _freeze(value: Any) -> Any:
    """Recursively freeze common JSON-like values for immutable records."""
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _canonical(value: Any) -> Any:
    """Convert frozen values back to canonical JSON-compatible structures."""
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    return value


def _digest(payload: Mapping[str, Any], prefix: str) -> str:
    encoded = json.dumps(
        _canonical(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(encoded).hexdigest()}"


@dataclass(frozen=True)
class Evidence:
    """An independently inspectable observation supplied to claim evaluation."""

    task_id: str
    source_type: EvidenceType
    payload: Mapping[str, Any]
    provenance: Mapping[str, Any]
    evidence_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(self.source_type, EvidenceType):
            raise TypeError("source_type must be an EvidenceType")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")

        frozen_payload = _freeze(self.payload)
        frozen_provenance = _freeze(self.provenance)
        object.__setattr__(self, "payload", frozen_payload)
        object.__setattr__(self, "provenance", frozen_provenance)

        expected_id = _digest(
            {
                "task_id": self.task_id,
                "source_type": self.source_type.value,
                "payload": frozen_payload,
                "provenance": frozen_provenance,
            },
            "evidence",
        )
        if self.evidence_id is not None and self.evidence_id != expected_id:
            raise ValueError("evidence_id does not match deterministic evidence identity")
        object.__setattr__(self, "evidence_id", expected_id)


@dataclass(frozen=True)
class Claim:
    """An agent-originated assertion awaiting deterministic evidence evaluation."""

    task_id: str
    actor: str
    payload: Mapping[str, Any]
    provenance: Mapping[str, Any]
    supporting_evidence_refs: tuple[str, ...] = ()
    verification_refs: tuple[str, ...] = ()
    state: ClaimState = ClaimState.PROPOSED
    claim_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(self.actor, str) or not self.actor.strip():
            raise ValueError("actor must be a non-empty string")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        if not isinstance(self.state, ClaimState):
            raise TypeError("state must be a ClaimState")
        if any(not isinstance(ref, str) or not ref for ref in self.supporting_evidence_refs):
            raise TypeError("supporting_evidence_refs must contain non-empty strings")
        if any(not isinstance(ref, str) or not ref for ref in self.verification_refs):
            raise TypeError("verification_refs must contain non-empty strings")

        frozen_payload = _freeze(self.payload)
        frozen_provenance = _freeze(self.provenance)
        object.__setattr__(self, "payload", frozen_payload)
        object.__setattr__(self, "provenance", frozen_provenance)

        expected_id = _digest(
            {
                "task_id": self.task_id,
                "actor": self.actor,
                "payload": frozen_payload,
                "provenance": frozen_provenance,
            },
            "claim",
        )
        if self.claim_id is not None and self.claim_id != expected_id:
            raise ValueError("claim_id does not match deterministic claim identity")
        object.__setattr__(self, "claim_id", expected_id)


@dataclass(frozen=True)
class ClaimEvaluation:
    """Deterministic evaluation result for one claim and supplied evidence."""

    claim: Claim
    state: ClaimState
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.claim, Claim):
            raise TypeError("claim must be a Claim")
        if not isinstance(self.state, ClaimState):
            raise TypeError("state must be a ClaimState")
        if any(not isinstance(ref, str) or not ref for ref in self.evidence_refs):
            raise TypeError("evidence_refs must contain non-empty strings")
        if any(not isinstance(ref, str) or not ref for ref in self.verification_refs):
            raise TypeError("verification_refs must contain non-empty strings")


class ClaimEvidenceEvaluator:
    """Apply deterministic evidence rules to an inert claim."""

    def evaluate(
        self,
        claim: Claim,
        evidence: Sequence[Evidence],
    ) -> ClaimEvaluation:
        if not isinstance(claim, Claim):
            raise TypeError("claim must be a Claim")
        if not isinstance(evidence, Sequence):
            raise TypeError("evidence must be a sequence")
        if any(not isinstance(item, Evidence) for item in evidence):
            raise TypeError("evidence must contain Evidence values")
        if any(item.task_id != claim.task_id for item in evidence):
            raise ValueError("evidence task_id must match claim task_id")

        evidence_refs = tuple(item.evidence_id for item in evidence)
        verification_refs = tuple(
            item.evidence_id
            for item in evidence
            if item.source_type in {EvidenceType.TEST_RESULT, EvidenceType.BUILD_RESULT}
        )

        if not evidence:
            state = ClaimState.UNKNOWN
        elif any(
            item.source_type == EvidenceType.CONTRADICTION
            or (
                item.source_type in {EvidenceType.TEST_RESULT, EvidenceType.BUILD_RESULT}
                and item.payload.get("passed") is False
            )
            for item in evidence
        ):
            state = ClaimState.CONTRADICTED
        elif any(
            item.source_type in {EvidenceType.TEST_RESULT, EvidenceType.BUILD_RESULT}
            and item.payload.get("passed") is True
            for item in evidence
        ):
            state = ClaimState.VERIFIED
        elif evidence:
            state = ClaimState.SUPPORTED
        else:
            state = ClaimState.UNKNOWN

        return ClaimEvaluation(
            claim=claim,
            state=state,
            evidence_refs=evidence_refs,
            verification_refs=verification_refs,
        )

    @staticmethod
    def accepted_claim(claim: Claim, evaluation: ClaimEvaluation) -> Claim:
        """Materialize an evaluated claim without granting any execution authority."""
        if evaluation.claim.claim_id != claim.claim_id:
            raise ValueError("evaluation does not belong to claim")
        return Claim(
            task_id=claim.task_id,
            actor=claim.actor,
            payload=claim.payload,
            provenance=claim.provenance,
            supporting_evidence_refs=evaluation.evidence_refs,
            verification_refs=evaluation.verification_refs,
            state=evaluation.state,
            claim_id=claim.claim_id,
        )


__all__ = [
    "Claim",
    "ClaimEvidenceEvaluator",
    "ClaimEvaluation",
    "ClaimState",
    "Evidence",
    "EvidenceType",
]
