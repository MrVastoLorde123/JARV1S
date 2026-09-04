import json
import unittest
from dataclasses import FrozenInstanceError

from src.knowledge.entities import Entity, EntityType
from src.knowledge.identity import (
    EntityIdentityResolver,
    IdentityResolution,
    IdentityResolutionError,
    IdentityResolutionStatus,
    MAX_CANDIDATES,
    MAX_REASON_LENGTH,
    normalize_identity_reference,
)


class IdentityResolutionTests(unittest.TestCase):
    def make_entity(self, entity_id="person-1", name="JARVIS User", entity_type=EntityType.PERSON, metadata=None):
        return Entity(
            entity_id=entity_id,
            entity_type=entity_type,
            canonical_name=name,
            metadata={} if metadata is None else metadata,
        )

    def test_normalization_only_removes_presentation_variance(self):
        self.assertEqual(normalize_identity_reference("  JARVIS   User "), "jarvis user")
        self.assertEqual(normalize_identity_reference("JARVIS USER"), "jarvis user")

    def test_exact_name_match_with_matching_type(self):
        result = EntityIdentityResolver().resolve(
            " JARVIS User ",
            (self.make_entity(),),
            expected_type=EntityType.PERSON,
        )
        self.assertEqual(result.status, IdentityResolutionStatus.EXACT_MATCH)
        self.assertEqual(result.entity_id, "person-1")
        self.assertEqual(result.score, 1.0)

    def test_exact_name_without_type_remains_possible_not_identity_guaranteed(self):
        result = EntityIdentityResolver().resolve(
            "JARVIS User",
            (self.make_entity(),),
        )
        self.assertEqual(result.status, IdentityResolutionStatus.POSSIBLE_MATCH)
        self.assertEqual(result.entity_id, "person-1")
        self.assertLess(result.score, 1.0)
        self.assertFalse(result.to_dict()["identity_guaranteed"])

    def test_alias_can_produce_possible_match(self):
        result = EntityIdentityResolver().resolve(
            "Mero",
            (
                self.make_entity(metadata={"aliases": ["Mero", "Jero"]}),
            ),
        )
        self.assertEqual(result.status, IdentityResolutionStatus.POSSIBLE_MATCH)
        self.assertEqual(result.entity_id, "person-1")
        self.assertIn("metadata_alias_exact", result.reasons)

    def test_type_conflict_prevents_false_match(self):
        result = EntityIdentityResolver().resolve(
            "JARVIS User",
            (self.make_entity(entity_type=EntityType.PROJECT),),
            expected_type=EntityType.PERSON,
        )
        self.assertEqual(result.status, IdentityResolutionStatus.NO_MATCH)
        self.assertIsNone(result.entity_id)
        self.assertIn("entity_type_conflict", result.reasons)

    def test_no_candidates(self):
        result = EntityIdentityResolver().resolve("Unknown", ())
        self.assertEqual(result.status, IdentityResolutionStatus.NO_MATCH)
        self.assertEqual(result.reasons, ("no_candidates",))

    def test_ambiguous_top_score_is_conflict(self):
        candidates = (
            self.make_entity(entity_id="person-1", name="Alex"),
            self.make_entity(entity_id="person-2", name="Alex"),
        )
        result = EntityIdentityResolver().resolve("Alex", candidates)
        self.assertEqual(result.status, IdentityResolutionStatus.CONFLICT)
        self.assertIsNone(result.entity_id)
        self.assertIn("multiple_candidates_share_top_score", result.reasons)

    def test_substring_match_is_only_possible_when_threshold_is_met(self):
        result = EntityIdentityResolver().resolve(
            "JARVIS",
            (self.make_entity(name="JARVIS User"),),
        )
        self.assertEqual(result.status, IdentityResolutionStatus.NO_MATCH)
        self.assertIsNone(result.entity_id)

    def test_result_is_immutable_and_serializable(self):
        result = IdentityResolution(
            reference="JARVIS User",
            entity_id="person-1",
            entity_type=EntityType.PERSON,
            status=IdentityResolutionStatus.POSSIBLE_MATCH,
            score=0.9,
            reasons=("metadata_alias_exact",),
        )
        with self.assertRaises(FrozenInstanceError):
            result.score = 0.1
        self.assertEqual(json.loads(result.to_json()), result.to_dict())

    def test_invalid_result_bounds_are_rejected(self):
        with self.assertRaises(IdentityResolutionError):
            IdentityResolution("x", None, None, IdentityResolutionStatus.NO_MATCH, -0.1)
        with self.assertRaises(IdentityResolutionError):
            IdentityResolution("x", None, None, IdentityResolutionStatus.NO_MATCH, 1.1)
        with self.assertRaises(IdentityResolutionError):
            IdentityResolution("x", None, None, IdentityResolutionStatus.NO_MATCH, 0.5, ("x" * (MAX_REASON_LENGTH + 1),))

    def test_candidate_count_is_bounded(self):
        candidates = tuple(self.make_entity(entity_id=f"p-{i}", name=f"Person {i}") for i in range(MAX_CANDIDATES + 1))
        with self.assertRaises(IdentityResolutionError):
            EntityIdentityResolver().resolve("Person", candidates)

    def test_identity_resolution_has_no_authority_semantics(self):
        result = EntityIdentityResolver().resolve("JARVIS User", (self.make_entity(),))
        payload = result.to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])

    def test_invalid_reference_and_candidate_inputs_are_rejected(self):
        with self.assertRaises(IdentityResolutionError):
            EntityIdentityResolver().resolve("   ", ())
        with self.assertRaises(IdentityResolutionError):
            EntityIdentityResolver().resolve("x", ("not an entity",))


if __name__ == "__main__":
    unittest.main(verbosity=2)
