import unittest

from src.agents.claim_evidence import (
    Claim,
    ClaimEvaluation,
    ClaimState,
)
from src.agents.coding_service import CodingAgentService
from src.agents.consequence_gate import (
    ConsequenceAction,
    ConsequenceKind,
    ConsequenceRequest,
)


class M30CodingServiceConsequenceTests(unittest.TestCase):
    def test_service_consumes_m29_evaluation_without_authorizing(self):
        service = CodingAgentService(
            planner=object(),
            worker=object(),
        )
        claim = Claim(
            task_id="task-30",
            actor="coding_agent",
            payload={"objective": "advance verified coding workflow"},
            provenance={"operation_id": "op-30"},
        )
        evaluation = ClaimEvaluation(
            claim=claim,
            state=ClaimState.VERIFIED,
            evidence_refs=("evidence-1",),
            verification_refs=("evidence-1",),
        )
        consequence = ConsequenceRequest(
            kind=ConsequenceKind.ADVANCE_WORKFLOW,
            consequence_id="coding:advance",
        )

        decision = service.decide_consequence(evaluation, consequence)

        self.assertEqual(decision.action, ConsequenceAction.ALLOW)
        self.assertTrue(decision.eligible)
        self.assertFalse(decision.authorized)
        self.assertEqual(decision.claim_id, claim.claim_id)
        self.assertEqual(decision.task_id, claim.task_id)


if __name__ == "__main__":
    unittest.main()
