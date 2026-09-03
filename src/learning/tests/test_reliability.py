import unittest

from src.learning.reliability import (
    LearningReliabilityController,
    ReliabilityAssessment,
    ReliabilityConflictError,
    ReliabilityEvidence,
    ReliabilityRecord,
    ReliabilityState,
    ReliabilityStore,
)


class LearningReliabilityTests(unittest.TestCase):
    def evidence(self, *, evidence_id="e1", supports_reliability=True):
        return ReliabilityEvidence(
            evidence_id,
            "new observation",
            supports_reliability,
        )

    def assessment(self, *, artifact_id="memory-1", evidence=None):
        evidence = evidence or (self.evidence(),)
        return LearningReliabilityController().assess(
            artifact_id=artifact_id,
            evidence=evidence,
            confidence=0.8,
        )

    def test_evidence_is_bounded_and_immutable(self):
        evidence = self.evidence()
        with self.assertRaises(Exception):
            evidence.signal = "changed"
        with self.assertRaises(ValueError):
            ReliabilityEvidence("", "signal", True)

    def test_assessment_detects_conflicting_evidence(self):
        assessment = self.assessment(
            evidence=(self.evidence(evidence_id="e1", supports_reliability=True),
                      self.evidence(evidence_id="e2", supports_reliability=False))
        )
        self.assertEqual(assessment.state, ReliabilityState.CONFLICTED)

    def test_directionless_evidence_enters_watch(self):
        assessment = self.assessment(evidence=(self.evidence(supports_reliability=None),))
        self.assertEqual(assessment.state, ReliabilityState.WATCH)

    def test_negative_evidence_suspends_learning(self):
        assessment = self.assessment(evidence=(self.evidence(supports_reliability=False),))
        self.assertEqual(assessment.state, ReliabilityState.SUSPENDED)

    def test_initialize_preserves_assessment_identity(self):
        assessment = self.assessment()
        record = LearningReliabilityController().initialize(assessment)
        self.assertEqual(record.artifact_id, assessment.artifact_id)
        self.assertEqual(record.assessment_id, assessment.assessment_id)
        self.assertEqual(record.predecessor_id, None)

    def test_reliability_transition_preserves_history(self):
        controller = LearningReliabilityController()
        first = controller.initialize(self.assessment())
        second_assessment = self.assessment(
            evidence=(self.evidence(evidence_id="e2", supports_reliability=False),)
        )
        second = controller.transition(
            first,
            second_assessment,
            state=ReliabilityState.SUSPENDED,
        )
        self.assertEqual(second.predecessor_id, first.record_id)
        self.assertEqual(second.artifact_id, first.artifact_id)

    def test_reversal_requires_explicit_reference(self):
        controller = LearningReliabilityController()
        first = controller.initialize(self.assessment())
        with self.assertRaises(ValueError):
            controller.transition(
                first,
                self.assessment(evidence=(self.evidence(supports_reliability=False),)),
                state=ReliabilityState.REVERSED,
            )

    def test_reversal_does_not_delete_history(self):
        controller = LearningReliabilityController()
        first = controller.initialize(self.assessment())
        reversed_record = controller.transition(
            first,
            self.assessment(evidence=(self.evidence(supports_reliability=False),)),
            state=ReliabilityState.REVERSED,
            reference="evidence-review-1",
        )
        store = ReliabilityStore((first,)).append(reversed_record)
        self.assertEqual(len(store.history("memory-1")), 2)
        self.assertEqual(store.current("memory-1").state, ReliabilityState.REVERSED)

    def test_supersession_requires_reference_and_preserves_predecessor(self):
        controller = LearningReliabilityController()
        first = controller.initialize(self.assessment())
        second = controller.transition(
            first,
            self.assessment(),
            state=ReliabilityState.SUPERSEDED,
            reference="replacement-1",
            supersession_reference="replacement-1",
        )
        self.assertEqual(second.state, ReliabilityState.SUPERSEDED)
        self.assertEqual(second.predecessor_id, first.record_id)
        self.assertEqual(second.supersession_reference, "replacement-1")

    def test_terminal_states_cannot_transition(self):
        controller = LearningReliabilityController()
        first = controller.initialize(self.assessment())
        reversed_record = controller.transition(
            first,
            self.assessment(evidence=(self.evidence(supports_reliability=False),)),
            state=ReliabilityState.REVERSED,
            reference="review-1",
        )
        with self.assertRaises(ValueError):
            controller.transition(
                reversed_record,
                self.assessment(),
                state=ReliabilityState.RETAINED,
            )

    def test_store_is_immutable_and_conflict_aware(self):
        record = LearningReliabilityController().initialize(self.assessment())
        store = ReliabilityStore()
        updated = store.append(record)
        self.assertEqual(store.records, ())
        self.assertEqual(updated.records, (record,))
        with self.assertRaises(ReliabilityConflictError):
            updated.append(record)

    def test_store_requires_existing_predecessor(self):
        record = ReliabilityRecord(
            record_id="memory-1:reliability:2",
            artifact_id="memory-1",
            state=ReliabilityState.WATCH,
            assessment_id="memory-1:reliability:2-assessment",
            predecessor_id="missing",
        )
        with self.assertRaises(ReliabilityConflictError):
            ReliabilityStore((record,))

    def test_serialization_is_non_authoritative_and_deterministic(self):
        record = LearningReliabilityController().initialize(self.assessment())
        store = ReliabilityStore((record,))
        first = store.to_json()
        second = store.to_json()
        self.assertEqual(first, second)
        self.assertIn('"authority_granted": false', first)
        self.assertIn('"authorization_granted": false', first)
        self.assertIn('"execution_requested": false', first)
        self.assertIn('"policy_mutation": false', first)


if __name__ == "__main__":
    unittest.main()
