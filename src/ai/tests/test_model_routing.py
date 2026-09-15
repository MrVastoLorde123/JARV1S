import unittest

from src.ai.model_routing import (
    ModelProfile,
    ModelRole,
    ModelRouter,
    RoutingRequest,
)


class ModelRoutingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = ModelRouter(
            [
                ModelProfile("granite-8b", frozenset({ModelRole.GENERAL, ModelRole.VERIFICATION}), priority=100),
                ModelProfile("qwen3-14b", frozenset({ModelRole.DIAGNOSTIC, ModelRole.GENERAL}), priority=90),
                ModelProfile("qwen3-coder-30b", frozenset({ModelRole.CODING}), priority=100),
                ModelProfile("fast-4b", frozenset({ModelRole.LIGHTWEIGHT}), priority=100),
                ModelProfile("offline-14b", frozenset({ModelRole.DIAGNOSTIC}), priority=120, available=False),
            ]
        )

    def test_role_selects_highest_priority_available_model(self) -> None:
        decision = self.router.route(RoutingRequest(ModelRole.DIAGNOSTIC))
        self.assertEqual(decision.model_id, "qwen3-14b")
        self.assertEqual(decision.reason, "highest-priority available model for role")
        self.assertEqual(decision.candidates_considered, ("qwen3-14b",))

    def test_unavailable_higher_priority_model_does_not_win(self) -> None:
        decision = self.router.route(RoutingRequest(ModelRole.DIAGNOSTIC, require_available=True))
        self.assertEqual(decision.model_id, "qwen3-14b")

    def test_explicit_model_preference_is_honored_when_role_matches(self) -> None:
        decision = self.router.route(
            RoutingRequest(ModelRole.GENERAL, preferred_model="qwen3-14b")
        )
        self.assertEqual(decision.model_id, "qwen3-14b")
        self.assertEqual(decision.reason, "explicit model preference")

    def test_explicit_model_preference_cannot_cross_role_boundary(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not serve role CODING"):
            self.router.route(
                RoutingRequest(ModelRole.CODING, preferred_model="granite-8b")
            )

    def test_unavailable_explicit_model_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "is unavailable"):
            self.router.route(
                RoutingRequest(ModelRole.DIAGNOSTIC, preferred_model="offline-14b")
            )

    def test_no_model_for_role_is_deterministic_failure(self) -> None:
        with self.assertRaisesRegex(LookupError, "no model available for role VERIFICATION"):
            empty = ModelRouter([ModelProfile("coding", frozenset({ModelRole.CODING}))])
            empty.route(RoutingRequest(ModelRole.VERIFICATION))

    def test_routing_decision_does_not_grant_authority_or_tools(self) -> None:
        decision = self.router.route(RoutingRequest(ModelRole.CODING))
        self.assertEqual(decision.model_id, "qwen3-coder-30b")
        self.assertFalse(hasattr(decision, "authority"))
        self.assertFalse(hasattr(decision, "permissions"))
        self.assertFalse(hasattr(decision, "tools"))

    def test_tie_break_is_stable_by_model_id(self) -> None:
        router = ModelRouter(
            [
                ModelProfile("zeta", frozenset({ModelRole.GENERAL}), priority=10),
                ModelProfile("alpha", frozenset({ModelRole.GENERAL}), priority=10),
            ]
        )
        decision = router.route(RoutingRequest(ModelRole.GENERAL))
        self.assertEqual(decision.model_id, "alpha")


if __name__ == "__main__":
    unittest.main()
