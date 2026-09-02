import unittest

from src.context.authorization_semantics import (
    AuthorizationDecision,
    AuthorizationEvaluator,
    AuthorizationStatus,
)
from src.context.confirmation_integrity_semantics import (
    ConfirmationIntegrityStatus,
    ConfirmationIntegrityValidator,
)
from src.context.confirmation_semantics import ConfirmationManager, ConfirmationStatus
from src.context.consequence_validation_semantics import ConsequenceValidationStatus
from src.context.policy_evaluation_semantics import PolicyEvaluator, PolicyOutcome
from src.context.policy_input_semantics import (
    ActionCharacteristics,
    ActionEffect,
    PolicyInput,
    PolicyInputProvenance,
)
from src.context.proposed_consequence_semantics import ConsequenceKind


class AuthorizationSemanticsTests(unittest.TestCase):
    def _policy_input(self, action):
        return PolicyInput(
            request="update config",
            proposal_id="proposal:0",
            validation_id="validation:0",
            proposal_kind=ConsequenceKind.PREPARE,
            validation_status=ConsequenceValidationStatus.VALID,
            action=action,
            provenance=PolicyInputProvenance("proposal:0", "validation:0"),
        )

    def _decision(self, action):
        return PolicyEvaluator().evaluate(self._policy_input(action))

    def _confirmed_chain(self):
        decision = self._decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        request = ConfirmationManager().request(decision, "confirmation:0", "Apply the change?")
        result = ConfirmationManager().resolve(request, ConfirmationStatus.CONFIRMED)
        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)
        return decision, result, integrity

    def test_allow_becomes_authorized_without_confirmation(self):
        decision = self._decision(ActionCharacteristics())
        result = AuthorizationEvaluator().evaluate(decision, authorization_id="authorization:0")

        self.assertIsInstance(result, AuthorizationDecision)
        self.assertEqual(result.status, AuthorizationStatus.AUTHORIZED)
        self.assertTrue(result.authorized)
        self.assertIsNone(result.confirmation_id)

    def test_deny_cannot_be_authorized(self):
        decision = self._decision(ActionCharacteristics())
        object.__setattr__(decision, "outcome", PolicyOutcome.DENY)
        result = AuthorizationEvaluator().evaluate(decision, authorization_id="authorization:0")

        self.assertEqual(result.status, AuthorizationStatus.DENIED)
        self.assertFalse(result.authorized)

    def test_confirmation_required_without_confirmation_is_denied(self):
        decision = self._decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        result = AuthorizationEvaluator().evaluate(decision, authorization_id="authorization:0")

        self.assertEqual(decision.outcome, PolicyOutcome.REQUIRE_CONFIRMATION)
        self.assertEqual(result.status, AuthorizationStatus.DENIED)

    def test_confirmed_intact_chain_is_authorized(self):
        decision, confirmation, integrity = self._confirmed_chain()
        result = AuthorizationEvaluator().evaluate(
            decision,
            confirmation_result=confirmation,
            confirmation_integrity=integrity,
            authorization_id="authorization:0",
        )

        self.assertEqual(result.status, AuthorizationStatus.AUTHORIZED)
        self.assertTrue(result.authorized)
        self.assertEqual(result.confirmation_id, "confirmation:0")

    def test_invalid_integrity_cannot_be_authorized(self):
        decision, confirmation, integrity = self._confirmed_chain()
        object.__setattr__(integrity, "status", ConfirmationIntegrityStatus.INVALID)
        result = AuthorizationEvaluator().evaluate(
            decision,
            confirmation_result=confirmation,
            confirmation_integrity=integrity,
            authorization_id="authorization:0",
        )

        self.assertEqual(result.status, AuthorizationStatus.DENIED)
        self.assertFalse(result.authorized)

    def test_denied_confirmation_cannot_be_authorized(self):
        decision = self._decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        request = ConfirmationManager().request(decision, "confirmation:0", "Apply the change?")
        confirmation = ConfirmationManager().resolve(request, ConfirmationStatus.DENIED)
        integrity = ConfirmationIntegrityValidator().validate(decision, request, confirmation)

        result = AuthorizationEvaluator().evaluate(
            decision,
            confirmation_result=confirmation,
            confirmation_integrity=integrity,
            authorization_id="authorization:0",
        )

        self.assertEqual(result.status, AuthorizationStatus.DENIED)

    def test_allow_with_confirmation_artifacts_is_denied(self):
        decision = self._decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        confirmation_request = ConfirmationManager().request(
            decision, "confirmation:0", "Apply the change?"
        )
        confirmation = ConfirmationManager().resolve(
            confirmation_request, ConfirmationStatus.CONFIRMED
        )
        integrity = ConfirmationIntegrityValidator().validate(
            decision, confirmation_request, confirmation
        )
        object.__setattr__(decision, "outcome", PolicyOutcome.ALLOW)

        result = AuthorizationEvaluator().evaluate(
            decision,
            confirmation_result=confirmation,
            confirmation_integrity=integrity,
            authorization_id="authorization:0",
        )
        self.assertEqual(result.status, AuthorizationStatus.DENIED)

    def test_integrity_for_different_policy_decision_is_denied(self):
        decision, confirmation, integrity = self._confirmed_chain()
        other_decision = self._decision(ActionCharacteristics(effect=ActionEffect.IRREVERSIBLE))

        result = AuthorizationEvaluator().evaluate(
            other_decision,
            confirmation_result=confirmation,
            confirmation_integrity=integrity,
            authorization_id="authorization:0",
        )

        self.assertEqual(result.status, AuthorizationStatus.DENIED)

    def test_confirmation_result_for_different_policy_decision_is_denied(self):
        decision, confirmation, integrity = self._confirmed_chain()
        other_decision = self._decision(ActionCharacteristics(effect=ActionEffect.IRREVERSIBLE))
        other_request = ConfirmationManager().request(
            other_decision, "confirmation:1", "Perform the action?"
        )
        other_confirmation = ConfirmationManager().resolve(
            other_request, ConfirmationStatus.CONFIRMED
        )

        result = AuthorizationEvaluator().evaluate(
            decision,
            confirmation_result=other_confirmation,
            confirmation_integrity=integrity,
            authorization_id="authorization:0",
        )

        self.assertEqual(result.status, AuthorizationStatus.DENIED)

    def test_authorization_preserves_identity_chain(self):
        decision, confirmation, integrity = self._confirmed_chain()
        result = AuthorizationEvaluator().evaluate(
            decision,
            confirmation_result=confirmation,
            confirmation_integrity=integrity,
            authorization_id="authorization:7",
        )

        self.assertEqual(result.authorization_id, "authorization:7")
        self.assertEqual(result.request, decision.request)
        self.assertEqual(result.proposal_id, decision.proposal_id)
        self.assertEqual(result.validation_id, decision.validation_id)
        self.assertEqual(result.policy_decision_id, decision.policy_decision_id)
        self.assertEqual(result.confirmation_id, confirmation.confirmation_id)

    def test_authorization_contains_no_execution_controls(self):
        decision = self._decision(ActionCharacteristics())
        result = AuthorizationEvaluator().evaluate(decision, authorization_id="authorization:0")
        context = result.to_context()

        self.assertNotIn("execute", context)
        self.assertNotIn("tool_handle", context)
        self.assertNotIn("provider", context)
        self.assertNotIn("invoke", context)

    def test_authorization_requires_explicit_identity(self):
        decision = self._decision(ActionCharacteristics())
        with self.assertRaises(ValueError):
            AuthorizationEvaluator().evaluate(decision)


if __name__ == "__main__":
    unittest.main()
