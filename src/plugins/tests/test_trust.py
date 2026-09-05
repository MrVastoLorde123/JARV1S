import unittest

from src.plugins.trust import (
    CapabilityProvenance,
    CapabilityTrustAssessment,
    CapabilityTrustError,
    ProvenanceEvidence,
    TrustStatus,
)


class CapabilityTrustTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = ProvenanceEvidence(
            evidence_type="publisher-verification",
            source="trusted-source",
            detail="Publisher identity was independently verified.",
        )
        self.provenance = CapabilityProvenance(
            capability_id="file.read",
            source="github",
            origin="owner/repository@abc123",
            publisher="owner",
            integrity_status="verified",
            verification_method="commit-digest",
            evidence=(self.evidence,),
        )

    def test_provenance_is_immutable(self) -> None:
        with self.assertRaises(Exception):
            self.provenance.origin = "changed"

    def test_provenance_requires_core_origin_fields(self) -> None:
        for kwargs in (
            {"capability_id": "", "source": "x", "origin": "x"},
            {"capability_id": "id", "source": "", "origin": "x"},
            {"capability_id": "id", "source": "x", "origin": ""},
            {"capability_id": "id", "source": "x", "origin": "x", "publisher": ""},
        ):
            with self.assertRaises(CapabilityTrustError):
                CapabilityProvenance(**kwargs)

    def test_evidence_is_structured_and_immutable(self) -> None:
        with self.assertRaises(Exception):
            self.evidence.detail = "changed"
        context = self.evidence.metadata
        self.assertEqual(context, {})

    def test_assessment_requires_bounded_confidence(self) -> None:
        for confidence in (-0.01, 1.01):
            with self.assertRaises(CapabilityTrustError):
                CapabilityTrustAssessment(
                    capability_id="file.read",
                    status=TrustStatus.CONDITIONAL,
                    confidence=confidence,
                    evidence=(self.evidence,),
                )

    def test_unassessed_trust_has_zero_confidence(self) -> None:
        assessment = CapabilityTrustAssessment(
            capability_id="file.read",
            status=TrustStatus.UNASSESSED,
            confidence=0.0,
        )
        self.assertEqual(assessment.status, TrustStatus.UNASSESSED)

    def test_assessed_trust_requires_supporting_evidence(self) -> None:
        for status in (
            TrustStatus.CONDITIONAL,
            TrustStatus.TRUSTED,
            TrustStatus.UNTRUSTED,
        ):
            with self.assertRaises(CapabilityTrustError):
                CapabilityTrustAssessment(
                    capability_id="file.read",
                    status=status,
                    confidence=0.8,
                )

    def test_assessment_requires_matching_capability_identity(self) -> None:
        assessment = CapabilityTrustAssessment(
            capability_id="web.search",
            status=TrustStatus.TRUSTED,
            confidence=0.9,
            evidence=(self.evidence,),
        )
        with self.assertRaises(CapabilityTrustError):
            assessment.validate_for(self.provenance)

    def test_assessment_is_evidence_linked_but_has_no_authority(self) -> None:
        assessment = CapabilityTrustAssessment(
            capability_id="file.read",
            status=TrustStatus.TRUSTED,
            confidence=0.9,
            evidence=(self.evidence,),
            rationale=("Publisher and integrity evidence verified.",),
            assessor="test-assessor",
        )
        assessment.validate_for(self.provenance)
        context = assessment.to_context()
        self.assertEqual(context["trust_status"], "TRUSTED")
        self.assertEqual(context["evidence_count"], 1)
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_provenance_context_has_no_permission_semantics(self) -> None:
        context = self.provenance.to_context()
        self.assertEqual(context["integrity_status"], "verified")
        self.assertEqual(context["evidence_count"], 1)
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])


if __name__ == "__main__":
    unittest.main()
