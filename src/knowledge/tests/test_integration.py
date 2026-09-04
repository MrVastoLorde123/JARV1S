import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.knowledge.associations import AssociationEvidence, EvidenceBackedAssociation
from src.knowledge.entities import Entity, EntityType
from src.knowledge.integration import KnowledgeIntegrationError, KnowledgeRuntime
from src.knowledge.persistence import EntityRepository
from src.knowledge.relationships import Relationship, RelationshipType


class KnowledgeRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "knowledge.db"
        self.repository = EntityRepository(
            connection_factory=lambda: sqlite3.connect(self.database_path)
        )
        self.person = Entity(
            entity_id="person-1",
            entity_type=EntityType.PERSON,
            canonical_name="Mero",
            metadata={"skill": "python"},
            evidence_refs=("evidence-1",),
        )
        self.project = Entity(
            entity_id="project-1",
            entity_type=EntityType.PROJECT,
            canonical_name="JARVIS",
        )
        self.repository.save(self.person)
        self.repository.save(self.project)
        self.relationship = Relationship(
            relationship_id="rel-1",
            relationship_type=RelationshipType.WORKS_ON,
            source_entity_id="person-1",
            target_entity_id="project-1",
            evidence_refs=("evidence-1",),
        )
        self.association = EvidenceBackedAssociation(
            relationship=self.relationship,
            evidence=(AssociationEvidence("evidence-1", "chat"),),
        )
        self.runtime = KnowledgeRuntime(repository=self.repository)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_entity_uses_existing_retrieval_boundary(self):
        self.assertEqual(self.runtime.get_entity("person-1"), self.person)

    def test_search_entities_uses_existing_retrieval_boundary(self):
        result = self.runtime.search_entities("python")
        self.assertEqual(tuple(item.entity.entity_id for item in result.matches), ("person-1",))

    def test_relationships_are_integrated_without_entity_mutation(self):
        integrated = self.runtime.with_relationship(self.relationship)
        self.assertEqual(integrated.relationships, (self.relationship,))
        self.assertEqual(integrated.get_entity("person-1"), self.person)

    def test_relationships_for_matches_both_endpoints(self):
        integrated = self.runtime.with_relationship(self.relationship)
        self.assertEqual(integrated.relationships_for("person-1"), (self.relationship,))
        self.assertEqual(integrated.relationships_for("project-1"), (self.relationship,))

    def test_association_requires_integrated_relationship(self):
        with self.assertRaises(KnowledgeIntegrationError):
            self.runtime.with_association(self.association)

    def test_association_integrates_after_relationship(self):
        integrated = self.runtime.with_relationship(self.relationship).with_association(self.association)
        self.assertEqual(integrated.associations_for("person-1"), (self.association,))

    def test_duplicate_relationship_is_rejected(self):
        integrated = self.runtime.with_relationship(self.relationship)
        with self.assertRaises(KnowledgeIntegrationError):
            integrated.with_relationship(self.relationship)

    def test_duplicate_association_is_rejected(self):
        integrated = self.runtime.with_relationship(self.relationship).with_association(self.association)
        with self.assertRaises(KnowledgeIntegrationError):
            integrated.with_association(self.association)

    def test_snapshot_combines_existing_knowledge_primitives(self):
        integrated = self.runtime.with_relationship(self.relationship).with_association(self.association)
        snapshot = integrated.snapshot()
        self.assertEqual(tuple(entity.entity_id for entity in snapshot.entities), ("person-1", "project-1"))
        self.assertEqual(snapshot.relationships, (self.relationship,))
        self.assertEqual(snapshot.associations, (self.association,))

    def test_snapshot_serialization_is_non_authoritative(self):
        integrated = self.runtime.with_relationship(self.relationship).with_association(self.association)
        payload = integrated.snapshot().to_dict()
        encoded = json.dumps(payload, sort_keys=True)
        self.assertTrue(encoded)
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["fact_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])

    def test_runtime_updates_are_immutable(self):
        integrated = self.runtime.with_relationship(self.relationship)
        self.assertEqual(self.runtime.relationships, ())
        self.assertEqual(integrated.relationships, (self.relationship,))

    def test_invalid_entity_id_is_rejected_for_relationship_lookup(self):
        with self.assertRaises(KnowledgeIntegrationError):
            self.runtime.relationships_for(" ")

    def test_invalid_entity_id_is_rejected_for_association_lookup(self):
        with self.assertRaises(KnowledgeIntegrationError):
            self.runtime.associations_for(" ")

    def test_matching_entities_returns_retrieval_matches(self):
        integrated = self.runtime.with_relationship(self.relationship)
        matches = integrated.matching_entities("jarvis")
        self.assertEqual(tuple(item.entity.entity_id for item in matches), ("project-1",))


if __name__ == "__main__":
    unittest.main()
