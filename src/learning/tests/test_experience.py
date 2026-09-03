import unittest

from src.learning.experience import Experience, ExperienceConflictError, ExperienceStore


class ExperienceTests(unittest.TestCase):
    def experience(self, **overrides):
        values = {
            "experience_id": "exp-1",
            "source": "execution",
            "objective_id": "obj-1",
            "action_reference": "action-1",
            "decision_reference": "decision-1",
            "observations": ("obs-1", "obs-2"),
            "outcome": "task completed",
            "user_feedback": "worked well",
            "evaluation": "preferred this sequence",
            "confidence": 0.8,
            "provenance": {"source_id": "exec:action-1"},
        }
        values.update(overrides)
        return Experience(**values)

    def test_experience_is_immutable(self):
        experience = self.experience()
        with self.assertRaises(Exception):
            experience.outcome = "changed"

    def test_experience_requires_identity_and_source(self):
        with self.assertRaises(ValueError):
            Experience(experience_id="", source="execution")
        with self.assertRaises(ValueError):
            Experience(experience_id="exp-1", source="")

    def test_experience_observations_are_unique_and_typed(self):
        with self.assertRaises(ValueError):
            self.experience(observations=("obs-1", "obs-1"))
        with self.assertRaises(TypeError):
            self.experience(observations=["obs-1"])

    def test_confidence_is_bounded(self):
        self.experience(confidence=0.0)
        self.experience(confidence=1.0)
        with self.assertRaises(ValueError):
            self.experience(confidence=1.1)
        with self.assertRaises(ValueError):
            self.experience(confidence=-0.1)

    def test_serialization_preserves_evidence_but_grants_no_authority(self):
        payload = self.experience().to_dict()
        self.assertEqual(payload["experience_id"], "exp-1")
        self.assertEqual(payload["observations"], ("obs-1", "obs-2"))
        self.assertEqual(payload["outcome"], "task completed")
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])

    def test_store_is_immutable(self):
        store = ExperienceStore()
        updated = store.append(self.experience())
        self.assertEqual(len(store.list()), 0)
        self.assertEqual(len(updated.list()), 1)
        self.assertEqual(updated.get("exp-1"), self.experience())

    def test_store_rejects_duplicate_identity(self):
        store = ExperienceStore().append(self.experience())
        with self.assertRaises(ExperienceConflictError):
            store.append(self.experience())

    def test_store_rejects_duplicate_initial_state(self):
        with self.assertRaises(ExperienceConflictError):
            ExperienceStore((self.experience(), self.experience()))

    def test_feedback_and_evaluation_are_distinct_fields(self):
        experience = self.experience(
            user_feedback="user preferred concise output",
            evaluation="concise output reduced rework",
        )
        self.assertNotEqual(experience.user_feedback, experience.evaluation)

    def test_json_serialization_is_deterministic(self):
        self.assertEqual(self.experience().to_json(), self.experience().to_json())


if __name__ == "__main__":
    unittest.main()
