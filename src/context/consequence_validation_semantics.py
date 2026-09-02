"""Deterministic validation semantics for proposed consequences.

M7.5 validates proposal structure and semantic boundaries without granting
authorization, selecting tools, invoking providers, or mutating state.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.interpretation_semantics import Interpretation
from src.context.prioritization_semantics import Prioritization
from src.context.proposed_consequence_semantics import (
    ProposedConsequence,
    ProposedConsequences,
)
from src.context.reasoning_semantics import ReasoningContext


class ConsequenceValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"


class ViolationSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class ConsequenceViolation:
    """A deterministic validation finding attached to a proposal."""

    code: str
    message: str
    severity: ViolationSeverity = ViolationSeverity.ERROR

    def __post_init__(self):
        if not isinstance(self.code, str) or not self.code.strip():
            raise ValueError("code must be a non-empty string.")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string.")
        if not isinstance(self.severity, ViolationSeverity):
            raise TypeError("severity must be a ViolationSeverity value.")

    def to_context(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
        }


@dataclass(frozen=True)
class ConsequenceValidation:
    """Validation result for one proposal; never an authorization decision."""

    request: str
    proposal_id: str
    status: ConsequenceValidationStatus
    violations: tuple[ConsequenceViolation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string.")
        if not isinstance(self.status, ConsequenceValidationStatus):
            raise TypeError("status must be a ConsequenceValidationStatus value.")
        if not isinstance(self.violations, tuple):
            raise TypeError("violations must be a tuple.")
        if any(not isinstance(item, ConsequenceViolation) for item in self.violations):
            raise TypeError("violations must contain ConsequenceViolation values.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")

        has_errors = any(
            violation.severity == ViolationSeverity.ERROR
            for violation in self.violations
        )
        if self.status == ConsequenceValidationStatus.VALID and has_errors:
            raise ValueError("valid validation cannot contain error violations.")
        if self.status == ConsequenceValidationStatus.INVALID and not has_errors:
            raise ValueError("invalid validation must contain an error violation.")

    @property
    def authorized(self) -> bool:
        """Validation never grants authorization."""
        return False

    def to_context(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "proposal_id": self.proposal_id,
            "status": self.status.value,
            "violations": tuple(item.to_context() for item in self.violations),
            "metadata": dict(self.metadata),
            "authorized": False,
        }


@dataclass(frozen=True)
class ConsequenceValidations:
    """Deterministic validation results for a proposal set."""

    request: str
    validations: tuple[ConsequenceValidation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.validations, tuple):
            raise TypeError("validations must be a tuple.")
        if any(not isinstance(item, ConsequenceValidation) for item in self.validations):
            raise TypeError("validations must contain ConsequenceValidation values.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        if any(item.request != self.request for item in self.validations):
            raise ValueError("validation request must match collection request.")

    @property
    def all_valid(self) -> bool:
        return all(
            item.status == ConsequenceValidationStatus.VALID
            for item in self.validations
        )

    def to_context(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "validations": tuple(item.to_context() for item in self.validations),
            "all_valid": self.all_valid,
            "metadata": dict(self.metadata),
        }


class ConsequenceValidationEngine:
    """Validate proposals without modifying them or granting execution authority."""

    _FORBIDDEN_KEYS = {"authorize", "authorization", "execute", "execution", "tool_handle"}

    def validate(
        self,
        reasoning_context: ReasoningContext,
        prioritization: Prioritization,
        proposal: ProposedConsequence,
        proposal_id: str,
        interpretation: Interpretation | None = None,
    ) -> ConsequenceValidation:
        violations: list[ConsequenceViolation] = []

        if not isinstance(reasoning_context, ReasoningContext):
            raise TypeError("reasoning_context must be a ReasoningContext.")
        if not isinstance(prioritization, Prioritization):
            raise TypeError("prioritization must be a Prioritization.")
        if not isinstance(proposal, ProposedConsequence):
            raise TypeError("proposal must be a ProposedConsequence.")
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string.")
        if interpretation is not None and not isinstance(interpretation, Interpretation):
            raise TypeError("interpretation must be an Interpretation or None.")

        if proposal.priority_target_id is not None:
            target_ids = {target.target_id for target in prioritization.targets}
            if proposal.priority_target_id not in target_ids:
                violations.append(
                    ConsequenceViolation(
                        "priority_target_unresolved",
                        "proposal priority target must reference the supplied prioritization.",
                    )
                )

        if any(
            ref.source_kind == "prioritization"
            and ref.source_id not in {target.target_id for target in prioritization.targets}
            for ref in proposal.support
        ):
            violations.append(
                ConsequenceViolation(
                    "support_reference_unresolved",
                    "proposal prioritization support must reference a known priority target.",
                )
            )

        if any(key in self._FORBIDDEN_KEYS for key in proposal.metadata):
            violations.append(
                ConsequenceViolation(
                    "forbidden_execution_control",
                    "proposal metadata contains authorization, execution, or tool-handle controls.",
                )
            )

        context = proposal.to_context()
        if context.get("epistemic_role") != "proposed":
            violations.append(
                ConsequenceViolation(
                    "invalid_epistemic_role",
                    "proposal serialization must preserve the proposed epistemic role.",
                )
            )
        if context.get("authorization") is not False:
            violations.append(
                ConsequenceViolation(
                    "authorization_boundary_violation",
                    "proposal serialization must never grant authorization.",
                )
            )

        status = (
            ConsequenceValidationStatus.INVALID
            if violations
            else ConsequenceValidationStatus.VALID
        )
        return ConsequenceValidation(
            request=reasoning_context.request,
            proposal_id=proposal_id,
            status=status,
            violations=tuple(violations),
            metadata={"validation_semantics": "m7.5"},
        )

    def validate_all(
        self,
        reasoning_context: ReasoningContext,
        prioritization: Prioritization,
        proposals: ProposedConsequences,
        interpretation: Interpretation | None = None,
    ) -> ConsequenceValidations:
        if not isinstance(reasoning_context, ReasoningContext):
            raise TypeError("reasoning_context must be a ReasoningContext.")
        if not isinstance(prioritization, Prioritization):
            raise TypeError("prioritization must be a Prioritization.")
        if not isinstance(proposals, ProposedConsequences):
            raise TypeError("proposals must be a ProposedConsequences.")
        if prioritization.request != reasoning_context.request:
            raise ValueError("prioritization request must match reasoning context request.")
        if proposals.request != reasoning_context.request:
            raise ValueError("proposals request must match reasoning context request.")
        if interpretation is not None and interpretation.request != reasoning_context.request:
            raise ValueError("interpretation request must match reasoning context request.")

        validations = tuple(
            self.validate(
                reasoning_context,
                prioritization,
                proposal,
                proposal_id=f"proposal:{index}",
                interpretation=interpretation,
            )
            for index, proposal in enumerate(proposals.proposals)
        )
        return ConsequenceValidations(
            request=proposals.request,
            validations=validations,
            metadata={"validation_semantics": "m7.5"},
        )
