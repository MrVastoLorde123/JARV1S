from __future__ import annotations

import unittest

from src.core.interface_backend import (
    InterfaceRequest,
    InterfaceResponse,
    InterfaceResponseStatus,
)
from src.core.runtime_kernel import JarvisRuntime
from src.core.world_model import (
    ValidityWindow,
    WorldEntity,
    WorldEntityType,
    WorldModelSystem,
    WorldObservation,
    WorldObservationAction,
    WorldRelation,
    WorldSnapshot,
)


_NOW = "2026-09-17T15:00:00+00:00"
_BEFORE = "2026-09-17T14:00:00+00:00"
_AFTER = "2026-09-17T16:00:00+00:00"


def _window(*, observed: str = _BEFORE, valid_from: str = _BEFORE, valid_until: str | None = None) -> ValidityWindow:
    return ValidityWindow(
        observed_at=observed,
        valid_from=valid_from,
        valid_until=valid_until,
    )


def _entity(entity_id: str, label: str, *, confidence: float = 0.8, observed: str = _BEFORE) -> WorldEntity:
    return WorldEntity(
        entity_id=entity_id,
        entity_type=WorldEntityType.DEVICE,
        label=label,
        attributes={"location": "lab"},
        confidence=confidence,
        provenance_ids=(f"prov-{entity_id}",),
        validity=_window(observed=observed, valid_from=observed),
    )


def _entity_observation(observation_id: str, entity: WorldEntity) -> WorldObservation:
    return WorldObservation(
        observation_id=observation_id,
        observed_at=entity.validity.observed_at,
        provenance_ids=entity.provenance_ids,
        entity=entity,
    )


class _Orchestration:
    def dispatch(self, request: InterfaceRequest) -> InterfaceResponse:
        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={},
            metadata={},
        )


