import unittest

from src.context.confirmation_integrity_semantics import (
    ConfirmationIntegrity,
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


class ConfirmationIntegritySemanticsTests(unittest.TestCase):
    def _artifacts(self):
        policy_input = PolicyInput(
            request="update config",
            proposal_id="proposal:0",
            validation_id="validation:0",
            proposal_kind=ConsequenceKind.PREPARE,
            validation_status=ConsequenceValidationStatus.VALID,
            action=ActionCharacteristics(effect=ActionEffect.STATE_CHANGE),
            provenance=PolicyInputProvenance("proposal:0", "validation:0"),
        )
        decision = PolicyEvaluator().evaluate(policy_input)
        request = ConfirmationManager().request(
            decision,
            "confirmation:0",
            "Apply the configuration change?",
        )
        result = ConfirmationManager().resolve(request, ConfirmationStatus.CONFIRMED)
        return decision, request, result

    def test_intact_chain_is_valid(self):
        decision, request, result = self._artifacts()
        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)

        self.assertIsInstance(integrity, ConfirmationIntegrity)
        self.assertEqual(integrity.status, ConfirmationIntegrityStatus.VALID)
        self.assertTrue(integrity.intact)
        self.assertEqual(integrity.confirmation_id, "confirmation:0")

    def test_request_id_mismatch_is_invalid(self):
        decision, request, result = self._artifacts()
        object.__setattr__(request, "policy_decision_id", "policy:other")

        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)

        self.assertEqual(integrity.status, ConfirmationIntegrityStatus.INVALID)
        self.assertIn("request_policy_decision_id_mismatch", {v.code for v in integrity.violations})

    def test_result_id_mismatch_is_invalid(self):
        decision, request, result = self._artifacts()
        object.__setattr__(result, "confirmation_id", "confirmation:other")

        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)

        self.assertEqual(integrity.status, ConfirmationIntegrityStatus.INVALID)
        self.assertIn("confirmation_id_mismatch", {v.code for v in integrity.violations})

    def test_proposal_identity_mismatch_is_invalid(self):
        decision, request, result = self._artifacts()
        object.__setattr__(result, "proposal_id", "proposal:other")

        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)

        self.assertEqual(integrity.status, ConfirmationIntegrityStatus.INVALID)
        self.assertIn("result_proposal_id_mismatch", {v.code for v in integrity.violations})

    def test_validation_identity_mismatch_is_invalid(self):
        decision, request, result = self._artifacts()
        object.__setattr__(request, "validation_id", "validation:other")

        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)

        self.assertEqual(integrity.status, ConfirmationIntegrityStatus.INVALID)
        self.assertIn("request_validation_id_mismatch", {v.code for v in integrity.violations})

    def test_request_and_result_must_match_each_other(self):
        decision, request, result = self._artifacts()
        object.__setattr__(result, "request", "different request")

        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)

        self.assertEqual(integrity.status, ConfirmationIntegrityStatus.INVALID)
        self.assertIn("result_request_mismatch", {v.code for v in integrity.violations})

    def test_request_policy_outcome_mismatch_is_invalid(self):
        decision, request, result = self._artifacts()
        object.__setattr__(request, "policy_outcome", PolicyOutcome.ALLOW)

        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)

        self.assertEqual(integrity.status, ConfirmationIntegrityStatus.INVALID)
        self.assertIn("request_policy_outcome_mismatch", {v.code for v in integrity.violations})

    def test_non_confirmation_policy_cannot_form_valid_integrity_chain(self):
        policy_input = PolicyInput(
            request="inspect config",
            proposal_id="proposal:0",
            validation_id="validation:0",
            proposal_kind=ConsequenceKind.PLAN,
            validation_status=ConsequenceValidationStatus.VALID,
            action=ActionCharacteristics(),
            provenance=PolicyInputProvenance("proposal:0", "validation:0"),
        )
        decision = PolicyEvaluator().evaluate(policy_input)
        self.assertEqual(decision.outcome, PolicyOutcome.ALLOW)
        request = object.__new__(type(self._artifacts()[1]))
        object.__setattr__(request, "confirmation_id", "confirmation:0")
        object.__setattr__(request, "request", decision.request)
        object.__setattr__(request, "proposal_id", decision.proposal_id)
        object.__setattr__(request, "validation_id", decision.validation_id)
        object.__setattr__(request, "policy_decision_id", decision.policy_decision_id)
        object.__setattr__(request, "policy_outcome", PolicyOutcome.REQUIRE_CONFIRMATION)
        object.__setattr__(request, "prompt", "Proceed?")
        object.__setattr__(request, "metadata", {})
        result = object.__new__(type(self._artifacts()[2]))
        object.__setattr__(result, "confirmation_id", "confirmation:0")
        object.__setattr__(result, "request", decision.request)
        object.__setattr__(result, "proposal_id", decision.proposal_id)
        object.__setattr__(result, "validation_id", decision.validation_id)
        object.__setattr__(result, "policy_decision_id", decision.policy_decision_id)
        object.__setattr__(result, "status", ConfirmationStatus.CONFIRMED)
        object.__setattr__(result, "metadata", {})

        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)

        self.assertEqual(integrity.status, ConfirmationIntegrityStatus.INVALID)
        self.assertIn("policy_confirmation_not_required", {v.code for v in integrity.violations})

    def test_pending_resolution_is_invalid_integrity(self):
        decision, request, result = self._artifacts()
        object.__setattr__(result, "status", ConfirmationStatus.PENDING)

        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)

        self.assertEqual(integrity.status, ConfirmationIntegrityStatus.INVALID)
        self.assertIn("pending_resolution", {v.code for v in integrity.violations})

    def test_integrity_does_not_grant_authority_or_execution(self):
        decision, request, result = self._artifacts()
        integrity = ConfirmationIntegrityValidator().validate(decision, request, result)
        context = integrity.to_context()

        self.assertTrue(integrity.intact)
        self.assertNotIn("authorized", context)
        self.assertNotIn("execute", context)
        self.assertNotIn("tool_handle", context)


if __name__ == "__main__":
    unittest.main()
