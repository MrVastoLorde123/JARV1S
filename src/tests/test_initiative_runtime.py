import json
import unittest

from src.evaluation import InitiativeEvaluation
from src.initiative import InitiativeCandidate
from src.initiative_runtime import InitiativeRuntime, InitiativeRuntimeValidationError
from src.initiative_safety import check_initiative_safety
from src.opportunities import OpportunityDetection, OpportunityDetectionSet, DetectionType
from src.proposals import InitiativeProposal
from src.scheduling import ProactiveSchedule


class InitiativeRuntimeTests(unittest.TestCase):
    def _artifacts(self):
        detection = OpportunityDetection("d1", DetectionType.OPPORTUNITY, "Review", "Review project")
        detections = OpportunityDetectionSet((detection,))
        candidate = InitiativeCandidate("i1", "Review project", "Review this project.")
        evaluation = InitiativeEvaluation("e1", candidate, 0.8, 0.7, 0.9, 0.2, 0.1)
        proposal = InitiativeProposal("p1", evaluation, "Review project", "Review this project.", "Review the project")
        schedule = ProactiveSchedule("s1", proposal, "2026-09-04T09:00:00+00:00")
        safety = check_initiative_safety(proposal)
        return detections, candidate, evaluation, proposal, schedule, safety

    def test_empty_runtime_valid(self):
        runtime = InitiativeRuntime()
        self.assertIsNone(runtime.proposal)

    def test_accepts_complete_chain(self):
        artifacts = self._artifacts()
        runtime = InitiativeRuntime(*artifacts)
        self.assertIs(runtime.detections, artifacts[0])
        self.assertIs(runtime.candidate, artifacts[1])
        self.assertIs(runtime.evaluation, artifacts[2])
        self.assertIs(runtime.proposal, artifacts[3])
        self.assertIs(runtime.schedule, artifacts[4])
        self.assertIs(runtime.safety, artifacts[5])

    def test_candidate_evaluation_lineage_required(self):
        candidate = InitiativeCandidate("i1", "Review", "Review this.")
        other = InitiativeCandidate("i2", "Other", "Other.")
        evaluation = InitiativeEvaluation("e1", other, 0.5, 0.5, 0.5, 0.5, 0.5)
        with self.assertRaises(InitiativeRuntimeValidationError):
            InitiativeRuntime(candidate=candidate, evaluation=evaluation)

    def test_evaluation_proposal_lineage_required(self):
        candidate = InitiativeCandidate("i1", "Review", "Review this.")
        evaluation = InitiativeEvaluation("e1", candidate, 0.5, 0.5, 0.5, 0.5, 0.5)
        other_candidate = InitiativeCandidate("i2", "Other", "Other.")
        other_evaluation = InitiativeEvaluation("e2", other_candidate, 0.5, 0.5, 0.5, 0.5, 0.5)
        proposal = InitiativeProposal("p1", other_evaluation, "Other", "Other.", "Do other")
        with self.assertRaises(InitiativeRuntimeValidationError):
            InitiativeRuntime(evaluation=evaluation, proposal=proposal)

    def test_schedule_proposal_lineage_required(self):
        artifacts = self._artifacts()
        other_candidate = InitiativeCandidate("i2", "Other", "Other.")
        other_evaluation = InitiativeEvaluation("e2", other_candidate, 0.5, 0.5, 0.5, 0.5, 0.5)
        other_proposal = InitiativeProposal("p2", other_evaluation, "Other", "Other.", "Do other")
        schedule = ProactiveSchedule("s2", other_proposal, "2026-09-04T09:00:00+00:00")
        with self.assertRaises(InitiativeRuntimeValidationError):
            InitiativeRuntime(proposal=artifacts[3], schedule=schedule)

    def test_safety_lineage_required(self):
        artifacts = self._artifacts()
        altered = artifacts[5].__class__("other", True, artifacts[5].blocked_authority_transitions)
        with self.assertRaises(InitiativeRuntimeValidationError):
            InitiativeRuntime(proposal=artifacts[3], safety=altered)

    def test_safety_check_requires_proposal(self):
        with self.assertRaises(InitiativeRuntimeValidationError):
            InitiativeRuntime().safety_check()

    def test_safety_check_delegates_to_existing_boundary(self):
        artifacts = self._artifacts()
        runtime = InitiativeRuntime(proposal=artifacts[3])
        result = runtime.safety_check()
        self.assertTrue(result.safe_for_downstream_validation)
        self.assertFalse(result.to_dict()["authorization_granted"])

    def test_functional_updates(self):
        artifacts = self._artifacts()
        runtime = InitiativeRuntime()
        updated = runtime.with_detections(artifacts[0]).with_candidate(artifacts[1]).with_evaluation(artifacts[2])
        updated = updated.with_proposal(artifacts[3]).with_schedule(artifacts[4]).with_safety(artifacts[5])
        self.assertIsNone(runtime.candidate)
        self.assertIs(updated.proposal, artifacts[3])

    def test_to_dict_explicitly_non_authoritative(self):
        runtime = InitiativeRuntime()
        data = runtime.to_dict()
        self.assertFalse(data["initiative_is_instruction"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["execution_requested"])

    def test_json_serializable(self):
        data = json.loads(InitiativeRuntime().to_json())
        self.assertIsInstance(data, dict)

    def test_with_invalid_types_rejected(self):
        with self.assertRaises(InitiativeRuntimeValidationError):
            InitiativeRuntime(candidate="bad")
        with self.assertRaises(InitiativeRuntimeValidationError):
            InitiativeRuntime(proposal="bad")


if __name__ == "__main__":
    unittest.main()
