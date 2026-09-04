import json
import unittest

from src.knowledge.associations import (
    AssociationEvidence,
    AssociationEvidenceValidationError,
    EvidenceBackedAssociation,
    MAX_ASSOCIATION_EVIDENCE_REFS,
    MAX_EVIDENCE_REF_LENGTH,
    MAX_SOURCE_LENGTH,
)
from src.knowledge.relationships import Relationship, RelationshipType


class EvidenceBackedAssociationTests(unittest.TestCase):
    def make_relationship(self, refs=("evidence-1",)):
        return Relationship(
            relationship_id="rel-1",
            relationship_type=RelationshipType.WORKS_ON,
            source_entity_id="person-1",
            target_entity_id="project-1",
            evidence_refs=tuple(refs),
        )

    def make_evidence(self, ref="evidence-1", source="chat"):
        return AssociationEvidence(evidence_ref=ref, source=source)

    def test_evidence_requires_non_empty_reference(self):
        with self.assertRaises(AssociationEvidenceValidationError):
            self.make_evidence(ref=" ")

    def test_evidence_requires_non_empty_source(self):
        with self.assertRaises(AssociationEvidenceValidationError):
            self.make_evidence(source=" ")

    def test_evidence_reference_and_source_are_bounded(self):
        with self.assertRaises(AssociationEvidenceValidationError):
            self.make_evidence(ref="x" * (MAX_EVIDENCE_REF_LENGTH + 1))
        with self.assertRaises(AssociationEvidenceValidationError):
            self.make_evidence(source="x" * (MAX_SOURCE_LENGTH + 1))

    def test_association_requires_relationship(self):
        with self.assertRaises(AssociationEvidenceValidationError):
            EvidenceBackedAssociation(
                relationship="not-a-relationship",
                evidence=(self.make_evidence(),),
            )

    def test_association_requires_evidence(self):
        with self.assertRaises(AssociationEvidenceValidationError):
            EvidenceBackedAssociation(
                relationship=self.make_relationship(),
                evidence=(),
            )

    def test_association_requires_tuple_evidence(self):
        with self.assertRaises(AssociationEvidenceValidationError):
            EvidenceBackedAssociation(
                relationship=self.make_relationship(),
                evidence=[self.make_evidence()],
            )

    def test_evidence_must_be_associated_with_relationship_refs(self):
        with self.assertRaises(AssociationEvidenceValidationError):
            EvidenceBackedAssociation(
                relationship=self.make_relationship(),
                evidence=(self.make_evidence(ref="not-attached"),),
            )

    def test_evidence_refs_are_unique(self):
        with self.assertRaises(AssociationEvidenceValidationError):
            EvidenceBackedAssociation(
                relationship=self.make_relationship(refs=("evidence-1", "evidence-2")),
                evidence=(self.make_evidence(), self.make_evidence()),
            )

    def test_evidence_count_respects_shared_relationship_boundary(self):
        refs = tuple(
            f"evidence-{index}" for index in range(MAX_ASSOCIATION_EVIDENCE_REFS)
        )
        relationship = self.make_relationship(refs=refs)
        evidence = tuple(self.make_evidence(ref=ref) for ref in refs)
        association = EvidenceBackedAssociation(
            relationship=relationship,
            evidence=evidence,
        )
        self.assertEqual(len(association.evidence_refs), MAX_ASSOCIATION_EVIDENCE_REFS)

    def test_association_is_immutable(self):
        association = EvidenceBackedAssociation(
            relationship=self.make_relationship(),
            evidence=(self.make_evidence(),),
        )
        with self.assertRaises(AttributeError):
            association.relationship_id = "changed"

    def test_projection_preserves_relationship_and_evidence_identity(self):
        relationship = self.make_relationship(refs=("evidence-1", "evidence-2"))
        association = EvidenceBackedAssociation(
            relationship=relationship,
            evidence=(self.make_evidence("evidence-1"), self.make_evidence("evidence-2", "notes")),
        )
        self.assertEqual(association.relationship_id, "rel-1")
        self.assertEqual(association.relationship_type, RelationshipType.WORKS_ON)
        self.assertEqual(association.evidence_refs, ("evidence-1", "evidence-2"))

    def test_serialization_is_deterministic_and_json_compatible(self):
        association = EvidenceBackedAssociation(
            relationship=self.make_relationship(),
            evidence=(self.make_evidence(),),
        )
        first = association.to_json()
        second = association.to_json()
        self.assertEqual(first, second)
        payload = json.loads(first)
        self.assertTrue(payload["evidence_backed"])
        self.assertEqual(payload["evidence"][0]["evidence_ref"], "evidence-1")

    def test_serialization_makes_no_authority_claims(self):
        association = EvidenceBackedAssociation(
            relationship=self.make_relationship(),
            evidence=(self.make_evidence(),),
        )
        payload = association.to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["fact_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["relationship"]["truth_guaranteed"])
        self.assertFalse(payload["evidence"][0]["truth_guaranteed"])

    def test_evidence_backing_does_not_change_relationship(self):
        relationship = self.make_relationship()
        association = EvidenceBackedAssociation(
            relationship=relationship,
            evidence=(self.make_evidence(),),
        )
        self.assertIs(association.relationship, relationship)
        self.assertEqual(relationship.evidence_refs, ("evidence-1",))


if __name__ == "__main__":
    unittest.main()
