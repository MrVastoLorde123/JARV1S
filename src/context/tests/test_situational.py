import json
import unittest

from src.context.situational import (
    MAX_SIGNALS,
    MAX_SIGNAL_ID_LENGTH,
    MAX_VALUE_LENGTH,
    SituationSignal,
    SituationalContext,
    SituationalContextValidationError,
)
from src.context.world_state import ContextState


class SituationalContextTests(unittest.TestCase):
    def context(self):
        return ContextState(
            context_id="ctx-1",
            state={"location": "work", "active_project": "jarvis"},
            source_refs=("source-1",),
            observed_at="2026-01-03T10:00:00+00:00",
        )

    def signal(self, signal_id="signal-1", category="environment", value="normal", source_ref="source-1"):
        return SituationSignal(
            signal_id=signal_id,
            category=category,
            value=value,
            source_ref=source_ref,
        )

    def test_signal_requires_id(self):
        with self.assertRaises(SituationalContextValidationError):
            self.signal(signal_id=" ")

    def test_signal_requires_category(self):
        with self.assertRaises(SituationalContextValidationError):
            self.signal(category=" ")

    def test_signal_id_and_source_are_bounded(self):
        with self.assertRaises(SituationalContextValidationError):
            self.signal(signal_id="x" * (MAX_SIGNAL_ID_LENGTH + 1))
        with self.assertRaises(SituationalContextValidationError):
            self.signal(source_ref="x" * (MAX_SIGNAL_ID_LENGTH + 1))

    def test_signal_value_is_immutable_and_json_like(self):
        signal = self.signal(value={"nested": ["a", "b"]})
        with self.assertRaises(TypeError):
            signal.value["nested"][0] = "changed"

    def test_signal_rejects_unsupported_value_types(self):
        with self.assertRaises(SituationalContextValidationError):
            self.signal(value=object())

    def test_context_requires_context_state(self):
        with self.assertRaises(SituationalContextValidationError):
            SituationalContext(context="not-context", signals=())

    def test_signals_require_tuple(self):
        with self.assertRaises(SituationalContextValidationError):
            SituationalContext(context=self.context(), signals=[self.signal()])

    def test_signal_ids_must_be_unique(self):
        first = self.signal("signal-1")
        second = self.signal("signal-1", category="network")
        with self.assertRaises(SituationalContextValidationError):
            SituationalContext(context=self.context(), signals=(first, second))

    def test_signal_count_is_bounded(self):
        signals = tuple(self.signal(f"signal-{index}") for index in range(MAX_SIGNALS + 1))
        with self.assertRaises(SituationalContextValidationError):
            SituationalContext(context=self.context(), signals=signals)

    def test_lookup_by_id_and_category(self):
        signals = (
            self.signal("signal-1", "network", "online"),
            self.signal("signal-2", "environment", "office"),
        )
        situation = SituationalContext(self.context(), signals)
        self.assertEqual(situation.signal("signal-1").value, "online")
        self.assertEqual(tuple(item.signal_id for item in situation.by_category("NETWORK")), ("signal-1",))

    def test_with_signal_returns_new_context(self):
        original = SituationalContext(self.context(), (self.signal(),))
        updated = original.with_signal(self.signal("signal-2"))
        self.assertEqual(len(original.signals), 1)
        self.assertEqual(len(updated.signals), 2)

    def test_with_signal_rejects_duplicate_id(self):
        situation = SituationalContext(self.context(), (self.signal(),))
        with self.assertRaises(SituationalContextValidationError):
            situation.with_signal(self.signal())

    def test_situation_is_immutable(self):
        situation = SituationalContext(self.context(), (self.signal(),))
        with self.assertRaises(AttributeError):
            situation.signals = ()

    def test_serialization_is_deterministic_and_non_authoritative(self):
        situation = SituationalContext(self.context(), (self.signal(),))
        first = situation.to_json()
        second = situation.to_json()
        self.assertEqual(first, second)
        payload = json.loads(first)
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["fact_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])

    def test_signal_serialization_preserves_source_reference(self):
        payload = self.signal().to_dict()
        self.assertEqual(payload["source_ref"], "source-1")
        self.assertFalse(payload["truth_guaranteed"])

    def test_empty_signals_are_valid(self):
        situation = SituationalContext(self.context())
        self.assertEqual(situation.signals, ())


if __name__ == "__main__":
    unittest.main()
