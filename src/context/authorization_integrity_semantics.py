"""Deterministic integrity validation for authorization artifacts.

M7.9.1 verifies that an authorization decision remains bound to the exact
policy decision and, when required, the exact confirmation chain that justified
it. Integrity never executes, selects tools, invokes providers, or mutates state.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.authorization_semantics import AuthorizationDecision, AuthorizationStatus
from src.context.confirmation_integrity_semantics import ConfirmationIntegrity, ConfirmationIntegrityStatus
from src.context.confirmation_semantics import ConfirmationResult, ConfirmationStatus
from src.context.policy_evaluation_semantics import PolicyDecision, PolicyOutcome


class AuthorizationIntegrityStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"


@dataclass(frozen=True)
class AuthorizationIntegrityViolation:
    code: str
    message: str

    def __post_init__(self):
        if not isinstance(self.code, str) or not self.code.strip():
            raise ValueError("code must be a non-empty string.")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string.")

    def to_context(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class AuthorizationIntegrity:
    request: str
    authorization_id: str
    proposal_id: str
    validation_id: str
    policy_decision_id: str
    confirmation_id: str | None
    status: AuthorizationIntegrityStatus
    violations: tuple[AuthorizationIntegrityViolation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for field_name in (
            "request",
            "authorization_id",
            "proposal_id",
            "validation_id",
            "policy_decision_id",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        if self.confirmation_id is not None and (
            not isinstance(self.confirmation_id, str) or not self.confirmation_id.strip()
        ):
            raise ValueError("confirmation_id must be a non-empty string when provided.")
        if not isinstance(self.status, AuthorizationIntegrityStatus):
            raise TypeError("status must be an AuthorizationIntegrityStatus value.")
        if not isinstance(self.violations, tuple):
            raise TypeError("violations must be a tuple.")
        if any(not isinstance(item, AuthorizationIntegrityViolation) for item in self.violations):
            raise TypeError("violations must contain AuthorizationIntegrityViolation values.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        if self.status is AuthorizationIntegrityStatus.VALID and self.violations:
            raise ValueError("valid integrity cannot contain violations.")
        if self.status is AuthorizationIntegrityStatus.INVALID and not self.violations:
            raise ValueError("invalid integrity must contain a violation.")

    @property
    def intact(self) -> bool:
        return self.status is AuthorizationIntegrityStatus.VALID

    def to_context(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "authorization_id": self.authorization_id,
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
            "policy_decision_id": self.policy_decision_id,
            "confirmation_id": self.confirmation_id,
            "status": self.status.value,
            "intact": self.intact,
            "violations": tuple(item.to_context() for item in self.violations),
            "metadata": dict(self.metadata),
        }


class AuthorizationIntegrityValidator:
    def validate(
        self,
        policy_decision: PolicyDecision,
        authorization_decision: AuthorizationDecision,
        confirmation_result: ConfirmationResult | None = None,
        confirmation_integrity: ConfirmationIntegrity | None = None,
    ) -> AuthorizationIntegrity:
        if not isinstance(policy_decision, PolicyDecision):
            raise TypeError("policy_decision must be a PolicyDecision.")
        if not isinstance(authorization_decision, AuthorizationDecision):
            raise TypeError("authorization_decision must be an AuthorizationDecision.")
        if confirmation_result is not None and not isinstance(confirmation_result, ConfirmationResult):
            raise TypeError("confirmation_result must be a ConfirmationResult or None.")
        if confirmation_integrity is not None and not isinstance(confirmation_integrity, ConfirmationIntegrity):
            raise TypeError("confirmation_integrity must be a ConfirmationIntegrity or None.")

        violations: list[AuthorizationIntegrityViolation] = []

        expected = {
            "request": policy_decision.request,
            "proposal_id": policy_decision.proposal_id,
            "validation_id": policy_decision.validation_id,
            "policy_decision_id": policy_decision.policy_decision_id,
        }
        actual = {
            "request": authorization_decision.request,
            "proposal_id": authorization_decision.proposal_id,
            "validation_id": authorization_decision.validation_id,
            "policy_decision_id": authorization_decision.policy_decision_id,
        }
        for field_name, expected_value in expected.items():
            if actual[field_name] != expected_value:
                violations.append(
                    AuthorizationIntegrityViolation(
                        f"authorization_{field_name}_mismatch",
                        f"authorization {field_name} does not match the policy decision.",
                    )
                )

        if authorization_decision.status is AuthorizationStatus.AUTHORIZED:
            if policy_decision.outcome is PolicyOutcome.DENY:
                violations.append(
                    AuthorizationIntegrityViolation(
                        "authorized_denied_policy",
                        "authorized decision cannot be bound to a DENY policy outcome.",
                    )
                )
            elif policy_decision.outcome is PolicyOutcome.REQUIRE_CONFIRMATION:
                if confirmation_result is None or confirmation_integrity is None:
                    violations.append(
                        AuthorizationIntegrityViolation(
                            "missing_confirmation_chain",
                            "authorized confirmation-required decision must include confirmation artifacts.",
                        )
                    )
                else:
                    if confirmation_integrity.status is not ConfirmationIntegrityStatus.VALID:
                        violations.append(
                            AuthorizationIntegrityViolation(
                                "invalid_confirmation_integrity",
                                "authorized decision requires valid confirmation integrity.",
                            )
                        )
                    if confirmation_result.status is not ConfirmationStatus.CONFIRMED:
                        violations.append(
                            AuthorizationIntegrityViolation(
                                "unconfirmed_result",
                                "authorized decision requires an explicitly confirmed result.",
                            )
                        )
                    for field_name, expected_value in expected.items():
                        if getattr(confirmation_result, field_name) != expected_value:
                            violations.append(
                                AuthorizationIntegrityViolation(
                                    f"confirmation_{field_name}_mismatch",
                                    f"confirmation result {field_name} does not match the policy decision.",
                                )
                            )
                    if confirmation_result.confirmation_id != authorization_decision.confirmation_id:
                        violations.append(
                            AuthorizationIntegrityViolation(
                                "authorization_confirmation_id_mismatch",
                                "authorized decision confirmation_id must match the confirmed result.",
                            )
                        )
                    if (
                        confirmation_integrity.request != expected["request"]
                        or confirmation_integrity.proposal_id != expected["proposal_id"]
                        or confirmation_integrity.validation_id != expected["validation_id"]
                        or confirmation_integrity.policy_decision_id != expected["policy_decision_id"]
                    ):
                        violations.append(
                            AuthorizationIntegrityViolation(
                                "confirmation_integrity_chain_mismatch",
                                "confirmation integrity does not match the current policy decision.",
                            )
                        )
            elif policy_decision.outcome is PolicyOutcome.ALLOW:
                if authorization_decision.confirmation_id is not None:
                    violations.append(
                        AuthorizationIntegrityViolation(
                            "unexpected_confirmation",
                            "ALLOW authorization must not carry a confirmation identity.",
                        )
                    )
        else:
            if authorization_decision.confirmation_id is not None and policy_decision.outcome is PolicyOutcome.ALLOW:
                violations.append(
                    AuthorizationIntegrityViolation(
                        "denied_allow_confirmation",
                        "DENIED authorization for ALLOW policy must not carry confirmation identity.",
                    )
                )

        if confirmation_result is not None and authorization_decision.confirmation_id != confirmation_result.confirmation_id:
            violations.append(
                AuthorizationIntegrityViolation(
                    "confirmation_id_mismatch",
                    "supplied confirmation result must match authorization confirmation identity.",
                )
            )

        status = AuthorizationIntegrityStatus.INVALID if violations else AuthorizationIntegrityStatus.VALID
        return AuthorizationIntegrity(
            request=policy_decision.request,
            authorization_id=authorization_decision.authorization_id,
            proposal_id=policy_decision.proposal_id,
            validation_id=policy_decision.validation_id,
            policy_decision_id=policy_decision.policy_decision_id,
            confirmation_id=authorization_decision.confirmation_id,
            status=status,
            violations=tuple(violations),
            metadata={"authorization_integrity_semantics": "m7.9.1"},
        )
