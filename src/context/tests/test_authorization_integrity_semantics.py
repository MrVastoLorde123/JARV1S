import unittest

from src.context.authorization_integrity_semantics import (
    AuthorizationIntegrity,
    AuthorizationIntegrityStatus,
    AuthorizationIntegrityValidator,
)
from src.context.authorization_semantics import AuthorizationEvaluator, AuthorizationStatus
from src.context.confirmation_integrity_semantics import ConfirmationIntegrityValidator
from src.context.confirmation_semantics import ConfirmationManager, ConfirmationStatus
from src.context.consequence_validation_semantics import ConsequenceValidationStatus
from src.context.policy_evaluation_semantics import PolicyEvaluator
from src.context.policy_input_semantics import ActionCharacteristics, ActionEffect, PolicyInput, PolicyInputProvenance
from src.context.proposed_consequence_semantics import ConsequenceKind


class AuthorizationIntegritySemanticsTests(unittest.TestCase):
    def _decision(self, action):
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

    def _allow_chain(self):
        decision = self._decision(ActionCharacteristics())
        authorization = AuthorizationEvaluator().evaluate(decision, authorization_id="authorization:0")
        return decision, authorization

    def _confirmed_chain(self):
        decision = self._decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        request = ConfirmationManager().request(decision, "confirmation:0", "Apply the change?")
        result = ConfirmationManager().resolve(request, ConfirmationStatus.CONFIRMED)
        confirmation_integrity = ConfirmationIntegrityValidator().validate(decision, request, result)
        authorization = AuthorizationEvaluator().evaluate(
            decision,
            confirmation_result=result,
            confirmation_integrity=confirmation_integrity,
            authorization_id="authorization:0",
        )
        return decision, result, confirmation_integrity, authorization

    def test_allow_authorization_has_valid_integrity(self):
        decision, authorization = self._allow_chain()
        integrity = AuthorizationIntegrityValidator().validate(decision, authorization)
        self.assertIsInstance(integrity, AuthorizationIntegrity)
        self.assertEqual(integrity.status, AuthorizationIntegrityStatus.VALID)
        self.assertTrue(integrity.intact)
        self.assertIsNone(integrity.confirmation_id)

    def test_confirmed_authorization_has_valid_integrity(self):
        decision, confirmation, confirmation_integrity, authorization = self._confirmed_chain()
        integrity = AuthorizationIntegrityValidator().validate(
            decision, authorization, confirmation, confirmation_integrity
        )
        self.assertEqual(integrity.status, AuthorizationIntegrityStatus.VALID)
        self.assertEqual(integrity.confirmation_id, "confirmation:0")

    def test_authorization_identity_mismatch_is_invalid(self):
        decision, authorization = self._allow_chain()
        object.__setattr__(authorization, "policy_decision_id", "policy:other")
        integrity = AuthorizationIntegrityValidator().validate(decision, authorization)
        self.assertEqual(integrity.status, AuthorizationIntegrityStatus.INVALID)
        self.assertIn("authorization_policy_decision_id_mismatch", {v.code for v in integrity.violations})

    def test_authorization_id_is_preserved(self):
        decision, authorization = self._allow_chain()
        integrity = AuthorizationIntegrityValidator().validate(decision, authorization)
        self.assertEqual(integrity.authorization_id, "authorization:0")

    def test_wrong_confirmation_is_invalid(self):
        decision, confirmation, confirmation_integrity, authorization = self._confirmed_chain()
        other_decision = self._decision(ActionCharacteristics(effect=ActionEffect.IRREVERSIBLE))
        other_request = ConfirmationManager().request(other_decision, "confirmation:1", "Perform action?")
        other_confirmation = ConfirmationManager().resolve(other_request, ConfirmationStatus.CONFIRMED)
        integrity = AuthorizationIntegrityValidator().validate(
            decision, authorization, other_confirmation, confirmation_integrity
        )
        self.assertEqual(integrity.status, AuthorizationIntegrityStatus.INVALID)
        self.assertTrue(any("confirmation_" in v.code for v in integrity.violations))

    def test_invalid_confirmation_integrity_is_invalid(self):
        decision, confirmation, confirmation_integrity, authorization = self._confirmed_chain()
        object.__setattr__(confirmation_integrity, "status", type(confirmation_integrity.status).INVALID)
        integrity = AuthorizationIntegrityValidator().validate(
            decision, authorization, confirmation, confirmation_integrity
        )
        self.assertEqual(integrity.status, AuthorizationIntegrityStatus.INVALID)
        self.assertIn("invalid_confirmation_integrity", {v.code for v in integrity.violations})

    def test_authorized_confirmation_chain_requires_confirmation_artifacts(self):
        decision = self._decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        authorization = object.__new__(type("AuthorizationStub", (), {}))
        self.assertRaises(TypeError, AuthorizationIntegrityValidator().validate, decision, authorization)

    def test_denied_authorization_can_have_valid_integrity_without_execution(self):
        decision = self._decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        authorization = AuthorizationEvaluator().evaluate(decision, authorization_id="authorization:denied")
        integrity = AuthorizationIntegrityValidator().validate(decision, authorization)
        self.assertEqual(authorization.status, AuthorizationStatus.DENIED)
        self.assertEqual(integrity.status, AuthorizationIntegrityStatus.VALID)
        self.assertNotIn("execute", integrity.to_context())

    def test_integrity_contains_no_execution_controls(self):
        decision, authorization = self._allow_chain()
        context = AuthorizationIntegrityValidator().validate(decision, authorization).to_context()
        self.assertNotIn("execute", context)
        self.assertNotIn("tool_handle", context)
        self.assertNotIn("provider", context)
        self.assertNotIn("invoke", context)

    def test_integrity_is_not_authorization(self):
        decision, authorization = self._allow_chain()
        integrity = AuthorizationIntegrityValidator().validate(decision, authorization)
        self.assertTrue(authorization.authorized)
        self.assertTrue(integrity.intact)
        self.assertNotIn("authorized", integrity.to_context())


if __name__ == "__main__":
    unittest.main()
