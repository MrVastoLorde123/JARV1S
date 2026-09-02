import unittest

from src.context.authorization_integrity_semantics import AuthorizationIntegrityValidator
from src.context.authorization_semantics import AuthorizationEvaluator, AuthorizationStatus
from src.context.confirmation_integrity_semantics import ConfirmationIntegrityValidator
from src.context.confirmation_semantics import ConfirmationManager, ConfirmationStatus
from src.context.consequence_validation_semantics import ConsequenceValidationStatus
from src.context.execution_semantics import (
    ExecutionGate,
    ExecutionPreparationStatus,
    ExecutionRequest,
)
from src.context.policy_evaluation_semantics import PolicyEvaluator
from src.context.policy_input_semantics import ActionCharacteristics, ActionEffect, PolicyInput, PolicyInputProvenance
from src.context.proposed_consequence_semantics import ConsequenceKind


class ExecutionSemanticsTests(unittest.TestCase):
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
        integrity = AuthorizationIntegrityValidator().validate(decision, authorization)
        return authorization, integrity

    def _confirmed_chain(self):
        decision = self._decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        confirmation_request = ConfirmationManager().request(decision, "confirmation:0", "Apply the change?")
        confirmation = ConfirmationManager().resolve(confirmation_request, ConfirmationStatus.CONFIRMED)
        confirmation_integrity = ConfirmationIntegrityValidator().validate(
            decision, confirmation_request, confirmation
        )
        authorization = AuthorizationEvaluator().evaluate(
            decision,
            confirmation_result=confirmation,
            confirmation_integrity=confirmation_integrity,
            authorization_id="authorization:0",
        )
        authorization_integrity = AuthorizationIntegrityValidator().validate(
            decision, authorization, confirmation, confirmation_integrity
        )
        return authorization, authorization_integrity

    def test_authorized_allow_is_ready(self):
        authorization, integrity = self._allow_chain()
        result = ExecutionGate().prepare(
            authorization,
            integrity,
            "execution:0",
            "inspect configuration",
        )
        self.assertEqual(result.status, ExecutionPreparationStatus.READY)
        self.assertTrue(result.ready)
        self.assertIsInstance(result.execution_request, ExecutionRequest)
        self.assertIsNone(result.execution_request.confirmation_id)

    def test_confirmed_authorized_chain_is_ready(self):
        authorization, integrity = self._confirmed_chain()
        result = ExecutionGate().prepare(
            authorization,
            integrity,
            "execution:0",
            "apply configuration",
            {"path": "config.yaml"},
        )
        self.assertEqual(result.status, ExecutionPreparationStatus.READY)
        self.assertEqual(result.execution_request.confirmation_id, "confirmation:0")

    def test_denied_authorization_is_blocked(self):
        decision = self._decision(ActionCharacteristics(effect=ActionEffect.STATE_CHANGE))
        authorization = AuthorizationEvaluator().evaluate(decision, authorization_id="authorization:denied")
        integrity = AuthorizationIntegrityValidator().validate(decision, authorization)
        result = ExecutionGate().prepare(authorization, integrity, "execution:0", "apply configuration")
        self.assertEqual(result.status, ExecutionPreparationStatus.BLOCKED)
        self.assertIn("authorization_required", {v.code for v in result.violations})
        self.assertIsNone(result.execution_request)

    def test_invalid_authorization_integrity_is_blocked(self):
        authorization, integrity = self._allow_chain()
        object.__setattr__(integrity, "status", type(integrity.status).INVALID)
        result = ExecutionGate().prepare(authorization, integrity, "execution:0", "inspect configuration")
        self.assertEqual(result.status, ExecutionPreparationStatus.BLOCKED)
        self.assertIn("authorization_integrity_required", {v.code for v in result.violations})

    def test_integrity_mismatch_is_blocked(self):
        authorization, integrity = self._allow_chain()
        object.__setattr__(integrity, "authorization_id", "authorization:other")
        result = ExecutionGate().prepare(authorization, integrity, "execution:0", "inspect configuration")
        self.assertEqual(result.status, ExecutionPreparationStatus.BLOCKED)
        self.assertIn("integrity_authorization_id_mismatch", {v.code for v in result.violations})

    def test_execution_identity_must_be_distinct(self):
        authorization, integrity = self._allow_chain()
        result = ExecutionGate().prepare(
            authorization, integrity, authorization.authorization_id, "inspect configuration"
        )
        self.assertEqual(result.status, ExecutionPreparationStatus.BLOCKED)
        self.assertIn("execution_identity_collision", {v.code for v in result.violations})

    def test_forbidden_arguments_are_blocked(self):
        authorization, integrity = self._allow_chain()
        result = ExecutionGate().prepare(
            authorization,
            integrity,
            "execution:0",
            "inspect configuration",
            {"execute": True},
        )
        self.assertEqual(result.status, ExecutionPreparationStatus.BLOCKED)
        self.assertIn("forbidden_execution_control", {v.code for v in result.violations})

    def test_forbidden_metadata_is_blocked(self):
        authorization, integrity = self._allow_chain()
        result = ExecutionGate().prepare(
            authorization,
            integrity,
            "execution:0",
            "inspect configuration",
            metadata={"provider": "shell"},
        )
        self.assertEqual(result.status, ExecutionPreparationStatus.BLOCKED)
        self.assertIn("forbidden_execution_metadata", {v.code for v in result.violations})

    def test_ready_request_preserves_identity_chain(self):
        authorization, integrity = self._allow_chain()
        result = ExecutionGate().prepare(authorization, integrity, "execution:7", "inspect configuration")
        request = result.execution_request
        self.assertEqual(request.request, authorization.request)
        self.assertEqual(request.proposal_id, authorization.proposal_id)
        self.assertEqual(request.validation_id, authorization.validation_id)
        self.assertEqual(request.policy_decision_id, authorization.policy_decision_id)
        self.assertEqual(request.authorization_id, authorization.authorization_id)
        self.assertEqual(request.execution_id, "execution:7")

    def test_execution_request_is_provider_neutral(self):
        authorization, integrity = self._allow_chain()
        request = ExecutionGate().prepare(
            authorization, integrity, "execution:0", "inspect configuration", {"path": "config.yaml"}
        ).execution_request
        context = request.to_context()
        self.assertIn("operation", context)
        self.assertNotIn("tool_handle", context)
        self.assertNotIn("provider", context)
        self.assertNotIn("credential", context)

    def test_ready_does_not_mean_executed(self):
        authorization, integrity = self._allow_chain()
        result = ExecutionGate().prepare(authorization, integrity, "execution:0", "inspect configuration")
        context = result.to_context()
        self.assertTrue(result.ready)
        self.assertNotIn("executed", context)
        self.assertNotIn("execution_result", context)

    def test_authorization_status_must_be_authorized(self):
        authorization, integrity = self._allow_chain()
        object.__setattr__(authorization, "status", AuthorizationStatus.DENIED)
        result = ExecutionGate().prepare(authorization, integrity, "execution:0", "inspect configuration")
        self.assertEqual(result.status, ExecutionPreparationStatus.BLOCKED)


if __name__ == "__main__":
    unittest.main()
