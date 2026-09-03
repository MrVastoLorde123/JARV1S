import json
import unittest

from src.interface.hitl import (
    DecisionOption,
    HumanDecisionRequest,
    HumanDecisionResponse,
    HumanDecisionRuntime,
    HumanDecisionState,
    HumanDecisionStore,
    HumanResponseStatus,
)


class HumanInTheLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = HumanDecisionRuntime()
        self.option_yes = DecisionOption("yes", "Continue")
        self.option_no = DecisionOption("no", "Stop")
        self.request = HumanDecisionRequest(
            decision_id="decision-1",
            prompt="Choose the next step.",
            options=(self.option_yes, self.option_no),
            session_id="session-1",
            source_request_id="req-1",
            metadata={"surface": "chat"},
        )
        self.state = HumanDecisionState(self.request)

    def test_option_is_immutable(self) -> None:
        with self.assertRaises(Exception):
            self.option_yes.label = "changed"
        with self.assertRaises(TypeError):
            self.option_yes.metadata["x"] = "y"

    def test_request_is_immutable_and_bounded(self) -> None:
        with self.assertRaises(Exception):
            self.request.prompt = "changed"
        with self.assertRaises(ValueError):
            HumanDecisionRequest(
                decision_id="d",
                prompt="choose",
                options=(self.option_yes, self.option_no),
                max_options=1,
            )

    def test_request_rejects_duplicate_options(self) -> None:
        with self.assertRaises(ValueError):
            HumanDecisionRequest(
                decision_id="d",
                prompt="choose",
                options=(self.option_yes, DecisionOption("yes", "Other")),
            )

    def test_request_requires_an_option(self) -> None:
        with self.assertRaises(ValueError):
            HumanDecisionRequest(decision_id="d", prompt="choose", options=())

    def test_submitted_response_requires_valid_selection(self) -> None:
        response = HumanDecisionResponse(
            decision_id="decision-1",
            response_id="response-1",
            status=HumanResponseStatus.SUBMITTED,
            selected_option_id="yes",
            responder_ref="human-1",
        )
        completed = self.runtime.respond(self.state, response)
        self.assertFalse(completed.pending)
        self.assertTrue(completed.terminal)
        self.assertEqual(completed.response.selected_option_id, "yes")

    def test_unknown_selected_option_is_rejected(self) -> None:
        response = HumanDecisionResponse(
            decision_id="decision-1",
            response_id="response-1",
            status=HumanResponseStatus.SUBMITTED,
            selected_option_id="maybe",
        )
        with self.assertRaises(ValueError):
            self.runtime.respond(self.state, response)

    def test_cancel_has_no_selection(self) -> None:
        completed = self.runtime.cancel(self.state, response_id="response-2", responder_ref="human-1")
        self.assertEqual(completed.response.status, HumanResponseStatus.CANCELLED)
        self.assertIsNone(completed.response.selected_option_id)

    def test_expire_has_no_selection(self) -> None:
        completed = self.runtime.expire(self.state, response_id="response-3")
        self.assertEqual(completed.response.status, HumanResponseStatus.EXPIRED)
        self.assertIsNone(completed.response.selected_option_id)

    def test_terminal_state_cannot_be_answered_twice(self) -> None:
        completed = self.runtime.cancel(self.state, response_id="response-2")
        second = HumanDecisionResponse(
            decision_id="decision-1",
            response_id="response-4",
            status=HumanResponseStatus.SUBMITTED,
            selected_option_id="yes",
        )
        with self.assertRaises(ValueError):
            self.runtime.respond(completed, second)

    def test_response_identity_must_match_request(self) -> None:
        response = HumanDecisionResponse(
            decision_id="other",
            response_id="response-1",
            status=HumanResponseStatus.SUBMITTED,
            selected_option_id="yes",
        )
        with self.assertRaises(ValueError):
            self.runtime.respond(self.state, response)

    def test_non_submitted_response_cannot_select_option(self) -> None:
        with self.assertRaises(ValueError):
            HumanDecisionResponse(
                decision_id="decision-1",
                response_id="response-1",
                status=HumanResponseStatus.CANCELLED,
                selected_option_id="yes",
            )

    def test_submitted_response_requires_selection(self) -> None:
        with self.assertRaises(ValueError):
            HumanDecisionResponse(
                decision_id="decision-1",
                response_id="response-1",
                status=HumanResponseStatus.SUBMITTED,
            )

    def test_store_is_immutable_and_conflict_aware(self) -> None:
        store = HumanDecisionStore().add(self.state)
        with self.assertRaises(ValueError):
            store.add(self.state)
        self.assertEqual(store.get("decision-1"), self.state)
        self.assertEqual(len(store.list()), 1)

    def test_store_replace_preserves_history_shape(self) -> None:
        store = HumanDecisionStore().add(self.state)
        completed = self.runtime.cancel(self.state, response_id="response-2")
        replaced = store.replace(completed)
        self.assertEqual(replaced.get("decision-1"), completed)

    def test_store_replace_requires_existing_decision(self) -> None:
        with self.assertRaises(ValueError):
            HumanDecisionStore().replace(self.state)

    def test_request_serialization_denies_authority(self) -> None:
        payload = self.request.to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["intent_interpreted"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_response_serialization_denies_authority(self) -> None:
        response = self.runtime.cancel(self.state, response_id="response-2").response
        payload = response.to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["intent_interpreted"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_serialization_is_deterministic(self) -> None:
        self.assertEqual(self.request.to_json(), self.request.to_json())
        response = self.runtime.cancel(self.state, response_id="response-2").response
        self.assertEqual(response.to_json(), response.to_json())
        self.assertEqual(json.loads(response.to_json())["status"], "CANCELLED")

    def test_human_response_is_not_authorization(self) -> None:
        response = HumanDecisionResponse(
            decision_id="decision-1",
            response_id="response-1",
            status=HumanResponseStatus.SUBMITTED,
            selected_option_id="yes",
        )
        payload = response.to_dict()
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])


if __name__ == "__main__":
    unittest.main()
