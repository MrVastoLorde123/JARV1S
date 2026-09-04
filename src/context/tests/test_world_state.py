import json
import unittest

from src.context.world_state import (
    ContextState,
    ContextStateValidationError,
    MAX_CONTEXT_ID_LENGTH,
    MAX_STATE_ITEMS,
)


class ContextStateTests(unittest.TestCase):
    def make_state(self):
        return ContextState(
            context_id="ctx-1",
            state={"current_project": "JARVIS", "status": {"phase": "M14"}},
            source_refs=("memory-1", "entity-1"),
            observed_at="2026-09-03T12:00:00+00:00",
        )

    def test_constructs_and_is_immutable(self):
        state = self.make_state()
        with self.assertRaises(AttributeError):
            state.context_id = "changed"

    def test_nested_state_is_defensively_frozen(self):
        state = self.make_state()
        with self.assertRaises(TypeError):
            state.state["status"]["phase"] = "other"

    def test_state_updates_return_new_value(self):
        state = self.make_state()
        updated = state.with_state(active=True)
        self.assertIsNot(updated, state)
        self.assertNotIn("active", state.state)
        self.assertTrue(updated.state["active"])

    def test_empty_update_returns_same_value(self):
        state = self.make_state()
        self.assertIs(state.with_state(), state)

    def test_source_refs_are_unique_and_bounded(self):
        with self.assertRaises(ContextStateValidationError):
            ContextState(context_id="ctx", source_refs=("a", "a"))
        with self.assertRaises(ContextStateValidationError):
            ContextState(
                context_id="ctx",
                source_refs=tuple(f"ref-{i}" for i in range(MAX_STATE_ITEMS + 1)),
            )

    def test_state_item_count_is_bounded(self):
        with self.assertRaises(ContextStateValidationError):
            ContextState(
                context_id="ctx",
                state={f"key-{i}": i for i in range(MAX_STATE_ITEMS + 1)},
            )

    def test_context_id_is_bounded(self):
        with self.assertRaises(ContextStateValidationError):
            ContextState(context_id="x" * (MAX_CONTEXT_ID_LENGTH + 1))

    def test_observed_at_must_be_iso8601(self):
        with self.assertRaises(ContextStateValidationError):
            ContextState(context_id="ctx", observed_at="not-a-time")

    def test_supported_json_like_values_round_trip(self):
        state = ContextState(
            context_id="ctx",
            state={"items": [1, "two", {"three": True}], "empty": None},
        )
        payload = json.loads(state.to_json())
        self.assertEqual(payload["state"]["items"][2]["three"], True)

    def test_serialization_is_deterministic(self):
        state = self.make_state()
        self.assertEqual(state.to_json(), state.to_json())

    def test_serialization_has_no_authority(self):
        payload = self.make_state().to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["fact_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])

    def test_state_rejects_non_json_like_values(self):
        with self.assertRaises(ContextStateValidationError):
            ContextState(context_id="ctx", state={"bad": object()})

    def test_non_finite_numbers_are_rejected(self):
        with self.assertRaises(ContextStateValidationError):
            ContextState(context_id="ctx", state={"bad": float("nan")})

    def test_source_ref_length_is_bounded(self):
        with self.assertRaises(ContextStateValidationError):
            ContextState(context_id="ctx", source_refs=("x" * 257,))


if __name__ == "__main__":
    unittest.main()
