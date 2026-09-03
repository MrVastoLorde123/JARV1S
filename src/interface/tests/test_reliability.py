import json
import unittest

from src.interface.reliability import (
    InterfaceRecoveryAction,
    InterfaceRecoveryState,
    InterfaceRecoveryStore,
    InterfaceReliabilityRecord,
    InterfaceReliabilityRuntime,
    InterfaceReliabilityState,
)


class InterfaceReliabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = InterfaceReliabilityRuntime()
        self.state = self.runtime.start("req-1")

    def test_empty_state_is_healthy(self) -> None:
        self.assertEqual(self.state.state, InterfaceReliabilityState.HEALTHY)
        self.assertEqual(self.state.recovery_action, InterfaceRecoveryAction.NONE)

    def test_records_are_immutable(self) -> None:
        record = InterfaceReliabilityRecord("rec-1", "req-1", InterfaceReliabilityState.HEALTHY)
        with self.assertRaises(Exception):
            record.state = InterfaceReliabilityState.FAILED

    def test_state_is_immutable_and_bounded(self) -> None:
        with self.assertRaises(Exception):
            self.state.records = ()
        with self.assertRaises(ValueError):
            InterfaceRecoveryState("req-2", max_records=0)

    def test_degrade_records_recovery_eligibility_without_authority(self) -> None:
        state = self.runtime.degrade(
            self.state,
            record_id="rec-1",
            reason="connection interrupted",
            action=InterfaceRecoveryAction.RETRY,
            attempt=1,
        )
        self.assertEqual(state.state, InterfaceReliabilityState.DEGRADED)
        self.assertEqual(state.recovery_action, InterfaceRecoveryAction.RETRY)
        payload = state.to_dict()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])

    def test_recovery_requires_explicit_transport_action(self) -> None:
        with self.assertRaises(ValueError):
            self.runtime.recover(self.state, record_id="rec-1", action=InterfaceRecoveryAction.NONE)
        with self.assertRaises(ValueError):
            self.runtime.recover(self.state, record_id="rec-1", action=InterfaceRecoveryAction.ABANDON)

    def test_recovery_action_is_not_semantic_permission(self) -> None:
        state = self.runtime.recover(
            self.state,
            record_id="rec-1",
            action=InterfaceRecoveryAction.RESUME,
            attempt=2,
        )
        payload = state.to_dict()
        self.assertEqual(payload["recovery_action"], "RESUME")
        self.assertFalse(payload["intent_interpreted"])
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_recovered_state_has_no_recovery_action(self) -> None:
        state = self.runtime.recovered(self.state, record_id="rec-1")
        self.assertEqual(state.state, InterfaceReliabilityState.RECOVERED)
        self.assertEqual(state.recovery_action, InterfaceRecoveryAction.NONE)

    def test_failed_state_requires_explicit_action(self) -> None:
        state = self.runtime.failed(self.state, record_id="rec-1", reason="transport unavailable")
        self.assertEqual(state.state, InterfaceReliabilityState.FAILED)
        self.assertEqual(state.recovery_action, InterfaceRecoveryAction.ABANDON)

    def test_healthy_state_rejects_recovery_action(self) -> None:
        with self.assertRaises(ValueError):
            InterfaceReliabilityRecord(
                "rec-1",
                "req-1",
                InterfaceReliabilityState.HEALTHY,
                InterfaceRecoveryAction.RETRY,
            )

    def test_failed_state_rejects_missing_recovery_action(self) -> None:
        with self.assertRaises(ValueError):
            InterfaceReliabilityRecord(
                "rec-1",
                "req-1",
                InterfaceReliabilityState.FAILED,
                InterfaceRecoveryAction.NONE,
            )

    def test_request_identity_is_preserved(self) -> None:
        state = self.runtime.degrade(self.state, record_id="rec-1", reason="timeout")
        self.assertEqual(state.latest.request_id, "req-1")
        with self.assertRaises(ValueError):
            state.append(
                InterfaceReliabilityRecord(
                    "rec-x", "other", InterfaceReliabilityState.DEGRADED,
                    InterfaceRecoveryAction.RETRY, reason="wrong request"
                )
            )

    def test_record_ids_are_unique(self) -> None:
        state = self.runtime.healthy(self.state, record_id="rec-1")
        with self.assertRaises(ValueError):
            state.append(InterfaceReliabilityRecord("rec-1", "req-1", InterfaceReliabilityState.HEALTHY))

    def test_history_bound_is_enforced(self) -> None:
        state = self.runtime.start("req-2", max_records=1)
        state = self.runtime.healthy(state, record_id="rec-1")
        with self.assertRaises(ValueError):
            self.runtime.healthy(state, record_id="rec-2")

    def test_attempt_must_be_non_negative(self) -> None:
        with self.assertRaises(ValueError):
            InterfaceReliabilityRecord(
                "rec-1", "req-1", InterfaceReliabilityState.DEGRADED,
                InterfaceRecoveryAction.RETRY, attempt=-1
            )

    def test_store_is_immutable_and_conflict_aware(self) -> None:
        store = InterfaceRecoveryStore()
        state = self.runtime.start("req-1")
        store2 = store.add(state)
        with self.assertRaises(ValueError):
            store2.add(state)
        with self.assertRaises(Exception):
            store.states = ()

    def test_store_replace_requires_existing_state(self) -> None:
        store = InterfaceRecoveryStore()
        state = self.runtime.start("req-1")
        with self.assertRaises(ValueError):
            store.replace(state)
        store = store.add(state)
        updated = self.runtime.healthy(state, record_id="rec-1")
        store2 = store.replace(updated)
        self.assertEqual(store2.get("req-1").latest.record_id, "rec-1")

    def test_store_rejects_duplicate_request_states(self) -> None:
        state = self.runtime.start("req-1")
        with self.assertRaises(ValueError):
            InterfaceRecoveryStore(states=(state, state))

    def test_serialization_is_deterministic(self) -> None:
        state = self.runtime.degrade(self.state, record_id="rec-1", reason="timeout")
        self.assertEqual(state.to_json(), state.to_json())
        self.assertEqual(json.loads(state.to_json())["request_id"], "req-1")

    def test_metadata_is_immutable(self) -> None:
        record = InterfaceReliabilityRecord(
            "rec-1", "req-1", InterfaceReliabilityState.HEALTHY,
            metadata={"surface": "chat"}
        )
        with self.assertRaises(TypeError):
            record.metadata["x"] = "y"

    def test_all_states_and_actions_are_transport_level(self) -> None:
        for state in InterfaceReliabilityState:
            for action in InterfaceRecoveryAction:
                if state is InterfaceReliabilityState.HEALTHY and action is not InterfaceRecoveryAction.NONE:
                    continue
                if state is InterfaceReliabilityState.FAILED and action is InterfaceRecoveryAction.NONE:
                    continue
                record = InterfaceReliabilityRecord(
                    f"{state.value}-{action.value}",
                    "req-kinds",
                    state,
                    action,
                )
                payload = record.to_dict()
                self.assertFalse(payload["authority_granted"])
                self.assertFalse(payload["authorization_granted"])
                self.assertFalse(payload["execution_requested"])


if __name__ == "__main__":
    unittest.main()