class Phase6WorldModelTests(unittest.TestCase):
    def test_validity_window_enforces_temporal_bounds(self) -> None:
        window = _window(valid_until=_NOW)
        self.assertTrue(window.is_active(_BEFORE))
        self.assertFalse(window.is_active(_NOW))
        with self.assertRaises(ValueError):
            ValidityWindow(
                observed_at=_BEFORE,
                valid_from=_NOW,
            )

    def test_entity_contract_is_immutable_and_bounded(self) -> None:
        entity = _entity("device-1", "Panel A")
        self.assertEqual(entity.entity_id, "device-1")
        self.assertFalse(entity.to_context()["truth_established"])
        with self.assertRaises(ValueError):
            _entity("device-2", "Panel B", confidence=1.1)

    def test_relation_requires_bounded_confidence_and_nonempty_identity(self) -> None:
        relation = WorldRelation(
            relation_id="rel-1",
            source_entity_id="device-1",
            target_entity_id="device-2",
            predicate="CONNECTED_TO",
            confidence=0.7,
            provenance_ids=("prov-rel-1",),
            validity=_window(),
        )
        self.assertEqual(relation.predicate, "CONNECTED_TO")
        with self.assertRaises(ValueError):
            WorldRelation(
                relation_id="",
                source_entity_id="device-1",
                target_entity_id="device-2",
                predicate="CONNECTED_TO",
                provenance_ids=("prov-rel-2",),
                validity=_window(),
            )

    def test_observation_requires_provenance(self) -> None:
        entity = _entity("device-1", "Panel A")
        with self.assertRaises(ValueError):
            WorldObservation(
                observation_id="obs-1",
                observed_at=_BEFORE,
                provenance_ids=(),
                entity=entity,
            )

    def test_observation_requires_exactly_one_payload(self) -> None:
        entity = _entity("device-1", "Panel A")
        with self.assertRaises(ValueError):
            WorldObservation(
                observation_id="obs-1",
                observed_at=_BEFORE,
                provenance_ids=("prov-1",),
            )

    def test_duplicate_identical_observation_is_idempotent(self) -> None:
        model = WorldModelSystem()
        observation = _entity_observation("obs-1", _entity("device-1", "Panel A"))
        self.assertTrue(model.observe(observation))
        self.assertFalse(model.observe(observation))
        self.assertEqual(len(model.observations()), 1)

    def test_conflicting_observations_remain_visible_as_conflict(self) -> None:
        model = WorldModelSystem()
        first = _entity_observation("obs-1", _entity("device-1", "Panel A", confidence=0.6))
        second = _entity_observation("obs-2", _entity("device-1", "Panel B", confidence=0.9))
        model.observe(first)
        model.observe(second)
        snapshot = model.snapshot(generated_at=_NOW)
        self.assertIsInstance(snapshot, WorldSnapshot)
        self.assertEqual(snapshot.entities[0].label, "Panel B")
        self.assertEqual(len(snapshot.conflicts), 1)
        self.assertTrue(snapshot.is_ambiguous)
        self.assertFalse(snapshot.conflicts[0].to_context()["truth_established"])

    def test_temporally_expired_observation_is_excluded(self) -> None:
        model = WorldModelSystem()
        entity = _entity("device-1", "Panel A")
        expired = WorldEntity(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            label=entity.label,
            attributes=entity.attributes,
            confidence=entity.confidence,
            provenance_ids=entity.provenance_ids,
            validity=_window(valid_until=_NOW),
        )
        model.observe(_entity_observation("obs-1", expired))
        snapshot = model.snapshot(generated_at=_NOW)
        self.assertEqual(snapshot.entities, ())

    def test_retraction_removes_previous_observation_from_current_view(self) -> None:
        model = WorldModelSystem()
        asserted = _entity_observation("obs-1", _entity("device-1", "Panel A"))
        model.observe(asserted)
        retract = WorldObservation(
            observation_id="obs-2",
            observed_at=_NOW,
            provenance_ids=("prov-retract",),
            action=WorldObservationAction.RETRACT,
            retracts_observation_id="obs-1",
        )
        self.assertTrue(model.observe(retract))
        snapshot = model.snapshot(generated_at=_NOW)
        self.assertEqual(snapshot.entities, ())

    def test_unknown_retraction_is_rejected(self) -> None:
        model = WorldModelSystem()
        with self.assertRaises(ValueError):
            model.observe(
                WorldObservation(
                    observation_id="obs-1",
                    observed_at=_NOW,
                    provenance_ids=("prov-1",),
                    action=WorldObservationAction.RETRACT,
                    retracts_observation_id="missing",
                )
            )

    def test_snapshot_is_deterministic_for_identical_state(self) -> None:
        model = WorldModelSystem()
        model.observe(_entity_observation("obs-1", _entity("device-1", "Panel A")))
        first = model.snapshot(generated_at=_NOW)
        second = model.snapshot(generated_at=_NOW)
        self.assertEqual(first.snapshot_id, second.snapshot_id)
        self.assertEqual(first.to_context(), second.to_context())

    def test_snapshot_contains_provenance_backed_observation_ids(self) -> None:
        model = WorldModelSystem()
        observation = _entity_observation("obs-1", _entity("device-1", "Panel A"))
        model.observe(observation)
        snapshot = model.snapshot(generated_at=_NOW)
        self.assertEqual(snapshot.observation_ids, ("obs-1",))
        self.assertEqual(snapshot.entities[0].provenance_ids, ("prov-device-1",))

    def test_relation_requires_current_source_and_target_as_context_only(self) -> None:
        model = WorldModelSystem()
        relation = WorldRelation(
            relation_id="rel-1",
            source_entity_id="device-1",
            target_entity_id="device-2",
            predicate="CONNECTED_TO",
            confidence=0.9,
            provenance_ids=("prov-rel-1",),
            validity=_window(),
        )
        model.observe(
            WorldObservation(
                observation_id="obs-rel-1",
                observed_at=_BEFORE,
                provenance_ids=("prov-rel-1",),
                relation=relation,
            )
        )
        snapshot = model.snapshot(generated_at=_NOW)
        self.assertEqual(snapshot.relations[0].source_entity_id, "device-1")
        self.assertFalse(snapshot.relations[0].to_context()["authority_granted"])

    def test_system_reports_no_authority_or_execution(self) -> None:
        model = WorldModelSystem()
        summary = model.summary()
        self.assertFalse(summary["truth_established"])
        self.assertFalse(summary["authority_granted"])
        self.assertFalse(summary["execution_requested"])
        self.assertFalse(summary["provider_selected"])
        self.assertFalse(model.authorizes_execution)
        self.assertFalse(model.executes_capability)
        self.assertFalse(model.mutates_external_state)
        self.assertFalse(model.persists_state)
        self.assertFalse(model.establishes_truth)
        self.assertFalse(model.establishes_certainty)
        self.assertFalse(model.selects_provider)

    def test_runtime_accepts_world_model_without_gaining_authority(self) -> None:
        world_model = WorldModelSystem()
        runtime = JarvisRuntime(
            orchestration=_Orchestration(),
            session_id="session-world-1",
            actor_id="actor-world-1",
            world_model=world_model,
        )
        self.assertIs(runtime.world_model, world_model)
        self.assertFalse(runtime.authorizes_execution)
        self.assertFalse(runtime.executes_capability)
        self.assertFalse(runtime.mutates_state)
        self.assertFalse(runtime.persists_state)
        self.assertFalse(runtime.establishes_truth)
        self.assertFalse(runtime.establishes_certainty)
        self.assertFalse(runtime.is_ai_provider)

    def test_runtime_rejects_wrong_world_model_type(self) -> None:
        with self.assertRaises(TypeError):
            JarvisRuntime(
                orchestration=_Orchestration(),
                session_id="session-world-1",
                actor_id="actor-world-1",
                world_model=object(),
            )

    def test_context_projection_is_provider_neutral(self) -> None:
        model = WorldModelSystem()
        model.observe(_entity_observation("obs-1", _entity("device-1", "Panel A")))
        projected = model.to_context(generated_at=_NOW)
        self.assertIn("snapshot", projected)
        self.assertFalse(projected["truth_established"])
        self.assertFalse(projected["authority_granted"])
        self.assertFalse(projected["execution_requested"])


if __name__ == "__main__":
    unittest.main()
