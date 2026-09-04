import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.knowledge.entities import Entity, EntityType
from src.knowledge.persistence import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    EntityPersistenceError,
    EntityRepository,
)


class EntityRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "knowledge.db"
        self.repository = EntityRepository(
            connection_factory=lambda: sqlite3.connect(self.database_path)
        )
        self.entity = Entity(
            entity_id="person-1",
            entity_type=EntityType.PERSON,
            canonical_name="Mero",
            metadata={"role": "builder", "skills": ["python", "networking"]},
            evidence_refs=("evidence-1", "evidence-2"),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialize_creates_entity_table(self):
        self.repository.initialize()
        connection = sqlite3.connect(self.database_path)
        try:
            table = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_entities'"
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(table[0], "knowledge_entities")

    def test_save_and_get_round_trip(self):
        self.repository.save(self.entity)
        restored = self.repository.get("person-1")
        self.assertEqual(restored, self.entity)
        self.assertIsNot(restored, self.entity)

    def test_round_trip_preserves_nested_metadata_and_evidence(self):
        self.repository.save(self.entity)
        restored = self.repository.require("person-1")
        self.assertEqual(restored.metadata["skills"], ("python", "networking"))
        self.assertEqual(restored.evidence_refs, ("evidence-1", "evidence-2"))

    def test_save_rejects_duplicate_identity_without_overwrite(self):
        self.repository.save(self.entity)
        replacement = Entity(
            entity_id="person-1",
            entity_type=EntityType.PERSON,
            canonical_name="Changed",
        )
        with self.assertRaises(EntityAlreadyExistsError):
            self.repository.save(replacement)
        self.assertEqual(self.repository.require("person-1").canonical_name, "Mero")

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.repository.get("missing"))

    def test_require_missing_raises(self):
        with self.assertRaises(EntityNotFoundError):
            self.repository.require("missing")

    def test_list_all_is_deterministically_ordered(self):
        second = Entity(
            entity_id="person-2",
            entity_type=EntityType.PERSON,
            canonical_name="Second",
        )
        self.repository.save(second)
        self.repository.save(self.entity)
        self.assertEqual(
            tuple(entity.entity_id for entity in self.repository.list_all()),
            ("person-1", "person-2"),
        )

    def test_delete_removes_only_selected_entity(self):
        self.repository.save(self.entity)
        self.assertTrue(self.repository.delete("person-1"))
        self.assertIsNone(self.repository.get("person-1"))
        self.assertFalse(self.repository.delete("person-1"))

    def test_invalid_entity_type_in_storage_is_rejected(self):
        self.repository.save(self.entity)
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                "UPDATE knowledge_entities SET entity_type = ? WHERE entity_id = ?",
                ("NOT_REAL", "person-1"),
            )
            connection.commit()
        finally:
            connection.close()
        with self.assertRaises(EntityPersistenceError):
            self.repository.get("person-1")

    def test_invalid_json_in_storage_is_rejected(self):
        self.repository.save(self.entity)
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                "UPDATE knowledge_entities SET metadata_json = ? WHERE entity_id = ?",
                ("{broken", "person-1"),
            )
            connection.commit()
        finally:
            connection.close()
        with self.assertRaises(EntityPersistenceError):
            self.repository.get("person-1")

    def test_persistence_does_not_add_authority(self):
        self.repository.save(self.entity)
        payload = self.repository.require("person-1").to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["fact_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])

    def test_storage_is_json_encoded_without_authority_fields(self):
        self.repository.save(self.entity)
        connection = sqlite3.connect(self.database_path)
        try:
            row = connection.execute(
                "SELECT metadata_json, evidence_refs_json FROM knowledge_entities WHERE entity_id = ?",
                ("person-1",),
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(json.loads(row[0])["role"], "builder")
        self.assertEqual(json.loads(row[1]), ["evidence-1", "evidence-2"])

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(TypeError):
            self.repository.save("not-an-entity")
        with self.assertRaises(ValueError):
            self.repository.get(" ")
        with self.assertRaises(ValueError):
            self.repository.delete(" ")


if __name__ == "__main__":
    unittest.main()
