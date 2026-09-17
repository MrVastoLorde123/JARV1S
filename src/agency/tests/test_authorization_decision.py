import unittest

from src.agency.authorization_decision import (
    AuthorizationDecision,
    AuthorizationDisposition,
    build_authorization_decision_set,
)
from src.agency.confirmation import (
    ConfirmationDisposition,
    ConfirmationRequest,
    ConfirmationResult,
)


class M52AuthorizationDecisionTests(unittest.TestCase):
    def _confirmation(self, disposition=ConfirmationDisposition.CONFIRMED):
        request = ConfirmationRequest(
            "verify:confirmation",
            "verify:proposals",
            "verify:proposal",
            "Confirm this proposal.",
            disposition=disposition,
            response_text="confirmed" if disposition is ConfirmationDisposition.CONFIRMED else None,
        )
        return ConfirmationResult("verify:result", "verify:proposals", (request,))

    def test_authorization_requires_confirmed_confirmation(self):
        confirmation = self._confirmation(ConfirmationDisposition.PENDING)
        decision = AuthorizationDecision(
            "verify:authorization",
            "verify:result",
            "verify:confirmation",
            AuthorizationDisposition.GRANTED,
            "explicit confirmation received",
        )
        with self.assertRaises(ValueError):
            build_authorization_decision_set(
                confirmation,
                decision_set_id="verify:decisions",
                decisions=(decision,),
            )

    def test_authorization_requires_supplied_confirmation_identity(self):
        confirmation = self._confirmation()
        decision = AuthorizationDecision(
            "verify:authorization",
            "verify:result",
            "unknown:confirmation",
            AuthorizationDisposition.GRANTED,
            "explicit confirmation received",
        )
        with self.assertRaises(ValueError):
            build_authorization_decision_set(
                confirmation,
                decision_set_id="verify:decisions",
                decisions=(decision,),
            )

    def test_granted_authorization_is_still_not_execution(self):
        confirmation = self._confirmation()
        decision = AuthorizationDecision(
            "verify:authorization",
            "verify:result",
            "verify:confirmation",
            AuthorizationDisposition.GRANTED,
            "explicit confirmation received",
        )
        result = build_authorization_decision_set(
            confirmation,
            decision_set_id="verify:decisions",
            decisions=(decision,),
        )
        payload = result.to_context()
        self.assertTrue(payload["authority_granted"])
        self.assertTrue(payload["permissions_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["execution_performed"])

    def test_non_granted_decision_does_not_grant_authority(self):
        confirmation = self._confirmation()
        decision = AuthorizationDecision(
            "verify:authorization",
            "verify:result",
            "verify:confirmation",
            AuthorizationDisposition.DENIED,
            "policy boundary denies execution",
        )
        result = build_authorization_decision_set(
            confirmation,
            decision_set_id="verify:decisions",
            decisions=(decision,),
        )
        payload = result.to_context()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["permissions_granted"])


if __name__ == "__main__":
    unittest.main()
