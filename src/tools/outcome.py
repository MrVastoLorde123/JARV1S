"""OPS-17 execution outcome evidence boundary.

Tool execution, external observation, and external verification are separate
states. A successful handler result proves only that the handler reported a
successful execution; it does not establish external state or truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .models import ToolRequest, ToolResult


class ToolExecutionState(str, Enum):
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class ExternalObservationState(str, Enum):
    NOT_OBSERVED = "NOT_OBSERVED"
    OBSERVED = "OBSERVED"


class ExternalVerificationState(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class VerificationFreshnessState(str, Enum):
    UNASSESSED = "UNASSESSED"
    FRESH = "FRESH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class ExternalOutcomeState(str, Enum):
    """Aggregate external-outcome claim state for a completed execution."""

    NOT_APPLICABLE = "NOT_APPLICABLE"
    EXECUTED_UNVERIFIED = "EXECUTED_UNVERIFIED"
    OBSERVED_UNVERIFIED = "OBSERVED_UNVERIFIED"
    VERIFIED = "VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class ExternalObservation:
    observation_id: str
    source: str
    subject_ref: str
    payload: Mapping[str, Any]
    observed_at: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name, value in (
            ("observation_id", self.observation_id),
            ("source", self.source),
            ("subject_ref", self.subject_ref),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.observed_at is not None and (
            not isinstance(self.observed_at, str) or not self.observed_at.strip()
        ):
            raise ValueError("observed_at must be a non-empty string or None")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))


@dataclass(frozen=True)
class ExternalVerification:
    verification_id: str
    observation_id: str
    verifier: str
    passed: bool | None
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name, value in (
            ("verification_id", self.verification_id),
            ("observation_id", self.observation_id),
            ("verifier", self.verifier),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.passed is not None and not isinstance(self.passed, bool):
            raise TypeError("passed must be bool or None")
        if any(not isinstance(ref, str) or not ref.strip() for ref in self.evidence_refs):
            raise TypeError("evidence_refs must contain non-empty strings")


@dataclass(frozen=True)
class ToolOutcome:
    outcome_id: str
    tool_name: str
    invocation_id: str | None
    target_ref: str
    execution_state: ToolExecutionState
    observation_state: ExternalObservationState
    verification_state: ExternalVerificationState
    execution_result: ToolResult
    observation: ExternalObservation | None = None
    verification: ExternalVerification | None = None
    freshness_state: VerificationFreshnessState = VerificationFreshnessState.UNASSESSED
    truth_established: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("outcome_id", self.outcome_id),
            ("tool_name", self.tool_name),
            ("target_ref", self.target_ref),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        if not isinstance(self.execution_state, ToolExecutionState):
            raise TypeError("execution_state must be a ToolExecutionState")
        if not isinstance(self.observation_state, ExternalObservationState):
            raise TypeError("observation_state must be an ExternalObservationState")
        if not isinstance(self.verification_state, ExternalVerificationState):
            raise TypeError("verification_state must be an ExternalVerificationState")
        if not isinstance(self.freshness_state, VerificationFreshnessState):
            raise TypeError("freshness_state must be a VerificationFreshnessState")
        if not isinstance(self.execution_result, ToolResult):
            raise TypeError("execution_result must be a ToolResult")
        if self.observation is not None and not isinstance(self.observation, ExternalObservation):
            raise TypeError("observation must be an ExternalObservation or None")
        if self.verification is not None and not isinstance(self.verification, ExternalVerification):
            raise TypeError("verification must be an ExternalVerification or None")
        if self.observation_state is ExternalObservationState.NOT_OBSERVED and self.observation is not None:
            raise ValueError("NOT_OBSERVED outcomes cannot contain an observation")
        if self.observation_state is ExternalObservationState.OBSERVED and self.observation is None:
            raise ValueError("OBSERVED outcomes require an observation")
        if self.verification_state is not ExternalVerificationState.UNVERIFIED and self.verification is None:
            raise ValueError("non-UNVERIFIED outcomes require verification evidence")
        if self.verification is not None and self.observation is None:
            raise ValueError("verification requires an external observation")
        if self.truth_established:
            raise ValueError("ToolOutcome cannot establish truth")

    @property
    def executed(self) -> bool:
        return self.execution_state is ToolExecutionState.EXECUTED

    @property
    def observed(self) -> bool:
        return self.observation_state is ExternalObservationState.OBSERVED

    @property
    def verified(self) -> bool:
        return self.verification_state is ExternalVerificationState.VERIFIED

    def to_context(self) -> dict[str, object]:
        return {
            "tool_outcome_id": self.outcome_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "target_ref": self.target_ref,
            "execution_state": self.execution_state.value,
            "observation_state": self.observation_state.value,
            "verification_state": self.verification_state.value,
            "verification_freshness_state": self.freshness_state.value,
            "external_outcome_state": ToolOutcomeService.aggregate((self,)).value,
            "executed": self.executed,
            "observed": self.observed,
            "verified": self.verified,
            "truth_established": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "verification_evidence_refs": (
                () if self.verification is None else self.verification.evidence_refs
            ),
        }


    @staticmethod
    def aggregate(outcomes: tuple[ToolOutcome, ...] | list[ToolOutcome]) -> ExternalOutcomeState:
        """Aggregate tool evidence without converting it into truth."""
        if not isinstance(outcomes, (tuple, list)):
            raise TypeError("outcomes must be a tuple or list of ToolOutcome")
        if not outcomes:
            return ExternalOutcomeState.NOT_APPLICABLE
        if any(not isinstance(outcome, ToolOutcome) for outcome in outcomes):
            raise TypeError("outcomes must contain only ToolOutcome values")

        states = {outcome.verification_state for outcome in outcomes}
        if ExternalVerificationState.CONTRADICTED in states:
            return ExternalOutcomeState.CONTRADICTED
        if ExternalVerificationState.INCONCLUSIVE in states:
            return ExternalOutcomeState.INCONCLUSIVE
        if states == {ExternalVerificationState.VERIFIED}:
            return ExternalOutcomeState.VERIFIED
        if any(
            outcome.observation_state is ExternalObservationState.OBSERVED
            for outcome in outcomes
        ):
            return ExternalOutcomeState.OBSERVED_UNVERIFIED
        return ExternalOutcomeState.EXECUTED_UNVERIFIED


class ToolOutcomeService:
    """Create and advance inert execution/outcome evidence."""

    @staticmethod
    def classify(request: ToolRequest, result: ToolResult) -> ToolOutcome:
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")
        if not isinstance(result, ToolResult):
            raise TypeError("result must be a ToolResult")
        if request.tool_name.strip().lower() != result.tool_name.strip().lower():
            raise ValueError("request and result tool identities must match")
        if (
            result.invocation_id is not None
            and request.invocation_id is not None
            and request.invocation_id != result.invocation_id
        ):
            raise ValueError("request and result invocation identities conflict")

        execution_invocation_id = (
            request.invocation_id
            if request.invocation_id is not None
            else result.invocation_id
        )

        execution_state = (
            ToolExecutionState.EXECUTED
            if result.success
            else ToolExecutionState.FAILED
        )
        target_payload = {
            "tool_name": request.tool_name.strip().lower(),
            "arguments": dict(request.arguments),
        }
        target_encoded = json.dumps(
            target_payload,
            sort_keys=True,
            separators=(",", ":"),
            default=repr,
        ).encode("utf-8")
        target_ref = f"tool-target-{hashlib.sha256(target_encoded).hexdigest()[:24]}"

        payload = {
            "tool_name": request.tool_name.strip().lower(),
            "invocation_id": execution_invocation_id,
            "target_ref": target_ref,
            "execution_state": execution_state.value,
            "success": result.success,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        outcome_id = f"tool-outcome-{hashlib.sha256(encoded).hexdigest()[:24]}"
        return ToolOutcome(
            outcome_id=outcome_id,
            tool_name=result.tool_name,
            invocation_id=execution_invocation_id,
            target_ref=target_ref,
            execution_state=execution_state,
            observation_state=ExternalObservationState.NOT_OBSERVED,
            verification_state=ExternalVerificationState.UNVERIFIED,
            execution_result=result,
        )

    @staticmethod
    def observe(
        outcome: ToolOutcome,
        observation: ExternalObservation,
    ) -> ToolOutcome:
        if not isinstance(outcome, ToolOutcome):
            raise TypeError("outcome must be a ToolOutcome")
        if not isinstance(observation, ExternalObservation):
            raise TypeError("observation must be an ExternalObservation")
        return ToolOutcome(
            outcome_id=outcome.outcome_id,
            tool_name=outcome.tool_name,
            invocation_id=outcome.invocation_id,
            target_ref=outcome.target_ref,
            execution_state=outcome.execution_state,
            observation_state=ExternalObservationState.OBSERVED,
            verification_state=outcome.verification_state,
            execution_result=outcome.execution_result,
            observation=observation,
            verification=outcome.verification,
            freshness_state=outcome.freshness_state,
        )

    @staticmethod
    def assess_freshness(
        outcome: ToolOutcome,
        *,
        as_of: str,
        max_age_seconds: float,
    ) -> ToolOutcome:
        if not isinstance(outcome, ToolOutcome):
            raise TypeError("outcome must be a ToolOutcome")
        if not outcome.observed or outcome.observation is None:
            raise ValueError("freshness requires an external observation")
        if not isinstance(as_of, str) or not as_of.strip():
            raise ValueError("as_of must be a non-empty ISO timestamp")
        if (
            isinstance(max_age_seconds, bool)
            or not isinstance(max_age_seconds, (int, float))
            or max_age_seconds < 0
        ):
            raise ValueError("max_age_seconds must be a non-negative number")

        observed_at = outcome.observation.observed_at
        if observed_at is None:
            freshness = VerificationFreshnessState.UNKNOWN
        else:
            try:
                observed_dt = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
                as_of_dt = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError("observed_at and as_of must be valid ISO timestamps") from exc

            if observed_dt.tzinfo is None:
                observed_dt = observed_dt.replace(tzinfo=timezone.utc)
            if as_of_dt.tzinfo is None:
                as_of_dt = as_of_dt.replace(tzinfo=timezone.utc)

            age_seconds = (as_of_dt - observed_dt).total_seconds()
            if age_seconds < 0:
                freshness = VerificationFreshnessState.UNKNOWN
            elif age_seconds <= float(max_age_seconds):
                freshness = VerificationFreshnessState.FRESH
            else:
                freshness = VerificationFreshnessState.STALE

        return ToolOutcome(
            outcome_id=outcome.outcome_id,
            tool_name=outcome.tool_name,
            invocation_id=outcome.invocation_id,
            target_ref=outcome.target_ref,
            execution_state=outcome.execution_state,
            observation_state=outcome.observation_state,
            verification_state=outcome.verification_state,
            execution_result=outcome.execution_result,
            observation=outcome.observation,
            verification=outcome.verification,
            freshness_state=freshness,
        )

    @staticmethod
    def verify(
        outcome: ToolOutcome,
        verification: ExternalVerification,
    ) -> ToolOutcome:
        if not isinstance(outcome, ToolOutcome):
            raise TypeError("outcome must be a ToolOutcome")
        if not outcome.observed or outcome.observation is None:
            raise ValueError("external verification requires an observed outcome")
        if outcome.observation.subject_ref != outcome.target_ref:
            raise ValueError("external observation is scoped to a different execution target")
        if not isinstance(verification, ExternalVerification):
            raise TypeError("verification must be an ExternalVerification")
        if verification.observation_id != outcome.observation.observation_id:
            raise ValueError("verification must reference the exact observation identity")

        state = (
            ExternalVerificationState.VERIFIED
            if verification.passed is True
            else (
                ExternalVerificationState.CONTRADICTED
                if verification.passed is False
                else ExternalVerificationState.INCONCLUSIVE
            )
        )
        return ToolOutcome(
            outcome_id=outcome.outcome_id,
            tool_name=outcome.tool_name,
            invocation_id=outcome.invocation_id,
            target_ref=outcome.target_ref,
            execution_state=outcome.execution_state,
            observation_state=outcome.observation_state,
            verification_state=state,
            execution_result=outcome.execution_result,
            observation=outcome.observation,
            verification=verification,
            freshness_state=VerificationFreshnessState.UNASSESSED,
        )


__all__ = [
    "ExternalObservation",
    "ExternalObservationState",
    "ExternalVerification",
    "ExternalVerificationState",
    "ExternalOutcomeState",
    "ToolExecutionState",
    "ToolOutcome",
    "ToolOutcomeService",
]
