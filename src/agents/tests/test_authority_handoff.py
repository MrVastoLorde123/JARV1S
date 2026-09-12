import unittest

from src.agents.authority_handoff import (
    AuthorityHandoffPolicy,
    AuthorityHandoffRequest,
    AuthorityHandoffStatus,
)
from src.agents.claim_evidence import (
    Claim,
    ClaimEvidenceEvaluator,
    ClaimState,
    Evidence,
    EvidenceType,
)
from src.agents.consequence_gate import (
    ConsequenceAction,
    ConsequenceKind,
    ConsequenceRequest,
    ConsequenceDecision,
    EvidenceGatedConsequencePolicy,
)


class M31AuthorityHandoffTests(unittest.TestCase):
    def setUp(self):
        self.policy = AuthorityHandoffPolicy()
        self.claim = Claim(
            task_id="task-31",
            actor="coding_agent",
            payload={"objective": "advance workflow"},
            provenance={"operation_id": "op-31"},
        )
        self.consequence = ConsequenceRequest(
            kind=ConsequenceKind.ADVANCE_WORKFLOW,
            consequence_id="coding:advance",
            metadata={"scope": "coding"},
        )

    def decision(self, action):
        return ConsequenceDecision(
            claim_id=self.claim.claim_id,
            task_id=self.claim.task_id,
            consequence=self.consequence,
            action=action,
            reason="m30 reason",
            evidence_refs=("evidence-1",),
            verification_refs=("verification-1",),
        )

    def test_allow_becomes_ready_for_authority(self):
        handoff = self.policy.handoff(self.decision(ConsequenceAction.ALLOW))
        self.assertEqual(handoff.status, AuthorityHandoffStatus.READY_FOR_AUTHORITY)
        self.assertTrue(handoff.ready_for_authority)
        self.assertFalse(handoff.authorized)
        self.assertIn("authority layer", handoff.reason)

    def test_review_does_not_reach_authority_as_ready(self):
        handoff = self.policy.handoff(self.decision(ConsequenceAction.REQUIRE_REVIEW))
        self.assertEqual(handoff.status, AuthorityHandoffStatus.REQUIRE_REVIEW)
        self.assertFalse(handoff.ready_for_authority)
        self.assertFalse(handoff.authorized)

    def test_blocked_consequence_cannot_reach_authority(self):
        handoff = self.policy.handoff(self.decision(ConsequenceAction.BLOCK))
        self.assertEqual(handoff.status, AuthorityHandoffStatus.BLOCKED)
        self.assertFalse(handoff.ready_for_authority)
        self.assertFalse(handoff.authorized)

    def test_provenance_and_consequence_context_are_preserved(self):
        decision = self.decision(ConsequenceAction.ALLOW)
        handoff = self.policy.handoff(
            decision,
            authority_target="coding_confirmation",
            authority_context={"operation_id": "op-31"},
        )
        self.assertEqual(handoff.claim_id, decision.claim_id)
        self.assertEqual(handoff.task_id, decision.task_id)
        self.assertEqual(handoff.consequence_kind, decision.consequence.kind)
        self.assertEqual(handoff.consequence_id, decision.consequence.consequence_id)
        self.assertEqual(dict(handoff.consequence_metadata), {"scope": "coding"})
        self.assertEqual(handoff.evidence_refs, decision.evidence_refs)
        self.assertEqual(handoff.verification_refs, decision.verification_refs)
        self.assertEqual(handoff.authority_target, "coding_confirmation")
        self.assertEqual(dict(handoff.authority_context), {"operation_id": "op-31"})

    def test_context_and_consequence_metadata_are_immutable(self):
        decision = self.decision(ConsequenceAction.ALLOW)
        handoff = self.policy.handoff(
            decision,
            authority_context={"operation_id": "op-31"},
        )
        with self.assertRaises(TypeError):
            handoff.authority_context["operation_id"] = "changed"
        with self.assertRaises(TypeError):
            handoff.consequence_metadata["scope"] = "changed"

    def test_handoff_identity_is_deterministic(self):
        decision = self.decision(ConsequenceAction.ALLOW)
        first = self.policy.handoff(
            decision,
            authority_target="coding_confirmation",
            authority_context={"operation_id": "op-31"},
        )
        second = self.policy.handoff(
            decision,
            authority_target="coding_confirmation",
            authority_context={"operation_id": "op-31"},
        )
        self.assertEqual(first.handoff_id, second.handoff_id)

    def test_context_changes_handoff_identity(self):
        decision = self.decision(ConsequenceAction.ALLOW)
        first = self.policy.handoff(
            decision,
            authority_context={"operation_id": "op-31"},
        )
        second = self.policy.handoff(
            decision,
            authority_context={"operation_id": "op-32"},
        )
        self.assertNotEqual(first.handoff_id, second.handoff_id)

    def test_different_authority_targets_get_distinct_identity(self):
        decision = self.decision(ConsequenceAction.ALLOW)
        first = self.policy.handoff(decision, authority_target="coding_confirmation")
        second = self.policy.handoff(decision, authority_target="workflow_authority")
        self.assertNotEqual(first.handoff_id, second.handoff_id)

    def test_wrong_decision_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.policy.handoff(object())

    def test_empty_authority_target_is_rejected(self):
        decision = self.decision(ConsequenceAction.ALLOW)
        with self.assertRaises(ValueError):
            self.policy.handoff(decision, authority_target=" ")

    def test_wrong_authority_context_type_is_rejected(self):
        decision = self.decision(ConsequenceAction.ALLOW)
        with self.assertRaises(TypeError):
            self.policy.handoff(decision, authority_context=object())

    def test_handoff_request_contract_rejects_malformed_state(self):
        with self.assertRaises(ValueError):
            AuthorityHandoffRequest(
                handoff_id="",
                claim_id="claim",
                task_id="task",
                consequence_kind=ConsequenceKind.ADVANCE_WORKFLOW,
                consequence_id="coding:advance",
                consequence_metadata={},
                authority_target="existing_authority",
                authority_context={},
                status=AuthorityHandoffStatus.READY_FOR_AUTHORITY,
                reason="reason",
                evidence_refs=(),
                verification_refs=(),
            )

    def test_handoff_is_inert(self):
        decision = self.decision(ConsequenceAction.ALLOW)
        before = decision
        handoff = self.policy.handoff(decision)
        self.assertIs(decision, before)
        self.assertEqual(handoff.status, AuthorityHandoffStatus.READY_FOR_AUTHORITY)
        self.assertFalse(handoff.authorized)

    def test_m29_to_m30_to_m31_chain_preserves_verification(self):
        evaluator = ClaimEvidenceEvaluator()
        evidence = Evidence(
            task_id=self.claim.task_id,
            source_type=EvidenceType.TEST_RESULT,
            payload={"passed": True},
            provenance={"invocation_id": "run-31"},
        )
        evaluation = evaluator.evaluate(self.claim, (evidence,))
        self.assertEqual(evaluation.state, ClaimState.VERIFIED)

        consequence_decision = EvidenceGatedConsequencePolicy().decide(
            evaluation,
            self.consequence,
        )
        self.assertEqual(consequence_decision.action, ConsequenceAction.ALLOW)

        handoff = self.policy.handoff(
            consequence_decision,
            authority_target="coding_confirmation",
            authority_context={"operation_id": "op-31"},
        )
        self.assertEqual(handoff.status, AuthorityHandoffStatus.READY_FOR_AUTHORITY)
        self.assertEqual(handoff.claim_id, self.claim.claim_id)
        self.assertEqual(handoff.task_id, self.claim.task_id)
        self.assertEqual(handoff.evidence_refs, evaluation.evidence_refs)
        self.assertEqual(handoff.verification_refs, evaluation.verification_refs)
        self.assertEqual(handoff.authorized, False)


if __name__ == "__main__":
    unittest.main()
