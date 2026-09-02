import unittest

from src.context.consequence_validation_semantics import ConsequenceValidationStatus
from src.context.policy_evaluation_semantics import PolicyDecision, PolicyEvaluator, PolicyOutcome
from src.context.policy_input_semantics import (
    ActionCharacteristics,
    ActionEffect,
    PolicyInput,
    PolicyInputProvenance,
)
from src.context.proposed_consequence_semantics import ConsequenceKind


class PolicyEvaluationSemanticsTests(unittest.TestCase):
    def _input(self, action=None):
        return PolicyInput(
            request="inspect config",
            proposal_id="proposal:0",
            validation_id="validation:0",
            proposal_kind=ConsequenceKind.PLAN,
            validation_status=ConsequenceValidationStatus.VALID,
            action=action or ActionCharacteristics(),
            provenance=PolicyInputProvenance("proposal:0", "validation:0"),
        )

    def test_no_effect_is_allowed(self):
        result = PolicyEvaluator().evaluate(self._input())
        self.assertEqual(result.outcome, PolicyOutcome.ALLOW)
        self.assertFalse(result.confirmation_required)
        self.assertEqual(result.rule_id, "no_effect_default")

    def test_state_change_requires_confirmation(self):
        result = PolicyEvaluator().evaluate(
            self._input(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        )
        self.assertEqual(result.outcome, PolicyOutcome.REQUIRE_CONFIRMATION)
        self.assertTrue(result.confirmation_required)

    def test_external_communication_requires_confirmation(self):
        result = PolicyEvaluator().evaluate(
            self._input(ActionCharacteristics(effect=ActionEffect.EXTERNAL_COMMUNICATION))
        )
        self.assertEqual(result.outcome, PolicyOutcome.REQUIRE_CONFIRMATION)
        self.assertEqual(result.rule_id, "external_communication")

    def test_irreversible_requires_confirmation(self):
        result = PolicyEvaluator().evaluate(
            self._input(ActionCharacteristics(effect=ActionEffect.IRREVERSIBLE))
        )
        self.assertEqual(result.outcome, PolicyOutcome.REQUIRE_CONFIRMATION)
        self.assertEqual(result.rule_id, "irreversible_effect")

    def test_high_sensitivity_requires_confirmation(self):
        result = PolicyEvaluator().evaluate(
            self._input(ActionCharacteristics(sensitivity=0.8))
        )
        self.assertEqual(result.outcome, PolicyOutcome.REQUIRE_CONFIRMATION)
        self.assertEqual(result.rule_id, "high_sensitivity")

    def test_low_reversibility_requires_confirmation(self):
        result = PolicyEvaluator().evaluate(
            self._input(ActionCharacteristics(reversibility=0.2))
        )
        self.assertEqual(result.outcome, PolicyOutcome.REQUIRE_CONFIRMATION)
        self.assertEqual(result.rule_id, "low_reversibility")

    def test_allow_is_not_execution_or_confirmation(self):
        result = PolicyEvaluator().evaluate(self._input())
        context = result.to_context()
        self.assertNotIn("execute", context)
        self.assertNotIn("tool_handle", context)
        self.assertNotIn("confirmed", context)

    def test_policy_decision_preserves_provenance(self):
        result = PolicyEvaluator().evaluate(self._input())
        self.assertEqual(result.request, "inspect config")
        self.assertEqual(result.proposal_id, "proposal:0")
        self.assertEqual(result.validation_id, "validation:0")
        self.assertTrue(result.policy_decision_id.startswith("policy:"))
        self.assertEqual(result.metadata["policy_semantics"], "m7.7")

    def test_invalid_validation_is_denied(self):
        policy_input = self._input()
        object.__setattr__(
            policy_input,
            "validation_status",
            ConsequenceValidationStatus.INVALID,
        )
        result = PolicyEvaluator().evaluate(policy_input)
        self.assertEqual(result.outcome, PolicyOutcome.DENY)
        self.assertEqual(result.rule_id, "validation_required")
        self.assertFalse(result.confirmation_required)

    def test_decision_invariants(self):
        with self.assertRaises(ValueError):
            PolicyDecision(
                "inspect config",
                "proposal:0",
                "validation:0",
                PolicyOutcome.ALLOW,
                "rule",
                "reason",
                confirmation_required=True,
            )


if __name__ == "__main__":
    unittest.main()
