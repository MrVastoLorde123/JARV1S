"""Deterministic handoff from evidence-eligible consequences to authority.

M31 consumes an M30 ``ConsequenceDecision`` and creates a provenance-preserving
handoff record for the existing authority/confirmation layer. It never grants
permission, invokes tools, changes policy, or executes the consequence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Mapping

from src.agents.consequence_gate import ConsequenceAction, ConsequenceDecision


class AuthorityHandoffStatus(str, Enum):
    """Disposition of an M30 decision at the authority handoff boundary."""

    READY_FOR_AUTHORITY = "READY_FOR_AUTHORITY"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"
    BLOCKED = "BLOCKED"


def _canonical(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_canonical(item) for item in value)
    if isinstance(value, Enum):
        return value.value
    return value


def _handoff_id(decision: ConsequenceDecision, authority_target: str) -> str:
    payload = {
        "claim_id": decision.claim_id,
        "task_id": decision.task_id,
        "consequence_kind": decision.consequence.kind.value,
        "consequence_id": decision.consequence.consequence_id,
        "metadata": decision.consequence.metadata,
        "action": decision.action.value,
        "reason": decision.reason,
        "evidence_refs": decision.evidence_refs,
        "verification_refs": decision.verification_refs,
        "authority_target": authority_target,
    }
    encoded = json.dumps(
        _canonical(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"authority-handoff-{hashlib.sha256(encoded).hexdigest()}"


@dataclass(frozen=True)
class AuthorityHandoffRequest:
    """A non-authorizing request handed to a separate authority layer."""

    handoff_id: str
    claim_id: str
    task_id: str
    consequence_id: str
    authority_target: str
    status: AuthorityHandoffStatus
    reason: str
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]

    @property
    def ready_for_authority(self) -> bool:
        return self.status is AuthorityHandoffStatus.READY_FOR_AUTHORITY

    @property
    def authorized(self) -> bool:
        """M31 never grants authorization."""
        return False


class AuthorityHandoffPolicy:
    """Translate bounded M30 eligibility into a non-authorizing handoff."""

    def handoff(
        self,
        decision: ConsequenceDecision,
        *,
        authority_target: str = "existing_authority",
    ) -> AuthorityHandoffRequest:
        if not isinstance(decision, ConsequenceDecision):
            raise TypeError("decision must be a ConsequenceDecision")
        if not isinstance(authority_target, str) or not authority_target.strip():
            raise ValueError("authority_target must be a non-empty string")

        if decision.action is ConsequenceAction.ALLOW:
            status = AuthorityHandoffStatus.READY_FOR_AUTHORITY
            reason = "M30 eligibility satisfied; authority layer may evaluate authorization"
        elif decision.action is ConsequenceAction.REQUIRE_REVIEW:
            status = AuthorityHandoffStatus.REQUIRE_REVIEW
            reason = "M30 requires review before authority evaluation"
        else:
            status = AuthorityHandoffStatus.BLOCKED
            reason = "M30 blocked this consequence from reaching authority"

        return AuthorityHandoffRequest(
            handoff_id=_handoff_id(decision, authority_target),
            claim_id=decision.claim_id,
            task_id=decision.task_id,
            consequence_id=decision.consequence.consequence_id,
            authority_target=authority_target,
            status=status,
            reason=reason,
            evidence_refs=decision.evidence_refs,
            verification_refs=decision.verification_refs,
        )


__all__ = [
    "AuthorityHandoffPolicy",
    "AuthorityHandoffRequest",
    "AuthorityHandoffStatus",
]
