from __future__ import annotations

import unittest

from src.agents.claim_evidence import (
    Claim,
    ClaimEvidenceEvaluator,
    ClaimState,
    Evidence,
    EvidenceType,
)


class M29ClaimEvidenceTests(unittest.TestCase):
    def make_claim(self) -> Claim:
        return Claim(
            task_id="task-1",
            actor="coding_agent",
            payload={"statement": "ui/index.html was updated"},
            provenance={"operation_id": "op-1"},
        )

    def test_agent_claim_starts_proposed(self) -> None:
        claim = self.make_claim()

        self.assertEqual(claim.state, ClaimState.PROPOSED)
        self.assertTrue(claim.claim_id.startswith("claim-"))

    def test_claim_identity_is_deterministic(self) -> None:
        first = self.make_claim()
        second = self.make_claim()

        self.assertEqual(first.claim_id, second.claim_id)
        self.assertEqual(first.payload, second.payload)
        self.assertEqual(first.provenance, second.provenance)

    def test_evidence_identity_is_deterministic(self) -> None:
        first = Evidence(
            task_id="task-1",
            source_type=EvidenceType.FILESYSTEM_OBSERVATION,
            payload={"path": "ui/index.html", "exists": True},
            provenance={"tool": "read_file"},
        )
        second = Evidence(
            task_id="task-1",
            source_type=EvidenceType.FILESYSTEM_OBSERVATION,
            payload={"path": "ui/index.html", "exists": True},
            provenance={"tool": "read_file"},
        )

        self.assertEqual(first.evidence_id, second.evidence_id)
        self.assertTrue(first.evidence_id.startswith("evidence-"))

    def test_no_evidence_evaluates_unknown(self) -> None:
        evaluation = ClaimEvidenceEvaluator().evaluate(self.make_claim(), ())

        self.assertEqual(evaluation.state, ClaimState.UNKNOWN)
        self.assertEqual(evaluation.evidence_refs, ())
        self.assertEqual(evaluation.verification_refs, ())

    def test_tool_observation_supports_claim_but_does_not_verify(self) -> None:
        evidence = Evidence(
            task_id="task-1",
            source_type=EvidenceType.FILESYSTEM_OBSERVATION,
            payload={"path": "ui/index.html", "contains_indicator": True},
            provenance={"tool": "read_file"},
        )

        evaluation = ClaimEvidenceEvaluator().evaluate(self.make_claim(), (evidence,))

        self.assertEqual(evaluation.state, ClaimState.SUPPORTED)
        self.assertEqual(evaluation.evidence_refs, (evidence.evidence_id,))
        self.assertEqual(evaluation.verification_refs, ())

    def test_build_pass_elevates_claim_to_verified(self) -> None:
        evidence = Evidence(
            task_id="task-1",
            source_type=EvidenceType.BUILD_RESULT,
            payload={"runner": "npm_build", "passed": True, "exit_code": 0},
            provenance={"tool": "run_test", "operation_id": "op-1"},
        )

        evaluation = ClaimEvidenceEvaluator().evaluate(self.make_claim(), (evidence,))

        self.assertEqual(evaluation.state, ClaimState.VERIFIED)
        self.assertEqual(evaluation.verification_refs, (evidence.evidence_id,))

    def test_failed_verification_contradicts_claim(self) -> None:
        evidence = Evidence(
            task_id="task-1",
            source_type=EvidenceType.TEST_RESULT,
            payload={"runner": "python_unittest", "passed": False, "exit_code": 1},
            provenance={"tool": "run_test"},
        )

        evaluation = ClaimEvidenceEvaluator().evaluate(self.make_claim(), (evidence,))

        self.assertEqual(evaluation.state, ClaimState.CONTRADICTED)
        self.assertEqual(evaluation.verification_refs, (evidence.evidence_id,))

    def test_explicit_contradiction_dominates_supporting_evidence(self) -> None:
        support = Evidence(
            task_id="task-1",
            source_type=EvidenceType.FILESYSTEM_OBSERVATION,
            payload={"contains_indicator": True},
            provenance={"tool": "read_file"},
        )
        contradiction = Evidence(
            task_id="task-1",
            source_type=EvidenceType.CONTRADICTION,
            payload={"reason": "file content differs from claimed state"},
            provenance={"tool": "read_file"},
        )

        evaluation = ClaimEvidenceEvaluator().evaluate(self.make_claim(), (support, contradiction))

        self.assertEqual(evaluation.state, ClaimState.CONTRADICTED)

    def test_wrong_task_evidence_is_rejected(self) -> None:
        evidence = Evidence(
            task_id="task-2",
            source_type=EvidenceType.BUILD_RESULT,
            payload={"passed": True},
            provenance={"tool": "run_test"},
        )

        with self.assertRaises(ValueError):
            ClaimEvidenceEvaluator().evaluate(self.make_claim(), (evidence,))

    def test_accepted_claim_preserves_claim_identity_and_is_inert(self) -> None:
        claim = self.make_claim()
        evidence = Evidence(
            task_id="task-1",
            source_type=EvidenceType.BUILD_RESULT,
            payload={"passed": True},
            provenance={"tool": "run_test"},
        )
        evaluation = ClaimEvidenceEvaluator().evaluate(claim, (evidence,))
        accepted = ClaimEvidenceEvaluator.accepted_claim(claim, evaluation)

        self.assertEqual(accepted.claim_id, claim.claim_id)
        self.assertEqual(accepted.state, ClaimState.VERIFIED)
        self.assertEqual(accepted.verification_refs, (evidence.evidence_id,))
        self.assertNotIn("authorize", accepted.payload)

    def test_records_are_immutable(self) -> None:
        claim = self.make_claim()
        evidence = Evidence(
            task_id="task-1",
            source_type=EvidenceType.TOOL_OBSERVATION,
            payload={"value": {"nested": True}},
            provenance={"tool": "read_file"},
        )

        with self.assertRaises(TypeError):
            claim.payload["new"] = "value"  # type: ignore[index]
        with self.assertRaises(TypeError):
            evidence.payload["new"] = "value"  # type: ignore[index]


if __name__ == "__main__":
    unittest.main()
