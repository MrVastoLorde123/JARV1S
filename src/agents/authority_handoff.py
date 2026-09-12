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
from types import MappingProxyType
from typing import Any, Mapping

from src.agents.consequence_gate import ConsequenceAction, ConsequenceDecision, ConsequenceKind


class AuthorityHandoffStatus(str, Enum):
    """Disposition of an M30 decision at the authority handoff boundary."""

    READY_FOR_AUTHORITY = "READY_FOR_AUTHORITY"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"
    BLOCKED = "BLOCKED"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _canonical(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(
            (_canonical(item) for item in value),
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
        )
    if isinstance(value, Enum):
        return value.value
    return value


def _handoff_id(
    decision: ConsequenceDecision,
    authority_target: str,
    authority_context: Mapping[str, Any],
) -> str:
    payload = {
        "claim_id": decision.claim_id,
        "task_id": decision.task_id,
        "consequence_kind": decision.consequence.kind.value,
        "consequence_id": decision.consequence.consequence_id,
        "consequence_metadata": decision.consequence.metadata,
        "action": decision.action.value,
        "reason": decision.reason,
        "evidence_refs": decision.evidence_refs,
        "verification_refs": decision.verification_refs,
        "authority_target": authority_target,
        "authority_context": authority_context,
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
    consequence_kind: ConsequenceKind
    consequence_id: str
    consequence_metadata: Mapping[str, object] | None
    authority_target: str
    authority_context: Mapping[str, object]
    status: AuthorityHandoffStatus
    reason: str
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.handoff_id, str) or not self.handoff_id.strip():
            raise ValueError("handoff_id must be a non-empty string")
        if not isinstance(self.claim_id, str) or not self.claim_id.strip():
            raise ValueError("claim_id must be a non-empty string")
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(self.consequence_kind, ConsequenceKind):
            raise TypeError("consequence_kind must be a ConsequenceKind")
        if not isinstance(self.consequence_id, str) or not self.consequence_id.strip():
            raise ValueError("consequence_id must be a non-empty string")
        if self.consequence_metadata is not None and not isinstance(self.consequence_metadata, Mapping):
            raise TypeError("consequence_metadata must be a mapping or None")
        if not isinstance(self.authority_target, str) or not self.authority_target.strip():
            raise ValueError("authority_target must be a non-empty string")
        if not isinstance(self.authority_context, Mapping):
            raise TypeError("authority_context must be a mapping")
        if not isinstance(self.status, AuthorityHandoffStatus):
            raise TypeError("status must be an AuthorityHandoffStatus")
        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")
        if any(not isinstance(ref, str) or not ref for ref in self.evidence_refs):
            raise TypeError("evidence_refs must contain non-empty strings")
        if any(not isinstance(ref, str) or not ref for ref in self.verification_refs):
            raise TypeError("verification_refs must contain non-empty strings")

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
        authority_context: Mapping[str, object] | None = None,
    ) -> AuthorityHandoffRequest:
        if not isinstance(decision, ConsequenceDecision):
            raise TypeError("decision must be a ConsequenceDecision")
        if not isinstance(authority_target, str) or not authority_target.strip():
            raise ValueError("authority_target must be a non-empty string")
        if authority_context is not None and not isinstance(authority_context, Mapping):
            raise TypeError("authority_context must be a mapping or None")

        frozen_context = _freeze(authority_context or {})
        if not isinstance(frozen_context, Mapping):
            raise TypeError("authority_context must freeze to a mapping")

        if decision.action is ConsequenceAction.ALLOW:
            status = AuthorityHandoffStatus.READY_FOR_AUTHORITY
            reason = "M30 eligibility satisfied; authority layer may evaluate authorization"
        elif decision.action is ConsequenceAction.REQUIRE_REVIEW:
            status = AuthorityHandoffStatus.REQUIRE_REVIEW
            reason = "M30 requires review before authority evaluation"
        else:
            status = AuthorityHandoffStatus.BLOCKED
            reason = "M30 blocked this consequence from reaching authority"

        consequence_metadata = _freeze(decision.consequence.metadata)
        return AuthorityHandoffRequest(
            handoff_id=_handoff_id(decision, authority_target, frozen_context),
            claim_id=decision.claim_id,
            task_id=decision.task_id,
            consequence_kind=decision.consequence.kind,
            consequence_id=decision.consequence.consequence_id,
            consequence_metadata=consequence_metadata,
            authority_target=authority_target,
            authority_context=frozen_context,
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
