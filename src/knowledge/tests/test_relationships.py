import json
import unittest
from types import MappingProxyType

from src.knowledge.relationships import (
    Relationship,
    RelationshipType,
    RelationshipValidationError,
    MAX_RELATIONSHIP_EVIDENCE_REFS,
    MAX_RELATIONSHIP_ID_LENGTH,
    MAX_RELATIONSHIP_METADATA_ITEMS,
)


class RelationshipBoundaryTests(unittest.TestCase):
    def make_relationship(self, **overrides):
        values = {
            "relationship_id": "relationship-001",
            "relationship_type": RelationshipType.WORKS_ON,
            "source_entity_id": "person-001",
            "target_entity_id": "project-001",
            "metadata": {"role": "builder", "active": True},
            "evidence_refs": ("memory-001", "evidence-001"),
        }
        values.update(overrides)
        return Relationship(**values)

    def test_supported_relationship_types_are_explicit(self):
        expected = {
            "works_on", "owns", "knows", "depends_on", "uses",
            "located_at", "related_to", "part_of", "learned_from",
            "supports", "conflicts_with",
        }
        self.assertEqual({item.value for item in RelationshipType}, expected)

    def test_relationship_constructs_from_enum_and_string_value(self):
        enum_relationship = self.make_relationship()
        string_relationship = self.make_relationship(relationship_type="supports")
        self.assertEqual(enum_relationship.relationship_type, RelationshipType.WORKS_ON)
        self.assertEqual(string_relationship.relationship_type, RelationshipType.SUPPORTS)

    def test_entity_endpoints_are_bounded_non_empty_strings(self):
        for field_name in ("source_entity_id", "target_entity_id"):
            with self.assertRaises(RelationshipValidationError):
                self.make_relationship(**{field_name: ""})
            with self.assertRaises(RelationshipValidationError):
                self.make_relationship(**{field_name: "x" * (MAX_RELATIONSHIP_ID_LENGTH + 1)})

    def test_relationship_is_frozen(self):
        relationship = self.make_relationship()
        with self.assertRaises((AttributeError, TypeError)):
            relationship.target_entity_id = "changed"

    def test_metadata_is_defensively_frozen(self):
        original = {"nested": {"value": "before"}}
        relationship = self.make_relationship(metadata=original)
        self.assertIsInstance(relationship.metadata, MappingProxyType)
        original["nested"]["value"] = "after"
        self.assertEqual(relationship.metadata["nested"]["value"], "before")
        with self.assertRaises(TypeError):
            relationship.metadata["new"] = "value"

    def test_evidence_refs_are_unique_and_bounded(self):
        with self.assertRaises(RelationshipValidationError):
            self.make_relationship(evidence_refs=("memory-001", "memory-001"))
        too_many = tuple(f"ref-{index}" for index in range(MAX_RELATIONSHIP_EVIDENCE_REFS + 1))
        with self.assertRaises(RelationshipValidationError):
            self.make_relationship(evidence_refs=too_many)

    def test_metadata_is_bounded(self):
        too_many = {f"key-{index}": index for index in range(MAX_RELATIONSHIP_METADATA_ITEMS + 1)}
        with self.assertRaises(RelationshipValidationError):
            self.make_relationship(metadata=too_many)

    def test_relationship_id_is_bounded(self):
        with self.assertRaises(RelationshipValidationError):
            self.make_relationship(relationship_id="x" * (MAX_RELATIONSHIP_ID_LENGTH + 1))

    def test_deterministic_json_serialization(self):
        relationship = self.make_relationship()
        first = relationship.to_json()
        second = relationship.to_json()
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), relationship.to_dict())

    def test_serialization_contains_non_authority_boundaries(self):
        payload = self.make_relationship().to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["fact_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])

    def test_relationship_does_not_claim_authority_or_intent(self):
        relationship = self.make_relationship()
        forbidden = {
            "authorization", "authorization_id", "policy", "policy_decision",
            "confirmation", "execution", "permission", "intent",
        }
        self.assertTrue(forbidden.isdisjoint(vars(relationship)))

    def test_relationship_is_association_not_fact(self):
        relationship = self.make_relationship()
        self.assertEqual(relationship.source_entity_id, "person-001")
        self.assertEqual(relationship.target_entity_id, "project-001")
        self.assertFalse(relationship.to_dict()["fact_guaranteed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
