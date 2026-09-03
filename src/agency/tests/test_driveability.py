import unittest

from src.agency.driveability import (
    ContinuationCycle,
    ContinuationDecision,
    ContinuationStopReason,
    DriveabilityController,
    NextStepProposal,
    Objective,
    ObjectiveState,
)


class DriveabilityTests(unittest.TestCase):
    def cycle(self, number=0, max_cycles=3):
        return ContinuationCycle(
            cycle_id=f"cycle-{number}",
            objective_id="obj-1",
            cycle_number=number,
            max_cycles=max_cycles,
        )

    def test_active_objective_produces_bounded_non_executing_proposal(self):
        objective = Objective("obj-1", "finish the project")
        decision = DriveabilityController().decide(
            objective,
            self.cycle(),
            observation_ids=("obs-1",),
            next_step="review the current implementation",
        )
        self.assertIsInstance(decision, ContinuationDecision)
        self.assertIsInstance(decision.proposal, NextStepProposal)
        self.assertEqual(decision.proposal.objective_id, "obj-1")
        self.assertFalse(decision.proposal.execution_requested)
        self.assertFalse(decision.proposal.authorization_granted)

    def test_objective_completion_stops(self):
        objective = Objective("obj-1", "finish", state=ObjectiveState.COMPLETED)
        decision = DriveabilityController().decide(objective, self.cycle())
        self.assertEqual(decision.stop_reason, ContinuationStopReason.COMPLETED)

    def test_objective_cancellation_stops(self):
        objective = Objective("obj-1", "finish", state=ObjectiveState.CANCELLED)
        decision = DriveabilityController().decide(objective, self.cycle())
        self.assertEqual(decision.stop_reason, ContinuationStopReason.CANCELLED)

    def test_uncertainty_stops_without_proposal(self):
        objective = Objective("obj-1", "finish")
        decision = DriveabilityController().decide(objective, self.cycle(), uncertain=True)
        self.assertEqual(decision.stop_reason, ContinuationStopReason.UNCERTAIN)
        self.assertIsNone(decision.proposal)

    def test_cycle_bound_stops_continuation(self):
        objective = Objective("obj-1", "finish")
        decision = DriveabilityController().decide(objective, self.cycle(number=2, max_cycles=3), next_step="continue")
        self.assertEqual(decision.stop_reason, ContinuationStopReason.BOUND_EXHAUSTED)

    def test_identity_mismatch_is_rejected(self):
        objective = Objective("obj-2", "finish")
        with self.assertRaises(ValueError):
            DriveabilityController().decide(objective, self.cycle())

    def test_proposals_cannot_be_unbounded_or_authorized(self):
        with self.assertRaises(ValueError):
            NextStepProposal(
                proposal_id="p1",
                objective_id="obj-1",
                cycle_id="cycle-0",
                description="do it",
                bounded=False,
            )
        with self.assertRaises(ValueError):
            NextStepProposal(
                proposal_id="p2",
                objective_id="obj-1",
                cycle_id="cycle-0",
                description="do it",
                authorization_granted=True,
            )


if __name__ == "__main__":
    unittest.main()
