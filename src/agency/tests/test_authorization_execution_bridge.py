import unittest

from src.agency.authorization_decision import AuthorizationDecision, AuthorizationDisposition
from src.agency.authorization_execution_bridge import create_authorization_execution_bridge
from src.context.execution_semantics import (
    ExecutionPreparation,
    ExecutionPreparationStatus,
    ExecutionPreparationViolation,
    ExecutionRequest,
)


class M53AuthorizationExecutionBridgeTests(unittest.TestCase):
    def _authorization(self):
        return AuthorizationDecision(
            "auth:1",
            "confirm-result:1",
            "confirmation:1",
            AuthorizationDisposition.GRANTED,
            "explicitly granted",
        )

    def _preparation(self, *, authorization_id="auth:1", confirmation_id="confirmation:1"):
        request = ExecutionRequest(
            execution_id="exec:1",
            request="Perform approved operation",
            proposal_id="proposal:1",
            validation_id="validation:1",
            policy_decision_id="policy:1",
            confirmation_id=confirmation_id,
            authorization_id=authorization_id,
            operation="approved_operation",
        )
        return ExecutionPreparation(
            request="Perform approved operation",
            execution_id="exec:1",
            status=ExecutionPreparationStatus.READY,
            execution_request=request,
        )

    def test_granted_authorization_can_bind_to_ready_preparation(self):
        bridge = create_authorization_execution_bridge(self._authorization(), self._preparation())
        self.assertEqual(bridge.authorization_id, "auth:1")
        self.assertEqual(bridge.execution_id, "exec:1")
        payload = bridge.to_context()
        self.assertFalse(payload["authorization_created"])
        self.assertFalse(payload["execution_prepared"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["execution_performed"])

    def test_non_granted_authorization_is_rejected(self):
        authorization = AuthorizationDecision(
            "auth:1",
            "confirm-result:1",
            "confirmation:1",
            AuthorizationDisposition.DENIED,
            "denied",
        )
        with self.assertRaises(ValueError):
            create_authorization_execution_bridge(authorization, self._preparation())

    def test_non_ready_preparation_is_rejected(self):
        blocked = ExecutionPreparation(
            request="Perform approved operation",
            execution_id="exec:1",
            status=ExecutionPreparationStatus.BLOCKED,
            violations=(
                ExecutionPreparationViolation(
                    "blocked_for_test",
                    "blocked fixture for bridge rejection test",
                ),
            ),
        )
        with self.assertRaises(ValueError):
            create_authorization_execution_bridge(self._authorization(), blocked)

    def test_upstream_identity_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            create_authorization_execution_bridge(
                self._authorization(),
                self._preparation(authorization_id="auth:other"),
            )
        with self.assertRaises(ValueError):
            create_authorization_execution_bridge(
                self._authorization(),
                self._preparation(confirmation_id="confirmation:other"),
            )


if __name__ == "__main__":
    unittest.main()
