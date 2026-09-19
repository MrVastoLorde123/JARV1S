import unittest

from src.agents.claim_evidence import (
    Claim,
    ClaimEvidenceEvaluator,
    ClaimEvaluation,
    ClaimState,
    VerificationFreshness,
    Evidence,
    EvidenceType,
)
from src.agents.consequence_gate import (
    ConsequenceAction,
    ConsequenceKind,
    ConsequenceRequest,
    EvidenceGatedConsequencePolicy,
)


class M30ConsequenceGateTests(unittest.TestCase):
    def setUp(self):
        self.evaluator = ClaimEvidenceEvaluator()
        self.policy = EvidenceGatedConsequencePolicy()
        self.consequence = ConsequenceRequest(
            kind=ConsequenceKind.ADVANCE_WORKFLOW,
            consequence_id="coding:advance",
        )

    @staticmethod
    def claim(task_id="task-1"):
        return Claim(
            task_id=task_id,
            actor="coding_agent",
            payload={"objective": "update implementation"},
            provenance={"operation_id": "op-1"},
        )

    def test_verified_allows_consequence_eligibility(self):
        claim = self.claim()
        evidence = Evidence(
            task_id=claim.task_id,
            source_type=EvidenceType.TEST_RESULT,
            payload={"passed": True},
            provenance={"invocation_id": "run-1"},
        )
        evaluation = self.evaluator.evaluate(claim, (evidence,))
        decision = self.policy.decide(evaluation, self.consequence)

        self.assertEqual(evaluation.state, ClaimState.VERIFIED)
        self.assertEqual(decision.action, ConsequenceAction.ALLOW)
        self.assertTrue(decision.eligible)
        self.assertFalse(decision.authorized)
        self.assertEqual(decision.claim_id, claim.claim_id)
        self.assertEqual(decision.task_id, claim.task_id)
        self.assertEqual(decision.verification_refs, (evidence.evidence_id,))

    def test_verified_historical_evidence_still_allows_without_current_requirement(self):
        claim = self.claim()
        evidence = Evidence(
            task_id=claim.task_id,
            source_type=EvidenceType.TEST_RESULT,
            payload={
                "passed": True,
                "verification_freshness_state": "STALE",
            },
            provenance={"invocation_id": "run-stale"},
        )
        evaluation = self.evaluator.evaluate(claim, (evidence,))
        decision = self.policy.decide(evaluation, self.consequence)

        self.assertEqual(evaluation.state, ClaimState.VERIFIED)
        self.assertEqual(evaluation.verification_freshness, VerificationFreshness.STALE)
        self.assertEqual(decision.action, ConsequenceAction.ALLOW)
        self.assertEqual(decision.verification_freshness, VerificationFreshness.STALE)
        self.assertFalse(decision.authorized)

    def test_current_requirement_allows_only_fresh_verification(self):
        claim = self.claim()
        evidence = Evidence(
            task_id=claim.task_id,
            source_type=EvidenceType.BUILD_RESULT,
            payload={
                "passed": True,
                "verification_freshness_state": "FRESH",
            },
            provenance={"invocation_id": "run-fresh"},
        )
        evaluation = self.evaluator.evaluate(claim, (evidence,))
        consequence = ConsequenceRequest(
            kind=ConsequenceKind.ADVANCE_WORKFLOW,
            consequence_id="coding:advance-current",
            metadata={"requires_current_verification": True},
        )

        decision = self.policy.decide(evaluation, consequence)

        self.assertEqual(evaluation.verification_freshness, VerificationFreshness.FRESH)
        self.assertEqual(decision.action, ConsequenceAction.ALLOW)
        self.assertTrue(decision.eligible)
        self.assertFalse(decision.authorized)

    def test_current_requirement_rejects_stale_verification_as_review_required(self):
        claim = self.claim()
        evidence = Evidence(
            task_id=claim.task_id,
            source_type=EvidenceType.BUILD_RESULT,
            payload={
                "passed": True,
                "verification_freshness_state": "STALE",
            },
            provenance={"invocation_id": "run-stale-current"},
        )
        evaluation = self.evaluator.evaluate(claim, (evidence,))
        consequence = ConsequenceRequest(
            kind=ConsequenceKind.MARK_COMPLETED,
            consequence_id="coding:complete-current",
            metadata={"requires_current_verification": True},
        )

        decision = self.policy.decide(evaluation, consequence)

        self.assertEqual(evaluation.state, ClaimState.VERIFIED)
        self.assertEqual(evaluation.verification_freshness, VerificationFreshness.STALE)
        self.assertEqual(decision.action, ConsequenceAction.REQUIRE_REVIEW)
        self.assertFalse(decision.eligible)
        self.assertIn("STALE", decision.reason)

    def test_current_requirement_rejects_unassessed_verification_as_review_required(self):
        claim = self.claim()
        evidence = Evidence(
            task_id=claim.task_id,
            source_type=EvidenceType.BUILD_RESULT,
            payload={"passed": True},
            provenance={"invocation_id": "run-unassessed"},
        )
        evaluation = self.evaluator.evaluate(claim, (evidence,))
        consequence = ConsequenceRequest(
            kind=ConsequenceKind.MARK_COMPLETED,
            consequence_id="coding:complete-current-unassessed",
            metadata={"requires_current_verification": True},
        )

        decision = self.policy.decide(evaluation, consequence)

        self.assertEqual(evaluation.state, ClaimState.VERIFIED)
        self.assertEqual(
            evaluation.verification_freshness,
            VerificationFreshness.UNASSESSED,
        )
        self.assertEqual(decision.action, ConsequenceAction.REQUIRE_REVIEW)
        self.assertFalse(decision.eligible)
        self.assertIn("UNASSESSED", decision.reason)


    def test_supported_requires_review(self):
        claim = self.claim()
        evidence = Evidence(
            task_id=claim.task_id,
            source_type=EvidenceType.FILESYSTEM_OBSERVATION,
            payload={"path": "ui/index.html", "written": True},
            provenance={"invocation_id": "write-1"},
        )
        evaluation = self.evaluator.evaluate(claim, (evidence,))
        decision = self.policy.decide(evaluation, self.consequence)

        self.assertEqual(evaluation.state, ClaimState.SUPPORTED)
        self.assertEqual(decision.action, ConsequenceAction.REQUIRE_REVIEW)
        self.assertFalse(decision.eligible)
        self.assertFalse(decision.authorized)

    def test_no_evidence_blocks(self):
        claim = self.claim()
        evaluation = self.evaluator.evaluate(claim, ())
        decision = self.policy.decide(evaluation, self.consequence)

        self.assertEqual(evaluation.state, ClaimState.UNKNOWN)
        self.assertEqual(decision.action, ConsequenceAction.BLOCK)
        self.assertFalse(decision.eligible)
        self.assertIn("lacks sufficient evidence", decision.reason)

    def test_proposed_blocks(self):
        claim = self.claim()
        evaluation = self.evaluator.evaluate(claim, ())
        evaluation = ClaimEvaluation(
            claim=claim,
            state=ClaimState.PROPOSED,
            evidence_refs=(),
            verification_refs=(),
        )
        decision = self.policy.decide(evaluation, self.consequence)
        self.assertEqual(decision.action, ConsequenceAction.BLOCK)

    def test_contradicted_blocks(self):
        claim = self.claim()
        evidence = Evidence(
            task_id=claim.task_id,
            source_type=EvidenceType.CONTRADICTION,
            payload={"reason": "implementation failed"},
            provenance={"source": "verification"},
        )
        evaluation = self.evaluator.evaluate(claim, (evidence,))
        decision = self.policy.decide(evaluation, self.consequence)

        self.assertEqual(evaluation.state, ClaimState.CONTRADICTED)
        self.assertEqual(decision.action, ConsequenceAction.BLOCK)

    def test_disputed_blocks(self):
        claim = self.claim()
        evaluation = ClaimEvaluation(
            claim=claim,
            state=ClaimState.DISPUTED,
            evidence_refs=(),
            verification_refs=(),
        )
        decision = self.policy.decide(evaluation, self.consequence)
        self.assertEqual(decision.action, ConsequenceAction.BLOCK)

    def test_rejects_wrong_types(self):
        with self.assertRaises(TypeError):
            self.policy.decide(object(), self.consequence)
        with self.assertRaises(TypeError):
            self.policy.decide(
                self.evaluator.evaluate(self.claim(), ()),
                object(),
            )

    def test_unknown_consequence_kind_is_blocked(self):
        class FakeKind:
            value = "UNDEFINED"

        claim = self.claim()
        evidence = Evidence(
            task_id=claim.task_id,
            source_type=EvidenceType.TEST_RESULT,
            payload={"passed": True},
            provenance={"invocation_id": "run-1"},
        )
        evaluation = self.evaluator.evaluate(claim, (evidence,))
        consequence = object.__new__(ConsequenceRequest)
        object.__setattr__(consequence, "kind", FakeKind())
        object.__setattr__(consequence, "consequence_id", "unknown")
        object.__setattr__(consequence, "metadata", None)
        decision = self.policy.decide(evaluation, consequence)
        self.assertEqual(decision.action, ConsequenceAction.BLOCK)

    def test_mismatched_task_provenance_is_preserved(self):
        claim = self.claim("task-42")
        evaluation = self.evaluator.evaluate(claim, ())
        decision = self.policy.decide(evaluation, self.consequence)
        self.assertEqual(decision.task_id, "task-42")
        self.assertEqual(decision.claim_id, claim.claim_id)


if __name__ == "__main__":
    unittest.main()
