"""Deterministic policy evaluation for canonical policy inputs.

M7.7 turns validated policy facts into an explicit policy outcome without
executing, confirming, selecting tools, invoking providers, or mutating state.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.consequence_validation_semantics import ConsequenceValidationStatus
from src.context.policy_input_semantics import ActionEffect, PolicyInput


class PolicyOutcome(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_CONFIRMATION = "require_confirmation"


@dataclass(frozen=True)
class PolicyDecision:
    """Explicit policy outcome with provenance and no execution capability."""

    request: str
    proposal_id: str
    validation_id: str
    outcome: PolicyOutcome
    rule_id: str
    rationale: str
    confirmation_required: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)
    policy_decision_id: str = ""

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string.")
        if not isinstance(self.validation_id, str) or not self.validation_id.strip():
            raise ValueError("validation_id must be a non-empty string.")
        if not isinstance(self.outcome, PolicyOutcome):
            raise TypeError("outcome must be a PolicyOutcome value.")
        if not isinstance(self.rule_id, str) or not self.rule_id.strip():
            raise ValueError("rule_id must be a non-empty string.")
        if not isinstance(self.rationale, str) or not self.rationale.strip():
            raise ValueError("rationale must be a non-empty string.")
        if not isinstance(self.confirmation_required, bool):
            raise TypeError("confirmation_required must be a bool.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        if not isinstance(self.policy_decision_id, str):
            raise TypeError("policy_decision_id must be a string.")

        expected_confirmation = self.outcome is PolicyOutcome.REQUIRE_CONFIRMATION
        if self.confirmation_required != expected_confirmation:
            raise ValueError(
                "confirmation_required must match the REQUIRE_CONFIRMATION outcome."
            )
        forbidden = {
            "execute",
            "execution",
            "tool_handle",
            "confirm",
            "confirmation",
            "authorized",
            "authorization",
        }
        if any(key in forbidden for key in self.metadata):
            raise ValueError(
                "policy decision metadata cannot contain execution or authority controls."
            )
        if not self.policy_decision_id.strip():
            object.__setattr__(
                self,
                "policy_decision_id",
                f"policy:{self.proposal_id}:{self.validation_id}:{self.rule_id}",
            )

    def to_context(self) -> dict[str, Any]:
        return {
            "policy_decision_id": self.policy_decision_id,
            "request": self.request,
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
            "outcome": self.outcome.value,
            "rule_id": self.rule_id,
            "rationale": self.rationale,
            "confirmation_required": self.confirmation_required,
            "metadata": dict(self.metadata),
        }


class PolicyEvaluator:
    """Evaluate canonical policy facts using deterministic first-match rules."""

    def evaluate(self, policy_input: PolicyInput) -> PolicyDecision:
        if not isinstance(policy_input, PolicyInput):
            raise TypeError("policy_input must be a PolicyInput.")

        if policy_input.validation_status is not ConsequenceValidationStatus.VALID:
            return self._decision(
                policy_input,
                PolicyOutcome.DENY,
                "validation_required",
                "policy input does not represent a valid consequence validation.",
            )

        action = policy_input.action

        if action.effect is ActionEffect.IRREVERSIBLE:
            return self._decision(
                policy_input,
                PolicyOutcome.REQUIRE_CONFIRMATION,
                "irreversible_effect",
                "irreversible effects require confirmation before proceeding.",
            )

        if action.effect is ActionEffect.EXTERNAL_COMMUNICATION:
            return self._decision(
                policy_input,
                PolicyOutcome.REQUIRE_CONFIRMATION,
                "external_communication",
                "external communication requires confirmation before proceeding.",
            )

        if action.effect is ActionEffect.STATE_CHANGE:
            return self._decision(
                policy_input,
                PolicyOutcome.REQUIRE_CONFIRMATION,
                "state_change",
                "state-changing effects require confirmation before proceeding.",
            )

        if action.sensitivity >= 0.8:
            return self._decision(
                policy_input,
                PolicyOutcome.REQUIRE_CONFIRMATION,
                "high_sensitivity",
                "high-sensitivity actions require confirmation before proceeding.",
            )

        if action.reversibility <= 0.2:
            return self._decision(
                policy_input,
                PolicyOutcome.REQUIRE_CONFIRMATION,
                "low_reversibility",
                "low-reversibility actions require confirmation before proceeding.",
            )

        return self._decision(
            policy_input,
            PolicyOutcome.ALLOW,
            "no_effect_default",
            "policy permits the no-effect consequence at this boundary.",
        )

    @staticmethod
    def _decision(
        policy_input: PolicyInput,
        outcome: PolicyOutcome,
        rule_id: str,
        rationale: str,
    ) -> PolicyDecision:
        return PolicyDecision(
            request=policy_input.request,
            proposal_id=policy_input.proposal_id,
            validation_id=policy_input.validation_id,
            outcome=outcome,
            rule_id=rule_id,
            rationale=rationale,
            confirmation_required=outcome is PolicyOutcome.REQUIRE_CONFIRMATION,
            metadata={"policy_semantics": "m7.7"},
        )
