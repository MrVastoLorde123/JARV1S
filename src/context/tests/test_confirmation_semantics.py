import unittest

from src.context.confirmation_semantics import (
    ConfirmationManager,
    ConfirmationRequest,
    ConfirmationResult,
    ConfirmationStatus,
)
from src.context.consequence_validation_semantics import ConsequenceValidationStatus
from src.context.policy_evaluation_semantics import PolicyEvaluator, PolicyOutcome
from src.context.policy_input_semantics import (
    ActionCharacteristics,
    ActionEffect,
    PolicyInput,
    PolicyInputProvenance,
)
from src.context.proposed_consequence_semantics import ConsequenceKind


class ConfirmationSemanticsTests(unittest.TestCase):
    def _policy_decision(self, action):
        policy_input = PolicyInput(
            request="update config",
            proposal_id="proposal:0",
            validation_id="validation:0",
            proposal_kind=ConsequenceKind.PREPARE,
            validation_status=ConsequenceValidationStatus.VALID,
            action=action,
            provenance=PolicyInputProvenance("proposal:0", "validation:0"),
        )
        return PolicyEvaluator().evaluate(policy_input)

    def test_confirmation_request_requires_policy_confirmation(self):
        decision = self._policy_decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        result = ConfirmationManager().request(decision, "confirmation:0", "Apply the configuration change?")

        self.assertIsInstance(result, ConfirmationRequest)
        self.assertEqual(result.confirmation_id, "confirmation:0")
        self.assertEqual(result.policy_decision_id, decision.policy_decision_id)
        self.assertEqual(result.proposal_id, "proposal:0")
        self.assertEqual(result.validation_id, "validation:0")

    def test_allow_cannot_create_confirmation_request(self):
        decision = self._policy_decision(ActionCharacteristics())
        self.assertEqual(decision.outcome, PolicyOutcome.ALLOW)
        with self.assertRaises(ValueError):
            ConfirmationManager().request(decision, "confirmation:0", "Proceed?")

    def test_confirmation_request_preserves_upstream_identity(self):
        decision = self._policy_decision(ActionCharacteristics(effect=ActionEffect.EXTERNAL_COMMUNICATION))
        request = ConfirmationManager().request(decision, "confirmation:7", "Send the message?")
        context = request.to_context()

        self.assertEqual(context["proposal_id"], decision.proposal_id)
        self.assertEqual(context["validation_id"], decision.validation_id)
        self.assertEqual(context["policy_decision_id"], decision.policy_decision_id)
        self.assertNotIn("execute", context)

    def test_pending_cannot_be_a_resolution(self):
        decision = self._policy_decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        request = ConfirmationManager().request(decision, "confirmation:0", "Apply change?")
        with self.assertRaises(ValueError):
            ConfirmationManager().resolve(request, ConfirmationStatus.PENDING)

    def test_confirmed_resolution_is_explicit(self):
        decision = self._policy_decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        request = ConfirmationManager().request(decision, "confirmation:0", "Apply change?")
        result = ConfirmationManager().resolve(request, ConfirmationStatus.CONFIRMED)

        self.assertIsInstance(result, ConfirmationResult)
        self.assertTrue(result.confirmed)
        self.assertEqual(result.status, ConfirmationStatus.CONFIRMED)
        self.assertEqual(result.confirmation_id, "confirmation:0")
        self.assertEqual(result.policy_decision_id, decision.policy_decision_id)

    def test_denied_resolution_is_not_confirmed(self):
        decision = self._policy_decision(ActionCharacteristics(effect=ActionEffect.IRREVERSIBLE))
        request = ConfirmationManager().request(decision, "confirmation:1", "Perform irreversible action?")
        result = ConfirmationManager().resolve(request, ConfirmationStatus.DENIED)

        self.assertFalse(result.confirmed)
        self.assertEqual(result.status, ConfirmationStatus.DENIED)

    def test_confirmation_artifacts_contain_no_execution_controls(self):
        decision = self._policy_decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        request = ConfirmationManager().request(decision, "confirmation:0", "Apply change?")
        result = ConfirmationManager().resolve(request, ConfirmationStatus.CONFIRMED)

        self.assertNotIn("execute", request.to_context())
        self.assertNotIn("tool_handle", request.to_context())
        self.assertNotIn("execute", result.to_context())
        self.assertNotIn("tool_handle", result.to_context())

    def test_confirmation_ids_are_distinct_from_upstream_ids(self):
        decision = self._policy_decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        request = ConfirmationManager().request(decision, "confirmation:0", "Apply change?")

        self.assertNotEqual(request.confirmation_id, request.proposal_id)
        self.assertNotEqual(request.confirmation_id, request.validation_id)
        self.assertNotEqual(request.confirmation_id, request.policy_decision_id)


if __name__ == "__main__":
    unittest.main()
