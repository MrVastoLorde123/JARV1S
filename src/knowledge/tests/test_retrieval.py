import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.knowledge.entities import Entity, EntityType
from src.knowledge.persistence import EntityRepository
from src.knowledge.retrieval import (
    KnowledgeMatch,
    KnowledgeRetrievalError,
    KnowledgeRetriever,
    RetrievalMatchField,
)


class KnowledgeRetrieverTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "knowledge.db"
        repository = EntityRepository(
            connection_factory=lambda: sqlite3.connect(self.database_path)
        )
        self.repository = repository
        self.retriever = KnowledgeRetriever(repository)
        self.person = Entity(
            entity_id="person-1",
            entity_type=EntityType.PERSON,
            canonical_name="Mero",
            metadata={"role": "builder", "skills": ["Python", "Networking"]},
            evidence_refs=("chat-1",),
        )
        self.project = Entity(
            entity_id="project-1",
            entity_type=EntityType.PROJECT,
            canonical_name="JARVIS",
            metadata={"status": "active", "owner": "person-1"},
            evidence_refs=("doc-1",),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def seed(self):
        self.repository.save(self.person)
        self.repository.save(self.project)

    def test_get_delegates_to_persistent_identity(self):
        self.seed()
        restored = self.retriever.get("person-1")
        self.assertEqual(restored, self.person)

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.retriever.get("missing"))

    def test_by_type_returns_matching_entities(self):
        self.seed()
        self.assertEqual(self.retriever.by_type(EntityType.PERSON), (self.person,))
        self.assertEqual(self.retriever.by_type("PROJECT"), (self.project,))

    def test_by_type_rejects_unknown_type(self):
        with self.assertRaises(KnowledgeRetrievalError):
            self.retriever.by_type("UNKNOWN")

    def test_search_matches_canonical_name_case_insensitively(self):
        self.seed()
        result = self.retriever.search("mero")
        self.assertEqual(result.entities, (self.person,))
        self.assertEqual(result.matches[0].matched_fields, (RetrievalMatchField.CANONICAL_NAME,))

    def test_search_matches_entity_id_and_type(self):
        self.seed()
        result = self.retriever.search("project")
        self.assertEqual(result.entities, (self.project,))
        self.assertIn(RetrievalMatchField.ENTITY_ID, result.matches[0].matched_fields)
        self.assertIn(RetrievalMatchField.ENTITY_TYPE, result.matches[0].matched_fields)

    def test_search_matches_nested_metadata_and_evidence(self):
        self.seed()
        metadata_result = self.retriever.search("networking")
        evidence_result = self.retriever.search("chat-1")
        self.assertIn(RetrievalMatchField.METADATA, metadata_result.matches[0].matched_fields)
        self.assertIn(RetrievalMatchField.EVIDENCE_REF, evidence_result.matches[0].matched_fields)

    def test_search_is_deterministically_ordered(self):
        self.seed()
        first = self.retriever.search("-")
        second = self.retriever.search("-")
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(tuple(match.entity.entity_id for match in first.matches), ("person-1", "project-1"))

    def test_search_result_is_bounded(self):
        for index in range(4):
            self.repository.save(
                Entity(
                    entity_id=f"entity-{index}",
                    entity_type=EntityType.CONCEPT,
                    canonical_name="shared",
                )
            )
        retriever = KnowledgeRetriever(self.repository, max_results=2)
        result = retriever.search("shared")
        self.assertEqual(len(result.matches), 2)
        self.assertTrue(result.truncated)

    def test_query_is_bounded_and_normalized(self):
        with self.assertRaises(KnowledgeRetrievalError):
            self.retriever.search("x" * 257)
        self.seed()
        self.assertEqual(self.retriever.search("  MeRo  ").query, "MeRo")

    def test_match_requires_entity_and_fields(self):
        with self.assertRaises(TypeError):
            KnowledgeMatch(entity="bad", matched_fields=(RetrievalMatchField.ENTITY_ID,))
        with self.assertRaises(KnowledgeRetrievalError):
            KnowledgeMatch(entity=self.person, matched_fields=())

    def test_serialization_preserves_non_authority_boundary(self):
        self.seed()
        payload = self.retriever.search("mero").to_dict()
        encoded = json.dumps(payload, sort_keys=True)
        self.assertEqual(json.loads(encoded)["matches"][0]["entity"]["canonical_name"], "Mero")
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["fact_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])

    def test_retrieval_does_not_mutate_entities(self):
        self.seed()
        result = self.retriever.search("python")
        self.assertEqual(result.entities[0], self.person)
        self.assertEqual(self.repository.require("person-1"), self.person)

    def test_all_returns_persisted_entities_in_repository_order(self):
        self.seed()
        self.assertEqual(self.retriever.all(), (self.person, self.project))


if __name__ == "__main__":
    unittest.main()
