from datetime import datetime, timedelta, timezone
import unittest

from src.proactive import (
    InitiativeCandidate,
    InitiativeDisposition,
    ProactiveTrigger,
    ProactiveTriggerSource,
    evaluate_initiative,
)


class InitiativeBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observed_at = datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc)
        self.trigger = ProactiveTrigger(
            trigger_id="trigger-1",
            source=ProactiveTriggerSource.OBSERVATION,
            reference_id="obs-1",
            signal="task may need attention",
            observed_at=self.observed_at,
            evidence_ids=("e1",),
            metadata={"origin": "test"},
        )
        self.candidate = InitiativeCandidate(
            candidate_id="candidate-1",
            trigger_id="trigger-1",
            title="Review stalled task",
            rationale="Observed state suggests attention may be useful.",
            evidence_ids=("e1",),
            expires_at=self.observed_at + timedelta(hours=1),
        )

    def test_trigger_is_immutable(self) -> None:
        with self.assertRaises(AttributeError):
            self.trigger.signal = "changed"

    def test_trigger_metadata_is_isolated(self) -> None:
        original = {"origin": "test"}
        trigger = ProactiveTrigger(
            trigger_id="t",
            source=ProactiveTriggerSource.SYSTEM_SIGNAL,
            reference_id="r",
            signal="signal",
            observed_at=self.observed_at,
            metadata=original,
        )
        original["origin"] = "mutated"
        self.assertEqual(trigger.metadata["origin"], "test")

    def test_candidate_rejects_authorization(self) -> None:
        with self.assertRaises(ValueError):
            InitiativeCandidate(
                candidate_id="c",
                trigger_id="t",
                title="candidate",
                rationale="reason",
                authorization_granted=True,
            )

    def test_candidate_rejects_execution(self) -> None:
        with self.assertRaises(ValueError):
            InitiativeCandidate(
                candidate_id="c",
                trigger_id="t",
                title="candidate",
                rationale="reason",
                execution_requested=True,
            )

    def test_identity_mismatch_is_rejected(self) -> None:
        candidate = InitiativeCandidate(
            candidate_id="c",
            trigger_id="different-trigger",
            title="candidate",
            rationale="reason",
        )
        with self.assertRaises(ValueError):
            evaluate_initiative(self.trigger, candidate, now=self.observed_at)

    def test_eligible_does_not_mean_authorized(self) -> None:
        evaluation = evaluate_initiative(self.trigger, self.candidate, now=self.observed_at)
        self.assertEqual(evaluation.disposition, InitiativeDisposition.ELIGIBLE)
        context = evaluation.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["execution_requested"])

    def test_suppression_wins_deterministically(self) -> None:
        evaluation = evaluate_initiative(
            self.trigger,
            self.candidate,
            now=self.observed_at,
            suppressed=True,
            needs_review=True,
        )
        self.assertEqual(evaluation.disposition, InitiativeDisposition.SUPPRESSED)

    def test_expiry_is_deterministic(self) -> None:
        evaluation = evaluate_initiative(
            self.trigger,
            self.candidate,
            now=self.candidate.expires_at,
        )
        self.assertEqual(evaluation.disposition, InitiativeDisposition.EXPIRED)

    def test_review_remains_bounded(self) -> None:
        evaluation = evaluate_initiative(
            self.trigger,
            self.candidate,
            now=self.observed_at,
            needs_review=True,
        )
        self.assertEqual(evaluation.disposition, InitiativeDisposition.NEEDS_REVIEW)

    def test_context_exposes_no_authority(self) -> None:
        trigger_context = self.trigger.to_context()
        candidate_context = self.candidate.to_context()
        self.assertFalse(trigger_context["authorization_granted"])
        self.assertFalse(trigger_context["execution_requested"])
        self.assertFalse(candidate_context["authorization_granted"])
        self.assertFalse(candidate_context["execution_requested"])

    def test_naive_datetime_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ProactiveTrigger(
                trigger_id="t",
                source=ProactiveTriggerSource.OBSERVATION,
                reference_id="r",
                signal="signal",
                observed_at=datetime(2026, 9, 4, 12, 0),
            )


if __name__ == "__main__":
    unittest.main()
