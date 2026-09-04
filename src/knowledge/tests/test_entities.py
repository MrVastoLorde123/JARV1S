import json
import unittest
from types import MappingProxyType

from src.knowledge.entities import (
    Entity,
    EntityType,
    EntityValidationError,
    MAX_ENTITY_EVIDENCE_REFS,
    MAX_ENTITY_ID_LENGTH,
    MAX_ENTITY_METADATA_ITEMS,
    MAX_ENTITY_NAME_LENGTH,
)


class EntityBoundaryTests(unittest.TestCase):
    def make_entity(self, **overrides):
        values = {
            "entity_id": "entity-001",
            "entity_type": EntityType.PERSON,
            "canonical_name": "JARVIS User",
            "metadata": {
                "role": "builder",
                "tags": ["python", "PCVUE"],
            },
            "evidence_refs": ("memory-001", "evidence-001"),
        }
        values.update(overrides)
        return Entity(**values)

    def test_supported_entity_types_are_explicit(self):
        self.assertEqual(EntityType.PERSON.value, "PERSON")
        self.assertEqual(EntityType.PROJECT.value, "PROJECT")
        self.assertEqual(EntityType.ORGANIZATION.value, "ORGANIZATION")
        self.assertEqual(EntityType.PRODUCT.value, "PRODUCT")
        self.assertEqual(EntityType.SYSTEM.value, "SYSTEM")
        self.assertEqual(EntityType.DEVICE.value, "DEVICE")
        self.assertEqual(EntityType.LOCATION.value, "LOCATION")
        self.assertEqual(EntityType.CONCEPT.value, "CONCEPT")
        self.assertEqual(EntityType.SKILL.value, "SKILL")
        self.assertEqual(EntityType.GOAL.value, "GOAL")
        self.assertEqual(EntityType.DOCUMENT.value, "DOCUMENT")
        self.assertEqual(EntityType.EVENT.value, "EVENT")

    def test_entity_constructs_from_enum_and_string_value(self):
        enum_entity = self.make_entity()
        string_entity = self.make_entity(entity_type="PROJECT")

        self.assertEqual(enum_entity.entity_type, EntityType.PERSON)
        self.assertEqual(string_entity.entity_type, EntityType.PROJECT)

    def test_metadata_is_immutable_and_defensively_frozen(self):
        original = {"nested": {"value": "before"}, "items": ["a", "b"]}
        entity = self.make_entity(metadata=original)

        self.assertIsInstance(entity.metadata, MappingProxyType)
        original["nested"]["value"] = "after"
        original["items"].append("c")

        self.assertEqual(entity.metadata["nested"]["value"], "before")
        self.assertEqual(entity.metadata["items"], ("a", "b"))
        with self.assertRaises(TypeError):
            entity.metadata["new"] = "value"
        with self.assertRaises(TypeError):
            entity.metadata["nested"]["value"] = "after"

    def test_entity_is_frozen(self):
        entity = self.make_entity()
        with self.assertRaises((AttributeError, TypeError)):
            entity.canonical_name = "Changed"

    def test_evidence_refs_are_unique_and_bounded(self):
        with self.assertRaises(EntityValidationError):
            self.make_entity(evidence_refs=("memory-001", "memory-001"))

        too_many = tuple(f"ref-{index}" for index in range(MAX_ENTITY_EVIDENCE_REFS + 1))
        with self.assertRaises(EntityValidationError):
            self.make_entity(evidence_refs=too_many)

    def test_bounded_identity_and_name(self):
        with self.assertRaises(EntityValidationError):
            self.make_entity(entity_id="x" * (MAX_ENTITY_ID_LENGTH + 1))

        with self.assertRaises(EntityValidationError):
            self.make_entity(canonical_name="x" * (MAX_ENTITY_NAME_LENGTH + 1))

        with self.assertRaises(EntityValidationError):
            self.make_entity(entity_id="   ")

        with self.assertRaises(EntityValidationError):
            self.make_entity(canonical_name="")

    def test_metadata_is_bounded_and_json_like(self):
        too_many = {f"key-{index}": index for index in range(MAX_ENTITY_METADATA_ITEMS + 1)}
        with self.assertRaises(EntityValidationError):
            self.make_entity(metadata=too_many)

        with self.assertRaises(EntityValidationError):
            self.make_entity(metadata={"unsupported": object()})

    def test_evidence_refs_require_non_empty_strings(self):
        with self.assertRaises(EntityValidationError):
            self.make_entity(evidence_refs=("memory-001", ""))

        with self.assertRaises(EntityValidationError):
            self.make_entity(evidence_refs=("memory-001", 42))

    def test_deterministic_serialization(self):
        entity = self.make_entity()
        first = entity.to_json()
        second = entity.to_json()

        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), entity.to_dict())

    def test_serialization_contains_non_authority_boundaries(self):
        payload = self.make_entity().to_dict()

        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["fact_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])

    def test_evidence_refs_are_references_not_claims(self):
        entity = self.make_entity(evidence_refs=("memory-123",))

        self.assertEqual(entity.evidence_refs, ("memory-123",))
        self.assertNotIn("truth", entity.to_dict())
        self.assertNotIn("fact", entity.to_dict())

    def test_no_authority_semantics_are_fields_on_entity(self):
        entity = self.make_entity()
        forbidden = {
            "authorization",
            "authorization_id",
            "policy",
            "policy_decision",
            "confirmation",
            "execution",
            "permission",
            "intent",
        }

        self.assertTrue(forbidden.isdisjoint(vars(entity)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
